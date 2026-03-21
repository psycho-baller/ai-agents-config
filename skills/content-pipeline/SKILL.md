---
name: content-pipeline
description: Full content pipeline orchestrator - runs content-research → content-hooks → content-writer for one transcript, a list of files, or all unprocessed transcripts. Use when asked to "run the content pipeline", "process my transcripts", or "turn my notes into content".
---

# content-pipeline

orchestrates the full 3-step content pipeline. accepts a single file, a list, a directory, or auto-detects unprocessed transcripts.

## transcript source

`/Users/rami/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/My Outputs/Transcriptions/`

## output root

`/Users/rami/Documents/life-os/notes-processing/`

each transcript gets its own folder:
```
notes-processing/{filename}/
  research.md   ← step 1
  hooks.md      ← step 2
  content.md    ← step 3
```

## invocation modes

**single file:**
> "run content pipeline on my-note.md"

**specific files:**
> "run content pipeline on file-a.md and file-b.md"

**directory:**
> "run content pipeline on all files in /path/to/folder"

**unprocessed (default):**
> "process unprocessed transcripts" / "run pipeline on new transcripts"
scan the Transcriptions folder, find files where `notes-processing/{filename}/content.md` does not exist, process those.

## preprocessing (apply before every step)

all transcripts contain Obsidian syntax that must be cleaned before processing:
- strip YAML frontmatter (everything between `---` at the top)
- convert wiki-links: `[[Note|display]]` → `display`, `[[Note]]` → `Note`
- remove `## Related Notes` section and everything after it
- work with clean plain text from this point forward

## content length tiers

assess each transcript after cleaning and apply the appropriate depth:

| tier | word count | research depth | hooks per medium |
|------|-----------|----------------|-----------------|
| short | < 150 words | 3-5 sources, 1-2 claims | 3 per medium |
| medium | 150-500 words | 5-8 sources, 3-5 claims | 4 per medium |
| long | 500+ words | 10+ sources, all claims | 5 per medium |

## steps per file

run in order:

1. **content-research** — clean transcript, extract claims by tier, do web research, write `research.md`
2. **content-hooks** — clean transcript, identify dominant themes, research trends, generate hooks + full tweets + ICE scores, write `hooks.md`
3. **content-writer** — clean transcript, pick top ICE hook, write master long-form piece infused with research, write `content.md`

print after each step: `[{step}] done — {filename}`

## completion report

after all files are processed, output a summary table:

| file | tier | overall ICE | linkedin | twitter | ig/tiktok | youtube |
|------|------|-------------|----------|---------|-----------|---------|

skipped files (already processed): list with "already done".

## notes

- if a step's output already exists, skip it and continue from the next
- create output folders as needed
- if a specified file doesn't exist, say so and stop
- for scattered multi-topic transcripts, identify the 1-2 dominant threads and focus the pipeline there
