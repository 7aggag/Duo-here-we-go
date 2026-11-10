#!/usr/bin/env python3
"""Checks before Duo Here We Go touches a project. Read-only, except that it adds
dhwg-out/ to the repository's local .git/info/exclude so the scratch folder never
shows up as a change.

usage: preflight.py <project-dir> [--out preflight.json]
exit 0 = ready, 2 = blocking problems (listed in "problems").
"""
import argparse
import json
import re
import sys
from pathlib import Path

from dhwg_common import EXCLUDED_DIRS, find_duo, log, project_files, run, write_json


def xcode_version() -> str:
    out = run(["xcodebuild", "-version"], check=False).stdout
    m = re.search(r"Xcode (\d+(?:\.\d+)*)", out)
    return m.group(1) if m else ""


def version_at_least(v: str, minimum: tuple) -> bool:
    parts = tuple(int(p) for p in v.split(".")) if v else ()
    return parts >= minimum


def exclude_output(root: Path) -> None:
    rel = run(["git", "-C", str(root), "rev-parse", "--git-path", "info/exclude"]).stdout.strip()
    path = Path(rel) if Path(rel).is_absolute() else root / rel
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if "dhwg-out/" in text.splitlines():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = "\n" if text and not text.endswith("\n") else ""
    path.write_text(text + prefix + "dhwg-out/\n", encoding="utf-8")


def git_state(root: Path) -> dict:
    inside = run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], check=False)
    if inside.returncode != 0:
        return {"repo": False}
    exclude_output(root)
    status = run(["git", "-C", str(root), "status", "--porcelain"], check=False).stdout
    branch = run(["git", "-C", str(root), "branch", "--show-current"], check=False).stdout.strip()
    return {"repo": True, "clean": status.strip() == "", "branch": branch}


def project_shape(root: Path) -> dict:
    containers = sorted(str(p.relative_to(root)) for p in root.rglob("*")
                        if p.suffix in (".xcodeproj", ".xcworkspace") and "Pods" not in p.parts
                        and not str(p).endswith("project.xcworkspace"))
    if (root / "Package.swift").exists():
        containers.append("Package.swift")
    swift = project_files(root, (".swift",))
    swiftui = uikit = 0
    for f in swift:
        text = f.read_text(encoding="utf-8", errors="ignore")
        swiftui += bool(re.search(r"^\s*import\s+SwiftUI\b", text, re.M))
        uikit += bool(re.search(r"^\s*import\s+UIKit\b", text, re.M))
    kind = "mixed" if swiftui and uikit else "swiftui" if swiftui else "uikit" if uikit else "unknown"

    plists = project_files(root, (".plist",))
    pbx = project_files(root, (".pbxproj",))
    scene = any("UIApplicationSceneManifest" in p.read_text(errors="ignore") for p in plists + pbx)

    arabic = any(not (EXCLUDED_DIRS & set(p.parts)) and not any(part.endswith(".app") for part in p.parts)
                 for p in root.rglob("ar.lproj"))
    for p in pbx:
        if re.search(r"knownRegions\s*=\s*\([^)]*\bar\b", p.read_text(errors="ignore"), re.S):
            arabic = True
    for p in plists:
        if re.search(r"CFBundleLocalizations</key>\s*<array>(?:(?!</array>).)*<string>ar</string>", p.read_text(errors="ignore"), re.S):
            arabic = True
    for p in project_files(root, (".xcstrings",)):
        if re.search(r'"ar"\s*:', p.read_text(errors="ignore")):
            arabic = True

    return {"containers": containers, "swift_files": len(swift), "swiftui_files": swiftui,
            "uikit_files": uikit, "kind": kind, "scene_manifest": scene, "arabic_localization": arabic}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out")
    args = ap.parse_args()
    root = Path(args.project).resolve()

    problems, warnings = [], []
    xv = xcode_version()
    if not version_at_least(xv, (27, 1)):
        problems.append(f"Xcode 27.1 or later is required (found {xv or 'none'}).")

    duo = find_duo()
    if duo is None:
        problems.append("No iPhone Duo simulator. Run scripts/setup_duo.py to create one.")

    git = git_state(root)
    if not git["repo"]:
        warnings.append("Project is not a git repository; before/after diffs and safe rollback are not available.")
    elif not git["clean"]:
        problems.append("Working tree has uncommitted changes. Commit or stash them before any phase edits code.")

    shape = project_shape(root)
    if not shape["containers"]:
        problems.append("No .xcodeproj, .xcworkspace or Package.swift found.")
    if not shape["scene_manifest"]:
        warnings.append("No UIApplicationSceneManifest found; the app may still use the app-delegate window lifecycle (Apple's skill covers this).")
    if not shape["arabic_localization"]:
        warnings.append("No Arabic localization found; Arabic runs will render left-to-right, so the RTL phase can only lint, not capture.")

    report = {"project": str(root), "xcode": xv, "duo_simulator": duo and {k: duo[k] for k in ("udid", "name", "state", "runtime")},
              "python": sys.version.split()[0], "git": git, "shape": shape, "problems": problems, "warnings": warnings}
    if args.out:
        write_json(Path(args.out), report)
    for p in problems:
        log(f"PROBLEM: {p}")
    for w in warnings:
        log(f"warning: {w}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
