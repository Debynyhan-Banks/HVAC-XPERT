import unittest
from pathlib import Path

from scripts.private_package_gate import PrivateKnowledgePackage
from simulator.engine import (
    ComponentKnowledge,
    ConflictingEffectError,
    DeterministicSimulator,
    OperatingInputs,
    SimulationDefinitionError,
    SimulationInputError,
    SimulationStatus,
    UnknownFaultError,
    UnknownOperatingStateError,
)


MODEL_ID = "SYNTHETIC-MODEL"
REVISION_ID = "SYNTHETIC-REVISION"
COMPONENT_A = f"{MODEL_ID}:component:a"
COMPONENT_B = f"{MODEL_ID}:component:b"


def provenance():
    return [
        {
            "source": {
                "document_id": "DOC-SYNTHETIC",
                "page": 1,
                "section": "Synthetic",
            }
        }
    ]


def effect(target_id, property_name, value, unit=None):
    return {
        "target_id": target_id,
        "property": property_name,
        "value": value,
        "unit": unit,
    }


def fault(code, effects=()):
    return {
        "fault_id": f"{MODEL_ID}:fault:{code}",
        "model_id": MODEL_ID,
        "revision_id": REVISION_ID,
        "code": code,
        "simulator_effects": list(effects),
    }


def command(component_id, property_name, value, unit=None):
    return {
        "component_id": component_id,
        "property": property_name,
        "value": value,
        "unit": unit,
    }


def operating_state(slug, commands=(), measurement_ids=(), transitions=(), entry_conditions=()):
    state_id = f"{MODEL_ID}:state:{slug}"
    return {
        "state_id": state_id,
        "name": slug.replace("-", " ").title(),
        "description": "Synthetic operating state",
        "entry_conditions": list(entry_conditions),
        "component_commands": list(commands),
        "transitions": list(transitions),
        "measurement_ids": list(measurement_ids),
        "provenance": provenance(),
    }


def diagnostic_measurement(slug, operating_state_id=None):
    measurement_id = f"{MODEL_ID}:measurement:{slug}"
    return {
        "measurement_id": measurement_id,
        "operating_state_id": operating_state_id,
        "name": slug.replace("-", " ").title(),
        "quantity": "VOLTAGE",
        "signal_type": "AC",
        "point_a": {
            "reference_type": "COMPONENT_TERMINAL",
            "reference_id": COMPONENT_A,
            "label": "A",
        },
        "point_b": None,
        "meter_mode": "VAC",
        "expected": {
            "nominal": 24,
            "minimum": 22,
            "maximum": 26,
            "unit": "VAC",
            "interpretation": "Synthetic range",
        },
        "safety_category": "ENERGIZED_LOW_VOLTAGE",
        "procedure": "Synthetic procedure",
        "provenance": provenance(),
    }


def package(faults=None, components=None, operating_states=(), measurements=()):
    return PrivateKnowledgePackage(
        root=Path("/synthetic/private/package"),
        manifest={"model_id": MODEL_ID, "revision_id": REVISION_ID},
        equipment_model={},
        components=tuple(
            components
            if components is not None
            else (
                {"component_id": COMPONENT_B},
                {"component_id": COMPONENT_A},
            )
        ),
        faults=tuple(
            faults
            if faults is not None
            else (
                fault("F02", (effect(COMPONENT_B, "availability", False),)),
                fault("F01"),
            )
        ),
        wiring_assertions=(),
        operating_states=tuple(operating_states),
        measurements=tuple(measurements),
    )


class DeterministicSimulatorTests(unittest.TestCase):
    def test_rejects_non_boolean_inputs(self):
        with self.assertRaisesRegex(SimulationInputError, "power_available"):
            OperatingInputs(power_available=1, operation_requested=False)

    def test_reports_input_derived_status_without_inventing_component_state(self):
        simulator = DeterministicSimulator(package())

        power_off = simulator.step(OperatingInputs(power_available=False, operation_requested=True))
        idle = simulator.step(OperatingInputs(power_available=True, operation_requested=False))
        requested = simulator.step(OperatingInputs(power_available=True, operation_requested=True))

        self.assertEqual(power_off.status, SimulationStatus.POWER_UNAVAILABLE)
        self.assertEqual(idle.status, SimulationStatus.IDLE)
        self.assertEqual(requested.status, SimulationStatus.OPERATION_REQUESTED)
        self.assertEqual(
            tuple(component.component_id for component in requested.components),
            (COMPONENT_A, COMPONENT_B),
        )
        self.assertTrue(all(component.knowledge is ComponentKnowledge.UNKNOWN for component in requested.components))
        self.assertTrue(all(component.commands == () for component in requested.components))
        self.assertTrue(all(component.properties == () for component in requested.components))

    def test_applies_only_effect_declared_by_active_fault(self):
        simulator = DeterministicSimulator(package())
        simulator.activate_fault("F02")

        snapshot = simulator.step(OperatingInputs(power_available=True, operation_requested=True))

        self.assertEqual(snapshot.status, SimulationStatus.FAULT_ACTIVE)
        self.assertEqual(snapshot.active_fault_codes, ("F02",))
        self.assertEqual(len(snapshot.applied_effects), 1)
        applied = snapshot.applied_effects[0]
        self.assertEqual((applied.target_id, applied.property, applied.value), (COMPONENT_B, "availability", False))
        component_b = next(component for component in snapshot.components if component.component_id == COMPONENT_B)
        self.assertEqual(component_b.knowledge, ComponentKnowledge.EXPLICIT_FAULT_EFFECT)
        self.assertEqual(component_b.properties, (applied,))

    def test_rejects_unknown_fault_code(self):
        simulator = DeterministicSimulator(package())
        with self.assertRaisesRegex(UnknownFaultError, "UNKNOWN"):
            simulator.activate_fault("UNKNOWN")

    def test_clearing_fault_restores_input_derived_status(self):
        simulator = DeterministicSimulator(package())
        simulator.activate_fault("F01")
        simulator.clear_fault("F01")

        snapshot = simulator.step(OperatingInputs(power_available=True, operation_requested=False))

        self.assertEqual(snapshot.status, SimulationStatus.IDLE)
        self.assertEqual(snapshot.active_fault_codes, ())

    def test_equal_event_sequences_produce_equal_snapshots(self):
        first = DeterministicSimulator(package())
        second = DeterministicSimulator(package())
        first.activate_fault("F02")
        second.activate_fault("F02")
        inputs = OperatingInputs(power_available=True, operation_requested=True)

        self.assertEqual(first.step(inputs), second.step(inputs))
        self.assertEqual(first.step(inputs), second.step(inputs))

    def test_identical_effects_combine_their_fault_sources(self):
        shared_effect = effect(COMPONENT_A, "availability", False)
        simulator = DeterministicSimulator(
            package(faults=(fault("F02", (shared_effect,)), fault("F01", (shared_effect,))))
        )
        simulator.activate_fault("F02")
        simulator.activate_fault("F01")

        snapshot = simulator.step(OperatingInputs(power_available=True, operation_requested=True))

        self.assertEqual(len(snapshot.applied_effects), 1)
        self.assertEqual(snapshot.applied_effects[0].source_fault_codes, ("F01", "F02"))

    def test_conflicting_active_fault_effects_fail_closed(self):
        simulator = DeterministicSimulator(
            package(
                faults=(
                    fault("F01", (effect(COMPONENT_A, "availability", True),)),
                    fault("F02", (effect(COMPONENT_A, "availability", False),)),
                )
            )
        )
        simulator.activate_fault("F01")
        simulator.activate_fault("F02")

        with self.assertRaisesRegex(ConflictingEffectError, "conflicting effects"):
            simulator.step(OperatingInputs(power_available=True, operation_requested=True))

    def test_invalid_simulator_effect_definition_is_rejected(self):
        invalid_effect = effect(COMPONENT_A, "availability", {"not": "canonical"})
        with self.assertRaisesRegex(SimulationDefinitionError, "unsupported value"):
            DeterministicSimulator(package(faults=(fault("F01", (invalid_effect,)),)))

    def test_missing_simulator_effect_field_is_rejected(self):
        invalid_effect = effect(COMPONENT_A, "availability", False)
        del invalid_effect["unit"]
        with self.assertRaisesRegex(SimulationDefinitionError, "missing fields: unit"):
            DeterministicSimulator(package(faults=(fault("F01", (invalid_effect,)),)))

    def test_manually_selects_operating_state_and_applies_commands(self):
        state = operating_state(
            "cooling-steady",
            commands=(command(COMPONENT_A, "operating_state", "RUNNING"),),
            entry_conditions=(
                {
                    "subject_id": MODEL_ID,
                    "property": "percent_demand",
                    "operator": "GT",
                    "value": 0,
                    "unit": "%",
                },
            ),
        )
        simulator = DeterministicSimulator(package(operating_states=(state,)))

        simulator.select_operating_state(state["state_id"])
        snapshot = simulator.step(OperatingInputs(power_available=True, operation_requested=True))

        self.assertEqual(simulator.known_operating_state_ids, (state["state_id"],))
        self.assertEqual(snapshot.selected_operating_state_id, state["state_id"])
        self.assertEqual(len(snapshot.applied_commands), 1)
        self.assertEqual(snapshot.applied_commands[0].value, "RUNNING")
        self.assertEqual(simulator.operating_states[0].entry_conditions[0].value, 0)
        component_a = next(component for component in snapshot.components if component.component_id == COMPONENT_A)
        self.assertEqual(component_a.knowledge, ComponentKnowledge.EXPLICIT_STATE_COMMAND)
        self.assertEqual(component_a.commands, snapshot.applied_commands)

    def test_operating_state_selection_is_manual_and_clearable(self):
        state = operating_state("cooling-startup")
        simulator = DeterministicSimulator(package(operating_states=(state,)))
        simulator.select_operating_state(state["state_id"])

        first = simulator.step(OperatingInputs(power_available=True, operation_requested=True))
        second = simulator.step(OperatingInputs(power_available=False, operation_requested=False))
        simulator.clear_operating_state()
        cleared = simulator.step(OperatingInputs(power_available=True, operation_requested=False))

        self.assertEqual(first.selected_operating_state_id, state["state_id"])
        self.assertEqual(second.selected_operating_state_id, state["state_id"])
        self.assertIsNone(cleared.selected_operating_state_id)

    def test_rejects_unknown_operating_state(self):
        simulator = DeterministicSimulator(package())
        with self.assertRaisesRegex(UnknownOperatingStateError, "UNKNOWN"):
            simulator.select_operating_state("UNKNOWN")

    def test_surfaces_general_and_selected_state_measurements(self):
        cooling = operating_state("cooling")
        standby = operating_state("standby")
        general = diagnostic_measurement("general")
        cooling_only = diagnostic_measurement("cooling-only", cooling["state_id"])
        standby_only = diagnostic_measurement("standby-only", standby["state_id"])
        simulator = DeterministicSimulator(
            package(
                operating_states=(standby, cooling),
                measurements=(standby_only, general, cooling_only),
            )
        )

        no_state = simulator.step(OperatingInputs(power_available=True, operation_requested=False))
        simulator.select_operating_state(cooling["state_id"])
        selected = simulator.step(OperatingInputs(power_available=True, operation_requested=True))

        self.assertEqual(
            tuple(value.measurement_id for value in no_state.diagnostic_measurements),
            (general["measurement_id"],),
        )
        self.assertEqual(
            tuple(value.measurement_id for value in selected.diagnostic_measurements),
            (cooling_only["measurement_id"], general["measurement_id"]),
        )
        self.assertEqual(selected.diagnostic_measurements[0].sources[0].page, 1)

    def test_state_command_and_fault_effect_conflict_fails_closed(self):
        state = operating_state(
            "cooling",
            commands=(command(COMPONENT_A, "availability", True),),
        )
        simulator = DeterministicSimulator(
            package(
                operating_states=(state,),
                faults=(fault("F01", (effect(COMPONENT_A, "availability", False),)),),
            )
        )
        simulator.select_operating_state(state["state_id"])
        simulator.activate_fault("F01")

        with self.assertRaisesRegex(ConflictingEffectError, "conflicting values"):
            simulator.step(OperatingInputs(power_available=True, operation_requested=True))

    def test_rejects_unknown_component_in_operating_state(self):
        state = operating_state(
            "cooling",
            commands=(command("UNKNOWN-COMPONENT", "operating_state", "RUNNING"),),
        )
        with self.assertRaisesRegex(SimulationDefinitionError, "unknown component"):
            DeterministicSimulator(package(operating_states=(state,)))

    def test_rejects_automatic_transition_definitions(self):
        state = operating_state(
            "cooling",
            transitions=(
                {
                    "target_state_id": f"{MODEL_ID}:state:standby",
                    "conditions": [],
                    "delay_seconds": None,
                    "priority": 0,
                },
            ),
        )
        with self.assertRaisesRegex(SimulationDefinitionError, "automatic transitions are not supported"):
            DeterministicSimulator(package(operating_states=(state,)))


if __name__ == "__main__":
    unittest.main()
