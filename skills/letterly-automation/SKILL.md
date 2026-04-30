---
name: letterly-automation
version: 1.1.0
description: Comprehensive automation for Letterly transcriptions. This skill exports the latest CSV from Letterly, processes "magic" notes into Obsidian markdown, requires generated frontmatter metadata, semantically links metadata-ready notes using a vector database, and moves them to the final Transcriptions directory. Use when the user asks to "process new Letterly transcriptions", "sync Letterly magic notes", or "import magic notes from Letterly".
---

# Letterly Automation

This skill provides a complete workflow for importing and processing your voice transcriptions from Letterly into your Obsidian vault.

## Workflow Summary

This master skill orchestrates the following independent sub-skills:

1. **`letterly-export`:** Uses a Playwright browser agent to log in and download the latest CSV export from `web.letterly.app`.
2. **`letterly-process`:** Extracts only notes marked as "magic" in the CSV, creates markdown files with custom frontmatter, and places them in `unprocessed/`.
3. **`generate-metadata`:** Agent-driven step that reads each new transcription, generates structured top-level frontmatter metadata, and uses the Python validator/merger to enforce the schema.
4. **`obsidian-semantic-linker`:** Analyzes metadata-ready notes and links them to existing vault content using the local semantic embedding database (`.smart-env/`).
5. **Deliver:** Moves notes with valid generated metadata to `My Outputs/Transcriptions/` and leaves notes with missing or invalid metadata in `unprocessed/`.

## Metadata Gate

Delivery is based on valid generated metadata, not on the presence of `## Related Notes`.

The automation script can validate metadata, but it cannot generate semantic metadata by itself because no AI API is called from Python. When running this as an agent workflow, run the `generate-metadata` skill after `letterly-process` creates markdown files and before semantic linking/delivery.

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

For the agent-driven metadata workflow, use the two-phase mode:

```bash
# 1. Export/process Letterly notes into unprocessed/
.venv/bin/python scripts/workflow.py --mode prepare

# 2. Run generate-metadata on the listed files

# 3. Validate/link/deliver metadata-ready notes
.venv/bin/python scripts/workflow.py --mode finish
```

`--mode full` is still available, but it can only deliver files that already have valid generated metadata.

## Troubleshooting

- **Login Timeout:** If the script times out waiting for login, ensure you have the browser window visible and log in within the 120-second window.
- **Database Missing:** Ensure you are running this from your Obsidian vault root where `.smart-env/` exists.
- **No Magic Notes:** The script only imports notes that have been processed with the "Magic" rewrite type in Letterly.
- **Metadata Missing:** Notes without valid generated metadata stay in `unprocessed/` instead of moving to `My Outputs/Transcriptions/`.
