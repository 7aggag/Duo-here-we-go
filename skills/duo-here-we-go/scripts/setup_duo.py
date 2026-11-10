#!/usr/bin/env python3
"""Make sure an iPhone Duo simulator exists, creating it and, with consent, downloading its runtime.

usage: setup_duo.py [--download] [--name "iPhone Duo"]

exit 0  ready; prints {"udid", "name", "runtime", "action"} where action is exists | created
exit 2  this Xcode has no iPhone Duo device type (needs Xcode 27.1 or later)
exit 5  no installed iOS runtime supports iPhone Duo; ask the user, then rerun with --download
exit 6  not enough free disk space for the download
exit 7  the download finished but still no runtime supports iPhone Duo
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from dhwg_common import DUO_DEVICE_TYPE, find_duo, log, run

# The iOS 27.1 runtime is a 7.9 GB download that unpacks to 7.3 GB; leave room for both plus slack.
DOWNLOAD_GB = 8
REQUIRED_FREE_GB = 16


def simctl_json(kind: str) -> List[dict]:
    return json.loads(run(["xcrun", "simctl", "list", kind, "-j"]).stdout)[kind]


def duo_runtimes(runtimes: List[dict]) -> List[dict]:
    """Available runtimes that list the iPhone Duo device type, newest first."""
    usable = [r for r in runtimes if r.get("isAvailable", True)
              and any(t.get("identifier") == DUO_DEVICE_TYPE for t in r.get("supportedDeviceTypes", []))]
    return sorted(usable, key=lambda r: tuple(int(p) for p in r["version"].split(".")), reverse=True)


def plan(has_device: bool, device_types: List[dict], runtimes: List[dict], free_gb: float, download: bool) -> str:
    if has_device:
        return "exists"
    if not any(t.get("identifier") == DUO_DEVICE_TYPE for t in device_types):
        return "no_device_type"
    if duo_runtimes(runtimes):
        return "create"
    if not download:
        return "ask_to_download"
    if free_gb < REQUIRED_FREE_GB:
        return "low_disk"
    return "download"


def create(name: str, runtime_id: str) -> str:
    return run(["xcrun", "simctl", "create", name, DUO_DEVICE_TYPE, runtime_id]).stdout.strip()


def free_gb() -> float:
    return shutil.disk_usage(str(Path.home())).free / 1e9


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true", help="download the iOS runtime if none supports iPhone Duo")
    ap.add_argument("--name", default="iPhone Duo")
    args = ap.parse_args()

    duo = find_duo()
    action = plan(duo is not None, simctl_json("devicetypes"), simctl_json("runtimes"), free_gb(), args.download)

    if action == "exists":
        print(json.dumps({"udid": duo["udid"], "name": duo["name"], "runtime": duo["runtime"], "action": "exists"}))
        return 0
    if action == "no_device_type":
        log("This Xcode has no iPhone Duo device type. Install Xcode 27.1 or later.")
        return 2
    if action == "ask_to_download":
        log(f"No installed iOS runtime supports iPhone Duo. The runtime is a ~{DOWNLOAD_GB} GB download from Apple "
            f"and needs ~{REQUIRED_FREE_GB} GB free (free now: {free_gb():.0f} GB). "
            "Ask the user, then rerun with --download.")
        return 5
    if action == "low_disk":
        log(f"Only {free_gb():.0f} GB free; the iPhone Duo runtime needs ~{REQUIRED_FREE_GB} GB. Ask the user to free space.")
        return 6
    if action == "download":
        log(f"Downloading the iOS runtime (~{DOWNLOAD_GB} GB). This takes a while.")
        result = subprocess.run(["xcodebuild", "-downloadPlatform", "iOS"], stdout=sys.stderr, stderr=sys.stderr)
        if result.returncode != 0 or not duo_runtimes(simctl_json("runtimes")):
            log("The download did not produce a runtime that supports iPhone Duo.")
            return 7

    runtime = duo_runtimes(simctl_json("runtimes"))[0]
    udid = create(args.name, runtime["identifier"])
    log(f"created {args.name} ({udid}) on {runtime['name']}")
    print(json.dumps({"udid": udid, "name": args.name, "runtime": runtime["identifier"], "action": "created"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
