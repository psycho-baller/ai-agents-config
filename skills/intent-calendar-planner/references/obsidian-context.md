# Obsidian Context

## Canonical Source

Always treat this iCloud path as the source of truth:

`/Users/rami/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian`

Do not prefer the mirrored copy under `Documents/Obsidian` when the iCloud vault is available.

## Access Pattern

Direct shell reads from the iCloud path may fail with `Operation not permitted`. Use the bundled staging helper:

```bash
bash scripts/stage_obsidian_context.sh --output-dir /private/tmp/intent-calendar-context --daily-notes 3
```

That helper uses Finder via AppleScript to duplicate the needed files into a readable local staging directory.

## What To Read

Read in this order:

1. `My Projects/CLAUDE.md`
2. Non-archived project files in `My Projects/`
3. `My Areas/My Areas.md`
4. Referenced area files when they exist
5. Recent daily notes only when they add planning signal

## Scope Rules

- Ignore `My Projects/Archive/` unless the user explicitly asks about paused or abandoned work.
- Ignore `My Projects.base` for planning decisions.
- Trust each project file's own frontmatter and body before the summary table in `CLAUDE.md`.
- Favor `Status: active` and `Priority: high` first, but still look for meaningful links across projects.
- Daily notes are secondary context. Use them for current Big 3, reminders, bottlenecks, and recent momentum.

## Area Handling

Project files usually declare an area via frontmatter such as:

```yaml
Area: "[[My Building]]"
```

Use the referenced areas to understand which parts of life are being served. If a dedicated area note exists, read it. If not, use `My Areas.md` plus the project file itself.

## Built-In Rule Precedence

This skill's own operating rules remain primary:

- hard constraints win
- approval before writes
- patch `Actions` by default
- one major task per event
- subtasks belong in the description
- use the Eisenhower matrix

Vault notes should refine planning judgment, not override these defaults unless the user says so.
