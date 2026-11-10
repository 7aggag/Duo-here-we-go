import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"))

from preflight import exclude_output, git_state, project_shape  # noqa: E402


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


class FlutterShape(unittest.TestCase):
    def make(self, files: dict) -> Path:
        root = Path(tempfile.mkdtemp())
        for rel, body in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(body)
        return root

    def test_flutter_project_with_arabic_arb(self):
        root = self.make({
            "pubspec.yaml": "name: app\ndependencies:\n  flutter:\n    sdk: flutter\n  foldable: 1.0.5\n",
            "lib/main.dart": "void main() {}\n",
            "lib/l10n/app_ar.arb": "{}",
            "ios/Runner.xcodeproj/project.pbxproj": "",
            "ios/Runner/Info.plist": "<dict></dict>",
            "ios/Runner/AppDelegate.swift": "import UIKit\n",
            ".dart_tool/x.dart": "",
        })
        shape = project_shape(root)
        self.assertEqual(shape["kind"], "flutter")
        self.assertEqual(shape["native_kind"], "uikit")
        self.assertTrue(shape["arabic_localization"])
        f = shape["flutter"]
        self.assertEqual((f["dart_files"], f["ios_runner"], f["ios_plist_lists_ar"], f["fold_bridge"]),
                         (1, True, False, ["foldable"]))

    def test_native_project_is_not_flutter(self):
        shape = project_shape(self.make({"App/App.swift": "import SwiftUI\n", "pubspec.yaml": "name: tool\n"}))
        self.assertEqual(shape["kind"], "swiftui")
        self.assertNotIn("flutter", shape)


if __name__ == "__main__":
    unittest.main()
