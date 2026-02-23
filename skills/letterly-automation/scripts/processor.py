import os
import csv
import re
import sys
from datetime import datetime

def get_vault_root():
    candidates = [
        os.getcwd(),
        "/Users/rami/Documents/life-os/Obsidian",
        "/Users/rami/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian"
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, ".nexus/cache.db")):
            return c
    return os.getcwd()

def sanitize_filename(name):
    """Removes characters that are illegal in file names."""
    sanitized = re.sub(r'[\/*?:"<>|]', "", name)
    return sanitized.strip()[:200]

def format_date(date_str):
    """Converts DD.MM.YYYY HH:MM:SS to YYYY-MM-DDTHH:MM:SS."""
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return date_str

def process_letterly_csv(vault_root):
    # Paths
    unprocessed_dir = os.path.join(vault_root, "unprocessed")
    transcriptions_dir = os.path.join(vault_root, "My Outputs/Transcriptions")

    # Ensure directories exist
    os.makedirs(unprocessed_dir, exist_ok=True)
    os.makedirs(transcriptions_dir, exist_ok=True)

    # Find the most recent CSV
    try:
        csv_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".csv") and f.startswith("Letterly-export")]
    except FileNotFoundError:
        print(f"Directory not found: {unprocessed_dir}")
        return

    if not csv_files:
        print("No Letterly export CSV found.")
        return

    csv_files.sort(reverse=True)
    latest_csv_filename = csv_files[0]
    latest_csv_path = os.path.join(unprocessed_dir, latest_csv_filename)
    print(f"Processing latest export: {latest_csv_path}")

    count_created = 0
    count_skipped = 0

    with open(latest_csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            note_type = (row.get('rewrite_type') or "").lower()
            if 'magic' not in note_type:
                continue

            title = row.get('title', '').strip()
            content = row.get('text', '').strip()
            created_at_raw = row.get('created_at', '')
            iso_date = format_date(created_at_raw)

            if not title:
                title = " ".join(content.split()[:5]) or "Untitled Note"

            safe_title = sanitize_filename(title)
            filename = safe_title + ".md"

            unprocessed_file_path = os.path.join(unprocessed_dir, filename)
            transcriptions_file_path = os.path.join(transcriptions_dir, filename)

            if os.path.exists(unprocessed_file_path) or os.path.exists(transcriptions_file_path):
                count_skipped += 1
                continue

            note_body = f"""---
Status: 🎙️
tags:
  - note
Links:
Created: {iso_date}
---

{content}
"""

            try:
                with open(unprocessed_file_path, 'w', encoding='utf-8') as note_file:
                    note_file.write(note_body)
                print(f"Created in unprocessed: {filename}")
                count_created += 1
            except Exception as e:
                print(f"Error creating {filename}: {e}")

    print("Processing complete.")
    print(f"New 'magic' notes created: {count_created}")
    print(f"Existing notes skipped: {count_skipped}")

    try:
        os.remove(latest_csv_path)
        print(f"Deleted source CSV: {latest_csv_filename}")
    except Exception as e:
        print(f"Error deleting CSV: {e}")

if __name__ == "__main__":
    v_root = sys.argv[1] if len(sys.argv) > 1 else get_vault_root()
    process_letterly_csv(v_root)
