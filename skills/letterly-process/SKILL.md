---
name: letterly-process
version: 1.1.0
description: Reads the Letterly CSV export in the unprocessed folder, extracts "magic" notes, preserves Letterly tags, and converts them into Markdown notes with frontmatter.
---

# Letterly Process

This skill processes downloaded CSV data from Letterly into Obsidian-friendly Markdown files.

## Frontmatter

Each generated note keeps the normal Obsidian note tag and also preserves the source tags from Letterly:

```yaml
tags:
  - note
letterly_tags:
  - journal
```

`letterly_tags` comes directly from the Letterly CSV `tags` column. Keep it separate from the Obsidian `tags` field so Letterly labels can guide later AI metadata generation without becoming vault-wide Obsidian tags.

## Usage

This skill is typically orchestrated by the main `letterly-automation` skill, but can be run independently:

```bash
uv run python scripts/process.py
```
