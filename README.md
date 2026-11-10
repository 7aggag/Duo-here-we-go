# Duo Here We Go

*Here we go, Duo.*

An agent skill that readies an existing SwiftUI or UIKit app for **iPhone Duo**, Apple's foldable, with first-class **Arabic and right-to-left** support.

1. Runs Apple's own `app-resizability` skill first (exported from your Xcode, never bundled).
2. Checks what it leaves: the vertical bar, the hinge, and RTL layout, with rules measured on the iPhone Duo simulator.
3. Captures closed, open and half-open poses in English and Arabic.
4. Writes one before/after `REPORT.md` with a readiness line and an honest "Not verified" list.

## Requirements

- macOS with Xcode 27.1 or later (the skill creates the iPhone Duo simulator, and downloads its runtime after asking you)
- Python 3.9+ (the one that ships with Xcode's command line tools works)
- An agent that can run terminal commands; the visual review needs a model that reads images

## Install

Pick one way. Using two installs the skill twice in the same agent.

**Every agent on your Mac** (Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Antigravity and more):

```bash
npx skills add 7aggag/Duo-here-we-go -g --agent '*' -y
```

Or only the agents you name:

```bash
npx skills add 7aggag/Duo-here-we-go -g -a claude-code -a cursor -a codex -a opencode -y
```

**Without Node:** clone once and link the skill where agents look for it.

```bash
git clone https://github.com/7aggag/Duo-here-we-go.git ~/.duo-here-we-go && mkdir -p ~/.agents/skills ~/.claude/skills && ln -sfn ~/.duo-here-we-go/skills/duo-here-we-go ~/.agents/skills/duo-here-we-go && ln -sfn ~/.duo-here-we-go/skills/duo-here-we-go ~/.claude/skills/duo-here-we-go
```

**Claude Code plugin:**

```bash
claude plugin marketplace add 7aggag/Duo-here-we-go
claude plugin install duo-here-we-go@duo-here-we-go
```

Then ask your agent: *"Get this app ready for iPhone Duo."*

## Layout

```
skills/duo-here-we-go/
  SKILL.md              steps the agent follows
  references/           Apple bridge, RTL rules, API cheat sheet
  scripts/              preflight, simulator setup, capture, lint, report (stdlib Python)
  vendor/hinge/         hinge CLI by Artem Novichkov (MIT), drives the simulator hinge
docs/                   architecture and research
research/rtl-probe/     the probe apps behind the RTL rules, with their captures
tests/                  python3 -m unittest discover -s tests
```

## Status

v0.1, verified on the simulator only. See `docs/ARCHITECTURE.md` for the phases still to come.

## License

MIT. Third-party code is listed in `skills/duo-here-we-go/THIRD_PARTY_NOTICES.md`. iPhone and iPhone Duo are trademarks of Apple Inc.; this project is not affiliated with Apple.
