---
name: update-patterns
version: 1.0.0
description: Update living Obsidian pattern markdown files from metadata-enriched transcriptions and notes. Use this skill whenever the user asks to populate pattern files, update recurring patterns, synthesize communication flaws, relationship patterns, identity beliefs, recurring fears, decision principles, open problems, experiments, people mentioned, or projects mentioned from generated frontmatter metadata. This skill is agent-driven: the agent decides how entries merge and the bundled Python script performs deterministic markdown upserts.
---

# Update Patterns

Use this skill to maintain living pattern files from notes that already have `generate-metadata` frontmatter.

The goal is not to summarize each note again. The goal is to accumulate cross-note intelligence so Rami can see repeated problems, beliefs, fears, principles, people, and projects over time.

This skill updates pattern files. It does not generate per-note metadata and it does not produce Atomic Habits principle reports. Use `generate-metadata` before this skill and `generate-principles` when the user asks for principles to live by.

The agent owns judgment. The script owns structure.

- The agent reads metadata and decides whether a value belongs in an existing pattern or a new entry.
- The script creates or updates markdown files using stable managed blocks.
- The script does not call an AI API and cannot infer patterns by itself.

## Pattern Files

Default pattern files:

- `Communication Flaws.md` from `communication_flaws`
- `Relationship Patterns.md` from `relationship_patterns`
- `Identity Beliefs.md` from `identity_beliefs`
- `Recurring Fears.md` from `recurring_fears`
- `Decision Principles.md` from `decision_principles`
- `Open Problems.md` from `open_problems`
- `Experiments To Run.md` from `experiments_to_run`
- `People Mentioned.md` from `people_mentioned`
- `Projects Mentioned.md` from `projects_mentioned`

The default output directory is:

```bash
../Obsidian/My Outputs/Patterns/
```

The directory is configurable. If the user asks for a different path, use that.

The list is expandable through `pattern_schema.json`.

## Input Requirements

Use markdown files with generated metadata frontmatter.

Before updating patterns, validate the notes when possible:

```bash
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/generate-metadata/scripts/generate_metadata.py validate path/to/note.md
```

If a note does not validate, skip it and report it. Do not block the whole batch.

## How To Update Patterns

For each input note:

1. Read the generated metadata fields.
2. Read the note body when the metadata is too compressed to understand the evidence.
3. Create a wiki-link that lets Rami identify the exact source note.
4. Read existing pattern files before deciding whether to merge or create entries.
5. Merge only when the same pattern is truly the same recurring thing.
6. Keep separate entries when the difference matters.
7. Use natural language phrases, not snake_case values.
8. Be blunt and action-oriented.

Do not create fake patterns from empty metadata fields.

Do not blindly create one pattern entry per metadata value. The agent should cluster related metadata values into the smallest useful set of recurring patterns while preserving meaningful distinctions.

The skill is doing second-order synthesis:

- first-order: a note says `fear of missing the one`
- second-order: several notes reveal `scarcity thinking around rare romantic opportunities`

Prefer the second-order pattern when multiple notes point to the same underlying loop.

## Entry Standard

Each pattern entry should include:

- `title`: readable phrase, not a tag slug
- `status`: `active`, `possible`, `resolved`, or `archived`
- `source_notes`: wiki-links to notes that support the pattern
- `evidence`: short note-backed evidence lines
- `summary`: what the pattern is
- `why_it_matters`: why Rami should care
- `action`: what Rami should do when this pattern appears
- `related_patterns`: optional wiki-links to other pattern entries or concept notes

For people and projects, the `action` can describe the practical reason to track them.

## Merge Rules

The script uses managed blocks with stable IDs:

```markdown
### getting too far ahead in your head
<!-- pattern-id: communication_flaws/getting-too-far-ahead-in-your-head -->
```

If a block with the same `pattern-id` already exists, the script replaces that managed block with the new merged version.

If no matching block exists, the script appends a new block.

Anything outside managed pattern blocks should be preserved.

Merge when two entries describe the same loop in different words:

- `turning uncertainty into fantasy`
- `projecting a future before enough facts exist`

Keep separate when the trigger, consequence, or action is different:

- `approval seeking in social situations`
- `overexplaining when trying to sound competent`

## Execution Protocol

1. Resolve the target markdown file or files.
2. Validate generated metadata where possible.
3. Read target notes and existing pattern files.
4. Build an update payload with merged entries.
5. Write the payload to `/tmp/update-patterns-<short-name>.json`.
6. Run the updater script.
7. Run validation on the updated pattern directory.
8. Report updated files, skipped invalid notes, and any entries created with `possible` status.

Apply updates:

```bash
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/update-patterns/scripts/update_patterns.py apply --payload-file /tmp/update-patterns.json --output-dir ../Obsidian/My Outputs/Patterns
```

Validate a pattern directory:

```bash
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/update-patterns/scripts/update_patterns.py validate --output-dir ../Obsidian/My Outputs/Patterns
```

Inspect the schema:

```bash
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/update-patterns/scripts/update_patterns.py schema
```

## Payload Format

Use this JSON shape:

```json
{
  "updates": [
    {
      "field": "communication_flaws",
      "title": "getting too far ahead in your head",
      "status": "active",
      "source_notes": [
        "[[Crush on Lebanese Girl and Unhealthy Expectations]]"
      ],
      "evidence": [
        "[[Crush on Lebanese Girl and Unhealthy Expectations]]: Rami turns uncertainty into fantasy before enough real-world evidence exists."
      ],
      "summary": "Rami can mentally sprint ahead of reality and start reacting to imagined futures instead of present facts.",
      "why_it_matters": "This burns attention, creates emotional volatility, and makes communication less grounded.",
      "action": "When you notice yourself building a future in your head, write the facts you actually know before deciding what the situation means.",
      "related_patterns": [
        "[[Recurring Fears#fear of missing the one]]"
      ]
    }
  ]
}
```

`field` should match a key in `pattern_schema.json`. You can also pass `pattern_file` directly, but `field` is preferred because it keeps the schema as the source of truth.

## Pattern Writing Rules

Use direct language.

Good:

- `approval seeking when the stakes feel social`
- `turning uncertainty into fantasy`
- `fear that a rare opportunity will disappear`
- `building products around emotional resonance`

Bad:

- `approval_seeking`
- `turning_uncertainty_into_fantasy`
- `relationship stuff`
- `interesting pattern`

If the wording would look stupid as an Obsidian heading, rewrite it.

## Source Link Rules

Use wiki-links that make the source note easy to recognize later. Prefer the note title without the `.md` extension:

- `[[Crush on Lebanese Girl and Unhealthy Expectations]]`
- `[[Sense of control determines communication performance]]`

If a metadata value already contains a useful wiki-link, preserve it. If a concept clearly deserves a note but does not exist yet, it is acceptable to create the wiki-link anyway.
