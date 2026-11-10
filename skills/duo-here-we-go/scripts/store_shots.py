#!/usr/bin/env python3
"""Turn iPhone Duo captures into App Store screenshots, one folder per language.

usage: store_shots.py --captures dhwg-out [--labels after] [--out dhwg-out/store]
                      [--poses open,half,closed] [--langs en,ar]

Reads <captures>/<label>/manifest.json for each label, keeps the Duo shots whose size App Store
Connect accepts for iPhone Duo, and writes them as alpha-free JPEGs to <out>/<lang>/NN-<label>-<pose>.jpg,
in label order then pose order, at most 10 per language. Black frames, regular-iPhone shots and the
Arabic shots of an app with no Arabic localization are left out and named in the warnings.
Nothing is uploaded: the user adds the folders to App Store Connect themselves.
exit 0 = done, 2 = no usable capture.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from capture import is_black_frame
from dhwg_common import LANG_ARGS, POSE_ANGLES, log, run, write_json

# App Store Connect, Screenshot specifications, iPhone Duo (checked November 2026). Both displays go into
# one set per language (API display type APP_IPHONE_DUO), so the 10-screenshot limit covers them together.
DUO_SIZES = {(1398, 2034): "outer", (2034, 1398): "outer", (2007, 2853): "inner", (2853, 2007): "inner"}
MAX_PER_LANG = 10


def png_size(png: bytes) -> Optional[Tuple[int, int]]:
    if png[:8] != b"\x89PNG\r\n\x1a\n" or png[12:16] != b"IHDR":
        return None
    return int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")


def select(manifests: List[dict], root: Path, poses: List[str], langs: List[str]) -> Tuple[Dict[str, list], List[str]]:
    """Pick the shots for each language. Returns ({lang: [entry, ...]}, warnings)."""
    picked: Dict[str, list] = {lang: [] for lang in langs}
    warnings: List[str] = []
    for m in manifests:
        label = m["label"]
        if "ar" in langs and m.get("arabic_in_bundle") is False:
            warnings.append(f"{label}: the app has no Arabic localization, so its 'ar' shots are left-to-right; "
                            "left out.")
        by_key = {(s["pose"], s["lang"]): s for s in m["shots"]}
        for lang in langs:
            if lang == "ar" and m.get("arabic_in_bundle") is False:
                continue
            for pose in poses:
                shot = by_key.get((pose, lang))
                if shot is None:
                    continue
                path = root / shot["path"]
                name = f"{label}/{pose}/{lang}"
                if not path.is_file():
                    warnings.append(f"{name}: {path} is missing; left out.")
                    continue
                data = path.read_bytes()
                size = png_size(data)
                if size not in DUO_SIZES:
                    warnings.append(f"{name}: {size} is not an iPhone Duo screenshot size; left out.")
                    continue
                if is_black_frame(data):
                    warnings.append(f"{name}: black frame; recapture this pose. Left out.")
                    continue
                if not shot.get("stable", True):
                    warnings.append(f"{name}: the screen was still moving when captured; check the shot.")
                picked[lang].append({"label": label, "pose": pose, "lang": lang, "source": str(path),
                                     "width": size[0], "height": size[1], "display": DUO_SIZES[size]})
    for lang, items in picked.items():
        if len(items) > MAX_PER_LANG:
            dropped = ", ".join(f"{i['label']}/{i['pose']}" for i in items[MAX_PER_LANG:])
            warnings.append(f"{lang}: App Store Connect takes at most {MAX_PER_LANG} screenshots per size; "
                            f"left out {dropped}.")
            del items[MAX_PER_LANG:]
        if not items:
            warnings.append(f"{lang}: no usable shot.")
    return picked, warnings


def to_jpeg(src: Path, dst: Path) -> None:
    """App Store screenshots may not carry an alpha channel; simulator PNGs do. JPEG drops it."""
    run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "best", str(src), "--out", str(dst)])


def write_store(picked: Dict[str, list], out: Path, convert: Callable[[Path, Path], None] = to_jpeg) -> None:
    for lang, items in picked.items():
        folder = out / lang
        if folder.is_dir():
            for old in folder.glob("*.jpg"):
                old.unlink()
        folder.mkdir(parents=True, exist_ok=True)
        for n, item in enumerate(items, 1):
            dst = folder / f"{n:02d}-{item['label']}-{item['pose']}.jpg"
            convert(Path(item["source"]), dst)
            item["file"] = str(dst.relative_to(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", default="dhwg-out")
    ap.add_argument("--labels", default="after", help="capture labels in store order, comma separated")
    ap.add_argument("--out")
    ap.add_argument("--poses", default="open,half,closed", help="pose order within each label")
    ap.add_argument("--langs", default="en,ar")
    args = ap.parse_args()

    root = Path(args.captures).resolve()
    out = Path(args.out).resolve() if args.out else root / "store"
    poses, langs = args.poses.split(","), args.langs.split(",")
    bad = [p for p in poses if p not in POSE_ANGLES] + [l for l in langs if l not in LANG_ARGS]
    if bad:
        log(f"unknown pose or language: {bad}")
        return 2

    manifests, warnings = [], []
    for label in args.labels.split(","):
        path = root / label / "manifest.json"
        if path.is_file():
            manifests.append(json.loads(path.read_text(encoding="utf-8")))
        else:
            warnings.append(f"{label}: no {path}; run capture.py --label {label} first.")
    picked, more = select(manifests, root, poses, langs)
    warnings += more
    if not any(picked.values()):
        log("no usable capture; " + " ".join(warnings))
        return 2
    write_store(picked, out)
    result = {"out": str(out), "languages": picked, "warnings": warnings,
              "next": "Add each language folder to the iPhone Duo screenshots of that localization in "
                      "App Store Connect, in file-name order."}
    write_json(out / "manifest.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
