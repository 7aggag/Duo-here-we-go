import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

from store_shots import MAX_PER_LANG, png_size, select, write_store  # noqa: E402


def png(width: int, height: int, pixel: bytes = b"\x20\x40\x60\xff") -> bytes:
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    rows = b"".join(bytes([0]) + pixel * width for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


class StoreShots(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def shot(self, label, pose, lang, size, pixel=b"\x20\x40\x60\xff", **extra):
        path = self.root / label / pose / f"{lang}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png(*size, pixel))
        return {"pose": pose, "lang": lang, "path": f"{label}/{pose}/{lang}.png", **extra}

    def test_png_size(self):
        self.assertEqual(png_size(png(2853, 2)), (2853, 2))
        self.assertIsNone(png_size(b"not a png"))

    def test_keeps_duo_sizes_in_pose_order_per_language(self):
        m = {"label": "after", "arabic_in_bundle": True, "shots": [
            self.shot("after", "closed", "en", (1398, 2034)),
            self.shot("after", "open", "en", (2853, 2007)),
            self.shot("after", "half", "ar", (2853, 2007)),
            self.shot("after", "iphone", "en", (1206, 2622)),
        ]}
        picked, warnings = select([m], self.root, ["open", "half", "closed"], ["en", "ar"])
        self.assertEqual([(i["pose"], i["display"]) for i in picked["en"]], [("open", "inner"), ("closed", "outer")])
        self.assertEqual([i["pose"] for i in picked["ar"]], ["half"])
        self.assertEqual(warnings, [])

    def test_wrong_size_and_black_frames_are_left_out(self):
        m = {"label": "after", "shots": [
            self.shot("after", "open", "en", (1206, 2622)),
            self.shot("after", "half", "en", (2853, 2007), pixel=b"\x00\x00\x00\xff"),
        ]}
        picked, warnings = select([m], self.root, ["open", "half"], ["en"])
        self.assertEqual(picked["en"], [])
        self.assertTrue(any("not an iPhone Duo screenshot size" in w for w in warnings))
        self.assertTrue(any("black frame" in w for w in warnings))

    def test_arabic_left_out_without_localization(self):
        m = {"label": "after", "arabic_in_bundle": False, "shots": [self.shot("after", "open", "ar", (2853, 2007))]}
        picked, warnings = select([m], self.root, ["open"], ["ar"])
        self.assertEqual(picked["ar"], [])
        self.assertTrue(any("no Arabic localization" in w for w in warnings))

    def test_caps_at_ten_per_language(self):
        manifests = [{"label": f"screen-{n}", "shots": [self.shot(f"screen-{n}", "open", "en", (2853, 2007))]}
                     for n in range(MAX_PER_LANG + 2)]
        picked, warnings = select(manifests, self.root, ["open"], ["en"])
        self.assertEqual(len(picked["en"]), MAX_PER_LANG)
        self.assertTrue(any("screen-10/open, screen-11/open" in w for w in warnings))

    def test_unstable_shot_kept_with_warning(self):
        m = {"label": "after", "shots": [self.shot("after", "open", "en", (2853, 2007), stable=False)]}
        picked, warnings = select([m], self.root, ["open"], ["en"])
        self.assertEqual(len(picked["en"]), 1)
        self.assertTrue(any("still moving" in w for w in warnings))

    def test_write_store_numbers_files_and_clears_old_ones(self):
        out = self.root / "store"
        (out / "en").mkdir(parents=True)
        (out / "en" / "07-old-open.jpg").write_bytes(b"old")
        picked = {"en": [{"label": "after", "pose": "open", "source": "a"},
                         {"label": "after", "pose": "closed", "source": "b"}]}
        write_store(picked, out, convert=lambda src, dst: dst.write_bytes(b"jpg"))
        self.assertEqual(sorted(p.name for p in (out / "en").iterdir()), ["01-after-open.jpg", "02-after-closed.jpg"])
        self.assertEqual(picked["en"][0]["file"], "en/01-after-open.jpg")


if __name__ == "__main__":
    unittest.main()
