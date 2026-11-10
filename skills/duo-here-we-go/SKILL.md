---
name: duo-here-we-go
description: Readies an existing SwiftUI, UIKit or Flutter app for iPhone Duo, Apple's foldable. Runs Apple's app-resizability skill first, then checks Arabic and right-to-left layout around the vertical bar and the hinge, captures every pose on the Duo simulator, and writes one before/after readiness report. Use when asked to prepare or optimize an iOS or Flutter app for iPhone Duo or the foldable iPhone, to check Arabic or RTL on iPhone Duo, or for a Duo readiness report, pose screenshots, or iPhone Duo App Store screenshots.
---

# Duo Here We Go

Scripts are in `scripts/` (Python 3.9+, standard library). Run them with `python3 <skill-dir>/scripts/<name>`. Everything they write goes to `<project>/dhwg-out/`, a scratch folder that stays out of commits.

## Ground rules

- **Flutter.** When preflight reports `kind: flutter`, read `references/flutter.md` first: it replaces the UIKit and SwiftUI parts of steps 2, 4 and 5, and the same steps, checkpoints and report apply otherwise.

- **Apple first.** Apple's `app-resizability` skill does the resizability migration. This skill covers what it leaves: the vertical bar, the hinge, Arabic and RTL, captures and the report. When the two disagree, follow Apple and record the difference in the report.
- **Evidence.** Every claim that something works points at a capture or a finding, and every finding carries `verified`: `static`, `simulator`, `device` or `unverified`. A pose you did not capture is reported as not captured.
- **Consent before edits.** Code changes happen only on a clean git tree, after the user says yes to that specific change at a checkpoint (step 4 for Apple's edits, step 6 for the rest). A request such as "get the app ready for iPhone Duo" starts the review; it is not a yes to edits. Leave every change in the working tree for the user to review and commit.
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

For Flutter, build with `flutter build ios --simulator --debug` instead (flavors and defines in `references/flutter.md`); the app is under `build/ios/iphonesimulator/`.

Done when the `.app` exists under `dhwg-out/DerivedData/Build/Products/` (or `build/ios/iphonesimulator/` for Flutter) and `xcrun vtool -show-build <App>.app/<executable>` reports `sdk 27.1` or later. An older SDK keeps the bars horizontal, so the captures would not show the Duo layout.

### 3. Baseline captures

First find the app's own test hooks: grep the sources for `ProcessInfo.processInfo.arguments` and the `UserDefaults` keys behind onboarding, so the captures land on real screens with data instead of a first-run welcome. A UI-testing flag that seeds sample data is the best case; a defaults key such as `-settings.onboardingDone YES` also works. Pass them after `--`.

```bash
python3 scripts/capture.py --app <path/App.app> --out <project>/dhwg-out --label baseline --iphone [-- <app launch args>]
```

`--iphone` adds English and Arabic shots from a regular iPhone simulator, for the comparison in step 5. To cover more screens, run it again per screen with the app's own hooks and a label such as `--label screen-reports`; the report shows every label.

Look at the first shot before trusting the rest:

- A system permission alert (notifications, tracking) covers every shot. Dismiss it once on the simulator, choosing the declining option unless the user says otherwise, then recapture; the choice lasts for the install.
- A splash screen means the app was still loading (often a network check): raise `--wait`.
- A video or looping animation never settles: pass a short `--settle-timeout` and accept the single warning it writes.
- A black shot: since Xcode 27.2 the Duo simulator returns black screenshots for a few minutes after boot. The script waits for that to pass (`--display-timeout`, default 300 s) and never counts a black frame as settled; a shot that is still black is named in `warnings`. Recapture that pose.

It captures closed, open (180°) and half-open (90°) poses, in English and Arabic, waiting for each screen to stop moving. Exit 3 means hinge control failed: ask the user to set that pose in Device Hub, then rerun with `--no-hinge --poses <pose>`. Done when `dhwg-out/baseline/manifest.json` lists six stable shots, or each missing or unstable one is in its `warnings`, and you have looked at every shot.

### 4. Apple pass

Follow `references/apple-bridge.md`. For Flutter, run it on `ios/Runner` only (UIScene, orientations, `Info.plist`): Apple's skill does not read Dart, and the layout work belongs to duo-adapt (see `references/flutter.md`), which the user installs and runs separately if they want it. Done when every file Apple's skill flags has a diff or a stated reason to skip, and `dhwg-out/findings-apple.json` exists.

### 5. Lint and visual review

```bash
python3 scripts/dhwg_lint.py <project> --out <project>/dhwg-out/findings-lint.json --fail-on never
```

For each finding, read its rule (`DHWG-RTL-*` in `references/rtl.md`, `DHWG-0xx` in `references/duo-layout.md`, `DHWG-FL-*` and `DHWG-RTL-006` in `references/flutter.md`; `DHWG-002` is about Touch ID copy, not layout), open the code, and mark it confirmed or a false positive. A false positive is suppressed in code with a reason, after the user agrees. Then review every shot with the checklists in both references (for Flutter, the one in `references/flutter.md`): each Arabic shot against its English twin, and each half-open shot against the hinge band. Record each visual problem in `dhwg-out/findings-visual.json` (a list; `id` is `DHWG-RTL-VIS` with `source: "rtl"` for a right-to-left problem, `DHWG-VIS` with `source: "dhwg"` otherwise; `severity`; `verified: "simulator"`; `evidence`: the shot path). When you can tie it to code, add `file` and `line`.

Two checks keep the findings honest:

- **Regular iPhone first.** Before recording a visual problem, look for it in the `iphone` shots. A problem that shows on both is the app's, not the Duo's: mention it to the user, keep it out of the findings.
- **Coverage.** List the screens the captures never reached (behind login, payment, deep flows) in one `DHWG-COVERAGE` finding with `verified: "unverified"`, so the report says what was not looked at.

Done when every lint finding has a verdict, every shot has been reviewed, and the coverage finding is written or every screen was reached.

### 6. Checkpoint

Write the report (step 8) as it stands, then stop and show the user each finding with the fix you propose: file, the change, and what it does on a regular iPhone. Wait for their answer. Done when the user has said yes, no or later to each proposed fix.

### 7. Fix and capture again

Apply only the fixes the user accepted. Then rebuild (step 2), capture again with `--label after` (same hooks and labels as before), and rerun the lint. For each finding the after shots show fixed, set `severity: "info"`, start its `message` with `Fixed:`, keep what the problem was, and point `evidence` at the after shot. Done when `dhwg-out/after/manifest.json` exists and every accepted fix is either shown fixed or reported as still open.

### 8. Report

```bash
python3 scripts/report.py --out <project>/dhwg-out/REPORT.md --captures <project>/dhwg-out --title "<App name>" \
  --preflight <project>/dhwg-out/preflight.json \
  --findings <project>/dhwg-out/findings-apple.json <project>/dhwg-out/findings-lint.json <project>/dhwg-out/findings-visual.json
```

Done when `REPORT.md` exists and you have told the user its readiness line, each error, every item under "Not verified", and which files changed (uncommitted).

### 9. App Store screenshots (only when asked)

Run this only when the user asks for store screenshots. App Store Connect accepts iPhone Duo screenshots at 1398 × 2034 (outer display) and 2007 × 2853 (inner display), in either orientation, and shows a badge on the product page when they are there. Capture the screens worth showing first, after the fixes and with the app's sample-data hooks, one label per screen (`--label store-home`, `--label store-detail`, ...), then:

```bash
python3 scripts/store_shots.py --captures <project>/dhwg-out --labels store-home,store-detail --poses open,half,closed
```

It keeps the Duo shots at those sizes, drops the alpha channel the simulator adds (App Store Connect rejects it), and writes `dhwg-out/store/<lang>/NN-<label>-<pose>.jpg` in label order, then pose order, at most 10 per language. Arabic shots of an app with no Arabic localization are left out: store screenshots in Arabic are always captured in Arabic, never mirrored from English (`references/rtl.md`). Look at every file before handing them over.

App Store Connect keeps one iPhone Duo set per language that takes both sizes together, up to 10 (API display type `APP_IPHONE_DUO`), so each language folder is one set.

It adds no titles, frames or marketing text and uploads nothing. Done when you have told the user where each language folder is, each warning, and that they add each folder themselves, in file-name order, under iPhone Duo in that language's Media Manager in App Store Connect. Mention the product-page preview there, and that `fastlane deliver` and the `asc` CLI can upload to `APP_IPHONE_DUO` if they want to automate it later.
