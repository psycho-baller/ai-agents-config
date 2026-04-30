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
SCHEMA_PATH = SKILL_DIR / "schema.json"
TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def managed_fields(schema: dict[str, Any]) -> set[str]:
    return set(schema["string_fields"]) | set(schema["list_fields"])


def now_utc() -> str:
    value = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return value.replace("+00:00", "Z")


def canonical_note_type(value: Any) -> str:
    normalized = str(value).strip().lower()
    normalized = re.sub(r"[\s-]+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    return normalized


def read_markdown(path: Path) -> tuple[list[str], str]:
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


def remove_managed_blocks(lines: list[str], fields: set[str]) -> list[str]:
    output: list[str] = []
    index = 0
    while index < len(lines):
        match = TOP_LEVEL_KEY_RE.match(lines[index])
        if not match or match.group(1) not in fields:
            output.append(lines[index])
            index += 1
            continue

        index += 1
        while index < len(lines) and not TOP_LEVEL_KEY_RE.match(lines[index]):
            index += 1

    return output


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def dump_metadata(metadata: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    ordered_fields = schema["string_fields"] + schema["list_fields"]

    for field in ordered_fields:
        value = metadata[field]
        if field in schema["string_fields"]:
            lines.append(f"{field}: {yaml_scalar(value)}")
            continue

        if not value:
            lines.append(f"{field}: []")
            continue

        lines.append(f"{field}:")
        for item in value:
            lines.append(f"  - {yaml_scalar(item)}")

    return lines


def write_markdown(path: Path, metadata: dict[str, Any], schema: dict[str, Any]) -> None:
    frontmatter, body = read_markdown(path)
    cleaned = [line.rstrip("\n") for line in remove_managed_blocks(frontmatter, managed_fields(schema))]
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()

    generated = dump_metadata(metadata, schema)
    merged = cleaned + ([""] if cleaned else []) + generated
    body = body.lstrip("\n")
    path.write_text("---\n" + "\n".join(merged) + "\n---\n\n" + body, encoding="utf-8")


def decode_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in {"", "null", "~"}:
        return ""
    if raw == "[]":
        return []
    if raw.startswith('"') and raw.endswith('"'):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.strip('"')
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    return raw


def parse_managed_frontmatter(path: Path, schema: dict[str, Any]) -> dict[str, Any]:
    frontmatter, _ = read_markdown(path)
    fields = managed_fields(schema)
    parsed: dict[str, Any] = {}
    index = 0

    while index < len(frontmatter):
        line = frontmatter[index]
        match = TOP_LEVEL_KEY_RE.match(line)
        if not match:
            index += 1
            continue

        key = match.group(1)
        suffix = line.split(":", 1)[1].strip()
        index += 1
        block: list[str] = []
        while index < len(frontmatter) and not TOP_LEVEL_KEY_RE.match(frontmatter[index]):
            block.append(frontmatter[index])
            index += 1

        if key not in fields:
            continue

        if key in schema["list_fields"]:
            if suffix == "[]":
                parsed[key] = []
                continue
            if suffix:
                parsed[key] = decode_scalar(suffix)
                continue

            items: list[str] = []
            for item_line in block:
                item = item_line.strip()
                if not item.startswith("-"):
                    continue
                items.append(str(decode_scalar(item[1:].strip())))
            parsed[key] = items
        else:
            parsed[key] = str(decode_scalar(suffix))

    return parsed


def coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def normalize_metadata(metadata: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    for field in schema["string_fields"]:
        if field == "metadata_schema_version":
            value = metadata.get(field) or schema["version"]
        elif field == "metadata_generated_at":
            value = metadata.get(field) or now_utc()
        else:
            value = metadata.get(field, "")

        if isinstance(value, list):
            value = "; ".join(str(item).strip() for item in value if str(item).strip())
        normalized[field] = str(value).strip()

    for field in schema["list_fields"]:
        source_field = "note_type" if field == "note_types" and "note_type" in metadata else field
        values = coerce_list(metadata.get(source_field, []))
        if field == "note_types":
            values = [canonical_note_type(value) for value in values]
        normalized[field] = values

    return normalized


def validate_metadata(metadata: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    allowed_note_types = set(schema["allowed_note_types"])

    for field in schema["required_fields"]:
        value = metadata.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"missing required field: {field}")

    for field in schema["string_fields"]:
        if field in metadata and not isinstance(metadata[field], str):
            errors.append(f"{field} must be a string")

    for field in schema["list_fields"]:
        value = metadata.get(field)
        if value is None:
            errors.append(f"missing list field: {field}")
            continue
        if not isinstance(value, list):
            errors.append(f"{field} must be a list")
            continue
        if any(not isinstance(item, str) for item in value):
            errors.append(f"{field} must contain only strings")

    note_types = metadata.get("note_types", [])
    if isinstance(note_types, list):
        for note_type in note_types:
            if note_type not in allowed_note_types:
                errors.append(f"unknown note_type: {note_type}")

    return errors


def validate_file(path: Path, schema: dict[str, Any]) -> list[str]:
    if not path.exists():
        return [f"file not found: {path}"]
    metadata = parse_managed_frontmatter(path, schema)
    return validate_metadata(metadata, schema)


def load_metadata_arg(args: argparse.Namespace) -> dict[str, Any]:
    if args.metadata_json:
        payload = json.loads(args.metadata_json)
    elif args.metadata_file:
        payload = json.loads(Path(args.metadata_file).read_text(encoding="utf-8"))
    else:
        raise ValueError("provide --metadata-json or --metadata-file")

    if "metadata" in payload and isinstance(payload["metadata"], dict):
        return payload["metadata"]
    return payload


def iter_batch(payload: dict[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    if "files" in payload:
        items = []
        for entry in payload["files"]:
            items.append((Path(entry["path"]), entry["metadata"]))
        return items

    items = []
    for path, metadata in payload.items():
        if isinstance(metadata, dict):
            items.append((Path(path), metadata))
    return items


def command_schema(_: argparse.Namespace) -> int:
    print(json.dumps(load_schema(), indent=2))
    return 0


def command_apply(args: argparse.Namespace) -> int:
    schema = load_schema()
    path = Path(args.file)
    metadata = normalize_metadata(load_metadata_arg(args), schema)
    errors = validate_metadata(metadata, schema)
    if errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
        return 1

    write_markdown(path, metadata, schema)
    errors = validate_file(path, schema)
    if errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
        return 1

    print(f"updated metadata: {path}")
    return 0


def command_apply_batch(args: argparse.Namespace) -> int:
    schema = load_schema()
    payload = json.loads(Path(args.metadata_file).read_text(encoding="utf-8"))
    failures = 0

    for path, raw_metadata in iter_batch(payload):
        metadata = normalize_metadata(raw_metadata, schema)
        errors = validate_metadata(metadata, schema)
        if errors:
            failures += 1
            for error in errors:
                print(f"{path}: {error}", file=sys.stderr)
            continue

        write_markdown(path, metadata, schema)
        errors = validate_file(path, schema)
        if errors:
            failures += 1
            for error in errors:
                print(f"{path}: {error}", file=sys.stderr)
            continue

        print(f"updated metadata: {path}")

    return 1 if failures else 0


def command_validate(args: argparse.Namespace) -> int:
    schema = load_schema()
    results = []
    has_errors = False

    for raw_path in args.files:
        path = Path(raw_path)
        errors = validate_file(path, schema)
        valid = not errors
        has_errors = has_errors or bool(errors)
        results.append({"path": str(path), "valid": valid, "errors": errors})

    if args.json:
        print(json.dumps({"files": results}, indent=2))
    else:
        for result in results:
            if result["valid"]:
                print(f"valid metadata: {result['path']}")
                continue
            for error in result["errors"]:
                print(f"{result['path']}: {error}", file=sys.stderr)

    return 1 if has_errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="merge and validate generated markdown metadata")
    subparsers = parser.add_subparsers(dest="command", required=True)

    schema_parser = subparsers.add_parser("schema", help="print metadata schema")
    schema_parser.set_defaults(func=command_schema)

    apply_parser = subparsers.add_parser("apply", help="apply metadata to one file")
    apply_parser.add_argument("file")
    apply_parser.add_argument("--metadata-json")
    apply_parser.add_argument("--metadata-file")
    apply_parser.set_defaults(func=command_apply)

    batch_parser = subparsers.add_parser("apply-batch", help="apply metadata to many files")
    batch_parser.add_argument("metadata_file")
    batch_parser.set_defaults(func=command_apply_batch)

    validate_parser = subparsers.add_parser("validate", help="validate metadata in files")
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.add_argument("files", nargs="+")
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
