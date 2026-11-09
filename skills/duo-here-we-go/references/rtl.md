# Arabic and RTL on iPhone Duo

Measured on the iPhone Duo simulator, iOS 27.1 (24A94425), with an app built against SDK 27.1. Not yet confirmed on a real device.

## What the device does

- The vertical bar (status items plus toolbar items) stays on the **same physical side** in every language. Only content mirrors.
- `toolbarVerticalEdge` (SwiftUI) and `verticalBarEdge` (UIKit) are **directional**: `trailing` in English, `leading` in Arabic, in every pose.
- Open flat, the inner display is 951 × 669 pt and the bar takes 84 pt. The hinge `division` region is at x = 455, 40 pt wide, active only when the device is partially open.
- At 90° split views snap to the hinge. The half beside the bar is narrower: 371 pt against 455 pt. In Arabic the sidebar moves to the bar side, so it gets the narrow half.
- `ArrangementView` with `overlayArrangementEdge(.trailing)` puts the primary on the trailing side, so in Arabic it moves to the other physical half and changes width.

## Rules

### DHWG-RTL-001 · error
`UIView.appearance().semanticContentAttribute` used for an in-app language switch while the system language stays LTR. Views flip, but `verticalBarEdge` keeps the system's side, so UIKit reserves room for the bar on the wrong side: an empty ~88 pt strip on the left (the bug in Apple forum thread 852870). **Fix:** also set `window.traitOverrides.layoutDirection = .rightToLeft` on every window (measured: the strip disappears and `verticalBarEdge` becomes `leading`). Better still, use the per-app language setting.

### DHWG-RTL-002 · warn
The project reads `UIView.reservedRegions` (physical frames, never mirrored) and `GeometryProxy.reservedRegions` with the default `.mirrors`. In Arabic the same hinge comes back at x = 455 from UIKit and x = 371 from SwiftUI. **Fix:** pass `layoutDirectionBehavior: .fixed` where SwiftUI frames meet UIKit frames.

### DHWG-RTL-003 · warn
The bar edge is mapped to `left`/`right`, `minX`/`maxX` or physical insets. **Fix:** keep it directional: leading/trailing padding or `safeAreaLayoutGuide` anchors.

### DHWG-RTL-004 · info
A fixed sidebar or arrangement width. **Fix:** min/ideal/max widths, then check the Arabic half-open capture.

### DHWG-RTL-005 · warn
The appearance-proxy switch in a project with SwiftUI views: SwiftUI ignores it, so SwiftUI screens stay LTR. **Fix (not yet verified on the Duo):** set `.environment(\.layoutDirection, .rightToLeft)` at the SwiftUI root.

## Comparing an Arabic shot with its English twin

- The bar is on the same physical side in both.
- No empty strip appears on the side away from the bar.
- Content is mirrored: titles, back buttons, list text and leading/trailing images.
- Half-open: the sidebar sits beside the bar and still fits the narrow half.
- Nothing important lands in the hinge band at x = 455 to 495.
- App Store screenshots are taken in Arabic, never made by flipping English ones, because the bar does not move.
