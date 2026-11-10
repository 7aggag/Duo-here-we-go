"""Shared helpers for the Duo Here We Go scripts. Python 3.9, standard library only."""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

SKILL_DIR = Path(__file__).resolve().parent.parent
HINGE = SKILL_DIR / "vendor" / "hinge" / "hinge"
DUO_DEVICE_TYPE = "com.apple.CoreSimulator.SimDeviceType.iPhone-Duo"
POSE_ANGLES = {"closed": 0, "open": 180, "half": 90}
LANG_ARGS = {
    "en": ["-AppleLanguages", "(en)", "-AppleLocale", "en_US"],
    "ar": ["-AppleLanguages", "(ar)", "-AppleLocale", "ar_EG"],
}


EXCLUDED_DIRS = {".git", "Pods", "Carthage", ".build", "DerivedData", "build", "SourcePackages", "node_modules", "dhwg-out"}


def project_files(root: Path, suffixes: tuple) -> List[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.endswith((".app", ".xcassets"))]
        found.extend(Path(dirpath) / f for f in filenames if f.endswith(suffixes))
    return sorted(found)


def log(msg: str) -> None:
    print(f"[dhwg] {msg}", file=sys.stderr)


def run(cmd: List[str], check: bool = True, timeout: Optional[float] = 120) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}")
    return result


def simctl_devices() -> List[dict]:
    data = json.loads(run(["xcrun", "simctl", "list", "devices", "-j"]).stdout)
    devices = []
    for runtime, items in data.get("devices", {}).items():
        for d in items:
            d["runtime"] = runtime
            devices.append(d)
    return devices


def find_duo(udid: Optional[str] = None) -> Optional[dict]:
    duos = [d for d in simctl_devices()
            if d.get("deviceTypeIdentifier") == DUO_DEVICE_TYPE and d.get("isAvailable", True)]
    if udid:
        return next((d for d in duos if d["udid"].upper() == udid.upper()), None)
    booted = [d for d in duos if d.get("state") == "Booted"]
    return (booted or duos or [None])[0]


def pick_regular_iphone(devices: List[dict]) -> Optional[dict]:
    """A non-foldable iPhone simulator for comparison, booted ones first."""
    phones = [d for d in devices if d.get("isAvailable", True)
              and ".SimDeviceType.iPhone-" in d.get("deviceTypeIdentifier", "")
              and d.get("deviceTypeIdentifier") != DUO_DEVICE_TYPE]
    booted = [d for d in phones if d.get("state") == "Booted"]
    return (booted or phones or [None])[0]


def ensure_booted(udid: str) -> None:
    state = next((d.get("state") for d in simctl_devices() if d["udid"] == udid), None)
    if state != "Booted":
        log(f"booting {udid}")
        run(["xcrun", "simctl", "boot", udid], check=False)
    run(["xcrun", "simctl", "bootstatus", udid, "-b"], timeout=300)


def hinge(udid: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ, HINGE_DEVICE=udid)
    result = subprocess.run([str(HINGE), *args], capture_output=True, text=True, env=env, timeout=120)
    if check and result.returncode != 0:
        raise RuntimeError(f"hinge {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
