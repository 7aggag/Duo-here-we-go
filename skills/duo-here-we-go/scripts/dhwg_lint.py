#!/usr/bin/env python3
"""Static checks for iPhone Duo layout, RTL and device-copy problems in Swift and Flutter projects, measured on the iOS 27.1 simulator.

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
# iPhone Duo has Touch ID in the side button and no Face ID, so hard-coded Face ID copy is wrong there.
FACE_ID_COPY = re.compile(r"""["'][^"'\n]*(?:\bFace\s?ID\b|بصمة الوجه|التعرف على الوجه)[^"'\n]*["']""", re.I)
BIOMETRY_TYPE = re.compile(r"\bbiometryType\b")
COPY_KEY = re.compile(r'^\s*"(NSFaceIDUsageDescription)"')
# Flutter (Dart). Flutter reads the Duo's system column as a physical safe-area inset and, without a
# bridge package, never reports the fold on iOS (flutter/flutter#192515).
FOLD_BRIDGES = ("foldable", "duo_kit", "iphone_duo_ui_pro", "duo_display")
DISPLAY_FEATURES = re.compile(r"\bdisplayFeatures(?:Of)?\b|\bDisplayFeatureSubScreen\b")
ORIENTATION_LOCK = re.compile(r"setPreferredOrientations\s*\(")
DIRECTIONAL_FROM_PHYSICAL = re.compile(
    r"EdgeInsetsDirectional\b.*\b(?:viewPadding|padding|viewInsets)\s*\.\s*(?:left|right)\b"
    r"|\b(?:viewPadding|padding)\s*\.\s*(?:left|right)\b.*EdgeInsetsDirectional\b")
DROPS_RIGHT_INSET = re.compile(r"\bremoveRight\s*:\s*true\b|\bSafeArea\s*\([^)]*\bright\s*:\s*false\b")
FLUTTER_BIOMETRY = re.compile(r"\bBiometricType\b|\bgetAvailableBiometrics\b")
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


def face_id_findings(files: List[SourceFile], strings: List[SourceFile]) -> List[dict]:
    adapts = any(BIOMETRY_TYPE.search(f.text) or FLUTTER_BIOMETRY.search(f.text) for f in files)
    out = []
    for f in files + strings:
        if f.path.name.startswith("InfoPlist."):
            continue  # NSFaceIDUsageDescription is only shown on Face ID devices
        for i in range(len(f.lines)):
            line = f.code(i) if f.path.suffix in (".swift", ".dart") else f.lines[i]
            if not FACE_ID_COPY.search(line) or COPY_KEY.search(line):
                continue
            out.append(dict(finding(
                "DHWG-002", "info" if adapts else "warn", f, i,
                "User-facing text names Face ID. iPhone Duo has Touch ID in the side button and no Face ID"
                + (", and this copy is not chosen from LAContext.biometryType." if not adapts else
                   "; the project reads biometryType, so check this copy is only shown for .faceID."),
                "Pick the wording from LAContext().biometryType (.touchID, .faceID, .opticID) or use a neutral "
                "phrase such as \"Unlock with biometrics\"."), source="dhwg"))
    return out


def flutter_findings(root: Path, dart: List[SourceFile]) -> List[dict]:
    pubspec = (root / "pubspec.yaml").read_text(errors="ignore") if (root / "pubspec.yaml").exists() else ""
    bridged = any(re.search(rf"^\s+{b}\s*:", pubspec, re.M) for b in FOLD_BRIDGES)
    out = []

    def add(rule, severity, f, i, message, fix, source="dhwg"):
        out.append(dict(finding(rule, severity, f, i, message, fix), source=source))

    for f in dart:
        for i in range(len(f.lines)):
            line = f.code(i)
            if not line.strip():
                continue
            if DISPLAY_FEATURES.search(line) and not bridged:
                add("DHWG-FL-001", "warn", f, i,
                    "Flutter fills MediaQuery.displayFeatures only on Android: on iPhone Duo the list is always empty, "
                    "so this fold logic never runs and dialogs and sheets can sit across the half-open fold.",
                    "Add a bridge package that reports the hinge (for example foldable, pinned) after the user agrees, "
                    "or check that the project's Flutter version already includes flutter/flutter#193025.")
            if ORIENTATION_LOCK.search(line):
                window = " ".join(f.code(j) for j in range(i, min(len(f.lines), i + 4)))
                if "portrait" in window and "landscape" not in window:
                    add("DHWG-FL-002", "warn", f, i,
                        "A portrait-only orientation lock. On the Duo's inner display a lock set at run time persists, "
                        "later requests to change it fail, and the inner display ignores supported orientations anyway.",
                        "Remove the lock for iPhone Duo (keep all orientations) and lay out from the available size.")
            if DROPS_RIGHT_INSET.search(line):
                add("DHWG-FL-004", "warn", f, i,
                    "The right safe-area inset is dropped. On iPhone Duo that inset is the 84 pt system column, "
                    "on the physical right in every language, so content slides under it.",
                    "Keep the right inset (SafeArea right: true, no removeRight), or pad by viewPadding.right yourself.")
            if DIRECTIONAL_FROM_PHYSICAL.search(line):
                add("DHWG-RTL-006", "warn", f, i,
                    "A physical inset (padding.left/right) is put into EdgeInsetsDirectional. The Duo's system column "
                    "stays on the physical right in Arabic, so start/end moves the 84 pt gap to the wrong side.",
                    "Keep MediaQuery insets physical: EdgeInsets.only(left: ..., right: ...), or SafeArea.", source="rtl")

    plist = root / "ios" / "Runner" / "Info.plist"
    if plist.exists():
        f = SourceFile(plist, root)
        for i, line in enumerate(f.lines):
            if "<key>UIRequiresFullScreen</key>" in line and i + 1 < len(f.lines) and "<true/>" in f.lines[i + 1]:
                add("DHWG-FL-003", "error", f, i,
                    "UIRequiresFullScreen is set: iOS scales the app into a portrait window on iPhone Duo and reports "
                    "no fold, so none of the Duo layout applies.",
                    "Remove UIRequiresFullScreen (and allow every orientation) unless there is a written reason to keep it.")
    return out


def lint(root: Path) -> Dict[str, List[dict]]:
    files = [SourceFile(p, root) for p in project_files(root, (".swift",))]
    dart = [SourceFile(p, root) for p in project_files(root, (".dart",))
            if not p.name.endswith((".g.dart", ".freezed.dart"))
            and p.relative_to(root).parts[0] not in ("test", "integration_test")]
    strings = [SourceFile(p, root) for p in project_files(root, (".strings", ".xcstrings", ".arb"))]
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

    out += face_id_findings(files + dart, strings)
    out += flutter_findings(root, dart)

    every = {s.rel: s for s in files + dart + strings}
    kept, suppressed = [], []
    for item in out:
        f = every.get(item["file"]) or SourceFile(root / item["file"], root)
        reason = f.suppression(item["line"] - 1, item["id"])
        if reason:
            suppressed.append({**item, "suppressed": reason})
        else:
            kept.append(item)
    return {"findings": kept, "suppressed": suppressed, "files_scanned": len(files) + len(dart)}


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
