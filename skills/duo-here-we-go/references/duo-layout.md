# iPhone Duo layout

Measured on the iPhone Duo simulator, iOS 27.1 (24A94425), with SwiftUI apps built against SDK 27.1. Not yet confirmed on a real device.

## What the device does

- Closed, the outer display is compact width (466 × 678 pt). A tab bar built with SDK 27.1 becomes a vertical bar on the physical right, below the status items.
- Open flat, the inner display is regular width (951 × 669 pt), the bar takes 84 pt on the right, and the hinge band sits at x = 455 to 495. Apps that switch layout on `horizontalSizeClass` show their iPad layout here.
- Half-open (90°), a `NavigationSplitView` snaps its columns to the hinge: sidebar 0 to 455 in a left-to-right language.

## Rules

### DHWG-001 · warn
`navigationSplitViewColumnWidth` with a max (or a fixed width) of 475 pt or less. Half-open in a left-to-right language the sidebar cannot reach the hinge, so the split view keeps the ideal width and the detail column runs across the fold. Measured with `.balanced` style, min 280, ideal 320: max 420 to 475 keeps the sidebar at 320; max 476 or no max snaps it to 455. Right-to-left is unaffected, because the sidebar sits beside the bar and its half is only 371 pt. **Fix:** raise the max above 475 (e.g. `max: 480`) or remove it, then check the English half-open capture.

## Reviewing a closed or open shot

- Content stays out of the vertical bar column (the 84 pt on the bar's side), unless it is a background. A view pinned to its superview's trailing edge instead of the safe area ends up inside it, in left-to-right languages only.

## Reviewing a half-open shot

- No text, control or card crosses the hinge band (x = 455 to 495 pt, or 1365 to 1485 px in a 3× capture).
- Each column ends at the hinge rather than near it.
- Floating buttons sit wholly inside one half.
- A full-width button or banner has its centred label on the fold (the centre of an 867 pt content area is 433 pt, and a label wider than about 45 pt reaches the band). Keeping it in one half, or one button per half, is a design decision for the user.
