import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

from capture import is_settled, moving_warnings  # noqa: E402

LAUNCH, UI = b"blank launch screen", b"home screen"


class Settling(unittest.TestCase):
    def test_two_identical_app_frames_settle(self):
        self.assertTrue(is_settled(UI, UI, LAUNCH))

    def test_blank_launch_screen_twice_does_not_settle(self):
        self.assertFalse(is_settled(LAUNCH, LAUNCH, LAUNCH))

    def test_changing_frames_do_not_settle(self):
        self.assertFalse(is_settled(LAUNCH, UI, LAUNCH))
        self.assertFalse(is_settled(None, UI, LAUNCH))


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
