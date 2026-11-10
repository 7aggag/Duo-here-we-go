import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

from preflight import exclude_output, git_state  # noqa: E402


class ExcludeOutput(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.exclude = self.root / ".git" / "info" / "exclude"

    def test_appends_on_its_own_line_when_file_lacks_trailing_newline(self):
        self.exclude.write_text(".DS_Store\nUserInterfaceState.xcuserstate")
        exclude_output(self.root)
        self.assertEqual(self.exclude.read_text().splitlines()[-2:], ["UserInterfaceState.xcuserstate", "dhwg-out/"])

    def test_idempotent(self):
        exclude_output(self.root)
        exclude_output(self.root)
        self.assertEqual(self.exclude.read_text().splitlines().count("dhwg-out/"), 1)

    def test_output_folder_keeps_tree_clean(self):
        (self.root / "dhwg-out").mkdir()
        (self.root / "dhwg-out" / "x.json").write_text("{}")
        self.assertTrue(git_state(self.root)["clean"])


if __name__ == "__main__":
    unittest.main()
