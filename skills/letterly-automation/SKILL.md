---
name: letterly-automation
version: 1.0.0
description: Comprehensive automation for Letterly transcriptions. This skill exports the latest CSV from Letterly, processes "magic" notes into Obsidian markdown with custom metadata, semantically links them using a vector database, and moves them to the final Transcriptions directory. Use when the user asks to "process new letterly transcriptions", "sync letterly", or "import magic notes from letterly".
---

# Letterly Automation

This skill provides a complete workflow for importing and processing your voice transcriptions from Letterly into your Obsidian vault.

## Workflow Summary

This master skill orchestrates the following independent sub-skills:

1. **`letterly-export`:** Uses a Playwright browser agent to log in and download the latest CSV export from `web.letterly.app`.
2. **`letterly-process`:** Extracts only notes marked as "magic" in the CSV, creates markdown files with custom frontmatter, and places them in `unprocessed/`.
3. **`obsidian-semantic-linker`:** Analyzes the new notes and links them to existing vault content using the local semantic embedding database (`.smart-env/`).
4. **Deliver:** Moves the final, linked notes to `My Outputs/Transcriptions/` and cleans up the temporary CSV.

## Usage

To trigger the full workflow, simply tell the model:
"Process new Letterly transcriptions" or "Sync my Letterly magic notes".

### Manual Execution

If you need to run it manually from the terminal:

```bash
# Setup (First time only)
uv venv .venv --python 3.12
uv pip install -r scripts/requirements.txt
.venv/bin/playwright install chromium

# Run
.venv/bin/python scripts/workflow.py
```

## Troubleshooting

- **Login Timeout:** If the script times out waiting for login, ensure you have the browser window visible and log in within the 120-second window.
- **Database Missing:** Ensure you are running this from your Obsidian vault root where `.nexus/cache.db` exists.
- **No Magic Notes:** The script only imports notes that have been processed with the "Magic" rewrite type in Letterly.
