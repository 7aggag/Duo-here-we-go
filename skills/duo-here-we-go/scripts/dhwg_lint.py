#!/usr/bin/env python3
"""Static checks for iPhone Duo layout and RTL problems, measured on the iOS 27.1 simulator.

usage: dhwg_lint.py <project-dir> [--out findings-lint.json] [--fail-on error|warn|never]

Suppress one finding with a reason, on the line itself or the line above:
    // dhwg:disable-next-line DHWG-RTL-001 -- we set traitOverrides in WindowFactory
    foo() // dhwg:disable DHWG-RTL-003 -- edge is only logged
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

from dhwg_common import project_files, write_json

SEVERITY_RANK = {"info": 0, "warn": 1, "error": 2}

APPEARANCE_SEMANTIC = re.compile(r"appearance\s*\([^)]*\)\s*\.semanticContentAttribute\s*=")
TRAIT_FIX = re.compile(r"traitOverrides\s*\.\s*layoutDirection\s*=|UITraitCollection\s*\(\s*layoutDirection\s*:")
SWIFTUI_APP = re.compile(r"@main\s+struct\s+\w+\s*:\s*(?:SwiftUI\.)?App\b")
REGIONS_CALL = re.compile(r"(?:(\w+)\s*\.\s*)?(?<!func )\breservedRegions\s*\(\s*kind\s*:")
PROXY_NAMES = re.compile(r"(\w+)\s*:\s*GeometryProxy\b|GeometryReader\s*\{\s*(\w+)\s+in\b")
BAR_EDGE = re.compile(r"\b(toolbarVerticalEdge|verticalBarEdge)\b")
PHYSICAL = re.compile(r"\.(left|right)\b|\b(minX|maxX)\b|\binsets?\.(left|right)\b")
FIXED_COLUMN = re.compile(
    r"navigationSplitViewColumnWidth\s*\(\s*\d|\b(preferred|minimum|maximum)PrimaryColumnWidth\s*=\s*\d")
FIXED_FRAME_WIDTH = re.compile(r"\.frame\s*\(\s*width\s*:\s*\d")
COLUMN_WIDTH = re.compile(r"navigationSplitViewColumnWidth\s*\(([^)]*)\)")
# Measured: at 90° a left-to-right sidebar snaps to the hinge only when its max width exceeds the hinge centre.
HINGE_CENTER_PT = 475
SUPPRESS = re.compile(r"//\s*dhwg:disable(-next-line)?\s+([\w\-, ]+?)\s+--\s+(.+)$")


class SourceFile:
    def __init__(self, path: Path, root: Path):
        self.path = path
        self.rel = str(path.relative_to(root))
        self.lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        self.text = "\n".join(self.lines)
        self.imports_swiftui = bool(re.search(r"^\s*import\s+SwiftUI\b", self.text, re.M))
        self.imports_uikit = bool(re.search(r"^\s*import\s+UIKit\b", self.text, re.M))
        self.proxies = {n for pair in PROXY_NAMES.findall(self.text) for n in pair if n}

    def region_calls(self, i: int) -> List[str]:
        """'swiftui' for a GeometryProxy receiver, 'uikit' for a UIView, per call on line i."""
        kinds = []
        for m in REGIONS_CALL.finditer(self.code(i)):
            receiver = m.group(1)
            is_swiftui = "layoutDirectionBehavior" in self.code(i) or (receiver in self.proxies) or (
                receiver is not None and re.fullmatch(r"(?i)proxy|geo|geometry|reader|gp", receiver) is not None)
            kinds.append("swiftui" if is_swiftui else "uikit")
        return kinds

    def code(self, i: int) -> str:
        line = self.lines[i]
        return "" if line.lstrip().startswith("//") else line.split("//", 1)[0]

    def suppression(self, i: int, rule: str):
        for j in (i, i - 1):
            if j < 0:
                continue
            m = SUPPRESS.search(self.lines[j])
            if m and (j == i) != bool(m.group(1)) and rule in [r.strip() for r in m.group(2).split(",")]:
                return m.group(3).strip()
        return None


def finding(rule, severity, f: SourceFile, i: int, message: str, fix: str) -> dict:
    return {"id": rule, "source": "rtl", "severity": severity, "file": f.rel, "line": i + 1,
            "message": message, "fix": fix, "verified": "static", "evidence": f.lines[i].strip()}


def lint(root: Path) -> Dict[str, List[dict]]:
    files = [SourceFile(p, root) for p in project_files(root, (".swift",))]
    has_trait_fix = any(TRAIT_FIX.search(f.text) for f in files)
    uses_swiftui = any(f.imports_swiftui or SWIFTUI_APP.search(f.text) for f in files)
    uikit_regions = any("uikit" in f.region_calls(i) for f in files for i in range(len(f.lines)))
    out: List[dict] = []

    for f in files:
        has_arrangement = "ArrangementView" in f.text
        for i in range(len(f.lines)):
            line = f.code(i)
            if not line.strip():
                continue

            if APPEARANCE_SEMANTIC.search(line):
                if not has_trait_fix:
                    out.append(finding(
                        "DHWG-RTL-001", "error", f, i,
                        "In-app RTL via the appearance proxy leaves verticalBarEdge on the system side: on iPhone Duo "
                        "the bar is placed for LTR and an empty ~88 pt inset appears on the left (Apple forum 852870).",
                        "Also set window.traitOverrides.layoutDirection = .rightToLeft on every window, or switch "
                        "language through the per-app language setting instead of forcing semantics."))
                if uses_swiftui:
                    out.append(finding(
                        "DHWG-RTL-005", "warn", f, i,
                        "This project has SwiftUI views, and SwiftUI ignores UIView.appearance().semanticContentAttribute: "
                        "SwiftUI screens stay left-to-right while UIKit screens flip.",
                        "Drive direction from SwiftUI with .environment(\\.layoutDirection, ...) at the root "
                        "(not yet verified on the Duo simulator)."))

            if uikit_regions and "layoutDirectionBehavior" not in line and "swiftui" in f.region_calls(i):
                out.append(finding(
                    "DHWG-RTL-002", "warn", f, i,
                    "SwiftUI reservedRegions defaults to .mirrors while UIView.reservedRegions returns physical frames; "
                    "this project uses both, so hinge and bar frames disagree in RTL (measured: x=371 vs x=455).",
                    "Pass layoutDirectionBehavior: .fixed when comparing with UIKit frames, or keep both sides directional."))

            if BAR_EDGE.search(line):
                window = " ".join(f.code(j) for j in range(i, min(len(f.lines), i + 3)))
                if PHYSICAL.search(window):
                    out.append(finding(
                        "DHWG-RTL-003", "warn", f, i,
                        "The vertical bar edge is leading/trailing and flips with the layout direction while the bar "
                        "stays on the same physical side; mapping it to left/right breaks in Arabic.",
                        "Keep the value directional (leading/trailing padding, safeAreaLayoutGuide anchors)."))

            for m in COLUMN_WIDTH.finditer(line):
                width_args = m.group(1)
                cap = re.search(r"\bmax\s*:\s*(\d+(?:\.\d+)?)", width_args) or re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*", width_args)
                if cap and float(cap.group(1)) <= HINGE_CENTER_PT:
                    out.append(dict(finding(
                        "DHWG-001", "warn", f, i,
                        f"Sidebar width is capped at {cap.group(1)} pt. Half-open (90°) in a left-to-right language, "
                        f"the split view aligns columns to the hinge only when the sidebar may grow past "
                        f"{HINGE_CENTER_PT} pt; otherwise the detail column runs across the fold.",
                        f"Raise the max above {HINGE_CENTER_PT} (e.g. max: 480) or drop it, then check the English "
                        "half-open capture."), source="dhwg"))

            if FIXED_COLUMN.search(line) or (has_arrangement and FIXED_FRAME_WIDTH.search(line)):
                out.append(finding(
                    "DHWG-RTL-004", "info", f, i,
                    "Fixed column width: at the half-open pose the two halves differ (455 pt vs 371 pt beside the bar) "
                    "and the sidebar or arrangement primary swaps halves in RTL.",
                    "Use min/ideal/max widths and check the Arabic half-open capture."))

    kept, suppressed = [], []
    for item in out:
        f = next(s for s in files if s.rel == item["file"])
        reason = f.suppression(item["line"] - 1, item["id"])
        if reason:
            suppressed.append({**item, "suppressed": reason})
        else:
            kept.append(item)
    return {"findings": kept, "suppressed": suppressed, "files_scanned": len(files)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out")
    ap.add_argument("--fail-on", default="error", choices=["error", "warn", "never"])
    args = ap.parse_args()
    result = lint(Path(args.project).resolve())
    if args.out:
        write_json(Path(args.out), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.fail_on == "never":
        return 0
    worst = max((SEVERITY_RANK[f["severity"]] for f in result["findings"]), default=-1)
    return 1 if worst >= SEVERITY_RANK[args.fail_on] else 0


if __name__ == "__main__":
    sys.exit(main())
