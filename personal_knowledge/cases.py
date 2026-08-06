import json
import os
import re
import tempfile
from pathlib import Path

from .entries import DEFAULT_PERSONAL_KNOWLEDGE_ROOT


DEFAULT_PERSONAL_CASE_ROOT = DEFAULT_PERSONAL_KNOWLEDGE_ROOT / "cases"
CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
CASE_STATES = {
    "SAFETY_ACKNOWLEDGEMENT_REQUIRED",
    "AWAITING_RESULT",
    "NEXT_TEST_AVAILABLE",
    "COMPLETE",
    "ESCALATION_REQUIRED",
    "STOPPED",
}
CASE_DISPOSITIONS = {"NEXT_TEST", "COMPLETE", "ESCALATE", "STOP", None}


class PersonalCaseValidationError(ValueError):
    pass


class PersonalCaseStorageError(OSError):
    pass


def _require(condition, message):
    if not condition:
        raise PersonalCaseValidationError(message)


class PersonalCaseStore:
    _REQUIRED_KEYS = {
        "schema_version",
        "case_id",
        "model_id",
        "revision_id",
        "knowledge_package_ids",
        "path_id",
        "mode",
        "state",
        "complaint_summary",
        "fault_codes",
        "safety_acknowledged",
        "current_step_id",
        "results",
        "evaluation",
        "disposition",
        "guidance",
        "created_at",
        "updated_at",
    }

    def __init__(self, root=DEFAULT_PERSONAL_CASE_ROOT):
        self._root = Path(root)

    @property
    def root(self):
        return self._root

    def save(self, snapshot):
        record = self._validate(snapshot)
        destination = self._root / f"{record['case_id']}.json"
        if destination.exists():
            existing = self._read(destination)
            if existing.get("updated_at", "") > record["updated_at"]:
                raise PersonalCaseValidationError("A newer private case snapshot already exists")
        self._write(destination, record)
        return record

    def search(self, query="", limit=12):
        if not isinstance(query, str) or len(query) > 240:
            raise PersonalCaseValidationError("Search query must be text with 240 characters or fewer")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
            raise PersonalCaseValidationError("Search limit must be an integer from 1 through 50")
        if not self._root.exists():
            return ()
        try:
            records = [self._read(path) for path in sorted(self._root.glob("CASE-*.json"))]
        except OSError as error:
            raise PersonalCaseStorageError(f"Could not list private cases: {error}") from error
        tokens = [token for token in query.casefold().split() if token]
        matches = [
            record
            for record in records
            if not tokens or all(token in self._searchable_text(record) for token in tokens)
        ]
        matches.sort(key=lambda record: (record["updated_at"], record["case_id"]), reverse=True)
        return tuple(matches[:limit])

    def _validate(self, snapshot):
        _require(isinstance(snapshot, dict), "Private case snapshot must be an object")
        _require(set(snapshot) == self._REQUIRED_KEYS, "Private case fields do not match the canonical contract")
        case_id = snapshot.get("case_id")
        _require(isinstance(case_id, str) and CASE_ID_PATTERN.fullmatch(case_id), "Private case ID is invalid")
        for field_name in ("model_id", "revision_id", "path_id", "complaint_summary", "created_at", "updated_at"):
            _require(isinstance(snapshot.get(field_name), str) and snapshot[field_name], f"Private case {field_name} is required")
        _require(snapshot.get("schema_version") == "1.0.0", "Private case schema version is unsupported")
        _require(snapshot.get("mode") == "FIELD", "Only field cases may enter personal case history")
        _require(snapshot.get("state") in CASE_STATES, "Private case state is unsupported")
        _require(snapshot.get("disposition") in CASE_DISPOSITIONS, "Private case disposition is unsupported")
        _require(snapshot.get("safety_acknowledged") is True, "Private case safety acknowledgement is required")
        package_ids = snapshot.get("knowledge_package_ids")
        _require(isinstance(package_ids, list) and package_ids, "Private case package lineage is required")
        _require(all(isinstance(value, str) and value for value in package_ids), "Private case package lineage is invalid")
        fault_codes = snapshot.get("fault_codes")
        _require(isinstance(fault_codes, list) and fault_codes, "Private case fault codes are required")
        _require(all(isinstance(value, str) and value for value in fault_codes), "Private case fault codes are invalid")
        results = snapshot.get("results")
        _require(isinstance(results, list) and results, "At least one technician result is required before saving a case")
        for result in results:
            _require(isinstance(result, dict), "Private case result must be an object")
            _require(result.get("source_type") == "TECHNICIAN_ENTRY", "Private case results must be technician-entered")
            _require(isinstance(result.get("recorded_by"), str) and result["recorded_by"], "Private case result recorder is required")
        return snapshot

    @staticmethod
    def _searchable_text(value):
        if isinstance(value, dict):
            return " ".join(PersonalCaseStore._searchable_text(item) for item in value.values()).casefold()
        if isinstance(value, list):
            return " ".join(PersonalCaseStore._searchable_text(item) for item in value).casefold()
        if value is None:
            return ""
        return str(value).casefold()

    def _read(self, path):
        try:
            if path.is_symlink() or not path.is_file():
                raise PersonalCaseStorageError(f"Private case is not a regular file: {path.name}")
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PersonalCaseStorageError(f"Could not read private case {path.name}: {error}") from error
        if not isinstance(record, dict) or record.get("case_id") != path.stem:
            raise PersonalCaseStorageError(f"Private case identity is invalid: {path.name}")
        return self._validate(record)

    def _write(self, destination, record):
        try:
            self._root.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(self._root, 0o700)
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
            raise PersonalCaseStorageError(f"Could not save private case: {error}") from error
