import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

from capture import is_settled  # noqa: E402

LAUNCH, UI = b"blank launch screen", b"home screen"


class Settling(unittest.TestCase):
    def test_two_identical_app_frames_settle(self):
        self.assertTrue(is_settled(UI, UI, LAUNCH))

    def test_blank_launch_screen_twice_does_not_settle(self):
        self.assertFalse(is_settled(LAUNCH, LAUNCH, LAUNCH))

    def test_changing_frames_do_not_settle(self):
        self.assertFalse(is_settled(LAUNCH, UI, LAUNCH))
        self.assertFalse(is_settled(None, UI, LAUNCH))


if __name__ == "__main__":
    unittest.main()
