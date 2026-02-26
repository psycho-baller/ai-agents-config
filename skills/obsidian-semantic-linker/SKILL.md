---
name: obsidian-semantic-linker
description: Semantically links notes in your Obsidian vault using a local vector database (.nexus/cache.db). It analyzes the content of notes, finds related ideas, and appends a "## Related Notes" section with wiki-links to similar notes. Use when asked to "link my notes", "find related notes", or "process semantic connections".
---

# Obsidian Semantic Linker

This skill analyzes your notes and creates automated cross-links based on semantic similarity.

## Features
- **Smart Linking:** Uses local embeddings to find notes with similar meaning, even if they use different keywords.
- **Auto-Wait:** If new files are being processed, it can poll the database until they are indexed by Obsidian.
- **Non-Destructive:** Only appends links if a "Related Notes" section doesn't already exist.

## Usage
Trigger it by asking:
"Link my new notes in the unprocessed folder" or "Process semantic links for my vault".

### Parameters
- **target_dir:** The directory to scan for files to link (defaults to `unprocessed/`).
