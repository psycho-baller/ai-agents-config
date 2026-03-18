---
name: letterly-process
version: 1.0.0
description: Reads the Letterly CSV export in the unprocessed folder, extracts "magic" notes, and converts them into Markdown notes with frontmatter.
---

# Letterly Process

This skill processes downloaded CSV data from Letterly into Obsidian-friendly Markdown files.

## Usage

This skill is typically orchestrated by the main `letterly-automation` skill, but can be run independently:

```bash
uv run python scripts/process.py
```
