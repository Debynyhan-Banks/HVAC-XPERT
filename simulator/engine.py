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


class UnknownOperatingStateError(KeyError):
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
    EXPLICIT_STATE_COMMAND = "EXPLICIT_STATE_COMMAND"
    EXPLICIT_FAULT_EFFECT = "EXPLICIT_FAULT_EFFECT"
    EXPLICIT_STATE_AND_FAULT = "EXPLICIT_STATE_AND_FAULT"


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
class SourceReference:
    document_id: str
    page: int
    section: str | None
    validation_level: str
    validation_outcome: str
    reviewed_by: str
    reviewed_at: str


@dataclass(frozen=True)
class OperatingCondition:
    subject_id: str
    property: str
    operator: str
    value: object
    unit: str | None


@dataclass(frozen=True)
class AppliedCommand:
    component_id: str
    property: str
    value: str | int | float | bool | None
    unit: str | None
    source_state_id: str


@dataclass(frozen=True)
class AppliedEffect:
    target_id: str
    property: str
    value: str | int | float | bool | None
    unit: str | None
    source_fault_codes: tuple[str, ...]


@dataclass(frozen=True)
class OperatingStateDefinition:
    state_id: str
    name: str
    description: str | None
    entry_conditions: tuple[OperatingCondition, ...]
    commands: tuple[AppliedCommand, ...]
    measurement_ids: tuple[str, ...]
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class MeasurementPoint:
    reference_type: str
    reference_id: str
    label: str | None


@dataclass(frozen=True)
class ExpectedMeasurement:
    nominal: int | float | None
    minimum: int | float | None
    maximum: int | float | None
    unit: str | None
    interpretation: str | None


@dataclass(frozen=True)
class DiagnosticMeasurementDefinition:
    measurement_id: str
    operating_state_id: str | None
    name: str
    quantity: str
    signal_type: str
    point_a: MeasurementPoint
    point_b: MeasurementPoint | None
    meter_mode: str
    expected: ExpectedMeasurement
    safety_category: str
    procedure: str | None
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class ComponentSnapshot:
    component_id: str
    knowledge: ComponentKnowledge
    commands: tuple[AppliedCommand, ...]
    properties: tuple[AppliedEffect, ...]


@dataclass(frozen=True)
class SimulationSnapshot:
    step_index: int
    model_id: str
    revision_id: str
    status: SimulationStatus
    inputs: OperatingInputs
    selected_operating_state_id: str | None
    applied_commands: tuple[AppliedCommand, ...]
    diagnostic_measurements: tuple[DiagnosticMeasurementDefinition, ...]
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
        self._operating_states_by_id = self._read_operating_states(
            package.operating_states,
            set(self._component_ids),
        )
        self._measurements_by_id = self._read_measurements(
            package.measurements,
            set(self._operating_states_by_id),
        )
        self._validate_state_measurements()
        self._faults_by_code = self._read_faults(package.faults)
        self._selected_operating_state_id: str | None = None
        self._active_fault_codes: set[str] = set()
        self._step_index = 0

    @property
    def model_id(self):
        return self._model_id

    @property
    def revision_id(self):
        return self._revision_id

    @property
    def operating_states(self):
        return tuple(self._operating_states_by_id[state_id] for state_id in self.known_operating_state_ids)

    @property
    def known_operating_state_ids(self):
        return tuple(sorted(self._operating_states_by_id))

    @property
    def selected_operating_state_id(self):
        return self._selected_operating_state_id

    @property
    def diagnostic_measurements(self):
        return tuple(self._measurements_by_id[measurement_id] for measurement_id in sorted(self._measurements_by_id))

    @property
    def known_fault_codes(self):
        return tuple(sorted(self._faults_by_code))

    @property
    def active_fault_codes(self):
        return tuple(sorted(self._active_fault_codes))

    def select_operating_state(self, state_id):
        if state_id not in self._operating_states_by_id:
            raise UnknownOperatingStateError(f"Unknown operating state for {self._model_id}: {state_id}")
        self._selected_operating_state_id = state_id

    def clear_operating_state(self):
        self._selected_operating_state_id = None

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

        selected_state = self._selected_state()
        commands = selected_state.commands if selected_state is not None else ()
        active_fault_codes = self.active_fault_codes
        effects = self._resolve_effects(active_fault_codes)
        self._require_compatible_commands_and_effects(commands, effects)
        commands_by_component = {component_id: [] for component_id in self._component_ids}
        effects_by_component = {component_id: [] for component_id in self._component_ids}
        for command in commands:
            commands_by_component[command.component_id].append(command)
        for effect in effects:
            if effect.target_id in effects_by_component:
                effects_by_component[effect.target_id].append(effect)

        components = tuple(
            ComponentSnapshot(
                component_id=component_id,
                knowledge=self._component_knowledge(
                    commands_by_component[component_id],
                    effects_by_component[component_id],
                ),
                commands=tuple(commands_by_component[component_id]),
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
            selected_operating_state_id=self._selected_operating_state_id,
            applied_commands=commands,
            diagnostic_measurements=self._available_measurements(selected_state),
            active_fault_codes=active_fault_codes,
            applied_effects=effects,
            components=components,
        )
        self._step_index += 1
        return snapshot

    def _selected_state(self):
        if self._selected_operating_state_id is None:
            return None
        return self._operating_states_by_id[self._selected_operating_state_id]

    def _available_measurements(self, selected_state):
        selected_state_id = selected_state.state_id if selected_state is not None else None
        selected_measurement_ids = set(selected_state.measurement_ids) if selected_state is not None else set()
        return tuple(
            measurement
            for measurement in self.diagnostic_measurements
            if measurement.operating_state_id is None
            or measurement.operating_state_id == selected_state_id
            or measurement.measurement_id in selected_measurement_ids
        )

    def _validate_state_measurements(self):
        available_measurement_ids = set(self._measurements_by_id)
        for state in self._operating_states_by_id.values():
            unknown_ids = set(state.measurement_ids) - available_measurement_ids
            if unknown_ids:
                raise SimulationDefinitionError(
                    f"Operating state {state.state_id} references unknown measurements: {sorted(unknown_ids)}"
                )

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
                if self._value_signature(existing_effect) != self._value_signature(effect):
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

    @classmethod
    def _require_compatible_commands_and_effects(cls, commands, effects):
        effects_by_property = {(effect.target_id, effect.property): effect for effect in effects}
        for command in commands:
            effect = effects_by_property.get((command.component_id, command.property))
            if effect is not None and cls._value_signature(command) != cls._value_signature(effect):
                raise ConflictingEffectError(
                    "Selected operating state and active fault declare conflicting values for "
                    f"{command.component_id}.{command.property}"
                )

    @staticmethod
    def _component_knowledge(commands, effects):
        if commands and effects:
            return ComponentKnowledge.EXPLICIT_STATE_AND_FAULT
        if commands:
            return ComponentKnowledge.EXPLICIT_STATE_COMMAND
        if effects:
            return ComponentKnowledge.EXPLICIT_FAULT_EFFECT
        return ComponentKnowledge.UNKNOWN

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
    def _value_signature(value_record):
        return type(value_record.value), value_record.value, value_record.unit

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
    def _read_operating_states(cls, records, component_ids):
        states_by_id = {}
        for record in records:
            state_id = record.get("state_id")
            name = record.get("name")
            if not isinstance(state_id, str) or not state_id:
                raise SimulationDefinitionError("Operating-state record is missing state_id")
            if state_id in states_by_id:
                raise SimulationDefinitionError(f"Duplicate operating-state ID: {state_id}")
            if not isinstance(name, str) or not name:
                raise SimulationDefinitionError(f"Operating state {state_id} is missing name")
            description = record.get("description")
            if description is not None and not isinstance(description, str):
                raise SimulationDefinitionError(f"Operating state {state_id} has an invalid description")
            transitions = record.get("transitions")
            if not isinstance(transitions, list):
                raise SimulationDefinitionError(f"Operating state {state_id} transitions must be an array")
            if transitions:
                raise SimulationDefinitionError(
                    f"Operating state {state_id} contains transitions, but automatic transitions are not supported"
                )
            condition_records = record.get("entry_conditions")
            command_records = record.get("component_commands")
            measurement_ids = record.get("measurement_ids")
            if not isinstance(condition_records, list):
                raise SimulationDefinitionError(f"Operating state {state_id} entry conditions must be an array")
            if not isinstance(command_records, list):
                raise SimulationDefinitionError(f"Operating state {state_id} component commands must be an array")
            if not isinstance(measurement_ids, list) or not all(
                isinstance(value, str) for value in measurement_ids
            ):
                raise SimulationDefinitionError(
                    f"Operating state {state_id} measurement IDs must be an array of strings"
                )
            conditions = tuple(cls._read_condition(value, state_id) for value in condition_records)
            commands = cls._read_commands(command_records, state_id, component_ids)
            sources = cls._read_sources(record, f"Operating state {state_id}")
            states_by_id[state_id] = OperatingStateDefinition(
                state_id=state_id,
                name=name,
                description=description,
                entry_conditions=conditions,
                commands=commands,
                measurement_ids=tuple(sorted(set(measurement_ids))),
                sources=sources,
            )
        return states_by_id

    @classmethod
    def _read_commands(cls, records, state_id, component_ids):
        commands_by_property = {}
        for record in records:
            if not isinstance(record, dict):
                raise SimulationDefinitionError(f"Operating state {state_id} has an invalid component command")
            missing_fields = {"component_id", "property", "value", "unit"} - record.keys()
            if missing_fields:
                missing = ", ".join(sorted(missing_fields))
                raise SimulationDefinitionError(f"Operating state {state_id} command is missing fields: {missing}")
            component_id = record.get("component_id")
            property_name = record.get("property")
            value = cls._read_scalar(record.get("value"), f"Operating state {state_id} command")
            unit = cls._read_unit(record.get("unit"), f"Operating state {state_id} command")
            if not isinstance(component_id, str) or not component_id:
                raise SimulationDefinitionError(f"Operating state {state_id} command is missing component_id")
            if component_id not in component_ids:
                raise SimulationDefinitionError(
                    f"Operating state {state_id} references unknown component {component_id}"
                )
            if not isinstance(property_name, str) or not property_name:
                raise SimulationDefinitionError(f"Operating state {state_id} command is missing property")
            command = AppliedCommand(
                component_id=component_id,
                property=property_name,
                value=value,
                unit=unit,
                source_state_id=state_id,
            )
            key = (component_id, property_name)
            existing = commands_by_property.get(key)
            if existing is not None and cls._value_signature(existing) != cls._value_signature(command):
                raise SimulationDefinitionError(
                    f"Operating state {state_id} contains conflicting commands for {component_id}.{property_name}"
                )
            commands_by_property[key] = command
        return tuple(commands_by_property[key] for key in sorted(commands_by_property))

    @classmethod
    def _read_condition(cls, record, state_id):
        if not isinstance(record, dict):
            raise SimulationDefinitionError(f"Operating state {state_id} has an invalid entry condition")
        missing_fields = {"subject_id", "property", "operator", "value", "unit"} - record.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise SimulationDefinitionError(f"Operating state {state_id} condition is missing fields: {missing}")
        subject_id = record.get("subject_id")
        property_name = record.get("property")
        operator = record.get("operator")
        unit = cls._read_unit(record.get("unit"), f"Operating state {state_id} condition")
        if not isinstance(subject_id, str) or not subject_id:
            raise SimulationDefinitionError(f"Operating state {state_id} condition is missing subject_id")
        if not isinstance(property_name, str) or not property_name:
            raise SimulationDefinitionError(f"Operating state {state_id} condition is missing property")
        if not isinstance(operator, str) or not operator:
            raise SimulationDefinitionError(f"Operating state {state_id} condition is missing operator")
        return OperatingCondition(
            subject_id=subject_id,
            property=property_name,
            operator=operator,
            value=cls._freeze_condition_value(record.get("value"), state_id),
            unit=unit,
        )

    @classmethod
    def _read_measurements(cls, records, state_ids):
        measurements_by_id = {}
        for record in records:
            measurement_id = record.get("measurement_id")
            if not isinstance(measurement_id, str) or not measurement_id:
                raise SimulationDefinitionError("Measurement record is missing measurement_id")
            if measurement_id in measurements_by_id:
                raise SimulationDefinitionError(f"Duplicate measurement ID: {measurement_id}")
            operating_state_id = record.get("operating_state_id")
            if operating_state_id is not None and not isinstance(operating_state_id, str):
                raise SimulationDefinitionError(
                    f"Measurement {measurement_id} has an invalid operating_state_id"
                )
            if operating_state_id is not None and operating_state_id not in state_ids:
                raise SimulationDefinitionError(
                    f"Measurement {measurement_id} references unknown operating state {operating_state_id}"
                )
            name = cls._required_string(record.get("name"), f"Measurement {measurement_id} name")
            quantity = cls._required_string(record.get("quantity"), f"Measurement {measurement_id} quantity")
            signal_type = cls._required_string(
                record.get("signal_type"),
                f"Measurement {measurement_id} signal type",
            )
            meter_mode = cls._required_string(record.get("meter_mode"), f"Measurement {measurement_id} meter mode")
            safety_category = cls._required_string(
                record.get("safety_category"),
                f"Measurement {measurement_id} safety category",
            )
            procedure = record.get("procedure")
            if procedure is not None and not isinstance(procedure, str):
                raise SimulationDefinitionError(f"Measurement {measurement_id} has an invalid procedure")
            measurements_by_id[measurement_id] = DiagnosticMeasurementDefinition(
                measurement_id=measurement_id,
                operating_state_id=operating_state_id,
                name=name,
                quantity=quantity,
                signal_type=signal_type,
                point_a=cls._read_measurement_point(record.get("point_a"), measurement_id, "point_a"),
                point_b=cls._read_measurement_point(record.get("point_b"), measurement_id, "point_b", nullable=True),
                meter_mode=meter_mode,
                expected=cls._read_expected_measurement(record.get("expected"), measurement_id),
                safety_category=safety_category,
                procedure=procedure,
                sources=cls._read_sources(record, f"Measurement {measurement_id}"),
            )
        return measurements_by_id

    @classmethod
    def _read_measurement_point(cls, record, measurement_id, point_name, nullable=False):
        if record is None and nullable:
            return None
        if not isinstance(record, dict):
            raise SimulationDefinitionError(f"Measurement {measurement_id} {point_name} must be an object")
        reference_type = cls._required_string(
            record.get("reference_type"),
            f"Measurement {measurement_id} {point_name} reference type",
        )
        reference_id = cls._required_string(
            record.get("reference_id"),
            f"Measurement {measurement_id} {point_name} reference ID",
        )
        label = record.get("label")
        if label is not None and (not isinstance(label, str) or not label):
            raise SimulationDefinitionError(f"Measurement {measurement_id} {point_name} has an invalid label")
        return MeasurementPoint(reference_type=reference_type, reference_id=reference_id, label=label)

    @classmethod
    def _read_expected_measurement(cls, record, measurement_id):
        if not isinstance(record, dict):
            raise SimulationDefinitionError(f"Measurement {measurement_id} expected value must be an object")
        missing_fields = {"nominal", "minimum", "maximum", "unit", "interpretation"} - record.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise SimulationDefinitionError(
                f"Measurement {measurement_id} expected value is missing fields: {missing}"
            )
        values = {}
        for field in ("nominal", "minimum", "maximum"):
            value = record.get(field)
            if type(value) not in (int, float, type(None)):
                raise SimulationDefinitionError(
                    f"Measurement {measurement_id} expected {field} must be numeric or null"
                )
            if type(value) is float and not isfinite(value):
                raise SimulationDefinitionError(f"Measurement {measurement_id} expected {field} must be finite")
            values[field] = value
        interpretation = record.get("interpretation")
        if interpretation is not None and not isinstance(interpretation, str):
            raise SimulationDefinitionError(f"Measurement {measurement_id} has an invalid interpretation")
        return ExpectedMeasurement(
            nominal=values["nominal"],
            minimum=values["minimum"],
            maximum=values["maximum"],
            unit=cls._read_unit(record.get("unit"), f"Measurement {measurement_id} expected value"),
            interpretation=interpretation,
        )

    @classmethod
    def _read_sources(cls, record, location):
        provenance = record.get("provenance")
        if not isinstance(provenance, list) or not provenance:
            raise SimulationDefinitionError(f"{location} is missing provenance")
        sources = set()
        for assertion in provenance:
            source = assertion.get("source") if isinstance(assertion, dict) else None
            validation = assertion.get("validation") if isinstance(assertion, dict) else None
            if not isinstance(source, dict):
                raise SimulationDefinitionError(f"{location} has invalid provenance")
            if not isinstance(validation, dict):
                raise SimulationDefinitionError(f"{location} has invalid validation metadata")
            document_id = cls._required_string(source.get("document_id"), f"{location} source document ID")
            page = source.get("page")
            section = source.get("section")
            if not isinstance(page, int) or page < 1:
                raise SimulationDefinitionError(f"{location} has an invalid source page")
            if section is not None and (not isinstance(section, str) or not section):
                raise SimulationDefinitionError(f"{location} has an invalid source section")
            sources.add(
                SourceReference(
                    document_id=document_id,
                    page=page,
                    section=section,
                    validation_level=cls._required_string(
                        validation.get("level"),
                        f"{location} validation level",
                    ),
                    validation_outcome=cls._required_string(
                        validation.get("outcome"),
                        f"{location} validation outcome",
                    ),
                    reviewed_by=cls._required_string(
                        validation.get("reviewed_by"),
                        f"{location} validation reviewer",
                    ),
                    reviewed_at=cls._required_string(
                        validation.get("reviewed_at"),
                        f"{location} validation timestamp",
                    ),
                )
            )
        return tuple(sorted(sources, key=lambda value: (value.document_id, value.page, value.section or "")))

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

    @classmethod
    def _read_effect(cls, record, fault_code):
        if not isinstance(record, dict):
            raise SimulationDefinitionError(f"Fault {fault_code} has an invalid simulator effect")
        missing_fields = {"target_id", "property", "value", "unit"} - record.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise SimulationDefinitionError(f"Fault {fault_code} effect is missing fields: {missing}")
        target_id = record.get("target_id")
        property_name = record.get("property")
        if not isinstance(target_id, str) or not target_id:
            raise SimulationDefinitionError(f"Fault {fault_code} effect is missing target_id")
        if not isinstance(property_name, str) or not property_name:
            raise SimulationDefinitionError(f"Fault {fault_code} effect is missing property")
        return _EffectDefinition(
            target_id=target_id,
            property=property_name,
            value=cls._read_scalar(record.get("value"), f"Fault {fault_code} effect"),
            unit=cls._read_unit(record.get("unit"), f"Fault {fault_code} effect"),
        )

    @staticmethod
    def _read_scalar(value, location):
        if type(value) not in (str, int, float, bool, type(None)):
            raise SimulationDefinitionError(f"{location} has an unsupported value")
        if type(value) is float and not isfinite(value):
            raise SimulationDefinitionError(f"{location} value must be finite")
        return value

    @staticmethod
    def _read_unit(unit, location):
        if unit is not None and (not isinstance(unit, str) or not unit):
            raise SimulationDefinitionError(f"{location} has an invalid unit")
        return unit

    @classmethod
    def _freeze_condition_value(cls, value, state_id):
        if isinstance(value, list):
            return tuple(cls._read_scalar(item, f"Operating state {state_id} condition") for item in value)
        return cls._read_scalar(value, f"Operating state {state_id} condition")

    @staticmethod
    def _required_string(value, location):
        if not isinstance(value, str) or not value:
            raise SimulationDefinitionError(f"{location} must be a non-empty string")
        return value
