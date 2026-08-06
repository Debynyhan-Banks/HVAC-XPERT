#!/usr/bin/env python3

import argparse
import sys
import webbrowser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from apps.private_simulator.server import LOCAL_HOST, PrivateSimulatorApplication, create_server
from personal_knowledge import DEFAULT_PERSONAL_ENTRY_ROOT, PersonalEntryStore
from scripts.private_package_gate import (
    DEFAULT_PRIVATE_ROOT,
    PackageValidationError,
    load_private_approved_package_with_extensions,
)
from simulator import SimulationDefinitionError


def parse_args():
    parser = argparse.ArgumentParser(description="Run the private HVAC XPERT simulator interface on localhost.")
    parser.add_argument("package", type=Path, help="Approved private base-package directory")
    parser.add_argument(
        "--extension",
        action="append",
        type=Path,
        default=[],
        help="Approved private extension directory",
    )
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the private interface in the default browser")
    return parser.parse_args()


def run(args):
    package = load_private_approved_package_with_extensions(
        args.package,
        args.extension,
        args.private_root,
    )
    application = PrivateSimulatorApplication(package, PersonalEntryStore(DEFAULT_PERSONAL_ENTRY_ROOT))
    return create_server(application, args.port)


def main():
    args = parse_args()
    try:
        server = run(args)
    except (PackageValidationError, SimulationDefinitionError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    address = f"http://{LOCAL_HOST}:{server.server_port}"
    print(f"HVAC XPERT private simulator: {address}")
    print("Press Ctrl+C to stop. Private package records remain local and are not exported.")
    print(f"Personal entries remain private under: {DEFAULT_PERSONAL_ENTRY_ROOT}")
    if args.open:
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping private simulator.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
