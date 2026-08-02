from dataclasses import dataclass
from enum import Enum
from math import isfinite

from scripts.private_package_gate import PrivateKnowledgePackage


class SimulationDefinitionError(ValueError):
    pass


class SimulationInputError(ValueError):
    pass


class UnknownFaultError(KeyError):
    pass


class ConflictingEffectError(ValueError):
    pass


class SimulationStatus(Enum):
    POWER_UNAVAILABLE = "POWER_UNAVAILABLE"
    IDLE = "IDLE"
    OPERATION_REQUESTED = "OPERATION_REQUESTED"
    FAULT_ACTIVE = "FAULT_ACTIVE"


class ComponentKnowledge(Enum):
    UNKNOWN = "UNKNOWN"
    EXPLICIT_FAULT_EFFECT = "EXPLICIT_FAULT_EFFECT"


@dataclass(frozen=True)
class OperatingInputs:
    power_available: bool
    operation_requested: bool

    def __post_init__(self):
        if type(self.power_available) is not bool:
            raise SimulationInputError("power_available must be a boolean")
        if type(self.operation_requested) is not bool:
            raise SimulationInputError("operation_requested must be a boolean")


@dataclass(frozen=True)
class AppliedEffect:
    target_id: str
    property: str
    value: str | int | float | bool | None
    unit: str | None
    source_fault_codes: tuple[str, ...]


@dataclass(frozen=True)
class ComponentSnapshot:
    component_id: str
    knowledge: ComponentKnowledge
    properties: tuple[AppliedEffect, ...]


@dataclass(frozen=True)
class SimulationSnapshot:
    step_index: int
    model_id: str
    revision_id: str
    status: SimulationStatus
    inputs: OperatingInputs
    active_fault_codes: tuple[str, ...]
    applied_effects: tuple[AppliedEffect, ...]
    components: tuple[ComponentSnapshot, ...]


@dataclass(frozen=True)
class _EffectDefinition:
    target_id: str
    property: str
    value: str | int | float | bool | None
    unit: str | None


@dataclass(frozen=True)
class _FaultDefinition:
    fault_id: str
    code: str
    effects: tuple[_EffectDefinition, ...]


class DeterministicSimulator:
    def __init__(self, package: PrivateKnowledgePackage):
        self._model_id = package.model_id
        self._revision_id = package.revision_id
        self._component_ids = self._read_component_ids(package.components)
        self._faults_by_code = self._read_faults(package.faults)
        self._active_fault_codes: set[str] = set()
        self._step_index = 0

    @property
    def model_id(self):
        return self._model_id

    @property
    def revision_id(self):
        return self._revision_id

    @property
    def known_fault_codes(self):
        return tuple(sorted(self._faults_by_code))

    @property
    def active_fault_codes(self):
        return tuple(sorted(self._active_fault_codes))

    def activate_fault(self, code):
        self._require_known_fault(code)
        self._active_fault_codes.add(code)

    def clear_fault(self, code):
        self._require_known_fault(code)
        self._active_fault_codes.discard(code)

    def clear_faults(self):
        self._active_fault_codes.clear()

    def step(self, inputs: OperatingInputs):
        if not isinstance(inputs, OperatingInputs):
            raise SimulationInputError("inputs must be an OperatingInputs instance")

        active_fault_codes = self.active_fault_codes
        effects = self._resolve_effects(active_fault_codes)
        effects_by_component = {component_id: [] for component_id in self._component_ids}
        for effect in effects:
            if effect.target_id in effects_by_component:
                effects_by_component[effect.target_id].append(effect)

        components = tuple(
            ComponentSnapshot(
                component_id=component_id,
                knowledge=(
                    ComponentKnowledge.EXPLICIT_FAULT_EFFECT
                    if effects_by_component[component_id]
                    else ComponentKnowledge.UNKNOWN
                ),
                properties=tuple(effects_by_component[component_id]),
            )
            for component_id in self._component_ids
        )
        snapshot = SimulationSnapshot(
            step_index=self._step_index,
            model_id=self._model_id,
            revision_id=self._revision_id,
            status=self._status(inputs, active_fault_codes),
            inputs=inputs,
            active_fault_codes=active_fault_codes,
            applied_effects=effects,
            components=components,
        )
        self._step_index += 1
        return snapshot

    def _require_known_fault(self, code):
        if code not in self._faults_by_code:
            raise UnknownFaultError(f"Unknown fault code for {self._model_id}: {code}")

    def _resolve_effects(self, active_fault_codes):
        effects_by_property: dict[tuple[str, str], tuple[_EffectDefinition, set[str]]] = {}
        for code in active_fault_codes:
            for effect in self._faults_by_code[code].effects:
                key = (effect.target_id, effect.property)
                existing = effects_by_property.get(key)
                if existing is None:
                    effects_by_property[key] = (effect, {code})
                    continue
                existing_effect, source_codes = existing
                if self._effect_signature(existing_effect) != self._effect_signature(effect):
                    raise ConflictingEffectError(
                        f"Active faults declare conflicting effects for {effect.target_id}.{effect.property}"
                    )
                source_codes.add(code)

        return tuple(
            AppliedEffect(
                target_id=effect.target_id,
                property=effect.property,
                value=effect.value,
                unit=effect.unit,
                source_fault_codes=tuple(sorted(source_codes)),
            )
            for _, (effect, source_codes) in sorted(effects_by_property.items())
        )

    @staticmethod
    def _status(inputs, active_fault_codes):
        if active_fault_codes:
            return SimulationStatus.FAULT_ACTIVE
        if not inputs.power_available:
            return SimulationStatus.POWER_UNAVAILABLE
        if inputs.operation_requested:
            return SimulationStatus.OPERATION_REQUESTED
        return SimulationStatus.IDLE

    @staticmethod
    def _effect_signature(effect):
        return type(effect.value), effect.value, effect.unit

    @staticmethod
    def _read_component_ids(records):
        component_ids = []
        for record in records:
            component_id = record.get("component_id")
            if not isinstance(component_id, str) or not component_id:
                raise SimulationDefinitionError("Component record is missing component_id")
            component_ids.append(component_id)
        if len(component_ids) != len(set(component_ids)):
            raise SimulationDefinitionError("Component IDs must be unique")
        return tuple(sorted(component_ids))

    @classmethod
    def _read_faults(cls, records):
        faults_by_code = {}
        for record in records:
            fault_id = record.get("fault_id")
            code = record.get("code")
            if not isinstance(fault_id, str) or not fault_id:
                raise SimulationDefinitionError("Fault record is missing fault_id")
            if not isinstance(code, str) or not code:
                raise SimulationDefinitionError(f"Fault {fault_id} is missing code")
            if code in faults_by_code:
                raise SimulationDefinitionError(f"Duplicate fault code: {code}")
            effect_records = record.get("simulator_effects")
            if not isinstance(effect_records, list):
                raise SimulationDefinitionError(f"Fault {code} simulator_effects must be an array")
            effects = tuple(cls._read_effect(effect, code) for effect in effect_records)
            faults_by_code[code] = _FaultDefinition(fault_id=fault_id, code=code, effects=effects)
        return faults_by_code

    @staticmethod
    def _read_effect(record, fault_code):
        if not isinstance(record, dict):
            raise SimulationDefinitionError(f"Fault {fault_code} has an invalid simulator effect")
        missing_fields = {"target_id", "property", "value", "unit"} - record.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise SimulationDefinitionError(f"Fault {fault_code} effect is missing fields: {missing}")
        target_id = record.get("target_id")
        property_name = record.get("property")
        value = record.get("value")
        unit = record.get("unit")
        if not isinstance(target_id, str) or not target_id:
            raise SimulationDefinitionError(f"Fault {fault_code} effect is missing target_id")
        if not isinstance(property_name, str) or not property_name:
            raise SimulationDefinitionError(f"Fault {fault_code} effect is missing property")
        if type(value) not in (str, int, float, bool, type(None)):
            raise SimulationDefinitionError(f"Fault {fault_code} effect has an unsupported value")
        if type(value) is float and not isfinite(value):
            raise SimulationDefinitionError(f"Fault {fault_code} effect value must be finite")
        if unit is not None and (not isinstance(unit, str) or not unit):
            raise SimulationDefinitionError(f"Fault {fault_code} effect has an invalid unit")
        return _EffectDefinition(target_id=target_id, property=property_name, value=value, unit=unit)
