#!/usr/bin/env python3
"""Install an app on the iPhone Duo simulator and screenshot it per pose and language.

usage: capture.py --app Build/MyApp.app [--label baseline|after] [--out dhwg-out]
                  [--poses closed,open,half] [--langs en,ar] [--udid UDID] [--wait 2]
                  [--settle-timeout 15] [--display-timeout 300] [--no-hinge] [--iphone] [-- app launch arguments ...]
--iphone also captures each language on a regular iPhone simulator (pose "iphone"), to tell
Duo problems from problems the app has everywhere.
exit 0 = done, 2 = setup error, 3 = hinge control failed (ask the user to set the pose by hand,
then rerun with --no-hinge --poses <that pose>).
"""
import argparse
import json
import plistlib
import sys
import time
import zlib
from pathlib import Path
from typing import Optional

from dhwg_common import (LANG_ARGS, POSE_ANGLES, ensure_booted, find_duo, hinge, log, pick_regular_iphone, run,
                         simctl_devices, write_json)


def bundle_info(app: Path) -> dict:
    with open(app / "Info.plist", "rb") as f:
        info = plistlib.load(f)
    flutter = (app / "Frameworks" / "App.framework" / "flutter_assets").is_dir()
    # Flutter compiles its translations into Dart code and reads the system languages directly,
    # so the bundle says nothing about Arabic; the Arabic shots themselves show it.
    arabic = None if flutter else (app / "ar.lproj").is_dir() or "ar" in info.get("CFBundleLocalizations", [])
    return {"bundle_id": info["CFBundleIdentifier"], "arabic_in_bundle": arabic, "flutter": flutter}


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


PNG_CHANNELS = {0: 1, 2: 3, 4: 2, 6: 4}  # colour type -> channels, 8-bit only
# Bytes a filtered all-black 8-bit scanline can hold: filter types 0-4, zero colour, alpha 255, and
# the Average filter's 128 (half of the opaque alpha to its left).
BLACK_ROW_BYTES = bytes([0, 1, 2, 3, 4, 128, 255])


def is_black_frame(png: bytes) -> bool:
    """True when a PNG is a single flat black frame. Since Xcode 27.2 the iPhone Duo simulator
    returns black screenshots for a few minutes after boot; such a frame is not the app."""
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    pos, ihdr, idat = 8, None, []
    while pos + 8 <= len(png):
        length = int.from_bytes(png[pos:pos + 4], "big")
        kind, body = png[pos + 4:pos + 8], png[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            ihdr = body
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
        pos += 12 + length
    if not ihdr or not idat or ihdr[8] != 8 or ihdr[9] not in PNG_CHANNELS or ihdr[12] != 0:
        return False  # not 8-bit, or interlaced: never what simctl writes
    try:
        raw = zlib.decompress(b"".join(idat))
    except zlib.error:
        return False
    # Any byte outside the black-row set means some pixel is not black.
    if raw.translate(None, BLACK_ROW_BYTES):
        return False
    # A flat white frame filtered with Sub/Up also reduces to 0s and 255s, so read the first pixel:
    # every filter predicts 0 for the first pixel of the first row, so it is stored as is.
    channels = PNG_CHANNELS[ihdr[9]]
    first = raw[1:1 + channels]
    colour = first if channels in (1, 3) else first[:-1]
    return not any(colour)


def is_settled(previous: Optional[bytes], current: bytes, launch_frame: bytes) -> bool:
    """Two identical frames in a row that are not the launch screen or a black frame."""
    return current == previous and current != launch_frame and not is_black_frame(current)


def wait_for_display(udid: str, path: Path, timeout: float, shoot=None) -> bool:
    """Poll screenshots until the simulator stops returning black frames. False on timeout."""
    shoot = shoot or duo_screenshot
    deadline = time.time() + timeout
    while True:
        shoot(udid, path)
        if not is_black_frame(path.read_bytes()):
            return True
        if time.time() > deadline:
            return False
        time.sleep(5.0)


def duo_screenshot(udid: str, path: Path) -> dict:
    return json.loads(hinge(udid, "screenshot", str(path), "--json").stdout)


def plain_screenshot(udid: str, path: Path) -> dict:
    run(["xcrun", "simctl", "io", udid, "screenshot", str(path)])
    return {"display": "main"}


def stable_shot(udid: str, path: Path, min_wait: float, timeout: float, shoot=duo_screenshot):
    """Screenshot until the app has drawn and stopped moving, so neither the blank launch
    screen nor a launch animation is captured. Returns (shot, settled, still_launch_frame)."""
    launch_frame = None
    deadline = time.time() + min_wait + timeout
    previous = None
    first = True
    while True:
        shot = shoot(udid, path)
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


def moving_warnings(moving: list, total: int, timeout: float) -> list:
    if not moving:
        return []
    if len(moving) == total and total > 1:
        return [f"Every shot was still changing after {timeout:g}s (a video or looping animation on screen?); "
                "shots are single frames of a moving screen."]
    return [f"{name}: screen still changing after {timeout:g}s; the shot may show an animation." for name in moving]


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
    ap.add_argument("--display-timeout", type=float, default=300.0,
                    help="max seconds to wait for the simulator to stop returning black screenshots after boot")
    ap.add_argument("--no-hinge", action="store_true")
    ap.add_argument("--iphone", action="store_true", help="also capture each language on a regular iPhone simulator")
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
    out.mkdir(parents=True, exist_ok=True)
    probe = out / ".display-check.png"
    log("waiting for the simulator to return non-black screenshots")
    if not wait_for_display(udid, probe, args.display_timeout):
        manifest["warnings"].append(f"The simulator still returned black screenshots {args.display_timeout:g}s "
                                    "after boot; shots may be black.")
    probe.unlink(missing_ok=True)
    if "ar" in langs and info["arabic_in_bundle"] is False:
        manifest["warnings"].append("App bundle has no Arabic localization; 'ar' shots render left-to-right.")

    moving = []

    def capture_langs(device: str, pose: str, angle, shoot) -> None:
        for lang in langs:
            run(["xcrun", "simctl", "terminate", device, info["bundle_id"]], check=False)
            launch = ["xcrun", "simctl", "launch", device, info["bundle_id"], *LANG_ARGS[lang], *launch_args]
            try:
                run(launch)
            except RuntimeError:
                # Right after a boot or an install SpringBoard can refuse the first launch.
                time.sleep(3.0)
                run(launch)
            path = out / pose / f"{lang}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            shot, stable, launch_only = stable_shot(device, path, args.wait, args.settle_timeout, shoot)
            if is_black_frame(path.read_bytes()):
                manifest["warnings"].append(f"{pose}/{lang}: the shot is a black frame (the simulator can return "
                                            "black screenshots for minutes after boot); recapture this pose.")
            elif launch_only:
                manifest["warnings"].append(f"{pose}/{lang}: the screen never changed from the first frame after launch; "
                                            "the shot may be the blank launch screen.")
            elif not stable:
                moving.append(f"{pose}/{lang}")
            manifest["shots"].append({"pose": pose, "angle": angle, "lang": lang, "stable": stable,
                                      "display": shot["display"], "path": str(path.relative_to(out.parent))})
            log(f"{args.label}/{pose}/{lang} -> {shot['display']}")

    for pose in poses:
        if not args.no_hinge:
            try:
                try:
                    hinge(udid, str(POSE_ANGLES[pose]))
                except RuntimeError:
                    # A busy simulator can miss the 2 s confirmation window; one slower retry.
                    time.sleep(1.0)
                    hinge(udid, "-t", "8", str(POSE_ANGLES[pose]))
                settle(udid, pose)
            except RuntimeError as e:
                manifest["warnings"].append(f"hinge control failed at pose {pose}: {e}")
                write_json(out / "manifest.json", manifest)
                log(f"hinge control failed; ask the user to set pose '{pose}' in Device Hub, "
                    f"then rerun with --no-hinge --poses {pose}")
                return 3
        capture_langs(udid, pose, POSE_ANGLES[pose], duo_screenshot)

    if args.iphone:
        phone = pick_regular_iphone(simctl_devices())
        if phone is None:
            manifest["warnings"].append("No regular iPhone simulator for the comparison shots.")
        else:
            ensure_booted(phone["udid"])
            run(["xcrun", "simctl", "install", phone["udid"], str(app)])
            manifest["iphone"] = {"udid": phone["udid"], "name": phone["name"]}
            capture_langs(phone["udid"], "iphone", None, plain_screenshot)

    manifest["warnings"] += moving_warnings(moving, len(manifest["shots"]), args.settle_timeout)
    write_json(out / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
