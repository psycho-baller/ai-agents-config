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
PRINCIPLE_MARKER_RE = re.compile(r"<!-- principle-id: ([^>]+) -->")


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def now_utc() -> str:
    value = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    return value.replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "principle"


def canonical_value(value: Any) -> str:
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


def score_value(value: Any, schema: dict[str, Any]) -> int:
    minimum = int(schema["score_scale"]["min"])
    maximum = int(schema["score_scale"]["max"])
    try:
        score = int(value)
    except (TypeError, ValueError):
        return minimum
    return max(minimum, min(maximum, score))


def score_label(total: int) -> str:
    if total >= 21:
        return "adopted-ready"
    if total >= 16:
        return "strong candidate"
    if total >= 10:
        return "needs more evidence or sharper behavior"
    return "rewrite or discard"


def normalize_principle(raw: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    principle: dict[str, Any] = {}
    principle["title"] = coerce_string(raw.get("title"))
    principle["id"] = coerce_string(raw.get("id")) or slugify(principle["title"])
    principle["status"] = canonical_value(raw.get("status") or "candidate")
    principle["domain"] = canonical_value(raw.get("domain") or "personal_growth")
    principle["confidence"] = canonical_value(raw.get("confidence") or "medium")

    for field in schema["required_principle_fields"]:
        if field in {"title", "status", "domain", "confidence"}:
            continue
        principle[field] = coerce_string(raw.get(field))

    for field in schema["required_list_fields"]:
        principle[field] = coerce_list(raw.get(field))

    raw_score = raw.get("score", {})
    if not isinstance(raw_score, dict):
        raw_score = {}
    principle["score"] = {
        field: score_value(raw_score.get(field), schema)
        for field in schema["score_fields"]
    }
    principle["score_total"] = sum(principle["score"].values())
    principle["score_label"] = score_label(principle["score_total"])

    return principle


def normalize_payload(raw: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    principles = raw.get("principles", [])
    if not isinstance(principles, list):
        raise ValueError("principles must be a list")

    return {
        "report_title": coerce_string(raw.get("report_title")) or "Principles Extraction",
        "generated_at": coerce_string(raw.get("generated_at")) or now_utc(),
        "sources": coerce_list(raw.get("sources")),
        "principles": [
            normalize_principle(item, schema)
            for item in principles
            if isinstance(item, dict)
        ],
    }


def validate_principle(principle: dict[str, Any], schema: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"principles[{index}]"

    for field in schema["required_principle_fields"]:
        value = principle.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.{field} is required")

    for field in schema["required_list_fields"]:
        value = principle.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{prefix}.{field} needs at least one item")

    if principle.get("status") not in schema["allowed_statuses"]:
        errors.append(f"{prefix}.status is not allowed: {principle.get('status')}")

    if principle.get("domain") not in schema["allowed_domains"]:
        errors.append(f"{prefix}.domain is not allowed: {principle.get('domain')}")

    if principle.get("confidence") not in schema["allowed_confidence"]:
        errors.append(f"{prefix}.confidence is not allowed: {principle.get('confidence')}")

    score = principle.get("score")
    if not isinstance(score, dict):
        errors.append(f"{prefix}.score must be an object")
        return errors

    for field in schema["score_fields"]:
        value = score.get(field)
        if not isinstance(value, int):
            errors.append(f"{prefix}.score.{field} must be an integer")
            continue
        if not schema["score_scale"]["min"] <= value <= schema["score_scale"]["max"]:
            errors.append(f"{prefix}.score.{field} must be between 1 and 5")

    return errors


def validate_payload(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not payload["principles"]:
        errors.append("payload needs at least one principle")

    for index, principle in enumerate(payload["principles"]):
        errors.extend(validate_principle(principle, schema, index))

    return errors


def bullet_list(items: list[str], empty: str = "none") -> list[str]:
    if not items:
        return [f"- {empty}"]
    return [f"- {item}" for item in items]


def render_principle(principle: dict[str, Any]) -> list[str]:
    lines = [
        f"### {principle['title']}",
        f"<!-- principle-id: {principle['id']} -->",
        f"- status: `{principle['status']}`",
        f"- domain: `{principle['domain']}`",
        f"- confidence: `{principle['confidence']}`",
        f"- score: `{principle['score_total']}/25` - {principle['score_label']}",
        "",
        "**Source notes**",
        *bullet_list(principle["source_notes"]),
        "",
        "**Principle**",
        "",
        principle["principle"],
        "",
        "**Reasoning**",
        "",
        principle["reasoning"],
        "",
        "**Evidence**",
        *bullet_list(principle["evidence"]),
        "",
        "**Atomic Habits Design**",
        f"- identity: {principle['identity']}",
        f"- cue: {principle['cue']}",
        f"- craving: {principle['craving']}",
        f"- response: {principle['response']}",
        f"- reward: {principle['reward']}",
        f"- implementation_intention: {principle['implementation_intention']}",
        f"- habit_stack: {principle['habit_stack']}",
        f"- environment_design: {principle['environment_design']}",
        f"- friction_to_reduce: {principle['friction_to_reduce']}",
        f"- friction_to_add: {principle['friction_to_add']}",
        "",
        "**Failure Mode**",
        "",
        principle["failure_mode"],
        "",
        "**Experiment**",
        "",
        principle["experiment"],
        "",
        f"**Review Cadence:** {principle['review_cadence']}",
        "",
        "**Score Breakdown**",
    ]
    for field, value in principle["score"].items():
        lines.append(f"- {field}: {value}/5")
    lines.append("")
    return lines


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# {payload['report_title']}",
        "",
        f"generated_at: {payload['generated_at']}",
        "",
        "## Sources",
        *bullet_list(payload["sources"]),
        "",
        "## Principles",
        "",
    ]

    for principle in payload["principles"]:
        lines.extend(render_principle(principle))

    return "\n".join(lines).rstrip() + "\n"


def load_payload_arg(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload_json:
        return json.loads(args.payload_json)
    if args.payload_file:
        return json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    raise ValueError("provide --payload-json or --payload-file")


def command_schema(_: argparse.Namespace) -> int:
    print(json.dumps(load_schema(), indent=2))
    return 0


def command_render(args: argparse.Namespace) -> int:
    schema = load_schema()
    payload = normalize_payload(load_payload_arg(args), schema)
    errors = validate_payload(payload, schema)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    report = render_report(payload)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(f"wrote principles report: {output}")
    else:
        print(report)
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
        print("valid principles payload")
    return 1 if errors else 0


def command_validate_report(args: argparse.Namespace) -> int:
    path = Path(args.report)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    markers = PRINCIPLE_MARKER_RE.findall(text)

    if "# " not in text:
        errors.append("report is missing a title")
    if "## Sources" not in text:
        errors.append("report is missing ## Sources")
    if "## Principles" not in text:
        errors.append("report is missing ## Principles")
    if not markers:
        errors.append("report has no principle-id markers")

    required_sections = [
        "**Principle**",
        "**Reasoning**",
        "**Evidence**",
        "**Atomic Habits Design**",
        "**Failure Mode**",
        "**Experiment**",
        "**Score Breakdown**",
    ]
    for section in required_sections:
        if section not in text:
            errors.append(f"report is missing {section}")

    if args.json:
        print(json.dumps({"valid": not errors, "principles": len(markers), "errors": errors}, indent=2))
    elif errors:
        for error in errors:
            print(f"{path}: {error}", file=sys.stderr)
    else:
        print(f"valid principles report: {path} ({len(markers)} principles)")

    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="render and validate generated principles")
    subparsers = parser.add_subparsers(dest="command", required=True)

    schema_parser = subparsers.add_parser("schema", help="print principles schema")
    schema_parser.set_defaults(func=command_schema)

    render_parser = subparsers.add_parser("render", help="render a principles markdown report")
    render_parser.add_argument("--payload-json")
    render_parser.add_argument("--payload-file")
    render_parser.add_argument("--output")
    render_parser.set_defaults(func=command_render)

    validate_payload_parser = subparsers.add_parser("validate-payload", help="validate a principles payload")
    validate_payload_parser.add_argument("--payload-json")
    validate_payload_parser.add_argument("--payload-file")
    validate_payload_parser.add_argument("--json", action="store_true")
    validate_payload_parser.set_defaults(func=command_validate_payload)

    validate_report_parser = subparsers.add_parser("validate-report", help="validate a rendered report")
    validate_report_parser.add_argument("report")
    validate_report_parser.add_argument("--json", action="store_true")
    validate_report_parser.set_defaults(func=command_validate_report)

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
