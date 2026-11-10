import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

import struct  # noqa: E402
import zlib  # noqa: E402

from capture import is_black_frame, is_settled, moving_warnings  # noqa: E402

LAUNCH, UI = b"blank launch screen", b"home screen"
PROBE = Path(__file__).resolve().parent.parent / "research" / "rtl-probe" / "results"


def png(pixel: bytes, width: int = 4, height: int = 3, filt: int = 0) -> bytes:
    """A flat 8-bit RGB or RGBA PNG, every row stored with one filter type (0 None, 1 Sub, 2 Up)."""
    n = len(pixel)
    rows = []
    for y in range(height):
        raw = pixel * width
        if filt == 1:
            raw = pixel + bytes(n * (width - 1))
        elif filt == 2 and y > 0:
            raw = bytes(n * width)
        rows.append(bytes([filt]) + raw)
    return encode(b"".join(rows), width, height, n)


def encode(rows: bytes, width: int, height: int, channels: int) -> bytes:
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6 if channels == 4 else 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(rows))
            + chunk(b"IEND", b""))


class BlackFrames(unittest.TestCase):
    def test_flat_black_is_black_with_any_filter(self):
        for filt in (0, 1, 2):
            self.assertTrue(is_black_frame(png(b"\x00\x00\x00\xff", filt=filt)), filt)
            self.assertTrue(is_black_frame(png(b"\x00\x00\x00", filt=filt)), filt)

    def test_flat_white_and_grey_are_not_black(self):
        for filt in (0, 1, 2):
            self.assertFalse(is_black_frame(png(b"\xff\xff\xff\xff", filt=filt)), filt)
            self.assertFalse(is_black_frame(png(b"\x80\x80\x80", filt=filt)), filt)

    def test_one_lit_pixel_is_not_black(self):
        rows = bytes([0]) + bytes(12) + bytes([0]) + bytes([0, 0, 0, 0, 40, 0]) + bytes(6) + bytes([0]) + bytes(12)
        self.assertFalse(is_black_frame(encode(rows, 4, 3, 3)))

    def test_not_a_png(self):
        self.assertFalse(is_black_frame(b"home screen"))

    def test_black_frames_never_settle(self):
        black = png(b"\x00\x00\x00\xff")
        self.assertFalse(is_settled(black, black, LAUNCH))

    @unittest.skipUnless(PROBE.is_dir(), "probe captures not present")
    def test_real_simulator_captures(self):
        # The outer display is off while the Duo is open, so its capture is black.
        self.assertTrue(is_black_frame((PROBE / "open" / "split-en" / "display-1.png").read_bytes()))
        self.assertFalse(is_black_frame((PROBE / "open" / "split-en" / "display-3.png").read_bytes()))
        self.assertFalse(is_black_frame((PROBE / "half" / "split-ar" / "display-3.png").read_bytes()))


class Settling(unittest.TestCase):
    def test_two_identical_app_frames_settle(self):
        self.assertTrue(is_settled(UI, UI, LAUNCH))

    def test_blank_launch_screen_twice_does_not_settle(self):
        self.assertFalse(is_settled(LAUNCH, LAUNCH, LAUNCH))

    def test_changing_frames_do_not_settle(self):
        self.assertFalse(is_settled(LAUNCH, UI, LAUNCH))
        self.assertFalse(is_settled(None, UI, LAUNCH))


class RegularIphone(unittest.TestCase):
    def test_booted_non_duo_iphone_is_preferred(self):
        from dhwg_common import pick_regular_iphone
        t = "com.apple.CoreSimulator.SimDeviceType."
        devices = [
            {"udid": "duo", "deviceTypeIdentifier": t + "iPhone-Duo", "state": "Booted"},
            {"udid": "ipad", "deviceTypeIdentifier": t + "iPad-Pro-11-inch-M5-12GB", "state": "Booted"},
            {"udid": "17-off", "deviceTypeIdentifier": t + "iPhone-17", "state": "Shutdown"},
            {"udid": "18-on", "deviceTypeIdentifier": t + "iPhone-18-Pro-Max", "state": "Booted"},
            {"udid": "gone", "deviceTypeIdentifier": t + "iPhone-17", "state": "Booted", "isAvailable": False},
        ]
        self.assertEqual(pick_regular_iphone(devices)["udid"], "18-on")
        self.assertEqual(pick_regular_iphone(devices[:3])["udid"], "17-off")
        self.assertIsNone(pick_regular_iphone(devices[:2]))


class MovingWarnings(unittest.TestCase):
    def test_all_shots_moving_collapse_to_one_warning(self):
        w = moving_warnings(["closed/en", "closed/ar", "open/en"], 3, 3)
        self.assertEqual(len(w), 1)
        self.assertIn("Every shot", w[0])

    def test_some_shots_moving_are_named(self):
        w = moving_warnings(["half/en"], 6, 15)
        self.assertEqual(w, ["half/en: screen still changing after 15s; the shot may show an animation."])

    def test_none_moving(self):
        self.assertEqual(moving_warnings([], 6, 15), [])


if __name__ == "__main__":
    unittest.main()
