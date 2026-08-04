"use strict";

const state = {
  definitions: null,
  activeFaults: new Set(),
  availableMeasurements: [],
  selectedMeasurementId: null,
};

const elements = {
  modelName: document.querySelector("#model-name"),
  revisionId: document.querySelector("#revision-id"),
  componentCount: document.querySelector("#component-count"),
  phaseCount: document.querySelector("#phase-count"),
  measurementCount: document.querySelector("#measurement-count"),
  phaseSelect: document.querySelector("#phase-select"),
  phaseDescription: document.querySelector("#phase-description"),
  powerToggle: document.querySelector("#power-toggle"),
  requestToggle: document.querySelector("#request-toggle"),
  faultSearch: document.querySelector("#fault-search"),
  faultList: document.querySelector("#fault-list"),
  faultCount: document.querySelector("#fault-count"),
  statusBadge: document.querySelector("#status-badge"),
  commandCount: document.querySelector("#command-count"),
  commandGrid: document.querySelector("#command-grid"),
  unknownSummary: document.querySelector("#unknown-summary"),
  diagnosticSelect: document.querySelector("#diagnostic-select"),
  meterMode: document.querySelector("#meter-mode"),
  meterReading: document.querySelector("#meter-reading"),
  meterInterpretation: document.querySelector("#meter-interpretation"),
  meterPointA: document.querySelector("#meter-point-a"),
  meterPointB: document.querySelector("#meter-point-b"),
  meterName: document.querySelector("#meter-name"),
  meterSafety: document.querySelector("#meter-safety"),
  meterValidation: document.querySelector("#meter-validation"),
  meterManufacturer: document.querySelector("#meter-manufacturer"),
  meterProcedure: document.querySelector("#meter-procedure"),
  meterSource: document.querySelector("#meter-source"),
  diagnosticCount: document.querySelector("#diagnostic-count"),
  diagnosticBody: document.querySelector("#diagnostic-body"),
  errorBanner: document.querySelector("#error-banner"),
  errorMessage: document.querySelector("#error-message"),
};

function node(tagName, className, text) {
  const value = document.createElement(tagName);
  if (className) value.className = className;
  if (text !== undefined) value.textContent = text;
  return value;
}

function showError(message) {
  elements.errorMessage.textContent = message;
  elements.errorBanner.hidden = false;
}

function clearError() {
  elements.errorBanner.hidden = true;
  elements.errorMessage.textContent = "";
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

function populateModel(model) {
  elements.modelName.textContent = model.model_id;
  elements.revisionId.textContent = model.revision_id;
  elements.revisionId.title = model.revision_id;
  elements.componentCount.textContent = model.component_count;
  elements.phaseCount.textContent = model.operating_state_count;
  elements.measurementCount.textContent = model.measurement_count;
}

function populatePhases(phases) {
  for (const phase of phases) {
    const option = document.createElement("option");
    option.value = phase.state_id;
    option.textContent = phase.name;
    elements.phaseSelect.append(option);
  }
}

function renderFaults(filter = "") {
  elements.faultList.replaceChildren();
  const normalized = filter.trim().toLowerCase();
  const codes = state.definitions.fault_codes.filter((code) => code.toLowerCase().includes(normalized));
  if (codes.length === 0) {
    elements.faultList.append(node("p", "fault-empty", "No approved fault codes match."));
    return;
  }
  for (const code of codes) {
    const label = node("label", "fault-option");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = code;
    checkbox.checked = state.activeFaults.has(code);
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) state.activeFaults.add(code);
      else state.activeFaults.delete(code);
      elements.faultCount.textContent = state.activeFaults.size;
      updateSnapshot();
    });
    label.append(checkbox, node("span", "", code));
    elements.faultList.append(label);
  }
}

function selectedPhase() {
  const selectedId = elements.phaseSelect.value;
  return state.definitions.operating_states.find((phase) => phase.state_id === selectedId) || null;
}

function updatePhaseDescription() {
  const phase = selectedPhase();
  elements.phaseDescription.textContent = phase?.description || "No phase selected. Nothing advances automatically.";
}

function formatValue(value, unit) {
  const display = value === null ? "Unknown" : String(value);
  return unit ? `${display} ${unit}` : display;
}

function humanize(value) {
  return value.replaceAll("_", " ").replaceAll("-", " ").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function componentName(referenceId) {
  const identifier = referenceId.split(":").at(-1) || referenceId;
  return humanize(identifier).replace(/^Dc\b/, "DC").replace(/^Pcb\b/, "PCB");
}

function commandPresentation(record, effect) {
  const rawValue = formatValue(record.value, record.unit);
  if (record.value === "PERCENT_DEMAND" && record.unit === "%") {
    return {
      value: "Demand-driven",
      note: "Exact compressor demand percentage is not specified in this approved phase definition.",
      rawValue,
    };
  }
  if (record.value === "VARIABLE_0_TO_8" && record.unit === "step") {
    return {
      value: "Variable steps 0–8",
      note: "Exact outdoor-fan step is not specified in this approved phase definition.",
      rawValue,
    };
  }
  if (record.value === null) {
    return {
      value: "Unknown",
      note: "The approved records do not define an exact value.",
      rawValue: null,
    };
  }
  return {
    value: rawValue,
    note: effect ? "Explicit effect from an active approved fault." : "Explicit command from the approved phase definition.",
    rawValue: null,
  };
}

function renderStatus(status) {
  const styles = {
    IDLE: ["Idle", "status-idle"],
    OPERATION_REQUESTED: ["Operation requested", "status-operation"],
    POWER_UNAVAILABLE: ["Power unavailable", "status-power"],
    FAULT_ACTIVE: ["Fault active", "status-fault"],
  };
  const [label, className] = styles[status] || [status, "status-loading"];
  elements.statusBadge.textContent = label;
  elements.statusBadge.className = `status-badge ${className}`;
}

function commandCard(record, effect = false) {
  const referenceId = effect ? record.target_id : record.component_id;
  const presentation = commandPresentation(record, effect);
  const card = node("article", `command-card${effect ? " effect-card" : ""}`);
  const heading = node("div", "command-card-heading");
  const identity = node("div", "command-identity");
  identity.append(
    node("strong", "command-component-name", componentName(referenceId)),
    node("code", "component-id", referenceId),
  );
  heading.append(identity, node("span", "command-kind", effect ? "Fault effect" : "Phase command"));
  const detail = node("div", "command-value");
  detail.append(
    node("span", "command-property", humanize(record.property)),
    node("strong", "", presentation.value),
  );
  card.append(heading, detail, node("p", "command-note", presentation.note));
  if (presentation.rawValue) {
    const rawDefinition = node("p", "raw-definition");
    rawDefinition.append(node("span", "", "Approved source value"), node("code", "", presentation.rawValue));
    card.append(rawDefinition);
  }
  return card;
}

function renderCommands(snapshot) {
  const commands = snapshot.applied_commands;
  const effects = snapshot.applied_effects;
  elements.commandCount.textContent = commands.length + effects.length;
  elements.commandGrid.replaceChildren();
  if (commands.length === 0 && effects.length === 0) {
    elements.commandGrid.className = "command-grid empty-state";
    elements.commandGrid.append(node("p", "", "No approved command or fault effect applies to this snapshot."));
  } else {
    elements.commandGrid.className = "command-grid";
    for (const command of commands) elements.commandGrid.append(commandCard(command));
    for (const effect of effects) elements.commandGrid.append(commandCard(effect, true));
  }
  const unknownCount = snapshot.components.filter((component) => component.knowledge === "UNKNOWN").length;
  elements.unknownSummary.textContent = `${unknownCount} of ${snapshot.components.length} components remain UNKNOWN; no state is inferred for them.`;
}

function formatPoint(point) {
  if (!point) return "—";
  const label = point.label ? ` · ${point.label}` : "";
  return `${point.reference_id}${label}`;
}

function formatExpected(expected) {
  if (expected.nominal !== null) return formatValue(expected.nominal, expected.unit);
  if (expected.minimum !== null || expected.maximum !== null) {
    const minimum = expected.minimum ?? "—";
    const maximum = expected.maximum ?? "—";
    return `${minimum}–${maximum}${expected.unit ? ` ${expected.unit}` : ""}`;
  }
  return "Unknown";
}

function formatSources(sources) {
  return sources.map((source) => `${source.document_id} · p. ${source.page}`).join("; ") || "No source listed";
}

function validationLabel(source) {
  if (!source) return "Validation unavailable";
  if (source.validation_level === "LEVEL_4_TECHNICIAN_REVIEWED") return "Technician reviewed · accepted";
  if (source.validation_level === "LEVEL_5_INSTRUCTOR_VALIDATED") return "Instructor validated · accepted";
  if (source.validation_level === "LEVEL_6_MANUFACTURER_VERIFIED") return "Manufacturer verified · accepted";
  return `${humanize(source.validation_level)} · ${humanize(source.validation_outcome)}`;
}

function renderMeter(measurement) {
  if (!measurement) {
    elements.meterMode.textContent = "—";
    elements.meterReading.textContent = "Select test";
    elements.meterInterpretation.textContent = "No live or simulated reading is generated.";
    elements.meterPointA.textContent = "Select a diagnostic definition";
    elements.meterPointB.textContent = "Select a diagnostic definition";
    elements.meterName.textContent = "No test selected";
    elements.meterSafety.textContent = "Safety category unavailable";
    elements.meterValidation.textContent = "Validation unavailable";
    elements.meterManufacturer.textContent = "Manufacturer verification pending";
    elements.meterManufacturer.className = "pending-pill";
    elements.meterProcedure.textContent = "Choose an approved diagnostic test above.";
    elements.meterSource.textContent = "No source selected.";
    return;
  }
  const primarySource = measurement.sources[0];
  const manufacturerVerified = measurement.sources.every(
    (source) => source.validation_level === "LEVEL_6_MANUFACTURER_VERIFIED",
  );
  elements.meterMode.textContent = measurement.meter_mode;
  elements.meterReading.textContent = formatExpected(measurement.expected);
  elements.meterInterpretation.textContent = measurement.expected.interpretation || "No interpretation provided.";
  elements.meterPointA.textContent = formatPoint(measurement.point_a);
  elements.meterPointB.textContent = measurement.point_b ? formatPoint(measurement.point_b) : "Second point not specified";
  elements.meterName.textContent = measurement.name;
  elements.meterSafety.textContent = humanize(measurement.safety_category);
  elements.meterValidation.textContent = `${validationLabel(primarySource)} · ${primarySource?.reviewed_by || "reviewer unavailable"}`;
  elements.meterManufacturer.textContent = manufacturerVerified
    ? "Manufacturer verified"
    : "Manufacturer verification pending";
  elements.meterManufacturer.className = manufacturerVerified ? "verified-pill" : "pending-pill";
  elements.meterProcedure.textContent = measurement.procedure || "No procedure provided.";
  elements.meterSource.textContent = formatSources(measurement.sources);
}

function syncDiagnosticSelect(measurements) {
  elements.diagnosticSelect.replaceChildren();
  const prompt = document.createElement("option");
  prompt.value = "";
  prompt.textContent = measurements.length === 0 ? "No tests apply to this phase" : "Choose an approved test…";
  elements.diagnosticSelect.append(prompt);
  for (const measurement of measurements) {
    const option = document.createElement("option");
    option.value = measurement.measurement_id;
    option.textContent = measurement.name;
    elements.diagnosticSelect.append(option);
  }
  elements.diagnosticSelect.value = state.selectedMeasurementId || "";
  elements.diagnosticSelect.disabled = measurements.length === 0;
}

function selectMeasurement(measurementId) {
  state.selectedMeasurementId = state.availableMeasurements.some(
    (measurement) => measurement.measurement_id === measurementId,
  ) ? measurementId : null;
  renderDiagnostics(state.availableMeasurements);
}

function renderDiagnostics(measurements) {
  state.availableMeasurements = measurements;
  if (!measurements.some((measurement) => measurement.measurement_id === state.selectedMeasurementId)) {
    state.selectedMeasurementId = null;
  }
  elements.diagnosticCount.textContent = measurements.length;
  elements.diagnosticBody.replaceChildren();
  syncDiagnosticSelect(measurements);
  if (measurements.length === 0) {
    const row = document.createElement("tr");
    const cell = node("td", "table-empty", "No diagnostic definition applies to this phase.");
    cell.colSpan = 4;
    row.append(cell);
    elements.diagnosticBody.append(row);
    renderMeter(null);
    return;
  }
  for (const measurement of measurements) {
    const row = document.createElement("tr");
    const selected = measurement.measurement_id === state.selectedMeasurementId;
    if (selected) row.className = "selected-diagnostic";
    const name = document.createElement("td");
    const inspectButton = node("button", "diagnostic-name-button");
    inspectButton.type = "button";
    inspectButton.setAttribute("aria-label", `Inspect ${measurement.name}`);
    inspectButton.setAttribute("aria-pressed", String(selected));
    inspectButton.append(
      node("span", "diagnostic-test-name", measurement.name),
      node("span", "inspect-action", selected ? "Loaded ✓" : "Inspect test →"),
    );
    inspectButton.addEventListener("click", () => selectMeasurement(measurement.measurement_id));
    name.append(inspectButton, node("small", "", `${measurement.quantity} · ${measurement.signal_type}`));
    const points = document.createElement("td");
    points.append(node("strong", "", measurement.meter_mode), node("small", "", `${formatPoint(measurement.point_a)} ↔ ${formatPoint(measurement.point_b)}`));
    const expected = document.createElement("td");
    expected.append(node("strong", "expected-value", formatExpected(measurement.expected)), node("small", "", measurement.expected.interpretation || "No interpretation provided"));
    const safety = document.createElement("td");
    safety.append(node("span", "safety-label", measurement.safety_category.replaceAll("_", " ")), node("small", "", formatSources(measurement.sources)));
    row.append(name, points, expected, safety);
    elements.diagnosticBody.append(row);
  }
  renderMeter(
    measurements.find((measurement) => measurement.measurement_id === state.selectedMeasurementId) || null,
  );
}

async function updateSnapshot() {
  if (!state.definitions) return;
  clearError();
  const request = {
    power_available: elements.powerToggle.checked,
    operation_requested: elements.requestToggle.checked,
    operating_state_id: elements.phaseSelect.value || null,
    fault_codes: [...state.activeFaults],
  };
  try {
    const snapshot = await requestJson("/api/snapshot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    renderStatus(snapshot.status);
    renderCommands(snapshot);
    renderDiagnostics(snapshot.diagnostic_measurements);
  } catch (error) {
    showError(error.message);
    elements.statusBadge.textContent = "Stopped";
    elements.statusBadge.className = "status-badge status-fault";
  }
}

async function initialize() {
  try {
    state.definitions = await requestJson("/api/definitions");
    if (state.definitions.measurement_behavior !== "REFERENCE_DEFINITION_ONLY") {
      throw new Error("Unsupported measurement behavior; simulator stopped.");
    }
    populateModel(state.definitions.model);
    populatePhases(state.definitions.operating_states);
    renderFaults();
    for (const control of [elements.phaseSelect, elements.powerToggle, elements.requestToggle, elements.faultSearch]) {
      control.disabled = false;
    }
    elements.phaseSelect.addEventListener("change", () => {
      updatePhaseDescription();
      updateSnapshot();
    });
    elements.powerToggle.addEventListener("change", updateSnapshot);
    elements.requestToggle.addEventListener("change", updateSnapshot);
    elements.faultSearch.addEventListener("input", () => renderFaults(elements.faultSearch.value));
    elements.diagnosticSelect.addEventListener("change", () => selectMeasurement(elements.diagnosticSelect.value));
    updatePhaseDescription();
    await updateSnapshot();
  } catch (error) {
    showError(error.message);
    elements.statusBadge.textContent = "Unavailable";
    elements.statusBadge.className = "status-badge status-fault";
  }
}

initialize();
