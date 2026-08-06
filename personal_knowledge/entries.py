import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PERSONAL_KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge-base" / "private"
DEFAULT_PERSONAL_ENTRY_ROOT = DEFAULT_PERSONAL_KNOWLEDGE_ROOT / "personal-entries"

ENTRY_KINDS = {"EQUIPMENT", "FAULT", "MEASUREMENT", "DIAGNOSTIC_BRANCH"}
CONFIDENCE_STATUSES = {"UNVERIFIED", "MANUAL_CONFIRMED", "FIELD_CONFIRMED", "CONFLICTED"}
CONTEXT_TYPES = {"MANUAL", "FIELD"}
SAFETY_CATEGORIES = {
    "NOT_ACTIONABLE",
    "DEENERGIZED_ONLY",
    "ENERGIZED_LOW_VOLTAGE",
    "ENERGIZED_LINE_VOLTAGE",
    "HIGH_VOLTAGE_DC",
    "REFRIGERANT_PRESSURE",
    "OTHER",
    "UNKNOWN",
}
QUALITATIVE_VALUES = {
    "CONTINUITY",
    "NO_CONTINUITY",
    "OPEN",
    "CLOSED",
    "PRESENT",
    "ABSENT",
    "OTHER",
    "UNKNOWN",
}
DISPOSITIONS = {"NEXT_TEST", "COMPLETE", "ESCALATE", "STOP"}


class PersonalEntryValidationError(ValueError):
    pass


class PersonalEntryStorageError(OSError):
    pass


def _require_object(value, location, allowed_keys, required_keys):
    if not isinstance(value, dict):
        raise PersonalEntryValidationError(f"{location} must be an object")
    unexpected = set(value) - set(allowed_keys)
    if unexpected:
        raise PersonalEntryValidationError(f"Unexpected {location} fields: {sorted(unexpected)}")
    missing = set(required_keys) - set(value)
    if missing:
        raise PersonalEntryValidationError(f"Missing {location} fields: {sorted(missing)}")
    return value


def _text(value, location, *, nullable=False, maximum=2000):
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise PersonalEntryValidationError(f"{location} must be text")
    normalized = value.strip()
    if not normalized and nullable:
        return None
    if not normalized:
        raise PersonalEntryValidationError(f"{location} is required")
    if len(normalized) > maximum:
        raise PersonalEntryValidationError(f"{location} must be {maximum} characters or fewer")
    return normalized


def _choice(value, location, choices):
    if value not in choices:
        raise PersonalEntryValidationError(f"{location} must be one of {sorted(choices)}")
    return value


def _number(value, location, *, nullable=False):
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise PersonalEntryValidationError(f"{location} must be a finite number")
    return value


def _validate_equipment(value):
    record = _require_object(
        value,
        "equipment",
        {"manufacturer", "brand", "model_number", "revision"},
        {"manufacturer", "brand", "model_number", "revision"},
    )
    return {
        "manufacturer": _text(record["manufacturer"], "equipment.manufacturer", maximum=160),
        "brand": _text(record["brand"], "equipment.brand", maximum=160),
        "model_number": _text(record["model_number"], "equipment.model_number", maximum=160),
        "revision": _text(record["revision"], "equipment.revision", nullable=True, maximum=160),
    }


def _validate_evidence(value, confidence_status):
    record = _require_object(
        value,
        "evidence",
        {"context_type", "document_id", "page", "field_context"},
        {"context_type", "document_id", "page", "field_context"},
    )
    context_type = _choice(record["context_type"], "evidence.context_type", CONTEXT_TYPES)
    document_id = _text(record["document_id"], "evidence.document_id", nullable=True, maximum=240)
    page = record["page"]
    field_context = _text(record["field_context"], "evidence.field_context", nullable=True, maximum=4000)

    if context_type == "MANUAL":
        if document_id is None:
            raise PersonalEntryValidationError("Manual evidence requires a document identifier or title")
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise PersonalEntryValidationError("Manual evidence requires a positive page number")
        if field_context is not None:
            raise PersonalEntryValidationError("Manual evidence cannot include field_context")
    else:
        if field_context is None:
            raise PersonalEntryValidationError("Field evidence requires private field context")
        if document_id is not None or page is not None:
            raise PersonalEntryValidationError("Field evidence cannot include document_id or page")

    if confidence_status == "MANUAL_CONFIRMED" and context_type != "MANUAL":
        raise PersonalEntryValidationError("MANUAL_CONFIRMED requires manual evidence")
    if confidence_status == "FIELD_CONFIRMED" and context_type != "FIELD":
        raise PersonalEntryValidationError("FIELD_CONFIRMED requires field evidence")

    return {
        "context_type": context_type,
        "document_id": document_id,
        "page": page,
        "field_context": field_context,
    }


def _validate_expected(value):
    record = _require_object(
        value,
        "details.expected_result",
        {"result_kind", "nominal", "minimum", "maximum", "unit", "qualitative_value"},
        {"result_kind", "nominal", "minimum", "maximum", "unit", "qualitative_value"},
    )
    result_kind = _choice(record["result_kind"], "details.expected_result.result_kind", {"NUMERIC", "QUALITATIVE"})
    nominal = _number(record["nominal"], "details.expected_result.nominal", nullable=True)
    minimum = _number(record["minimum"], "details.expected_result.minimum", nullable=True)
    maximum = _number(record["maximum"], "details.expected_result.maximum", nullable=True)
    unit = _text(record["unit"], "details.expected_result.unit", nullable=True, maximum=40)
    qualitative_value = record["qualitative_value"]

    if result_kind == "NUMERIC":
        if nominal is None and minimum is None and maximum is None:
            raise PersonalEntryValidationError("Numeric expected result requires a nominal, minimum, or maximum")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise PersonalEntryValidationError("Expected minimum cannot exceed maximum")
        if nominal is not None and minimum is not None and nominal < minimum:
            raise PersonalEntryValidationError("Expected nominal cannot be below minimum")
        if nominal is not None and maximum is not None and nominal > maximum:
            raise PersonalEntryValidationError("Expected nominal cannot exceed maximum")
        if unit is None:
            raise PersonalEntryValidationError("Numeric expected result requires a unit")
        if qualitative_value is not None:
            raise PersonalEntryValidationError("Numeric expected result cannot include a qualitative value")
    else:
        _choice(qualitative_value, "details.expected_result.qualitative_value", QUALITATIVE_VALUES)
        if any(value is not None for value in (nominal, minimum, maximum, unit)):
            raise PersonalEntryValidationError("Qualitative expected result cannot include numeric values or a unit")

    return {
        "result_kind": result_kind,
        "nominal": nominal,
        "minimum": minimum,
        "maximum": maximum,
        "unit": unit,
        "qualitative_value": qualitative_value,
    }


def _validate_details(entry_kind, value):
    if entry_kind == "EQUIPMENT":
        record = _require_object(value, "details", {"equipment_type", "notes"}, {"equipment_type", "notes"})
        return {
            "equipment_type": _text(record["equipment_type"], "details.equipment_type", maximum=160),
            "notes": _text(record["notes"], "details.notes", nullable=True, maximum=4000),
        }
    if entry_kind == "FAULT":
        record = _require_object(value, "details", {"fault_code", "meaning", "notes"}, {"fault_code", "meaning", "notes"})
        return {
            "fault_code": _text(record["fault_code"], "details.fault_code", maximum=80),
            "meaning": _text(record["meaning"], "details.meaning", maximum=2000),
            "notes": _text(record["notes"], "details.notes", nullable=True, maximum=4000),
        }
    if entry_kind == "MEASUREMENT":
        record = _require_object(
            value,
            "details",
            {"name", "meter_mode", "point_a", "point_b", "expected_result", "procedure"},
            {"name", "meter_mode", "point_a", "point_b", "expected_result", "procedure"},
        )
        return {
            "name": _text(record["name"], "details.name", maximum=240),
            "meter_mode": _text(record["meter_mode"], "details.meter_mode", maximum=80),
            "point_a": _text(record["point_a"], "details.point_a", maximum=500),
            "point_b": _text(record["point_b"], "details.point_b", nullable=True, maximum=500),
            "expected_result": _validate_expected(record["expected_result"]),
            "procedure": _text(record["procedure"], "details.procedure", maximum=4000),
        }

    record = _require_object(
        value,
        "details",
        {"fault_code", "condition", "disposition", "next_action"},
        {"fault_code", "condition", "disposition", "next_action"},
    )
    return {
        "fault_code": _text(record["fault_code"], "details.fault_code", nullable=True, maximum=80),
        "condition": _text(record["condition"], "details.condition", maximum=2000),
        "disposition": _choice(record["disposition"], "details.disposition", DISPOSITIONS),
        "next_action": _text(record["next_action"], "details.next_action", maximum=4000),
    }


def _guidance_status(entry_kind, confidence_status, revision, safety_category):
    if confidence_status == "UNVERIFIED":
        return "BLOCKED_UNVERIFIED"
    if confidence_status == "CONFLICTED":
        return "BLOCKED_CONFLICTED"
    if revision is None:
        return "BLOCKED_REVISION_UNKNOWN"
    if entry_kind in {"MEASUREMENT", "DIAGNOSTIC_BRANCH"} and safety_category in {"UNKNOWN", "OTHER"}:
        return "BLOCKED_SAFETY_UNKNOWN"
    if entry_kind in {"EQUIPMENT", "FAULT"}:
        return "REFERENCE_ONLY_CONFIRMED"
    return "ELIGIBLE_FOR_RULE_REVIEW"


def validate_personal_entry_request(request):
    record = _require_object(
        request,
        "request",
        {"entry_kind", "equipment", "title", "details", "evidence", "safety_category", "confidence_status"},
        {"entry_kind", "equipment", "title", "details", "evidence", "safety_category", "confidence_status"},
    )
    entry_kind = _choice(record["entry_kind"], "entry_kind", ENTRY_KINDS)
    confidence_status = _choice(record["confidence_status"], "confidence_status", CONFIDENCE_STATUSES)
    equipment = _validate_equipment(record["equipment"])
    evidence = _validate_evidence(record["evidence"], confidence_status)
    safety_category = _choice(record["safety_category"], "safety_category", SAFETY_CATEGORIES)

    if entry_kind in {"EQUIPMENT", "FAULT"} and safety_category != "NOT_ACTIONABLE":
        raise PersonalEntryValidationError(f"{entry_kind} entries must use NOT_ACTIONABLE safety")
    if entry_kind in {"MEASUREMENT", "DIAGNOSTIC_BRANCH"} and safety_category == "NOT_ACTIONABLE":
        raise PersonalEntryValidationError(f"{entry_kind} entries require an applicable safety category")
    if confidence_status in {"MANUAL_CONFIRMED", "FIELD_CONFIRMED"} and equipment["revision"] is None:
        raise PersonalEntryValidationError("Confirmed entries require exact revision applicability")
    if (
        confidence_status in {"MANUAL_CONFIRMED", "FIELD_CONFIRMED"}
        and entry_kind in {"MEASUREMENT", "DIAGNOSTIC_BRANCH"}
        and safety_category in {"UNKNOWN", "OTHER"}
    ):
        raise PersonalEntryValidationError("Confirmed actionable entries require a specific safety category")

    return {
        "entry_kind": entry_kind,
        "equipment": equipment,
        "title": _text(record["title"], "title", maximum=240),
        "details": _validate_details(entry_kind, record["details"]),
        "evidence": evidence,
        "safety_category": safety_category,
        "confidence_status": confidence_status,
    }


class PersonalEntryStore:
    def __init__(self, root=DEFAULT_PERSONAL_ENTRY_ROOT):
        self._root = Path(root)

    @property
    def root(self):
        return self._root

    def create(self, request):
        values = validate_personal_entry_request(request)
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entry_id = f"PENTRY-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:12].upper()}"
        guidance_status = _guidance_status(
            values["entry_kind"],
            values["confidence_status"],
            values["equipment"]["revision"],
            values["safety_category"],
        )
        record = {
            "schema_version": "1.0.0",
            "entry_id": entry_id,
            **values,
            "guidance_status": guidance_status,
            "deterministic_guidance_active": False,
            "created_at": created_at,
            "updated_at": created_at,
        }
        self._write(record)
        return record

    def _write(self, record):
        try:
            self._root.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(self._root, 0o700)
            destination = self._root / f"{record['entry_id']}.json"
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._root,
                prefix=".pending-",
                suffix=".json",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                os.chmod(temporary_path, 0o600)
                json.dump(record, temporary, ensure_ascii=False, indent=2, sort_keys=True)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, destination)
        except OSError as error:
            if "temporary_path" in locals():
                temporary_path.unlink(missing_ok=True)
            raise PersonalEntryStorageError(f"Could not save private personal entry: {error}") from error
