import os
import csv
import json
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
        if os.path.exists(os.path.join(c, ".smart-env")):
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

def row_value(row, *names):
    lookup = {str(key).strip().lower(): value for key, value in row.items() if key}
    for name in names:
        value = lookup.get(name.lower())
        if value is not None:
            return value
    return ""

def note_id(row):
    return row_value(row, 'id', 'note_id', 'noteid', 'note id', 'uuid', 'note_uuid', 'note uuid').strip()

def normalized_title(row):
    return row_value(row, 'title').strip().casefold()

def is_magic_rewrite(row):
    rewrite_type = (row_value(row, 'rewrite_type') or "").lower()
    return 'magic' in rewrite_type

def is_original_note(row):
    row_type = (row_value(row, 'type') or "").strip().lower()
    rewrite_type = (row_value(row, 'rewrite_type') or "").strip().lower()
    if row_type == "note" and not rewrite_type:
        return True
    return not row_type and not rewrite_type

def normalize_letterly_tag(value):
    tag = str(value).strip()
    if not tag:
        return ""
    return tag.removeprefix("#").strip()

def parse_letterly_tags(raw_tags):
    raw = str(raw_tags or "").strip()
    if not raw:
        return []

    candidates = []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None

        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    candidates.append(item.get("name") or item.get("title") or item.get("tag") or "")
                else:
                    candidates.append(item)

    if not candidates:
        for separator in [",", ";", "|", "\n"]:
            if separator in raw:
                candidates = raw.split(separator)
                break

    if not candidates:
        candidates = [part for part in raw.split("#") if part.strip()] if raw.count("#") > 1 else [raw]

    tags = []
    seen = set()
    for candidate in candidates:
        tag = normalize_letterly_tag(candidate)
        if tag and tag not in seen:
            tags.append(tag)
            seen.add(tag)
    return tags

def yaml_scalar(value):
    return json.dumps(str(value), ensure_ascii=False)

def yaml_list(field, values):
    if not values:
        return f"{field}: []"

    lines = [f"{field}:"]
    for value in values:
        lines.append(f"  - {yaml_scalar(value)}")
    return "\n".join(lines)

def build_original_note_indexes(rows):
    originals_by_id = {}
    originals_by_title = {}

    for row in rows:
        if not is_original_note(row):
            continue

        row_id = note_id(row)
        if row_id and row_id not in originals_by_id:
            originals_by_id[row_id] = row

        title = normalized_title(row)
        if title and title not in originals_by_title:
            originals_by_title[title] = row

    return originals_by_id, originals_by_title

def find_original_note(row, originals_by_id, originals_by_title):
    row_id = note_id(row)
    if row_id and row_id in originals_by_id:
        return originals_by_id[row_id]

    title = normalized_title(row)
    if title and title in originals_by_title:
        return originals_by_title[title]

    return None

def process_letterly_csv(vault_root):
    # paths
    unprocessed_dir = os.path.join(vault_root, "unprocessed")
    transcriptions_dir = os.path.join(vault_root, "My Outputs/Transcriptions")

    # ensure directories exist
    os.makedirs(unprocessed_dir, exist_ok=True)
    os.makedirs(transcriptions_dir, exist_ok=True)

    # find the most recent CSV
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
        rows = list(csv.DictReader(f))

    originals_by_id, originals_by_title = build_original_note_indexes(rows)

    for row in rows:
        if not is_magic_rewrite(row):
            continue

        title = row_value(row, 'title').strip()
        content = row_value(row, 'text').strip()
        letterly_tags = parse_letterly_tags(row_value(row, 'tags', 'tag', 'letterly_tags'))
        original_note = find_original_note(row, originals_by_id, originals_by_title)
        created_at_raw = row_value(original_note or {}, 'created_at') or row_value(row, 'created_at')
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
{yaml_list("letterly_tags", letterly_tags)}
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
