# Running Apple's app-resizability skill

Apple ships `app-resizability` inside Xcode 27.1. It **edits code**: it migrates `UIScreen.main`, orientation checks, `userInterfaceIdiom`, the app/scene lifecycle and safe-area insets, and runs three read-only `Info.plist` checks first. Xcode's license forbids redistributing it, so it is exported fresh on the user's Mac and never copied into any repository or report.

## Run it

1. Confirm `git status` is clean and the user has agreed that Apple's skill may edit the project.
2. Export:
   ```bash
   scripts/export_apple_skills.sh
   ```
   It prints the skill folder inside `$TMPDIR`. Exit 3 means the Xcode is older than 27.1; exit 4 means its export has no resizability skill. In both cases use the fallback below.
3. Read that folder's `SKILL.md` and follow its workflow exactly as written, loading its task files from the same folder. Its own rules (stay in scope, never skip a file silently) apply while it runs.
4. When it finishes, run `git diff --stat` and keep its prerequisite report.

## Turn its result into findings

Write `dhwg-out/findings-apple.json` as a JSON list, in your own words (no text copied from Apple's files):

| Situation | `id` | `severity` | `message` |
|---|---|---|---|
| A file it changed | `APPLE-<task>` (`uiscreen`, `orientation`, `idiom`, `scene-lifecycle`, `safe-area`) | `info` | `Applied: <what changed>` |
| A TODO it left | `APPLE-<task>` | `warn` | what is still open |
| A prerequisite check it reported as failing | `APPLE-prerequisite` | `error` | the key and what it blocks |
| It ran and found nothing to change | `APPLE-summary` | `info` | which checks passed and which tasks found no target API |

Every entry has `source: "apple"`, `fix`, and `verified: "static"`; entries tied to code also have `file` and `line` (the first changed line). Always write at least one entry, so the report shows the Apple pass ran.

## Fallback without Apple's skill

Check these by hand, record each hit as `APPLE-manual` with `verified: "static"`, and tell the user the official skill did not run:

- Layout reads `UIScreen.main` bounds or scale instead of the view, window or scene.
- Layout branches on interface orientation instead of size classes or the available size.
- Code treats `userInterfaceIdiom` or a size class as the device type.
- Full-bleed media relies on `.scaleAspectFill` cropping a fixed aspect ratio.
- `UIRequiresFullScreen` is set, or the app has no launch screen.
