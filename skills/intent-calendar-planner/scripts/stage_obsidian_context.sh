#!/usr/bin/env bash
set -euo pipefail

VAULT_ROOT="${VAULT_ROOT:-/Users/rami/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian}"
OUTPUT_DIR=""
DAILY_NOTES=3
INCLUDE_DAILY=1

usage() {
  cat <<'EOF'
Stage the canonical Obsidian iCloud context into a readable local folder.

Usage:
  bash scripts/stage_obsidian_context.sh --output-dir /private/tmp/intent-calendar-context [--daily-notes 3] [--skip-daily-notes]

Options:
  --output-dir DIR     Required. Local directory to write staged files into.
  --daily-notes N      Number of recent daily notes to stage. Default: 3.
  --skip-daily-notes   Do not stage recent daily notes.
EOF
}

duplicate_file() {
  local source_path="$1"
  local target_dir="$2"

  mkdir -p "$target_dir"
  osascript - "$source_path" "$target_dir" <<'APPLESCRIPT' >/dev/null
on run argv
  set sourcePOSIX to item 1 of argv
  set targetDirPOSIX to item 2 of argv
  set sourceAlias to POSIX file sourcePOSIX as alias
  set targetDirAlias to POSIX file targetDirPOSIX as alias
  tell application "Finder"
    duplicate file sourceAlias to folder targetDirAlias with replacing
  end tell
end run
APPLESCRIPT
}

list_items() {
  local folder_path="$1"

  osascript - "$folder_path" <<'APPLESCRIPT'
on run argv
  set folderPOSIX to item 1 of argv
  set folderAlias to POSIX file folderPOSIX as alias
  tell application "Finder"
    set sourceFolder to folder folderAlias
    set itemNames to name of every item of sourceFolder
  end tell
  set AppleScript's text item delimiters to linefeed
  return itemNames as text
end run
APPLESCRIPT
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --daily-notes)
      DAILY_NOTES="${2:-}"
      shift 2
      ;;
    --skip-daily-notes)
      INCLUDE_DAILY=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$OUTPUT_DIR" ]]; then
  echo "--output-dir is required" >&2
  usage >&2
  exit 1
fi

if [[ ! "$DAILY_NOTES" =~ ^[0-9]+$ ]]; then
  echo "--daily-notes must be an integer" >&2
  exit 1
fi

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/My Projects" "$OUTPUT_DIR/My Areas" "$OUTPUT_DIR/My Calendar/My Daily Notes"

duplicate_file "$VAULT_ROOT/My Projects/CLAUDE.md" "$OUTPUT_DIR/My Projects"
duplicate_file "$VAULT_ROOT/My Areas/My Areas.md" "$OUTPUT_DIR/My Areas"

while IFS= read -r item_name; do
  [[ -z "$item_name" ]] && continue

  if [[ "$item_name" == "Archive" || "$item_name" == "CLAUDE.md" || "$item_name" == "My Projects.base" ]]; then
    continue
  fi

  if [[ "$item_name" == *.md ]]; then
    duplicate_file "$VAULT_ROOT/My Projects/$item_name" "$OUTPUT_DIR/My Projects"
  fi
done < <(list_items "$VAULT_ROOT/My Projects")

area_names=$(
  (
    rg '^Area:' "$OUTPUT_DIR/My Projects"/*.md --no-filename || true
  ) \
    | perl -ne '
        s/^Area:\s*"?\[\[([^]|]+)(\|[^]]+)?\]\]"?/$1/;
        s/^Area:\s*"?([^"]+)"?/$1/ unless /\[\[/;
        s/\s+$//;
        print "$_\n" if length $_;
      ' \
    | sort -u
)

if [[ -n "$area_names" ]]; then
  while IFS= read -r area_name; do
    [[ -z "$area_name" ]] && continue
    if printf '%s\n' "$(list_items "$VAULT_ROOT/My Areas")" | rg -Fxq "${area_name}.md"; then
      duplicate_file "$VAULT_ROOT/My Areas/${area_name}.md" "$OUTPUT_DIR/My Areas"
    fi
  done <<< "$area_names"
fi

if [[ "$INCLUDE_DAILY" -eq 1 && "$DAILY_NOTES" -gt 0 ]]; then
  list_items "$VAULT_ROOT/My Calendar/My Daily Notes" \
    | rg '^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' \
    | sort \
    | tail -n "$DAILY_NOTES" \
    | while IFS= read -r note_name; do
        duplicate_file "$VAULT_ROOT/My Calendar/My Daily Notes/$note_name" "$OUTPUT_DIR/My Calendar/My Daily Notes"
      done
fi

find "$OUTPUT_DIR" -name .DS_Store -delete

{
  echo "Vault root: $VAULT_ROOT"
  echo "Staged at: $OUTPUT_DIR"
  echo
  echo "Files:"
  find "$OUTPUT_DIR" -type f | sort
} > "$OUTPUT_DIR/manifest.txt"

echo "Staged Obsidian context into $OUTPUT_DIR"
