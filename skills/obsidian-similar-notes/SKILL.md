---
name: obsidian-similar-notes
description: Finds notes semantically similar to a given file using Smart Connections embeddings. Supports both note-level and block-level (per-heading) similarity, so it can surface which specific section of a note relates to which other notes. Use when asked to "find notes similar to X", "what's related to this note", "show me similar notes", or "find connections for [file]".
---

# Obsidian Similar Notes

Queries Smart Connections embeddings (.smart-env/multi/) to find the most semantically related notes to any file in your vault.

## Features
- **Note-level mode**: compares whole-note embeddings
- **Block-level mode**: compares per-heading embeddings - identifies *which section* of the target note matches *which section* of similar notes
- **Both mode** (default): runs both and shows results side by side

## Usage

```bash
cd ai-agents-config/skills/
.venv/bin/python obsidian-similar-notes/scripts/find_similar.py "path/to/note.md"
```

### Arguments
- positional: file path (absolute, relative to cwd, or vault-relative)
- `--mode note|block|both` - similarity mode (default: both)
- `--threshold 0.45` - minimum similarity score (default: 0.45)
- `--top 10` - number of results to show (default: 10)
- `--vault /path/to/vault` - vault root (auto-detected if omitted)

### Example

```bash
.venv/bin/python obsidian-similar-notes/scripts/find_similar.py \
  "My Outputs/Transcriptions/Sense of control.md" --mode both --top 5
```
