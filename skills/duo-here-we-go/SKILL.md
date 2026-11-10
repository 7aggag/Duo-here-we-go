---
name: duo-here-we-go
description: Readies an existing SwiftUI or UIKit app for iPhone Duo, Apple's foldable. Runs Apple's app-resizability skill first, then checks Arabic and right-to-left layout around the vertical bar and the hinge, captures every pose on the Duo simulator, and writes one before/after readiness report. Use when asked to prepare or optimize an iOS app for iPhone Duo or the foldable iPhone, to check Arabic or RTL on iPhone Duo, or for a Duo readiness report or pose screenshots.
---

# Duo Here We Go

Scripts are in `scripts/` (Python 3.9+, standard library). Run them with `python3 <skill-dir>/scripts/<name>`. Everything they write goes to `<project>/dhwg-out/`, a scratch folder that stays out of commits.

## Ground rules

- **Apple first.** Apple's `app-resizability` skill does the resizability migration. This skill covers what it leaves: the vertical bar, the hinge, Arabic and RTL, captures and the report. When the two disagree, follow Apple and record the difference in the report.
- **Evidence.** Every claim that something works points at a capture or a finding, and every finding carries `verified`: `static`, `simulator`, `device` or `unverified`. A pose you did not capture is reported as not captured.
- **Consent before edits.** Code changes happen only on a clean git tree, after the user agrees to the phase that makes them.
- **Real APIs only.** Before writing any iPhone Duo API, confirm it in the installed SDK (see `references/duo-apis.md`) and wrap new calls in `#available(iOS 27.1, *)`.

## Steps

### 1. Preflight

```bash
python3 scripts/preflight.py <project> --out <project>/dhwg-out/preflight.json
```

If it reports no iPhone Duo simulator, run `python3 scripts/setup_duo.py`. It creates one when an installed runtime supports the device. Exit 5 means the runtime itself is missing: tell the user it is a ~8 GB download from Apple and how much disk is free, and rerun with `--download` only after they agree. Exit 2 means the Xcode is older than 27.1; exit 6 means not enough disk.

Done when preflight exits 0, or the user has fixed or explicitly accepted each item in `problems`. Preflight also adds `dhwg-out/` to the repo's local `.git/info/exclude`, so the scratch folder never dirties the tree. If `arabic_localization` is false, tell the user the RTL step can lint but cannot show Arabic layout until the app ships an Arabic localization.

### 2. Build for the Duo simulator

Pick the scheme with `xcodebuild -list` (ask the user when there is more than one app scheme), then:

```bash
xcodebuild -scheme <Scheme> -destination 'platform=iOS Simulator,id=<duo udid from preflight>' \
  -derivedDataPath <project>/dhwg-out/DerivedData build
```

Done when the `.app` exists under `dhwg-out/DerivedData/Build/Products/` and `xcrun vtool -show-build <App>.app/<executable>` reports `sdk 27.1` or later. An older SDK keeps the bars horizontal, so the captures would not show the Duo layout.

### 3. Baseline captures

First find the app's own test hooks: grep the sources for `ProcessInfo.processInfo.arguments` and the `UserDefaults` keys behind onboarding, so the captures land on real screens with data instead of a first-run welcome. A UI-testing flag that seeds sample data is the best case; a defaults key such as `-settings.onboardingDone YES` also works. Pass them after `--`.

```bash
python3 scripts/capture.py --app <path/App.app> --out <project>/dhwg-out --label baseline [-- <app launch args>]
```

Look at the first shot before trusting the rest:

- A system permission alert (notifications, tracking) covers every shot. Dismiss it once on the simulator, choosing the declining option unless the user says otherwise, then recapture; the choice lasts for the install.
- A splash screen means the app was still loading (often a network check): raise `--wait`.
- A video or looping animation never settles: pass a short `--settle-timeout` and accept the single warning it writes.

It captures closed, open (180°) and half-open (90°) poses, in English and Arabic, waiting for each screen to stop moving. Exit 3 means hinge control failed: ask the user to set that pose in Device Hub, then rerun with `--no-hinge --poses <pose>`. Done when `dhwg-out/baseline/manifest.json` lists six stable shots, or each missing or unstable one is in its `warnings`, and you have looked at every shot.

### 4. Apple pass

Follow `references/apple-bridge.md`. Done when every file Apple's skill flags has a diff or a stated reason to skip, and `dhwg-out/findings-apple.json` exists.

### 5. Lint and visual review

```bash
python3 scripts/dhwg_lint.py <project> --out <project>/dhwg-out/findings-lint.json --fail-on never
```

For each finding, read its rule (`DHWG-RTL-*` in `references/rtl.md`, `DHWG-0xx` in `references/duo-layout.md`), open the code, and mark it confirmed or a false positive. A false positive is suppressed in code with a reason, after the user agrees. Then review every shot with the checklists in both references: each Arabic shot against its English twin, and each half-open shot against the hinge band. Record each visual problem in `dhwg-out/findings-visual.json` (a list; `id` is `DHWG-RTL-VIS` for a right-to-left problem and `DHWG-VIS` otherwise; `verified: "simulator"`; `evidence`: the shot path). When you can tie it to code, add `file` and `line`.

Two checks keep the findings honest:

- **Regular iPhone first.** Before recording a visual problem, install the same build on a regular iPhone simulator and look for it there. A problem that shows on both is the app's, not the Duo's: mention it to the user, keep it out of the findings.
- **Coverage.** List the screens the captures never reached (behind login, payment, deep flows) in one `DHWG-COVERAGE` finding with `verified: "unverified"`, so the report says what was not looked at.

Propose fixes; apply them only when the user asks. Done when every lint finding has a verdict, every shot has been reviewed, and the coverage finding is written or every screen was reached.

### 6. After captures

If steps 4 or 5 changed code, rebuild (step 2) and capture again with `--label after`. Done when `dhwg-out/after/manifest.json` exists, or nothing changed.

### 7. Report

```bash
python3 scripts/report.py --out <project>/dhwg-out/REPORT.md --captures <project>/dhwg-out \
  --preflight <project>/dhwg-out/preflight.json \
  --findings <project>/dhwg-out/findings-apple.json <project>/dhwg-out/findings-lint.json <project>/dhwg-out/findings-visual.json
```

Done when `REPORT.md` exists and you have told the user its readiness line, each error, and every item under "Not verified".
