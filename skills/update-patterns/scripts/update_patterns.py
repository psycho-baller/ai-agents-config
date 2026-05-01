#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_DIR / "pattern_schema.json"
TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")
PATTERN_BLOCK_RE = re.compile(
    r"^### (?P<title>.+?)\n<!-- pattern-id: (?P<id>[^>]+) -->\n(?P<body>.*?)(?=^### |\Z)",
    re.MULTILINE | re.DOTALL,
)


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def now_utc() -> str:
    value = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return value.replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pattern"


def canonical_field(value: Any) -> str:
    value = str(value or "").strip().lower()
    value = re.sub(r"[\s-]+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value


def coerce_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(value)
    return output


def find_vault(start: Path) -> Path | None:
    start = start.resolve()
    candidates = [start, *start.parents]
    for base in candidates:
        if (base / ".smart-env").exists():
            return base
        linked = base / "Obsidian"
        if linked.exists() and (linked / ".smart-env").exists():
            return linked
    return None


def default_output_dir(schema: dict[str, Any]) -> Path:
    vault = find_vault(Path.cwd())
    if vault:
        return vault / schema["default_output_subdir"]
    return Path(schema["default_output_subdir"])


def read_markdown(path: Path) -> tuple[list[str], str]:
    if not path.exists():
        return [], ""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return [], text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            frontmatter = lines[1:index]
            body = "".join(lines[index + 1 :])
            return frontmatter, body

    return [], text


def remove_managed_frontmatter(lines: list[str]) -> list[str]:
    managed = {"pattern_schema_version", "pattern_updated_at", "pattern_field"}
    output: list[str] = []
    index = 0
    while index < len(lines):
        match = TOP_LEVEL_KEY_RE.match(lines[index])
        if not match or match.group(1) not in managed:
            output.append(lines[index].rstrip("\n"))
            index += 1
            continue

        index += 1
        while index < len(lines) and not TOP_LEVEL_KEY_RE.match(lines[index]):
            index += 1
    return output


def dump_frontmatter(existing: list[str], field: str, schema: dict[str, Any]) -> str:
    cleaned = remove_managed_frontmatter(existing)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()

    managed = [
        f'pattern_schema_version: "{schema["version"]}"',
        f'pattern_updated_at: "{now_utc()}"',
        f'pattern_field: "{field}"',
    ]
    lines = cleaned + ([""] if cleaned else []) + managed
    return "---\n" + "\n".join(lines) + "\n---\n\n"


def ensure_body(body: str, file_def: dict[str, Any]) -> str:
    if not body.strip():
        return (
            f"# {file_def['title']}\n\n"
            f"{file_def['description']}\n\n"
            "## Active Patterns\n\n"
        )
    if "## Active Patterns" not in body:
        return body.rstrip() + "\n\n## Active Patterns\n\n"
    return body


def extract_existing_list(block: str, label: str) -> list[str]:
    pattern = re.compile(rf"^- {re.escape(label)}:\n(?P<items>(?:  - .+\n?)*)", re.MULTILINE)
    match = pattern.search(block)
    if not match:
        return []
    items: list[str] = []
    for line in match.group("items").splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
    return items


def existing_blocks(text: str) -> dict[str, str]:
    return {
        match.group("id"): match.group(0).rstrip()
        for match in PATTERN_BLOCK_RE.finditer(text)
    }


def normalize_entry(raw: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    field = canonical_field(raw.get("field"))
    if not field and raw.get("pattern_file"):
        wanted_file = coerce_string(raw.get("pattern_file"))
        for candidate_field, file_def in schema["pattern_files"].items():
            if file_def["file"] == wanted_file:
                field = candidate_field
                break

    title = coerce_string(raw.get("title"))
    pattern_id = coerce_string(raw.get("id")) or f"{field}/{slugify(title)}"

    return {
        "field": field,
        "id": pattern_id,
        "title": title,
        "status": canonical_field(raw.get("status") or "active"),
        "source_notes": coerce_list(raw.get("source_notes")),
        "evidence": coerce_list(raw.get("evidence")),
        "summary": coerce_string(raw.get("summary")),
        "why_it_matters": coerce_string(raw.get("why_it_matters")),
        "action": coerce_string(raw.get("action")),
        "related_patterns": coerce_list(raw.get("related_patterns")),
    }


def validate_entry(entry: dict[str, Any], schema: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"updates[{index}]"

    if entry["field"] not in schema["pattern_files"]:
        errors.append(f"{prefix}.field is not allowed: {entry['field']}")

    if entry["status"] not in schema["allowed_statuses"]:
        errors.append(f"{prefix}.status is not allowed: {entry['status']}")

    for field in ["title", "summary", "why_it_matters", "action"]:
        if not entry[field]:
            errors.append(f"{prefix}.{field} is required")

    for field in ["source_notes", "evidence"]:
        if not entry[field]:
            errors.append(f"{prefix}.{field} needs at least one item")

    return errors


def normalize_payload(raw: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    updates = raw.get("updates", [])
    if not isinstance(updates, list):
        raise ValueError("updates must be a list")
    return {
        "updates": [
            normalize_entry(item, schema)
            for item in updates
            if isinstance(item, dict)
        ]
    }


def validate_payload(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not payload["updates"]:
        errors.append("payload needs at least one update")
    for index, entry in enumerate(payload["updates"]):
        errors.extend(validate_entry(entry, schema, index))
    return errors


def merge_entry_with_existing(entry: dict[str, Any], existing: str | None) -> dict[str, Any]:
    if not existing:
        return entry

    merged = dict(entry)
    for field in ["source_notes", "evidence", "related_patterns"]:
        merged[field] = unique(extract_existing_list(existing, field) + entry[field])
    return merged


def render_list(label: str, values: list[str]) -> list[str]:
    if not values:
        return [f"- {label}: []"]
    lines = [f"- {label}:"]
    lines.extend(f"  - {value}" for value in values)
    return lines


def render_entry(entry: dict[str, Any]) -> str:
    lines = [
        f"### {entry['title']}",
        f"<!-- pattern-id: {entry['id']} -->",
        f"- status: `{entry['status']}`",
        f"- last_updated: `{now_utc()}`",
        *render_list("source_notes", entry["source_notes"]),
        *render_list("evidence", entry["evidence"]),
        f"- summary: {entry['summary']}",
        f"- why_it_matters: {entry['why_it_matters']}",
        f"- action: {entry['action']}",
        *render_list("related_patterns", entry["related_patterns"]),
    ]
    return "\n".join(lines).rstrip()


def upsert_block(text: str, block_id: str, rendered: str) -> str:
    for match in PATTERN_BLOCK_RE.finditer(text):
        if match.group("id") != block_id:
            continue
        return text[: match.start()] + rendered + "\n\n" + text[match.end() :].lstrip("\n")
    return text.rstrip() + "\n\n" + rendered + "\n"


def apply_updates(payload: dict[str, Any], output_dir: Path, schema: dict[str, Any]) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in payload["updates"]:
        grouped.setdefault(entry["field"], []).append(entry)

    updated_files: list[Path] = []
    for field, entries in grouped.items():
        file_def = schema["pattern_files"][field]
        path = output_dir / file_def["file"]
        frontmatter, body = read_markdown(path)
        body = ensure_body(body, file_def)
        blocks = existing_blocks(body)

        for entry in entries:
            merged = merge_entry_with_existing(entry, blocks.get(entry["id"]))
            body = upsert_block(body, merged["id"], render_entry(merged))
            blocks[merged["id"]] = render_entry(merged)

        text = dump_frontmatter(frontmatter, field, schema) + body.lstrip("\n")
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        updated_files.append(path)

    return updated_files


def validate_pattern_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("missing frontmatter")
    if "## Active Patterns" not in text:
        errors.append("missing ## Active Patterns")
    for match in PATTERN_BLOCK_RE.finditer(text):
        block = match.group(0)
        for section in ["source_notes", "evidence"]:
            if f"- {section}:" not in block:
                errors.append(f"{match.group('id')} missing {section}")
    return errors


def load_payload_arg(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload_json:
        return json.loads(args.payload_json)
    if args.payload_file:
        return json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    raise ValueError("provide --payload-json or --payload-file")


def command_schema(_: argparse.Namespace) -> int:
    print(json.dumps(load_schema(), indent=2))
    return 0


def command_apply(args: argparse.Namespace) -> int:
    schema = load_schema()
    payload = normalize_payload(load_payload_arg(args), schema)
    errors = validate_payload(payload, schema)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir(schema)
    updated_files = apply_updates(payload, output_dir, schema)
    for path in updated_files:
        print(f"updated pattern file: {path}")
    return 0


def command_validate_payload(args: argparse.Namespace) -> int:
    schema = load_schema()
    payload = normalize_payload(load_payload_arg(args), schema)
    errors = validate_payload(payload, schema)
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("valid update-patterns payload")
    return 1 if errors else 0


def command_validate(args: argparse.Namespace) -> int:
    schema = load_schema()
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir(schema)
    results = []
    has_errors = False

    for file_def in schema["pattern_files"].values():
        path = output_dir / file_def["file"]
        if not path.exists():
            continue
        errors = validate_pattern_file(path)
        has_errors = has_errors or bool(errors)
        results.append({"path": str(path), "valid": not errors, "errors": errors})

    if args.json:
        print(json.dumps({"files": results}, indent=2))
    else:
        for result in results:
            if result["valid"]:
                print(f"valid pattern file: {result['path']}")
                continue
            for error in result["errors"]:
                print(f"{result['path']}: {error}", file=sys.stderr)

    return 1 if has_errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="update living pattern markdown files")
    subparsers = parser.add_subparsers(dest="command", required=True)

    schema_parser = subparsers.add_parser("schema", help="print pattern schema")
    schema_parser.set_defaults(func=command_schema)

    apply_parser = subparsers.add_parser("apply", help="apply pattern updates")
    apply_parser.add_argument("--payload-json")
    apply_parser.add_argument("--payload-file")
    apply_parser.add_argument("--output-dir")
    apply_parser.set_defaults(func=command_apply)

    validate_payload_parser = subparsers.add_parser("validate-payload", help="validate a pattern update payload")
    validate_payload_parser.add_argument("--payload-json")
    validate_payload_parser.add_argument("--payload-file")
    validate_payload_parser.add_argument("--json", action="store_true")
    validate_payload_parser.set_defaults(func=command_validate_payload)

    validate_parser = subparsers.add_parser("validate", help="validate pattern files")
    validate_parser.add_argument("--output-dir")
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.set_defaults(func=command_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
