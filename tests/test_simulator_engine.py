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
)


MODEL_ID = "SYNTHETIC-MODEL"
REVISION_ID = "SYNTHETIC-REVISION"
COMPONENT_A = f"{MODEL_ID}:component:a"
COMPONENT_B = f"{MODEL_ID}:component:b"


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


def package(faults=None, components=None):
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


if __name__ == "__main__":
    unittest.main()
