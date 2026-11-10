#!/usr/bin/env python3
"""Install an app on the iPhone Duo simulator and screenshot it per pose and language.

usage: capture.py --app Build/MyApp.app [--label baseline|after] [--out dhwg-out]
                  [--poses closed,open,half] [--langs en,ar] [--udid UDID] [--wait 2]
                  [--settle-timeout 15] [--no-hinge] [-- app launch arguments ...]
exit 0 = done, 2 = setup error, 3 = hinge control failed (ask the user to set the pose by hand,
then rerun with --no-hinge --poses <that pose>).
"""
import argparse
import json
import plistlib
import sys
import time
from pathlib import Path
from typing import Optional

from dhwg_common import LANG_ARGS, POSE_ANGLES, ensure_booted, find_duo, hinge, log, run, write_json


def bundle_info(app: Path) -> dict:
    with open(app / "Info.plist", "rb") as f:
        info = plistlib.load(f)
    arabic = (app / "ar.lproj").is_dir() or "ar" in info.get("CFBundleLocalizations", [])
    return {"bundle_id": info["CFBundleIdentifier"], "arabic_in_bundle": arabic}


def posture(udid: str) -> dict:
    return json.loads(hinge(udid, "posture", "--json").stdout)


def settle(udid: str, pose: str, timeout: float = 8.0) -> dict:
    want_primary = pose == "closed"
    deadline = time.time() + timeout
    while True:
        p = posture(udid)
        active = next((d for d in p["displays"] if d["active"]), None)
        if active and active["primary"] == want_primary and active["backlight"] != "off":
            return p
        if time.time() > deadline:
            raise RuntimeError(f"display did not settle for pose {pose}: {p}")
        time.sleep(0.5)


def is_settled(previous: Optional[bytes], current: bytes, launch_frame: bytes) -> bool:
    """Two identical frames in a row that are not the launch screen."""
    return current == previous and current != launch_frame


def stable_shot(udid: str, path: Path, min_wait: float, timeout: float):
    """Screenshot until the app has drawn and stopped moving, so neither the blank launch
    screen nor a launch animation is captured. Returns (shot, settled, still_launch_frame)."""
    launch_frame = None
    deadline = time.time() + min_wait + timeout
    previous = None
    first = True
    while True:
        shot = json.loads(hinge(udid, "screenshot", str(path), "--json").stdout)
        frame = path.read_bytes()
        if first:
            launch_frame, first = frame, False
            time.sleep(min_wait)
            continue
        if is_settled(previous, frame, launch_frame):
            return shot, True, False
        if time.time() > deadline:
            return shot, False, frame == launch_frame
        previous = frame
        time.sleep(1.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True)
    ap.add_argument("--label", default="baseline")
    ap.add_argument("--out", default="dhwg-out")
    ap.add_argument("--poses", default="closed,open,half")
    ap.add_argument("--langs", default="en,ar")
    ap.add_argument("--udid")
    ap.add_argument("--wait", type=float, default=2.0, help="seconds before the first screenshot")
    ap.add_argument("--settle-timeout", type=float, default=15.0, help="max seconds to wait for a still screen")
    ap.add_argument("--no-hinge", action="store_true")
    argv = sys.argv[1:]
    launch_args = argv[argv.index("--") + 1:] if "--" in argv else []
    args = ap.parse_args(argv[:argv.index("--")] if "--" in argv else argv)

    app = Path(args.app).resolve()
    poses = args.poses.split(",")
    langs = args.langs.split(",")
    bad = [p for p in poses if p not in POSE_ANGLES] + [l for l in langs if l not in LANG_ARGS]
    if bad:
        log(f"unknown pose or language: {bad}")
        return 2

    duo = find_duo(args.udid)
    if duo is None:
        log("no iPhone Duo simulator; run preflight.py")
        return 2
    udid = duo["udid"]
    ensure_booted(udid)
    info = bundle_info(app)
    run(["xcrun", "simctl", "install", udid, str(app)])

    out = Path(args.out).resolve() / args.label
    manifest = {"label": args.label, "app": str(app), "udid": udid, "runtime": duo["runtime"],
                **info, "shots": [], "warnings": []}
    if "ar" in langs and not info["arabic_in_bundle"]:
        manifest["warnings"].append("App bundle has no Arabic localization; 'ar' shots render left-to-right.")

    for pose in poses:
        if not args.no_hinge:
            try:
                hinge(udid, str(POSE_ANGLES[pose]))
                settle(udid, pose)
            except RuntimeError as e:
                manifest["warnings"].append(f"hinge control failed at pose {pose}: {e}")
                write_json(out / "manifest.json", manifest)
                log(f"hinge control failed; ask the user to set pose '{pose}' in Device Hub, "
                    f"then rerun with --no-hinge --poses {pose}")
                return 3
        for lang in langs:
            run(["xcrun", "simctl", "terminate", udid, info["bundle_id"]], check=False)
            run(["xcrun", "simctl", "launch", udid, info["bundle_id"], *LANG_ARGS[lang], *launch_args])
            path = out / pose / f"{lang}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            shot, stable, launch_only = stable_shot(udid, path, args.wait, args.settle_timeout)
            if launch_only:
                manifest["warnings"].append(f"{pose}/{lang}: the screen never changed from the first frame after launch; "
                                            "the shot may be the blank launch screen.")
            elif not stable:
                manifest["warnings"].append(f"{pose}/{lang}: screen still changing after {args.settle_timeout:g}s; "
                                            "the shot may show an animation.")
            manifest["shots"].append({"pose": pose, "angle": POSE_ANGLES[pose], "lang": lang, "stable": stable,
                                      "display": shot["display"], "path": str(path.relative_to(out.parent))})
            log(f"{args.label}/{pose}/{lang} -> {shot['display']}")

    write_json(out / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
