# Third-party notices

## hinge

- Source: https://github.com/artemnovichkov/hinge
- Commit: `06cb720276281da7f1aadd3874acb0d0ae5eb2b5` (v0.3.1)
- Files: `vendor/hinge/hinge`, `vendor/hinge/hinge_helper.m` (unmodified)
- License: MIT, Copyright (c) 2026 Artem Novichkov — full text in `vendor/hinge/LICENSE`

The helper posts the same private HID event that Xcode's Device Hub sends for its hinge slider. It runs only inside the iOS Simulator and may break with a future Xcode.

## Apple

Apple's `app-resizability` skill is not included. `scripts/export_apple_skills.sh` exports it from the user's own Xcode into a temporary folder at run time. Xcode's license does not permit redistributing it.
