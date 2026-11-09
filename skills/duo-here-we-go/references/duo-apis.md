# iPhone Duo APIs (iOS 27.1 SDK)

Read from the SDK 27.1 Swift interfaces. Before using one, confirm it in the user's installed SDK:

```bash
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
grep -rn "<symbol>" "$SDK"/System/Library/Frameworks/{SwiftUICore,SwiftUI,UIKit}.framework/Modules/*.swiftmodule/arm64-apple-ios-simulator.swiftinterface
```

## SwiftUI

| API | Shape |
|---|---|
| `EnvironmentValues.toolbarVerticalEdge` | `HorizontalEdge?`; `nil` where there is no vertical bar |
| `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)` | `→ [ReservedRegion]`; behaviour defaults to `.mirrors` |
| `ReservedRegion` | `id`, `kind` (`.occlusion`, `.division`), `frame`, `margins: EdgeInsets`, `isActive` |
| `View.onHingeChange(isEnabled:_:)` | `(DeviceHingeContext, DeviceHingeContext) -> Void`; `context.hinge?.status` is `.closed`, `.partiallyOpen` or `.fullyOpen`, `angle: Angle` |
| `ArrangementView(primary:secondary:)` | with `.arrangementViewStyle(OverlayArrangementViewStyle())` or `SplitArrangementViewStyle` |
| `View.overlayArrangementEdge(_:)` | `HorizontalEdge?` or `VerticalEdge?` |
| `EnvironmentValues.overlayArrangementZIndex` | `Int` |

## UIKit

| API | Shape |
|---|---|
| `UITraitCollection.verticalBarEdge` | `UIVerticalBarEdge`: `.unspecified`, `.leading`, `.trailing` |
| `UITraitCollection.systemTraitsAffectingVerticalBarEdge` | pass to `registerForTraitChanges`; includes the layout-direction trait |
| `UIView.reservedRegions(kind:options:)` | `→ [UIView.ReservedRegion]`, view coordinates, no direction option |
| `UIHingeInteraction`, `UIArrangementViewController` | present in the headers; not yet exercised by this skill |
