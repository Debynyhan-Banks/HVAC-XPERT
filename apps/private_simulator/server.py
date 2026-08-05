import json
from dataclasses import fields, is_dataclass
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from diagnostics import (
    DiagnosticCaseEngine,
    DiagnosticCaseInputError,
    DiagnosticDefinitionError,
    UnknownDiagnosticPathError,
)
from scripts.private_package_gate import PrivateKnowledgePackage
from simulator import DeterministicSimulator, OperatingInputs
from training import (
    TrainingAttemptInputError,
    TrainingReplayEngine,
    UnknownTrainingReplayError,
)


LOCAL_HOST = "127.0.0.1"
MAX_REQUEST_BYTES = 64 * 1024
STATIC_ROOT = Path(__file__).resolve().parent / "static"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/assets/app.css": ("app.css", "text/css; charset=utf-8"),
    "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class ApplicationRequestError(ValueError):
    pass


def json_value(value):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {field.name: json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [json_value(item) for item in value]
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    return value


class PrivateSimulatorApplication:
    def __init__(self, package: PrivateKnowledgePackage):
        self._package = package
        self._definitions = DeterministicSimulator(package)
        self._diagnostic_cases = DiagnosticCaseEngine(package)
        self._training = TrainingReplayEngine(package)

    def definitions(self):
        return {
            "classification": "PRIVATE_LOCAL_ONLY",
            "automatic_transitions_enabled": False,
            "measurement_behavior": "REFERENCE_DEFINITION_ONLY",
            "topology_behavior": "REFERENCE_DEFINITION_ONLY",
            "diagnostic_case_behavior": "TECHNICIAN_ENTRY_DETERMINISTIC_EVALUATION",
            "training_behavior": "DETERMINISTIC_SIMULATED_REPLAY_SCORING",
            "model": {
                "model_id": self._definitions.model_id,
                "revision_id": self._definitions.revision_id,
                "component_count": len(self._package.components),
                "fault_count": len(self._package.faults),
                "operating_state_count": len(self._definitions.operating_states),
                "measurement_count": len(self._definitions.diagnostic_measurements),
                "connector_count": len(self._package.connectors),
                "pin_count": len(self._package.pins),
                "node_count": len(self._package.nodes),
                "connection_count": len(self._package.connections),
                "diagnostic_path_count": len(self._diagnostic_cases.diagnostic_paths),
                "training_replay_count": len(self._training.training_replays),
            },
            "operating_states": json_value(self._definitions.operating_states),
            "fault_codes": list(self._definitions.known_fault_codes),
            "diagnostic_paths": json_value(self._diagnostic_cases.diagnostic_paths),
            "training_replays": json_value(self._training.training_replays),
            "topology": {
                "connectors": json_value(self._package.connectors),
                "pins": json_value(self._package.pins),
                "nodes": json_value(self._package.nodes),
                "connections": json_value(self._package.connections),
            },
        }

    def snapshot(self, request):
        values = self._validate_snapshot_request(request)
        simulator = DeterministicSimulator(self._package)
        if values["operating_state_id"] is not None:
            simulator.select_operating_state(values["operating_state_id"])
        for fault_code in values["fault_codes"]:
            simulator.activate_fault(fault_code)
        snapshot = simulator.step(
            OperatingInputs(
                power_available=values["power_available"],
                operation_requested=values["operation_requested"],
            )
        )
        return json_value(snapshot)

    def case_snapshot(self, request):
        return json_value(self._diagnostic_cases.evaluate(request))

    def training_snapshot(self, request):
        return json_value(self._training.evaluate(request))

    @staticmethod
    def _validate_snapshot_request(request):
        if not isinstance(request, dict):
            raise ApplicationRequestError("Request body must be a JSON object")
        allowed_keys = {
            "power_available",
            "operation_requested",
            "operating_state_id",
            "fault_codes",
        }
        unexpected_keys = set(request) - allowed_keys
        if unexpected_keys:
            raise ApplicationRequestError(f"Unexpected request fields: {sorted(unexpected_keys)}")
        for field_name in ("power_available", "operation_requested"):
            if type(request.get(field_name)) is not bool:
                raise ApplicationRequestError(f"{field_name} must be a boolean")
        operating_state_id = request.get("operating_state_id")
        if operating_state_id is not None and (
            not isinstance(operating_state_id, str) or not operating_state_id
        ):
            raise ApplicationRequestError("operating_state_id must be null or a non-empty string")
        fault_codes = request.get("fault_codes", [])
        if not isinstance(fault_codes, list) or not all(
            isinstance(code, str) and code for code in fault_codes
        ):
            raise ApplicationRequestError("fault_codes must be an array of non-empty strings")
        return {
            "power_available": request["power_available"],
            "operation_requested": request["operation_requested"],
            "operating_state_id": operating_state_id,
            "fault_codes": tuple(sorted(set(fault_codes))),
        }


def is_local_host_header(value):
    if not value:
        return False
    hostname = urlsplit(f"//{value}").hostname
    return hostname in {LOCAL_HOST, "localhost"}


def create_handler(application, static_root=STATIC_ROOT):
    class PrivateSimulatorHandler(BaseHTTPRequestHandler):
        server_version = "HVAC-XPERT-Local/1"

        def do_GET(self):
            if not self._request_is_local():
                self._send_error(HTTPStatus.FORBIDDEN, "Only localhost requests are allowed")
                return
            path = urlsplit(self.path).path
            if path == "/api/definitions":
                self._send_json(HTTPStatus.OK, application.definitions())
                return
            static_file = STATIC_FILES.get(path)
            if static_file is None:
                self._send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            filename, content_type = static_file
            try:
                body = (static_root / filename).read_bytes()
            except OSError:
                self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Application asset is unavailable")
                return
            self._send(HTTPStatus.OK, body, content_type)

        def do_POST(self):
            if not self._request_is_local():
                self._send_error(HTTPStatus.FORBIDDEN, "Only localhost requests are allowed")
                return
            path = urlsplit(self.path).path
            if path not in {"/api/snapshot", "/api/case", "/api/training"}:
                self._send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            content_type = self.headers.get_content_type()
            if content_type != "application/json":
                self._send_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_error(HTTPStatus.BAD_REQUEST, "Invalid Content-Length")
                return
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                self._send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body size is invalid")
                return
            try:
                request = json.loads(self.rfile.read(content_length))
                if path == "/api/snapshot":
                    response = application.snapshot(request)
                elif path == "/api/case":
                    response = application.case_snapshot(request)
                else:
                    response = application.training_snapshot(request)
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_error(HTTPStatus.BAD_REQUEST, "Request body must contain valid JSON")
                return
            except (
                ApplicationRequestError,
                DiagnosticCaseInputError,
                DiagnosticDefinitionError,
                UnknownDiagnosticPathError,
                TrainingAttemptInputError,
                UnknownTrainingReplayError,
                KeyError,
                ValueError,
            ) as error:
                self._send_error(HTTPStatus.UNPROCESSABLE_ENTITY, str(error))
                return
            self._send_json(HTTPStatus.OK, response)

        def do_OPTIONS(self):
            self._send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Cross-origin requests are not supported")

        def log_message(self, format, *args):
            return

        def _request_is_local(self):
            return is_local_host_header(self.headers.get("Host"))

        def _send_error(self, status, message):
            self._send_json(status, {"error": message})

        def _send_json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8")

        def _send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(body)

    return PrivateSimulatorHandler


def create_server(application, port=8765):
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("port must be an integer from 0 through 65535")
    return ThreadingHTTPServer((LOCAL_HOST, port), create_handler(application))
