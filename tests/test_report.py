import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts" / "report.py"


def write(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


def manifest(label: str, poses) -> dict:
    return {"label": label, "runtime": "com.apple.CoreSimulator.SimRuntime.iOS-27-1", "warnings": [],
            "shots": [{"pose": p, "lang": l, "path": f"{label}/{p}/{l}.png"} for p in poses for l in ("en", "ar")]}


class Report(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.out = self.dir / "dhwg-out"

    def render(self, *extra) -> str:
        report = self.out / "REPORT.md"
        subprocess.run([sys.executable, str(SCRIPT), "--out", str(report), *extra], check=True, capture_output=True)
        return report.read_text()

    def test_error_means_not_ready_and_errors_sort_first(self):
        f = write(self.dir / "lint.json", {"findings": [
            {"id": "DHWG-RTL-004", "source": "rtl", "severity": "info", "file": "A.swift", "line": 3,
             "message": "m", "fix": "f", "verified": "static"},
            {"id": "DHWG-RTL-001", "source": "rtl", "severity": "error", "file": "B.swift", "line": 9,
             "message": "pipe | inside", "fix": "f", "verified": "static"},
        ], "suppressed": [{"id": "DHWG-RTL-003", "file": "C.swift", "line": 1, "suppressed": "logged only"}]})
        text = self.render("--findings", str(f), "--title", "Demo")
        self.assertIn("## Readiness: NOT READY", text)
        self.assertLess(text.index("DHWG-RTL-001"), text.index("DHWG-RTL-004"))
        self.assertIn("pipe \\| inside", text)
        self.assertIn("logged only", text)

    def test_apple_list_and_rtl_findings_are_counted_by_source(self):
        apple = write(self.dir / "apple.json", [{"id": "APPLE-uiscreen", "source": "apple", "severity": "warn",
                                                 "file": "X.swift", "line": 1, "message": "m", "fix": "f",
                                                 "verified": "static"}])
        text = self.render("--findings", str(apple))
        self.assertIn("## Readiness: NEEDS WORK", text)
        self.assertIn("| apple | 0 | 1 | 0 |", text)

    def test_screens_before_and_after_with_relative_paths(self):
        write(self.out / "baseline" / "manifest.json", manifest("baseline", ["closed", "open", "half"]))
        write(self.out / "after" / "manifest.json", manifest("after", ["closed", "half"]))
        text = self.render("--captures", str(self.out))
        self.assertIn("## Readiness: READY ON THE SIMULATOR", text)
        self.assertIn("Before · ar | After · en", text)
        self.assertIn('src="baseline/half/ar.png"', text)
        self.assertIn('src="after/closed/en.png"', text)
        self.assertNotIn("Poses not captured", text)

    def test_preflight_problems_and_runtime_name_are_shown(self):
        write(self.out / "baseline" / "manifest.json", manifest("baseline", ["open"]))
        pre = write(self.dir / "preflight.json", {"project": "/x/MyApp", "xcode": "27.1",
                                                  "problems": ["Working tree has uncommitted changes."],
                                                  "warnings": ["No Arabic localization found."]})
        text = self.render("--captures", str(self.out), "--preflight", str(pre))
        self.assertIn("report — MyApp", text)
        self.assertIn("**Simulator runtime:** iOS 27.1", text)
        self.assertIn("Preflight problem the run continued with: Working tree has uncommitted changes.", text)
        self.assertIn("- No Arabic localization found.", text)

    def test_regular_iphone_row_and_extra_screen_sets(self):
        base = manifest("baseline", ["closed", "open", "half", "iphone"])
        write(self.out / "baseline" / "manifest.json", base)
        extra = manifest("after-reports", ["open", "half"])
        extra["warnings"] = ["half/ar: moving"]
        write(self.out / "after-reports" / "manifest.json", extra)
        text = self.render("--captures", str(self.out))
        self.assertIn("| Regular iPhone (comparison) |", text)
        self.assertIn('src="baseline/iphone/ar.png"', text)
        self.assertIn("### More screens: after-reports", text)
        self.assertIn('src="after-reports/half/en.png"', text)
        self.assertIn("- after-reports: half/ar: moving", text)
        self.assertNotIn("Poses not captured", text)

    def test_unverified_finding_without_a_file_shows_its_message(self):
        f = write(self.dir / "v.json", [{"id": "DHWG-COVERAGE", "source": "dhwg", "severity": "info",
                                         "message": "Screens behind login were not captured.", "fix": "-",
                                         "verified": "unverified"}])
        text = self.render("--findings", str(f))
        self.assertIn("- DHWG-COVERAGE: Screens behind login were not captured.", text)
        self.assertNotIn("`?:?`", text)

    def test_missing_poses_are_listed_as_not_verified(self):
        write(self.out / "baseline" / "manifest.json", manifest("baseline", ["open"]))
        text = self.render("--captures", str(self.out))
        self.assertIn("Poses not captured: closed, half.", text)
        self.assertIn("Nothing here ran on a real iPhone Duo", text)


if __name__ == "__main__":
    unittest.main()
