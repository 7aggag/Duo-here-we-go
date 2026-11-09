# Duo Here We Go

*Here we go, Duo.*

An agent skill that readies an existing SwiftUI or UIKit app for **iPhone Duo**, Apple's foldable, with first-class **Arabic and right-to-left** support.

1. Runs Apple's own `app-resizability` skill first (exported from your Xcode, never bundled).
2. Checks what it leaves: the vertical bar, the hinge, and RTL layout, with rules measured on the iPhone Duo simulator.
3. Captures closed, open and half-open poses in English and Arabic.
4. Writes one before/after `REPORT.md` with a readiness line and an honest "Not verified" list.

## Requirements

- macOS with Xcode 27.1 or later and the iOS 27.1 simulator runtime
- An iPhone Duo simulator
- Python 3.9+ (the one that ships with Xcode's command line tools works)

## Install (Claude Code)

```bash
claude plugin marketplace add <path-or-git-url-of-this-repo>
claude plugin install duo-here-we-go@duo-here-we-go
```

Then ask: *"Get this app ready for iPhone Duo."*

## Layout

```
skills/duo-here-we-go/
  SKILL.md              steps the agent follows
  references/           Apple bridge, RTL rules, API cheat sheet
  scripts/              preflight, capture, lint, report (stdlib Python)
  vendor/hinge/         hinge CLI by Artem Novichkov (MIT), drives the simulator hinge
docs/                   architecture and research
research/rtl-probe/     the probe apps behind the RTL rules, with their captures
tests/                  python3 -m unittest discover -s tests
```

## Status

v0.1, verified on the simulator only. See `docs/ARCHITECTURE.md` for the phases still to come.

## License

MIT. Third-party code is listed in `skills/duo-here-we-go/THIRD_PARTY_NOTICES.md`. iPhone and iPhone Duo are trademarks of Apple Inc.; this project is not affiliated with Apple.
