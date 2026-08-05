"use strict";

const state = {
  definitions: null,
  activeFaults: new Set(),
  availableMeasurements: [],
  selectedMeasurementId: null,
  selectedPathId: null,
  caseId: null,
  caseCreatedAt: null,
  caseResults: [],
  caseSnapshot: null,
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
  topologyCount: document.querySelector("#topology-count"),
  topologyView: document.querySelector("#topology-view"),
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
  caseStatus: document.querySelector("#case-status"),
  caseEmpty: document.querySelector("#case-empty"),
  caseWorkspace: document.querySelector("#case-workspace"),
  casePathSelect: document.querySelector("#case-path-select"),
  caseTitle: document.querySelector("#case-title"),
  caseComplaint: document.querySelector("#case-complaint"),
  caseFaults: document.querySelector("#case-faults"),
  caseSafetyList: document.querySelector("#case-safety-list"),
  caseSafetyAck: document.querySelector("#case-safety-ack"),
  caseTestName: document.querySelector("#case-test-name"),
  caseTestSafety: document.querySelector("#case-test-safety"),
  caseRationale: document.querySelector("#case-rationale"),
  caseTestDetails: document.querySelector("#case-test-details"),
  caseMeterMode: document.querySelector("#case-meter-mode"),
  caseTestPoints: document.querySelector("#case-test-points"),
  caseExpected: document.querySelector("#case-expected"),
  caseProcedureBlock: document.querySelector("#case-procedure-block"),
  caseProcedure: document.querySelector("#case-procedure"),
  caseResultEntry: document.querySelector("#case-result-entry"),
  caseResultSelect: document.querySelector("#case-result-select"),
  caseResultNumber: document.querySelector("#case-result-number"),
  caseTechnician: document.querySelector("#case-technician"),
  caseEvaluate: document.querySelector("#case-evaluate"),
  caseOutcome: document.querySelector("#case-outcome"),
  caseEvaluation: document.querySelector("#case-evaluation"),
  caseGuidance: document.querySelector("#case-guidance"),
  caseActualResult: document.querySelector("#case-actual-result"),
  caseExpectedResult: document.querySelector("#case-expected-result"),
  caseEvidenceType: document.querySelector("#case-evidence-type"),
  caseRecordedBy: document.querySelector("#case-recorded-by"),
  caseRecordMeta: document.querySelector("#case-record-meta"),
  caseSource: document.querySelector("#case-source"),
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

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const WIRE_COLORS = {
  BLACK: "#8fa4ae",
  RED: "#ff7d7d",
  YELLOW: "#f4d35e",
  BLUE: "#6ca8ff",
  GREEN: "#8ee5a4",
  WHITE: "#dce8eb",
};

function svgNode(tagName, attributes = {}, text) {
  const value = document.createElementNS(SVG_NAMESPACE, tagName);
  for (const [name, attributeValue] of Object.entries(attributes)) {
    value.setAttribute(name, String(attributeValue));
  }
  if (text !== undefined) value.textContent = text;
  return value;
}

function truncate(value, maximum = 38) {
  if (!value || value.length <= maximum) return value || "Unknown";
  return `${value.slice(0, maximum - 1)}…`;
}

function topologySources(topology) {
  const sources = new Map();
  for (const group of Object.values(topology)) {
    for (const record of group) {
      for (const assertion of record.provenance || []) {
        const source = assertion.source || {};
        const validation = assertion.validation || {};
        const key = `${source.document_id}:${source.page}`;
        sources.set(key, {
          label: `${source.document_id || "Unknown document"} · p. ${source.page || "—"}`,
          reviewer: validation.reviewed_by,
          level: validation.level,
          outcome: validation.outcome,
        });
      }
    }
  }
  return [...sources.values()];
}

function endpointDefinition(nodeId, pinsByNode, connectorsById, nodesById) {
  const pin = pinsByNode.get(nodeId);
  const connector = pin ? connectorsById.get(pin.connector_id) : null;
  const nodeRecord = nodesById.get(nodeId);
  return {
    title: connector ? connector.label : nodeRecord?.label || nodeId,
    terminal: pin ? `Terminal ${pin.pin_number}` : humanize(nodeRecord?.node_type || "unknown node"),
    signalType: pin?.signal_type || nodeRecord?.node_type || "UNKNOWN",
    wireColor: pin?.wire_color || null,
  };
}

function topologyStat(label, value) {
  const item = node("span", "topology-stat");
  item.append(node("strong", "", value), node("small", "", label));
  return item;
}

function renderTopology(topology) {
  const connectors = topology.connectors || [];
  const pins = topology.pins || [];
  const nodes = topology.nodes || [];
  const connections = topology.connections || [];
  elements.topologyCount.textContent = connections.length;
  elements.topologyView.replaceChildren();
  if (connectors.length === 0 && pins.length === 0 && nodes.length === 0 && connections.length === 0) {
    elements.topologyView.className = "topology-view empty-state";
    elements.topologyView.append(node("p", "", "No approved topology extension loaded."));
    return;
  }

  elements.topologyView.className = "topology-view";
  const summary = node("div", "topology-summary");
  summary.append(
    topologyStat("connectors", connectors.length),
    topologyStat("terminals", pins.length),
    topologyStat("nodes", nodes.length),
    topologyStat("explicit wires", connections.length),
  );

  const connectorsById = new Map(connectors.map((record) => [record.connector_id, record]));
  const nodesById = new Map(nodes.map((record) => [record.node_id, record]));
  const pinsByNode = new Map(pins.filter((record) => record.node_id).map((record) => [record.node_id, record]));
  const endpointNodeIds = new Set();
  const rowHeight = 86;
  const svgHeight = Math.max(180, connections.length * rowHeight + 30);
  const svg = svgNode("svg", {
    viewBox: `0 0 960 ${svgHeight}`,
    role: "img",
    "aria-labelledby": "topology-svg-title topology-svg-description",
  });
  svg.append(
    svgNode("title", {id: "topology-svg-title"}, "Approved electrical connection topology"),
    svgNode(
      "desc",
      {id: "topology-svg-description"},
      "Reference-only map of explicit technician-reviewed node-to-node connections. It does not calculate electrical state.",
    ),
  );

  connections.forEach((connection, index) => {
    endpointNodeIds.add(connection.from_node_id);
    endpointNodeIds.add(connection.to_node_id);
    const from = endpointDefinition(connection.from_node_id, pinsByNode, connectorsById, nodesById);
    const to = endpointDefinition(connection.to_node_id, pinsByNode, connectorsById, nodesById);
    const y = index * rowHeight + 15;
    const lineY = y + 29;
    const wireColor = WIRE_COLORS[from.wireColor] || WIRE_COLORS[to.wireColor] || "#8fa4ae";
    const group = svgNode("g", {class: "topology-wire-row"});
    group.append(
      svgNode("title", {}, `${connection.connection_id}: ${connection.from_node_id} to ${connection.to_node_id}`),
      svgNode("rect", {x: 20, y, width: 280, height: 58, rx: 10, class: "topology-endpoint"}),
      svgNode("rect", {x: 660, y, width: 280, height: 58, rx: 10, class: "topology-endpoint"}),
      svgNode("line", {x1: 300, y1: lineY, x2: 660, y2: lineY, stroke: wireColor, class: "topology-wire"}),
      svgNode("circle", {cx: 300, cy: lineY, r: 5, fill: wireColor}),
      svgNode("circle", {cx: 660, cy: lineY, r: 5, fill: wireColor}),
      svgNode("text", {x: 34, y: y + 22, class: "topology-endpoint-title"}, truncate(from.title)),
      svgNode("text", {x: 34, y: y + 43, class: "topology-endpoint-detail"}, from.terminal),
      svgNode("text", {x: 674, y: y + 22, class: "topology-endpoint-title"}, truncate(to.title)),
      svgNode("text", {x: 674, y: y + 43, class: "topology-endpoint-detail"}, to.terminal),
      svgNode("text", {x: 480, y: y + 20, class: "topology-signal", "text-anchor": "middle"}, humanize(from.signalType)),
      svgNode(
        "text",
        {x: 480, y: y + 48, class: "topology-wire-label", "text-anchor": "middle"},
        from.wireColor ? `${humanize(from.wireColor)} conductor` : "Color not documented",
      ),
    );
    svg.append(group);
  });

  const stage = node("div", "topology-stage");
  stage.append(svg);
  const metadata = node("div", "topology-metadata");
  const unconnected = nodes.filter((record) => !endpointNodeIds.has(record.node_id));
  const boundary = node("div", "topology-boundary");
  boundary.append(node("span", "detail-label", "Bounded nodes without mapped connection"));
  if (unconnected.length === 0) {
    boundary.append(node("p", "", "No explicit standalone node is present in this bounded slice."));
  } else {
    const list = node("div", "topology-node-list");
    for (const record of unconnected) {
      const definition = endpointDefinition(record.node_id, pinsByNode, connectorsById, nodesById);
      const item = node("span", "topology-node-chip");
      item.append(node("strong", "", definition.title), node("small", "", definition.terminal));
      list.append(item);
    }
    boundary.append(list, node("p", "topology-boundary-note", "No unreviewed bonding or downstream connectivity is inferred."));
  }

  const traceability = node("div", "topology-traceability");
  traceability.append(node("span", "detail-label", "Approval and traceability"));
  const sources = topologySources(topology);
  if (sources.length === 0) {
    traceability.append(node("p", "", "Approved source metadata unavailable."));
  } else {
    traceability.append(
      node("p", "", sources.map((source) => source.label).join("; ")),
      node("small", "", `${humanize(sources[0].level)} · ${humanize(sources[0].outcome)} · ${sources[0].reviewer || "Reviewer unavailable"}`),
    );
  }
  metadata.append(boundary, traceability);
  elements.topologyView.append(summary, stage, metadata);
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

function formatSources(...sourceGroups) {
  const labelsBySource = new Map();
  for (const source of sourceGroups.flat()) {
    const key = `${source.document_id}:${source.page}`;
    labelsBySource.set(key, `${source.document_id} · p. ${source.page}`);
  }
  return [...labelsBySource.values()].join("; ") || "No source listed";
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

function selectedCasePath() {
  return state.definitions?.diagnostic_paths.find((path) => path.path_id === state.selectedPathId) || null;
}

function caseStep(path, stepId) {
  return path?.steps.find((step) => step.step_id === stepId) || null;
}

function caseExpected(expected) {
  if (expected.result_kind === "QUALITATIVE") return humanize(expected.qualitative_value);
  if (expected.minimum !== null || expected.maximum !== null) {
    const minimum = expected.minimum ?? "—";
    const maximum = expected.maximum ?? "—";
    return `${minimum}–${maximum} ${expected.unit}`;
  }
  return formatValue(expected.nominal, expected.unit);
}

function caseResultOptions(expectedValue) {
  const pairs = {
    CONTINUITY: ["CONTINUITY", "NO_CONTINUITY", "UNKNOWN"],
    NO_CONTINUITY: ["NO_CONTINUITY", "CONTINUITY", "UNKNOWN"],
    OPEN: ["OPEN", "CLOSED", "UNKNOWN"],
    CLOSED: ["CLOSED", "OPEN", "UNKNOWN"],
    PRESENT: ["PRESENT", "ABSENT", "UNKNOWN"],
    ABSENT: ["ABSENT", "PRESENT", "UNKNOWN"],
  };
  return pairs[expectedValue] || [expectedValue, "OTHER", "UNKNOWN"];
}

function formatCaseResult(result) {
  if (result.result_kind === "QUALITATIVE") return humanize(result.qualitative_value);
  return formatValue(result.numeric_value, result.unit);
}

function renderCaseStatus(caseState) {
  const presentations = {
    SAFETY_ACKNOWLEDGEMENT_REQUIRED: ["Safety acknowledgement required", "status-power"],
    AWAITING_RESULT: ["Awaiting technician result", "status-operation"],
    NEXT_TEST_AVAILABLE: ["Next approved test available", "status-operation"],
    COMPLETE: ["Bounded path complete", "status-idle"],
    ESCALATION_REQUIRED: ["Escalation required", "status-fault"],
    STOPPED: ["Case stopped", "status-fault"],
  };
  const [label, className] = presentations[caseState] || ["Case unavailable", "status-loading"];
  elements.caseStatus.textContent = label;
  elements.caseStatus.className = `status-badge ${className}`;
}

function populateCasePaths(paths) {
  elements.casePathSelect.replaceChildren();
  const prompt = document.createElement("option");
  prompt.value = "";
  prompt.textContent = "Choose an approved path…";
  elements.casePathSelect.append(prompt);
  for (const path of paths) {
    const option = document.createElement("option");
    option.value = path.path_id;
    option.textContent = path.title;
    elements.casePathSelect.append(option);
  }
  const hasPaths = paths.length > 0;
  elements.caseEmpty.hidden = hasPaths;
  elements.caseWorkspace.hidden = !hasPaths;
  elements.casePathSelect.disabled = !hasPaths;
  if (!hasPaths) {
    elements.caseStatus.textContent = "No approved path loaded";
    elements.caseStatus.className = "status-badge status-loading";
  }
}

function renderCasePath(path) {
  elements.caseTitle.textContent = path?.title || "Select a path";
  elements.caseComplaint.textContent = path?.complaint_summary || "No complaint selected.";
  elements.caseFaults.replaceChildren();
  elements.caseSafetyList.replaceChildren();
  if (!path) return;
  for (const code of path.entry_fault_codes) {
    elements.caseFaults.append(node("span", "case-fault-chip", code));
  }
  for (const acknowledgement of path.safety_acknowledgements) {
    const item = node("div", "case-safety-item");
    item.append(
      node("strong", "", humanize(acknowledgement.safety_category)),
      node("span", "", acknowledgement.label),
    );
    elements.caseSafetyList.append(item);
  }
  elements.caseSource.textContent = formatSources(path.sources);
}

function prepareResultControl(step) {
  const expected = step.expected_result;
  elements.caseResultSelect.replaceChildren();
  if (expected.result_kind === "QUALITATIVE") {
    const prompt = document.createElement("option");
    prompt.value = "";
    prompt.textContent = "Choose the actual observed result…";
    elements.caseResultSelect.append(prompt);
    for (const value of caseResultOptions(expected.qualitative_value)) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = humanize(value);
      elements.caseResultSelect.append(option);
    }
    elements.caseResultSelect.hidden = false;
    elements.caseResultNumber.hidden = true;
    elements.caseResultNumber.value = "";
  } else {
    elements.caseResultSelect.hidden = true;
    elements.caseResultNumber.hidden = false;
    elements.caseResultNumber.value = "";
    elements.caseResultNumber.placeholder = `Enter actual ${expected.unit}`;
  }
}

function renderCaseStep(path, step, allowEntry) {
  if (!step) {
    elements.caseTestDetails.hidden = true;
    elements.caseProcedureBlock.hidden = true;
    elements.caseResultEntry.hidden = true;
    return;
  }
  const measurement = step.measurement;
  elements.caseTestName.textContent = measurement.name;
  elements.caseTestSafety.textContent = humanize(measurement.safety_category);
  elements.caseRationale.textContent = step.rationale;
  elements.caseMeterMode.textContent = measurement.meter_mode;
  elements.caseTestPoints.textContent = `${formatPoint(measurement.point_a)} ↔ ${formatPoint(measurement.point_b)}`;
  elements.caseExpected.textContent = caseExpected(step.expected_result);
  elements.caseProcedure.textContent = measurement.procedure || "No approved procedure is available.";
  elements.caseTestDetails.hidden = false;
  elements.caseProcedureBlock.hidden = false;
  elements.caseResultEntry.hidden = !allowEntry;
  elements.caseSource.textContent = formatSources(path.sources, measurement.sources);
  if (allowEntry) prepareResultControl(step);
}

function renderCaseSnapshot(snapshot) {
  state.caseSnapshot = snapshot;
  const path = selectedCasePath();
  renderCaseStatus(snapshot.state);
  elements.caseOutcome.hidden = snapshot.evaluation === null;
  if (snapshot.evaluation !== null) {
    const evaluatedStep = caseStep(path, snapshot.evaluation.step_id);
    const latestResult = snapshot.results.at(-1);
    elements.caseEvaluation.textContent = humanize(snapshot.evaluation.outcome);
    elements.caseGuidance.textContent = snapshot.guidance || "No additional guidance is available.";
    elements.caseActualResult.textContent = formatCaseResult(latestResult);
    elements.caseExpectedResult.textContent = caseExpected(evaluatedStep.expected_result);
    elements.caseEvidenceType.textContent = humanize(latestResult.source_type);
    elements.caseRecordedBy.textContent = latestResult.recorded_by;
    elements.caseRecordMeta.textContent = `${snapshot.case_id} · ${latestResult.recorded_at} · Packages: ${snapshot.knowledge_package_ids.join(", ")}`;
  }
  if (snapshot.state === "SAFETY_ACKNOWLEDGEMENT_REQUIRED") {
    elements.caseTestName.textContent = "Safety acknowledgement required";
    elements.caseTestSafety.textContent = "Unavailable";
    elements.caseRationale.textContent = "The procedure remains hidden until the required safety acknowledgement is recorded.";
    renderCaseStep(path, null, false);
    return;
  }
  const currentStep = caseStep(path, snapshot.current_step_id);
  const evaluatedStep = caseStep(path, snapshot.evaluation?.step_id);
  renderCaseStep(path, currentStep || evaluatedStep, currentStep !== null);
}

function newCaseIdentity() {
  const createdAt = new Date().toISOString();
  state.caseId = `CASE-${Date.now()}`;
  state.caseCreatedAt = createdAt;
  state.caseResults = [];
  state.caseSnapshot = null;
}

async function updateCase(results = state.caseResults) {
  const path = selectedCasePath();
  if (!path || !state.caseId) return;
  clearError();
  const request = {
    case_id: state.caseId,
    path_id: path.path_id,
    mode: "FIELD",
    fault_codes: path.entry_fault_codes,
    safety_acknowledged: elements.caseSafetyAck.checked,
    results,
    created_at: state.caseCreatedAt,
    updated_at: new Date().toISOString(),
  };
  try {
    const snapshot = await requestJson("/api/case", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    state.caseResults = results;
    renderCaseSnapshot(snapshot);
  } catch (error) {
    showError(error.message);
    elements.caseStatus.textContent = "Case stopped";
    elements.caseStatus.className = "status-badge status-fault";
  }
}

async function selectCasePath(pathId) {
  state.selectedPathId = pathId || null;
  newCaseIdentity();
  elements.caseSafetyAck.checked = false;
  elements.caseSafetyAck.disabled = !state.selectedPathId;
  elements.caseOutcome.hidden = true;
  const path = selectedCasePath();
  renderCasePath(path);
  if (path) await updateCase();
}

async function submitCaseResult() {
  const path = selectedCasePath();
  const step = caseStep(path, state.caseSnapshot?.current_step_id);
  const technician = elements.caseTechnician.value.trim();
  if (!path || !step) return;
  if (!technician) {
    showError("Recorded by is required before evaluating a technician-entered result.");
    elements.caseTechnician.focus();
    return;
  }
  const expected = step.expected_result;
  let numericValue = null;
  let qualitativeValue = null;
  if (expected.result_kind === "QUALITATIVE") {
    qualitativeValue = elements.caseResultSelect.value;
    if (!qualitativeValue) {
      showError("Choose the actual observed result before evaluation.");
      elements.caseResultSelect.focus();
      return;
    }
  } else {
    if (elements.caseResultNumber.value === "") {
      showError("Enter the actual numeric result before evaluation.");
      elements.caseResultNumber.focus();
      return;
    }
    numericValue = Number(elements.caseResultNumber.value);
  }
  const recordedAt = new Date().toISOString();
  const result = {
    result_id: `${state.caseId}:result:${state.caseResults.length + 1}`,
    step_id: step.step_id,
    measurement_id: step.measurement_id,
    source_type: "TECHNICIAN_ENTRY",
    result_kind: expected.result_kind,
    numeric_value: numericValue,
    qualitative_value: qualitativeValue,
    unit: expected.unit,
    recorded_by: technician,
    recorded_at: recordedAt,
    notes: null,
  };
  await updateCase([...state.caseResults, result]);
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
    if (state.definitions.topology_behavior !== "REFERENCE_DEFINITION_ONLY") {
      throw new Error("Unsupported topology behavior; simulator stopped.");
    }
    if (state.definitions.diagnostic_case_behavior !== "TECHNICIAN_ENTRY_DETERMINISTIC_EVALUATION") {
      throw new Error("Unsupported diagnostic case behavior; application stopped.");
    }
    populateModel(state.definitions.model);
    populatePhases(state.definitions.operating_states);
    populateCasePaths(state.definitions.diagnostic_paths);
    renderFaults();
    renderTopology(state.definitions.topology);
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
    elements.casePathSelect.addEventListener("change", () => selectCasePath(elements.casePathSelect.value));
    elements.caseSafetyAck.addEventListener("change", () => {
      state.caseResults = [];
      updateCase();
    });
    elements.caseEvaluate.addEventListener("click", submitCaseResult);
    updatePhaseDescription();
    await updateSnapshot();
  } catch (error) {
    showError(error.message);
    elements.statusBadge.textContent = "Unavailable";
    elements.statusBadge.className = "status-badge status-fault";
  }
}

initialize();
