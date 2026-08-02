"use strict";

const state = {
  definitions: null,
  activeFaults: new Set(),
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
  const card = node("article", `command-card${effect ? " effect-card" : ""}`);
  card.append(node("span", "component-id", effect ? record.target_id : record.component_id));
  const detail = node("div", "command-value");
  detail.append(
    node("span", "", record.property.replaceAll("_", " ")),
    node("strong", "", formatValue(record.value, record.unit)),
  );
  card.append(detail);
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

function renderDiagnostics(measurements) {
  elements.diagnosticCount.textContent = measurements.length;
  elements.diagnosticBody.replaceChildren();
  if (measurements.length === 0) {
    const row = document.createElement("tr");
    const cell = node("td", "table-empty", "No diagnostic definition applies to this phase.");
    cell.colSpan = 4;
    row.append(cell);
    elements.diagnosticBody.append(row);
    return;
  }
  for (const measurement of measurements) {
    const row = document.createElement("tr");
    const name = document.createElement("td");
    name.append(node("strong", "", measurement.name), node("small", "", `${measurement.quantity} · ${measurement.signal_type}`));
    const points = document.createElement("td");
    points.append(node("strong", "", measurement.meter_mode), node("small", "", `${formatPoint(measurement.point_a)} ↔ ${formatPoint(measurement.point_b)}`));
    const expected = document.createElement("td");
    expected.append(node("strong", "expected-value", formatExpected(measurement.expected)), node("small", "", measurement.expected.interpretation || "No interpretation provided"));
    const safety = document.createElement("td");
    safety.append(node("span", "safety-label", measurement.safety_category.replaceAll("_", " ")), node("small", "", formatSources(measurement.sources)));
    row.append(name, points, expected, safety);
    elements.diagnosticBody.append(row);
  }
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
    updatePhaseDescription();
    await updateSnapshot();
  } catch (error) {
    showError(error.message);
    elements.statusBadge.textContent = "Unavailable";
    elements.statusBadge.className = "status-badge status-fault";
  }
}

initialize();
