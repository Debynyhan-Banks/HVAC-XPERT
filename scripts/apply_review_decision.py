#!/usr/bin/env python3

import json
import sys
from pathlib import Path


PENDING_STATUS = "PENDING_TECHNICAL_REVIEW"
APPROVED_STATUS = "TECHNICALLY_APPROVED_LEGAL_HOLD"
TOPOLOGY_REVIEW_ACTIONS = """## Review actions

1. Compare every connector, pin, node, and connection to the cited private page 50.
2. Confirm the black/red supply mapping and red/yellow/blue compressor mapping.
3. Confirm positional fan-terminal mapping is acceptable while numeric identifiers remain unknown.
4. Reject or revise any record that overstates the diagram.
5. Keep `publication_authorized` false because the source-rights hold remains."""


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record_paths(package_root):
    model_path = package_root / "equipment-model.json"
    if model_path.is_file():
        yield model_path
    for directory in (
        "components",
        "faults",
        "operating-states",
        "measurements",
        "connectors",
        "pins",
        "nodes",
        "connections",
    ):
        yield from sorted((package_root / directory).glob("*.json"))


def apply_validation(assertion, reviewer_id, reviewed_at, notes):
    validation = assertion["validation"]
    if validation.get("outcome") != "PENDING" or validation.get("level") != "LEVEL_1_AI_EXTRACTED":
        raise ValueError(f"Assertion {assertion.get('fact_id')} is not pending AI extraction")
    validation.update(
        {
            "level": "LEVEL_4_TECHNICIAN_REVIEWED",
            "outcome": "ACCEPTED",
            "reviewed_by": reviewer_id,
            "reviewed_at": reviewed_at,
            "notes": notes,
        }
    )


def update_summary(package_root, reviewer_id, reviewed_at, assertion_count):
    summary_path = package_root / "REVIEW_SUMMARY.md"
    summary = summary_path.read_text(encoding="utf-8")
    summary = summary.replace("- Status: `PENDING_TECHNICAL_REVIEW`", "- Status: `TECHNICALLY_APPROVED_LEGAL_HOLD`")
    summary = summary.replace("- Publication allowed: No", f"- Technical review: Accepted by `{reviewer_id}` at `{reviewed_at}`\n- Publication allowed: No - legal and source-rights hold remains")
    summary = summary.replace(
        "Your approval of the base package and simulator code does not approve these new assertions. Review each item against the cited private PDF pages before creating `review-decision.json`.",
        f"All extension assertions were accepted by `{reviewer_id}` at `{reviewed_at}` and advanced to `LEVEL_4_TECHNICIAN_REVIEWED`. The extension remains private under the legal and source-rights hold.",
    )
    summary = summary.replace(
        "## Review actions\n\n1. Compare each record to its cited PDF page.\n2. Mark each assertion `ACCEPTED`, `REVISED`, `REJECTED`, or `CONFLICTED`.\n3. Record your reviewer ID, review timestamp, and notes for every decision.\n4. Do not promote records with unresolved applicability or revision questions.",
        f"## Review decision\n\nAll assertions were accepted by `{reviewer_id}` at `{reviewed_at}` and advanced to `LEVEL_4_TECHNICIAN_REVIEWED`. The package remains private because source-rights and publication authorization are unresolved.",
    )
    summary = summary.replace(
        "The three wiring pages appear to contain the same applicable 3.5-5.0 ton outdoor AC drawing. Duplicate status remains pending reviewer confirmation.",
        "The technical reviewer accepted the three wiring pages as equivalent applicable source renderings of the 3.5-5.0 ton outdoor AC drawing.",
    )
    summary = summary.replace(
        "## Review actions\n\n1. Compare every record to its cited PDF page.\n2. Confirm the cooling phase/component mapping applies to `ASXS6S4810AA` revision `AA`.\n3. Confirm measurement points, values, units, procedures, and safety categories.\n4. Mark the complete package accepted only if every assertion is correct; otherwise record revisions or rejections before approval.\n5. Keep `publication_authorized` false because the legal and source-rights hold remains.",
        f"## Review decision\n\nAll assertions were accepted by `{reviewer_id}` at `{reviewed_at}`. Publication remains unauthorized.",
    )
    summary = summary.replace(
        TOPOLOGY_REVIEW_ACTIONS,
        f"## Review decision\n\nAll {assertion_count} topology assertions were accepted by `{reviewer_id}` at `{reviewed_at}` and advanced to `LEVEL_4_TECHNICIAN_REVIEWED`. Positional fan-terminal identifiers and unknown wire colors remain explicitly bounded. Publication remains unauthorized under the legal and source-rights hold.",
    )
    summary_path.write_text(summary, encoding="utf-8")


def apply(package_root, decision_path):
    manifest_path = package_root / "package-manifest.json"
    manifest = load_json(manifest_path)
    decision = load_json(decision_path)

    if manifest.get("status") != PENDING_STATUS:
        raise ValueError(f"Package status must be {PENDING_STATUS}")
    if decision.get("package_id") != manifest.get("package_id"):
        raise ValueError("Decision package ID does not match manifest")
    if decision.get("reviewer_id") != manifest.get("assigned_reviewer"):
        raise ValueError("Decision reviewer does not match assigned reviewer")
    if decision.get("outcome") != "ACCEPTED":
        raise ValueError("This command applies only a complete ACCEPTED decision")
    if decision.get("scope") != "ALL_ASSERTIONS":
        raise ValueError("Complete approval requires ALL_ASSERTIONS scope")
    if decision.get("publication_authorized") is not False:
        raise ValueError("Technical approval cannot authorize publication")
    if not isinstance(decision.get("reviewed_at"), str) or not decision["reviewed_at"]:
        raise ValueError("Complete approval requires a review timestamp")
    if not isinstance(decision.get("reviewer_statement"), str) or not decision["reviewer_statement"]:
        raise ValueError("Complete approval requires a reviewer statement")

    reviewer_id = decision["reviewer_id"]
    reviewed_at = decision["reviewed_at"]
    notes = decision["reviewer_statement"]
    assertion_count = 0

    for path in record_paths(package_root):
        record = load_json(path)
        for assertion in record["provenance"]:
            apply_validation(assertion, reviewer_id, reviewed_at, notes)
            assertion_count += 1
        write_json(path, record)

    for path in sorted((package_root / "wiring").glob("*.json")):
        assertion = load_json(path)
        apply_validation(assertion, reviewer_id, reviewed_at, notes)
        assertion["value"]["duplicate_review_status"] = "ACCEPTED_AS_EQUIVALENT_APPLICABLE_DRAWING"
        write_json(path, assertion)
        assertion_count += 1

    manifest.update(
        {
            "status": APPROVED_STATUS,
            "publication_allowed": False,
            "technical_review": {
                "outcome": "ACCEPTED",
                "scope": "ALL_ASSERTIONS",
                "reviewer_id": reviewer_id,
                "reviewed_at": reviewed_at,
                "assertion_count": assertion_count,
                "decision_file": decision_path.name,
                "legal_hold": True,
            },
        }
    )
    write_json(manifest_path, manifest)
    update_summary(package_root, reviewer_id, reviewed_at, assertion_count)
    print(f"Applied technical approval to {assertion_count} assertions in {manifest['package_id']}; publication remains blocked.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/apply_review_decision.py <package-directory> <decision.json>", file=sys.stderr)
        raise SystemExit(2)
    try:
        apply(Path(sys.argv[1]), Path(sys.argv[2]))
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
