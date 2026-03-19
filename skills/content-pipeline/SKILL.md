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
process that one file.

**specific files:**
> "run content pipeline on file-a.md and file-b.md"
process each in sequence.

**directory:**
> "run content pipeline on all files in /path/to/folder"
process every `.md` file in that folder.

**unprocessed (default):**
> "process unprocessed transcripts" / "run pipeline on new transcripts"
scan the Transcriptions folder, find files where `notes-processing/{filename}/content.md` does not exist, process those.

## steps per file

run in order for each transcript:

1. **content-research** — extract claims, do 10+ web searches, write `research.md`
2. **content-hooks** — research trends, generate hooks + full tweets + ICE scores, write `hooks.md`
3. **content-writer** — write master long-form piece using transcript + research + top hook, write `content.md`

print after each step: `[{step}] done — {filename}`

## completion report

after all files are processed, print a summary table:

| file | overall ICE | linkedin ICE | twitter ICE | ig/tiktok ICE | youtube ICE |
|------|-------------|--------------|-------------|----------------|-------------|

if a file was skipped (already processed), note it in the table with "already done".

## notes

- if a step's output file already exists, skip that step and continue from the next one
- create output folders as needed
- if the user specifies a file that doesn't exist, say so and stop
