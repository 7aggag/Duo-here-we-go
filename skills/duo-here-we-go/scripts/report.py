#!/usr/bin/env python3
"""Merge findings and captures into one REPORT.md.

usage: report.py --out dhwg-out/REPORT.md [--findings a.json b.json ...] [--captures dhwg-out]
                 [--preflight dhwg-out/preflight.json] [--title "MyApp"]

A findings file is either {"findings": [...], "suppressed": [...]} or a bare list.
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

SEVERITIES = ["error", "warn", "info"]
POSES = ["closed", "open", "half"]
POSE_NAMES = {"closed": "Closed (outer display)", "open": "Open 180°", "half": "Half-open 90°"}


def load_findings(paths: List[str]):
    findings, suppressed = [], []
    for p in paths:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        if isinstance(data, list):
            findings += data
        else:
            findings += data.get("findings", [])
            suppressed += data.get("suppressed", [])
    findings.sort(key=lambda f: (SEVERITIES.index(f.get("severity", "info")), f.get("file", ""), f.get("line", 0)))
    return findings, suppressed


def load_manifest(captures: Optional[Path], label: str) -> Optional[dict]:
    if not captures:
        return None
    path = captures / label / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def readiness(findings: List[dict]) -> str:
    if any(f["severity"] == "error" for f in findings):
        return "NOT READY — fix the errors below first"
    if any(f["severity"] == "warn" for f in findings):
        return "NEEDS WORK — no errors, warnings remain"
    return "READY ON THE SIMULATOR — still unverified on a real iPhone Duo"


def cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def shot_cell(manifest: Optional[dict], pose: str, lang: str, captures: Path, out_dir: Path) -> str:
    if not manifest:
        return "—"
    shot = next((s for s in manifest["shots"] if s["pose"] == pose and s["lang"] == lang), None)
    if not shot:
        return "—"
    rel = os.path.relpath(captures / shot["path"], out_dir)
    return f'<img src="{rel}" width="220" alt="{manifest["label"]} {pose} {lang}">'


def build(args) -> str:
    out_dir = Path(args.out).resolve().parent
    findings, suppressed = load_findings(args.findings)
    captures = Path(args.captures).resolve() if args.captures else None
    before, after = load_manifest(captures, "baseline"), load_manifest(captures, "after")
    pre = json.loads(Path(args.preflight).read_text(encoding="utf-8")) if args.preflight else {}

    lines = [f"# Duo Here We Go report — {args.title or Path(pre.get('project', '.')).name}", ""]
    meta = [f"**Date:** {date.today().isoformat()}"]
    if pre.get("xcode"):
        meta.append(f"**Xcode:** {pre['xcode']}")
    runtime = (after or before or {}).get("runtime")
    if runtime:
        name = runtime.rsplit(".", 1)[-1]
        os_name, _, version = name.partition("-")
        meta.append(f"**Simulator runtime:** {os_name} {version.replace('-', '.')}")
    lines += [" · ".join(meta), "", f"## Readiness: {readiness(findings)}", ""]

    sources = sorted({f.get("source", "?") for f in findings})
    lines += ["| Source | " + " | ".join(SEVERITIES) + " |", "|---|" + "---|" * len(SEVERITIES)]
    for s in sources:
        counts = [sum(1 for f in findings if f.get("source") == s and f["severity"] == sev) for sev in SEVERITIES]
        lines.append(f"| {s} | " + " | ".join(map(str, counts)) + " |")
    if not sources:
        lines.append("| — | 0 | 0 | 0 |")
    lines.append("")

    lines += ["## Findings", ""]
    if findings:
        lines += ["| Rule | Severity | Where | Problem | Fix | Verified |", "|---|---|---|---|---|---|"]
        for f in findings:
            where = f"`{f.get('file', '?')}:{f.get('line', '?')}`" if f.get("file") else "—"
            lines.append(f"| {f['id']} | {f['severity']} | {where} | {cell(f.get('message', ''))} | "
                         f"{cell(f.get('fix', ''))} | {f.get('verified', 'unverified')} |")
    else:
        lines.append("No findings.")
    lines.append("")
    if suppressed:
        lines += ["### Suppressed in code", ""]
        lines += [f"- {s['id']} at `{s['file']}:{s['line']}` — {s['suppressed']}" for s in suppressed]
        lines.append("")

    if before or after:
        lines += ["## Screens", ""]
        labels = [("Before", before), ("After", after)] if after else [("Now", before)]
        header = [f"{name} · {lang}" for name, m in labels for lang in ("en", "ar")]
        lines += ["| Pose | " + " | ".join(header) + " |", "|---|" + "---|" * len(header)]
        for pose in POSES:
            cells = [shot_cell(m, pose, lang, captures, out_dir) for _, m in labels for lang in ("en", "ar")]
            if any(c != "—" for c in cells):
                lines.append(f"| {POSE_NAMES[pose]} | " + " | ".join(cells) + " |")
        lines.append("")

    notes = [f"Preflight problem the run continued with: {p}" for p in pre.get("problems", [])]
    notes += pre.get("warnings", [])
    for m in (before, after):
        if m:
            notes += [f"{m['label']}: {w}" for w in m.get("warnings", [])]
    if notes:
        lines += ["## Warnings", ""] + [f"- {n}" for n in notes] + [""]

    unverified = ["Nothing here ran on a real iPhone Duo; every screen above is from the simulator."]
    captured = {s["pose"] for m in (before, after) if m for s in m["shots"]}
    missing = [p for p in POSES if p not in captured]
    if missing:
        unverified.append(f"Poses not captured: {', '.join(missing)}.")
    unverified += [f"{f['id']} at `{f.get('file', '?')}:{f.get('line', '?')}`" for f in findings if f.get("verified") == "unverified"]
    lines += ["## Not verified", ""] + [f"- {u}" for u in unverified] + [""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--findings", nargs="*", default=[])
    ap.add_argument("--captures")
    ap.add_argument("--preflight")
    ap.add_argument("--title")
    args = ap.parse_args()
    text = build(args)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
