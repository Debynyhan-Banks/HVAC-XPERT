#!/usr/bin/env python3

import argparse
import json
import sys
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from scripts.private_package_gate import (
    DEFAULT_PRIVATE_ROOT,
    PackageValidationError,
    load_private_approved_package_with_extensions,
)
from simulator import (
    ConflictingEffectError,
    DeterministicSimulator,
    OperatingInputs,
    SimulationDefinitionError,
    SimulationInputError,
    UnknownFaultError,
    UnknownOperatingStateError,
)


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


def parse_args():
    parser = argparse.ArgumentParser(description="Run the deterministic simulator with approved private packages.")
    parser.add_argument("package", type=Path, help="Approved private base-package directory")
    parser.add_argument(
        "--extension",
        action="append",
        type=Path,
        default=[],
        help="Approved private extension directory",
    )
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--state", help="Exact approved operating-state ID to select manually")
    parser.add_argument("--fault", action="append", default=[], help="Exact approved fault code to activate")
    parser.add_argument("--power-available", action="store_true")
    parser.add_argument("--operation-requested", action="store_true")
    parser.add_argument("--list-states", action="store_true")
    parser.add_argument("--list-measurements", action="store_true")
    return parser.parse_args()


def run(args):
    package = load_private_approved_package_with_extensions(
        args.package,
        args.extension,
        args.private_root,
    )
    simulator = DeterministicSimulator(package)
    if args.list_states or args.list_measurements:
        output = {}
        if args.list_states:
            output["operating_states"] = simulator.operating_states
        if args.list_measurements:
            output["diagnostic_measurements"] = simulator.diagnostic_measurements
        return output

    if args.state:
        simulator.select_operating_state(args.state)
    for fault_code in args.fault:
        simulator.activate_fault(fault_code)
    return simulator.step(
        OperatingInputs(
            power_available=args.power_available,
            operation_requested=args.operation_requested,
        )
    )


def main():
    args = parse_args()
    try:
        output = run(args)
    except (
        PackageValidationError,
        SimulationDefinitionError,
        SimulationInputError,
        UnknownFaultError,
        UnknownOperatingStateError,
        ConflictingEffectError,
    ) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(json_value(output), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
