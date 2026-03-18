---
name: letterly-export
version: 1.0.0
description: Automates the process of exporting your data from Letterly as a CSV file to your Obsidian vault's unprocessed directory. Used as the first step in the Letterly automation pipeline.
---

# Letterly Export

This skill automates the process of exporting data from [Letterly](https://web.letterly.app) and saving it to your Obsidian vault.

## Usage

This skill is typically orchestrated by the main `letterly-automation` skill, but can be run independently:

```bash
uv run python scripts/export.py
```
