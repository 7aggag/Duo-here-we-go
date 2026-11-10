# Flutter apps on iPhone Duo

Flutter draws its own bars and reads its own safe area, so most of `duo-layout.md` and `rtl.md` (UIKit traits, SwiftUI regions, split views) does not apply. What does apply is below.

Measured on the iPhone Duo simulator, iOS 27.1 (24A94425), with Flutter 3.47.9 and an app built against SDK 27.1 (`research/flutter-probe`). Not yet confirmed on a real device; the outer display in landscape, tabletop and Split View are not measured.

## What the device does to a Flutter app

- **The system column is a safe-area inset.** `viewPadding` and `padding` are `L0 T0 R84 B34` closed (466 × 678 pt), open (951 × 669 pt) and half-open, in English and in Arabic: the column stays on the physical right. `devicePixelRatio` is 3.0. (Open with the device upright, duo-adapt reports `T82 B34`; not measured here.)
- **Flutter's own bars do not move.** An `AppBar`, `NavigationBar` or `BottomNavigationBar` stays at the top or bottom; only native UIKit bars go vertical. Apple's guidance is to leave the bars where the system puts them, which for Flutter means drawing them in the column yourself (duo-adapt's `AdaptiveShell` does this).
- **Body content runs under the column; `AppBar` and dialogs do not.** A `ListView` without `SafeArea` reaches the screen edge, and the clock and Wi-Fi cover the end of the first rows (to about 150 pt from the top closed, 100 pt open). `AppBar` keeps its back button and actions out of the column, and dialogs centre in the space beside it. `SafeArea` stops the rows at 867 pt.
- **No fold.** `MediaQuery.displayFeatures` is empty even half-open, so dialogs, sheets and menus ignore the hinge: an `AlertDialog` half-open spans about x = 294 to 573 pt, across the hinge band at 455 to 495, in both languages. A bridge package (`foldable`, pinned) or a Flutter release with PR #193025 fills it; the fold then arrives about a second after the hinge settles.
- **Orientation locks stick.** On the inner display the app's supported orientations are ignored, a `setPreferredOrientations` lock set at run time persists, and later changes fail. `UIRequiresFullScreen` makes iOS scale the app into a portrait window with no fold at all.
- **`PlatformDispatcher.displays`** reports the outer display (1398 × 2034 px) in every pose, open included; read sizes from `MediaQuery`/`LayoutBuilder`.

## Arabic

- The column stays on the physical right in Arabic. `viewPadding` is physical, so `SafeArea` and `EdgeInsets.only(right: viewPadding.right)` are right in both languages.
- In Arabic a row's start is on the right, so without `SafeArea` it is the **title**, not the trailing detail, that sits under the clock and Wi-Fi. Check the Arabic shot even when the English one looks fine.
- Turning a physical inset into a directional one (`EdgeInsetsDirectional.only(end: padding.right)`) puts the gap on the left in Arabic while the column is still on the right.
- A two-pane layout puts the leading pane on the right in Arabic, so half-open the primary pane moves to the half beside the column.
- Flutter reads the system languages directly, so `-AppleLanguages (ar)` switches the app as long as `supportedLocales` has Arabic. List `ar` in `ios/Runner/Info.plist` `CFBundleLocalizations` too, so iOS offers the language in Settings and the App Store.

## Rules

### DHWG-FL-001 · warn
App code reads `displayFeatures` (or uses `DisplayFeatureSubScreen`) and `pubspec.yaml` has no bridge package. The list is empty on iOS, so the fold logic never runs on iPhone Duo. **Fix:** add a bridge such as `foldable` (a new dependency: ask first), or confirm the project's Flutter version includes PR #193025.

### DHWG-FL-002 · warn
A portrait-only `SystemChrome.setPreferredOrientations`. **Fix:** remove the lock and lay out from the available size.

### DHWG-FL-003 · error
`UIRequiresFullScreen` is true in `ios/Runner/Info.plist`. **Fix:** remove it and allow every orientation, unless there is a written reason.

### DHWG-FL-004 · warn
The right inset is dropped (`SafeArea(right: false)`, `removeRight: true`), so content runs under the column. **Fix:** keep it, or pad by `viewPadding.right`.

### DHWG-RTL-006 · warn
A physical inset in `EdgeInsetsDirectional`. **Fix:** keep MediaQuery insets physical.

`DHWG-002` (Face ID copy) also checks `.dart` strings and `.arb` files; it drops to info when the app reads `getAvailableBiometrics`/`BiometricType`. Tests under `test/` and `integration_test/` and generated `*.g.dart`/`*.freezed.dart` files are not linted.

## Building and capturing

```bash
flutter build ios --simulator --debug [--flavor <flavor> -t lib/main_<flavor>.dart] [--dart-define=...]
```

The app is `build/ios/iphonesimulator/Runner.app` (the flavor's name when there is one). Check it with `xcrun vtool -show-build` as in step 2: it must report `sdk 27.1` or later, which needs `xcode-select` on Xcode 27.1. A debug simulator build runs on its own without `flutter run`. Flutter apps rarely read launch arguments, so the test hooks for step 3 are usually `--dart-define` values at build time (a dev route, seeded data) rather than arguments after `--`.

## Reviewing Flutter shots

- Closed and open in landscape: no text, row or button under the right-hand column, in both languages; the first rows under the clock and Wi-Fi are the usual sign.
- Open in portrait: the app's own bars at the top and bottom, nothing under the status area.
- Half-open: dialogs, sheets and menus open on one side of the fold, or the coverage finding says no bridge is installed. Two-pane layouts meet at the fold.
- Arabic against English: the column on the right in both; the leading pane on the right in Arabic; no empty strip on the left.

## Adapting the layout

This skill reviews, captures and reports; it does not redesign a Flutter app. For the layout work (navigation in the side column, list/detail that survives folding, the fold layer) point the user to [duo-adapt](https://github.com/islam-diab/duo-adapt) (MIT), a separate Claude Code plugin they install themselves. A good order is this skill's baseline captures and report first, duo-adapt's plan second, then this skill's `after` captures for the before/after report. Never install it, or copy its templates into the project, without the user asking.
