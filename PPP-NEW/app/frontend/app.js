const form = document.getElementById("case-form");
const statusBox = document.getElementById("status");
const summary = document.getElementById("summary");
const engineeringNote = document.getElementById("engineering-note");
const checks = document.getElementById("checks");
const table = document.getElementById("results-table");
const plot = document.getElementById("plot");
const oracle = document.getElementById("oracle");
const caseJsonButton = document.getElementById("case-json-button");
const csvButton = document.getElementById("csv-button");
const jsonButton = document.getElementById("json-button");
const reportButton = document.getElementById("report-button");
const legacyInButton = document.getElementById("legacy-in-button");
const printButton = document.getElementById("print-button");
const importFile = document.getElementById("import-file");
const importJsonFile = document.getElementById("import-json-file");
const importOutFile = document.getElementById("import-out-file");
const waterType = form.elements["water.type"];

let lastPayload = null;

form.addEventListener("submit", async event => {
  event.preventDefault();
  await runCase();
});

waterType.addEventListener("change", () => {
  const preset = WATER_PRESETS[waterType.value];
  if (!preset) {
    return;
  }
  setValue("water.density_kg_m3", preset.density_kg_m3);
  setValue("water.kinematic_viscosity_m2_s", preset.kinematic_viscosity_m2_s);
});

caseJsonButton.addEventListener("click", () => {
  downloadText(JSON.stringify(buildPayload(), null, 2), "ppp-case.json", "application/json");
});

csvButton.addEventListener("click", async () => {
  const payload = buildPayload();
  const response = await fetch("/api/export/csv", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  const text = await response.text();
  if (!response.ok) {
    statusBox.textContent = text || "CSV export failed";
    return;
  }
  downloadText(text, "ppp-results.csv", "text/csv");
});

jsonButton.addEventListener("click", async () => {
  const response = await fetch("/api/export/json", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(buildPayload())
  });
  const payload = await response.json();
  if (!response.ok) {
    statusBox.textContent = payload.error || "Export failed";
    return;
  }
  downloadText(JSON.stringify(payload, null, 2), "ppp-results.json", "application/json");
});

reportButton.addEventListener("click", async () => {
  const response = await fetch("/api/export/report.md", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(buildPayload())
  });
  const text = await response.text();
  if (!response.ok) {
    statusBox.textContent = text || "Report export failed";
    return;
  }
  downloadText(text, "ppp-engineering-report.md", "text/markdown");
});

legacyInButton.addEventListener("click", async () => {
  const payload = buildPayload();
  const options = buildLegacyOptions();
  if (Object.keys(options).length > 0) {
    payload.options = options;
  }
  const response = await fetch("/api/export/legacy-in-candidate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  const text = await response.text();
  if (!response.ok) {
    statusBox.textContent = text || "Legacy IN export failed";
    return;
  }
  downloadText(text, "PPP-candidate.IN", "text/plain");
});

printButton.addEventListener("click", () => {
  window.print();
});

function downloadText(text, filename, type) {
  const blob = new Blob([text], {type});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

importJsonFile.addEventListener("change", async () => {
  const file = importJsonFile.files[0];
  if (!file) {
    return;
  }
  let payload = null;
  try {
    payload = JSON.parse(await file.text());
  } catch (error) {
    statusBox.textContent = "Import JSON failed: invalid JSON";
    importJsonFile.value = "";
    return;
  }
  const caseData = payload && (payload.case || payload);
  const validationError = validateImportedCase(caseData);
  if (validationError) {
    statusBox.textContent = `Import JSON failed: ${validationError}`;
    importJsonFile.value = "";
    return;
  }
  applyCase(caseData);
  if (payload.point_count) {
    setValue("point_count", payload.point_count);
  }
  statusBox.textContent = "Imported";
  await runCase();
  importJsonFile.value = "";
});


importFile.addEventListener("change", async () => {
  const file = importFile.files[0];
  if (!file) {
    return;
  }
  statusBox.textContent = "Importing";
  const response = await fetch("/api/import/ppp", {
    method: "POST",
    body: await file.arrayBuffer()
  });
  const imported = await response.json();
  if (!response.ok) {
    statusBox.textContent = imported.error || "Import failed";
    importFile.value = "";
    return;
  }
  applyCase(imported);
  statusBox.textContent = "Imported";
  await runCase();
  importFile.value = "";
});

importOutFile.addEventListener("change", async () => {
  const file = importOutFile.files[0];
  if (!file) {
    return;
  }
  statusBox.textContent = "Comparing";
  const body = buildPayload();
  const speedTolerance = legacySpeedTolerance();
  if (speedTolerance !== null) {
    body.speed_tolerance = speedTolerance;
  }
  body.legacy_out_text = await file.text();
  body.fields = [
    "frictional_resistance_n",
    "rf_form_resistance_n",
    "appendage_resistance_n",
    "wave_resistance_n",
    "bulb_resistance_n",
    "transom_resistance_n",
    "total_resistance_n",
    "effective_power_kw",
    "required_thrust_n"
  ];
  const response = await fetch("/api/compare/out", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const comparison = await response.json();
  if (!response.ok) {
    statusBox.textContent = comparison.error || "Compare failed";
    importOutFile.value = "";
    return;
  }
  renderOracleComparison(comparison);
  statusBox.textContent = `Compared ${comparison.matched_speed_count} speeds`;
  importOutFile.value = "";
});

async function runCase() {
  statusBox.textContent = "Running";
  const payload = buildPayload();
  const response = await fetch("/api/evaluate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  const result = await response.json();
  if (!response.ok) {
    statusBox.textContent = result.error || "Run failed";
    return;
  }
  lastPayload = payload;
  renderSummary(result);
  renderEngineeringNote(result);
  renderChecks(result);
  renderTable(result);
  renderPlot(result);
  oracle.replaceChildren();
  statusBox.textContent = result.applicability.every(item => item.ok) ? "Complete" : "Check inputs";
}

function buildPayload() {
  const data = new FormData(form);
  return {
    point_count: numberValue(data, "point_count"),
    case: {
      schema: "navarch.ppp.case",
      version: 1,
      project: {
        name: data.get("project.name"),
        run_id: data.get("project.run_id")
      },
      speed_sweep: {
        initial_speed_knots: numberValue(data, "speed_sweep.initial_speed_knots"),
        speed_increment_knots: numberValue(data, "speed_sweep.speed_increment_knots"),
        status: "user"
      },
      hull: {
        lwl_m: numberValue(data, "hull.lwl_m"),
        beam_lwl_m: numberValue(data, "hull.beam_lwl_m"),
        draft_forward_m: numberValue(data, "hull.draft_forward_m"),
        draft_aft_m: numberValue(data, "hull.draft_aft_m"),
        block_coefficient: numberValue(data, "hull.block_coefficient"),
        midship_coefficient: numberValue(data, "hull.midship_coefficient"),
        waterplane_coefficient: numberValue(data, "hull.waterplane_coefficient"),
        lcb_percent_lwl_from_midships_forward_positive: numberValue(data, "hull.lcb_percent_lwl_from_midships_forward_positive")
      },
      features: {
        bulb_area_station_0_m2: numberValue(data, "features.bulb_area_station_0_m2"),
        bulb_vertical_center_m: numberValue(data, "features.bulb_vertical_center_m"),
        transom_immersed_area_zero_speed_m2: numberValue(data, "features.transom_immersed_area_zero_speed_m2"),
        stern_type: data.get("features.stern_type")
      },
      propulsion: {
        type: data.get("propulsion.type"),
        propeller_diameter_m: numberValue(data, "propulsion.propeller_diameter_m"),
        expanded_area_ratio: numberValue(data, "propulsion.expanded_area_ratio"),
        pitch_diameter_ratio: optionalNumberValue(data, "propulsion.pitch_diameter_ratio")
      },
      appendages: {
        mode: data.get("appendages.mode"),
        percent_bare_hull_resistance: numberValue(data, "appendages.percent_bare_hull_resistance"),
        equivalent_wetted_area_form_factor_m2: numberValue(data, "appendages.equivalent_wetted_area_form_factor_m2")
      },
      modeling: {
        air_drag: data.get("modeling.air_drag") === "true",
        air_drag_coefficient: numberValue(data, "modeling.air_drag_coefficient"),
        depth_at_bow_m: numberValue(data, "modeling.depth_at_bow_m"),
        deckhouse_cargo_frontal_area_m2: numberValue(data, "modeling.deckhouse_cargo_frontal_area_m2"),
        wetted_surface_mode: data.get("modeling.wetted_surface_mode"),
        wetted_surface_m2: numberValue(data, "modeling.wetted_surface_m2"),
        half_angle_entrance_mode: data.get("modeling.half_angle_entrance_mode"),
        half_angle_entrance_degrees: numberValue(data, "modeling.half_angle_entrance_degrees")
      },
      water: {
        type: data.get("water.type"),
        density_kg_m3: numberValue(data, "water.density_kg_m3"),
        kinematic_viscosity_m2_s: numberValue(data, "water.kinematic_viscosity_m2_s")
      },
      margin: {
        design_margin_percent: numberValue(data, "margin.design_margin_percent")
      }
    }
  };
}

function applyCase(caseData) {
  setValue("project.name", caseData.project.name);
  setValue("project.run_id", caseData.project.run_id);
  setValue("speed_sweep.initial_speed_knots", caseData.speed_sweep.initial_speed_knots);
  setValue("speed_sweep.speed_increment_knots", caseData.speed_sweep.speed_increment_knots);
  setValue("hull.lwl_m", caseData.hull.lwl_m);
  setValue("hull.beam_lwl_m", caseData.hull.beam_lwl_m);
  setValue("hull.draft_forward_m", caseData.hull.draft_forward_m);
  setValue("hull.draft_aft_m", caseData.hull.draft_aft_m);
  setValue("hull.block_coefficient", caseData.hull.block_coefficient);
  setValue("hull.midship_coefficient", caseData.hull.midship_coefficient);
  setValue("hull.waterplane_coefficient", caseData.hull.waterplane_coefficient);
  setValue("hull.lcb_percent_lwl_from_midships_forward_positive", caseData.hull.lcb_percent_lwl_from_midships_forward_positive);
  setValue("features.bulb_area_station_0_m2", caseData.features.bulb_area_station_0_m2);
  setValue("features.bulb_vertical_center_m", caseData.features.bulb_vertical_center_m);
  setValue("features.transom_immersed_area_zero_speed_m2", caseData.features.transom_immersed_area_zero_speed_m2);
  setValue("features.stern_type", caseData.features.stern_type);
  setValue("propulsion.type", caseData.propulsion.type);
  setValue("propulsion.propeller_diameter_m", caseData.propulsion.propeller_diameter_m);
  setValue("propulsion.expanded_area_ratio", caseData.propulsion.expanded_area_ratio);
  if (caseData.propulsion.pitch_diameter_ratio !== null && caseData.propulsion.pitch_diameter_ratio !== undefined) {
    setValue("propulsion.pitch_diameter_ratio", caseData.propulsion.pitch_diameter_ratio);
  }
  setValue("appendages.mode", caseData.appendages.mode || "percent_bare_hull_resistance");
  setValue("appendages.percent_bare_hull_resistance", caseData.appendages.percent_bare_hull_resistance);
  setValue("appendages.equivalent_wetted_area_form_factor_m2", caseData.appendages.equivalent_wetted_area_form_factor_m2 || 0);
  setValue("modeling.air_drag", String(caseData.modeling.air_drag));
  if (caseData.modeling.air_drag_coefficient !== undefined && caseData.modeling.air_drag_coefficient !== null) {
    setValue("modeling.air_drag_coefficient", caseData.modeling.air_drag_coefficient);
  }
  setValue("modeling.depth_at_bow_m", caseData.modeling.depth_at_bow_m);
  setValue("modeling.deckhouse_cargo_frontal_area_m2", caseData.modeling.deckhouse_cargo_frontal_area_m2);
  setValue("modeling.wetted_surface_mode", caseData.modeling.wetted_surface_mode || "user");
  setValue("modeling.wetted_surface_m2", caseData.modeling.wetted_surface_m2);
  setValue("modeling.half_angle_entrance_mode", caseData.modeling.half_angle_entrance_mode || "user");
  setValue("modeling.half_angle_entrance_degrees", caseData.modeling.half_angle_entrance_degrees);
  setValue("water.type", caseData.water.type);
  setValue("water.density_kg_m3", caseData.water.density_kg_m3);
  setValue("water.kinematic_viscosity_m2_s", caseData.water.kinematic_viscosity_m2_s);
  setValue("margin.design_margin_percent", caseData.margin.design_margin_percent);
  const presetMismatch = waterPresetMismatch(caseData.water);
  if (presetMismatch) {
    statusBox.textContent = presetMismatch;
  }
}


function setValue(name, value) {
  const field = form.elements[name];
  if (field && value !== null && value !== undefined) {
    field.value = value;
  }
}

function numberValue(data, key) {
  return Number(data.get(key));
}

function optionalNumberValue(data, key) {
  const value = data.get(key);
  return value === "" || value === null ? null : Number(value);
}

function buildLegacyOptions() {
  const data = new FormData(form);
  const values = {
    first_record_order: data.get("legacy_options.first_record_order") || null,
    propeller_record_order: data.get("legacy_options.propeller_record_order") || null,
    stern_correction: optionalNumberValue(data, "legacy_options.stern_correction"),
    pitch_diameter_ratio: optionalNumberValue(data, "legacy_options.pitch_diameter_ratio"),
    water_type_code: optionalNumberValue(data, "legacy_options.water_type_code"),
    appendage_primary_value: optionalNumberValue(data, "legacy_options.appendage_primary_value"),
    appendage_model_total: optionalNumberValue(data, "legacy_options.appendage_model_total")
  };
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== null));
}

function legacySpeedTolerance() {
  const value = new FormData(form).get("legacy_options.speed_tolerance");
  return value === "" || value === null ? null : Number(value);
}

function renderSummary(result) {
  const last = result.speeds[result.speeds.length - 1];
  const failed = result.applicability.filter(item => !item.ok);
  const metrics = [
    ["CP", result.derived.prismatic_coefficient.toFixed(4)],
    ["B/T", result.derived.beam_draft_ratio.toFixed(2)],
    ["L/B", result.derived.lwl_beam_ratio.toFixed(2)],
    ["LCB FP", `${formatNumber(result.derived.lcb_m_from_fp)} m`],
    ["Disp", `${formatNumber(result.derived.displacement_mass_tonnes)} t`],
    ["Awp", `${formatNumber(result.derived.waterplane_area_m2)} m2`],
    ["Am", `${formatNumber(result.derived.midship_area_m2)} m2`],
    ["L/V^(1/3)", result.derived.length_displacement_ratio.toFixed(2)],
    ["Last RT", `${formatNumber(last.total_resistance_n / 1000)} kN`],
    ["Applicability", failed.length === 0 ? "OK" : `${failed.length} warning`]
  ];
  replaceChildren(summary, metrics.map(([label, value]) => metricNode(label, value)));
}

function metricNode(label, value) {
  const wrap = document.createElement("div");
  wrap.className = "metric";
  wrap.append(textElement("span", label), textElement("strong", value));
  return wrap;
}

function renderEngineeringNote(result) {
  const review = result.engineering_review || {};
  const statuses = Array.isArray(review.statuses) ? review.statuses : (review.status ? [review.status] : []);
  const statusText = statuses.length ? statuses.join(", ") : "not reported";
  const note = review.note || "Preliminary resistance and powering estimate. Use with naval architect review and project-specific validation before design, procurement, or operational decisions.";
  const children = [
    textElement("strong", "Engineering review status"),
    textElement("span", `${note} Current calculation status: ${statusText}.`)
  ];
  const warnings = Array.isArray(review.warnings) ? review.warnings : [];
  if (warnings.length) {
    const list = document.createElement("ul");
    for (const warning of warnings) {
      list.append(textElement("li", warning));
    }
    children.push(list);
  }
  replaceChildren(engineeringNote, children);
}

function renderChecks(result) {
  const nodes = result.applicability.map(item => {
    const wrap = document.createElement("div");
    wrap.className = `check ${item.ok ? "ok" : "warn"}`;
    wrap.append(
      textElement("strong", item.label),
      textElement("span", `${item.value.toFixed(4)} within ${item.lower} to ${item.upper}`)
    );
    return wrap;
  });
  replaceChildren(checks, nodes);
}

function renderTable(result) {
  const columns = [
    ["speed_knots", "V kn"],
    ["speed_mps", "V m/s"],
    ["froude_number", "Fn"],
    ["speed_length_ratio", "SLR"],
    ["friction_coefficient", "CF"],
    ["residual_resistance_coefficient", "CR"],
    ["correlation_allowance_coefficient", "CA"],
    ["appendage_mode", "Appendage"],
    ["frictional_resistance_n", "RF N"],
    ["rf_form_resistance_n", "RF*K1 N"],
    ["appendage_resistance_n", "RAPP N"],
    ["wave_resistance_n", "RW N"],
    ["bulb_resistance_n", "RB N"],
    ["transom_resistance_n", "RTR N"],
    ["correlation_allowance_resistance_n", "RA N"],
    ["air_resistance_n", "RAIR N"],
    ["total_resistance_n", "RT N"],
    ["effective_power_kw", "PE kW"],
    ["wake_fraction", "w"],
    ["thrust_deduction", "t"],
    ["required_thrust_n", "REQ.THR N"],
    ["hull_efficiency", "etaH"],
    ["relative_rotative_efficiency", "etaRR"]
  ];
  const headRow = document.createElement("tr");
  for (const [, label] of columns) {
    headRow.append(textElement("th", label));
  }
  replaceChildren(table.tHead, [headRow]);
  const bodyRows = result.speeds.map(row => {
    const tr = document.createElement("tr");
    for (const [key] of columns) {
      tr.append(textElement("td", formatCell(row[key])));
    }
    return tr;
  });
  replaceChildren(table.tBodies[0], bodyRows);
}

function renderOracleComparison(comparison) {
  const rows = comparison.comparisons.flatMap(speedRow => {
    return speedRow.fields.map(field => {
      return {
        speed_knots: speedRow.speed_knots,
        field: field.field,
        legacy: field.legacy,
        modern: field.modern,
        delta: field.absolute_delta,
        status: field.status
      };
    });
  });
  if (rows.length === 0) {
    const empty = document.createElement("div");
    empty.className = "oracle-empty";
    empty.textContent = `No matching speeds. Legacy: ${comparison.unmatched_legacy_speeds.join(", ")} Modern: ${comparison.unmatched_modern_speeds.join(", ")}`;
    replaceChildren(oracle, [empty]);
    return;
  }
  const counts = comparison.summary ? comparison.summary.status_counts : {};
  const maxDelta = comparison.summary ? comparison.summary.max_absolute_delta : null;
  const maxRelativeDelta = comparison.summary ? comparison.summary.max_relative_delta : null;
  const maxDeltaText = maxDelta ? `${maxDelta.field} at ${formatCell(maxDelta.speed_knots)} kn: ${formatCell(maxDelta.absolute_delta)}` : "";
  const maxRelativeText = maxRelativeDelta ? `${maxRelativeDelta.field}: ${formatCell(maxRelativeDelta.absolute_relative_delta)}` : "";
  const heading = textElement("h2", "Legacy OUT Comparison");
  const printNotice = document.createElement("div");
  printNotice.className = "oracle-print-notice";
  printNotice.textContent = "Excluded from printed engineering report by design. Use the JSON or CSV export to attach legacy diagnostics.";
  const meta = document.createElement("div");
  meta.className = "oracle-meta";
  meta.append(
    textElement("span", `${comparison.matched_speed_count} matched speeds`),
    textElement("span", `${counts.numeric_delta || 0} numeric deltas`),
    textElement("span", `${counts.missing_modern || 0} missing modern fields`),
    textElement("span", maxDeltaText),
    textElement("span", maxRelativeText)
  );
  const tableWrap = document.createElement("div");
  tableWrap.className = "oracle-table";
  const tableNode = document.createElement("table");
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const header of ["V kn", "Field", "Legacy", "Modern", "Abs delta", "Status"]) {
    headerRow.append(textElement("th", header));
  }
  thead.append(headerRow);
  const tbody = document.createElement("tbody");
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.append(
      textElement("td", formatCell(row.speed_knots)),
      textElement("td", row.field),
      textElement("td", formatCell(row.legacy)),
      textElement("td", formatCell(row.modern)),
      textElement("td", formatCell(row.delta)),
      textElement("td", row.status)
    );
    tbody.append(tr);
  }
  tableNode.append(thead, tbody);
  tableWrap.append(tableNode);
  replaceChildren(oracle, [heading, printNotice, meta, tableWrap]);
}

function textElement(tag, text) {
  const node = document.createElement(tag);
  node.textContent = text == null ? "" : String(text);
  return node;
}

function replaceChildren(parent, children) {
  parent.replaceChildren(...children);
}

function formatCell(value) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "number") {
    return Math.abs(value) >= 1000 ? formatNumber(value) : value.toFixed(4);
  }
  return value;
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", {maximumFractionDigits: 2}).format(value);
}

let lastPlotState = null;

function renderPlot(result) {
  const ctx = plot.getContext("2d");
  const width = plot.width;
  const height = plot.height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, width, height);
  const margin = {left: 78, right: 78, top: 30, bottom: 50};
  const rows = result.speeds;
  if (rows.length === 0) {
    lastPlotState = null;
    return;
  }
  const maxRt = Math.max(...rows.map(row => row.total_resistance_n));
  const maxPe = Math.max(...rows.map(row => row.effective_power_kw));
  const minSpeed = Math.min(...rows.map(row => row.speed_knots));
  const maxSpeed = Math.max(...rows.map(row => row.speed_knots));
  const rtScale = niceScale(maxRt);
  const peScale = niceScale(maxPe);
  drawGrid(ctx, width, height, margin, rtScale.ticks, minSpeed, maxSpeed, rows);
  drawAxes(ctx, width, height, margin, rtScale, peScale, minSpeed, maxSpeed);
  drawLine(ctx, rows, margin, width, height, minSpeed, maxSpeed, rtScale.max, "total_resistance_n", "#0f766e");
  drawLine(ctx, rows, margin, width, height, minSpeed, maxSpeed, peScale.max, "effective_power_kw", "#334155", true);
  drawLegend(ctx, width);
  lastPlotState = {rows, margin, width, height, minSpeed, maxSpeed, rtMax: rtScale.max, peMax: peScale.max};
}


function drawGrid(ctx, width, height, margin, ticks, minSpeed, maxSpeed, rows) {
  ctx.strokeStyle = "#e2e8f0";
  ctx.lineWidth = 1;
  const plotBottom = height - margin.bottom;
  for (const tick of ticks) {
    const y = plotBottom - (tick / ticks[ticks.length - 1]) * (plotBottom - margin.top);
    ctx.beginPath();
    ctx.moveTo(margin.left, y);
    ctx.lineTo(width - margin.right, y);
    ctx.stroke();
  }
  const xTicks = rows.length;
  if (xTicks > 1) {
    for (let i = 0; i < rows.length; i++) {
      const x = margin.left + (rows[i].speed_knots - minSpeed) / Math.max(maxSpeed - minSpeed, 1) * (width - margin.left - margin.right);
      ctx.beginPath();
      ctx.moveTo(x, margin.top);
      ctx.lineTo(x, plotBottom);
      ctx.stroke();
    }
  }
}

function drawAxes(ctx, width, height, margin, rtScale, peScale, minSpeed, maxSpeed) {
  ctx.strokeStyle = "#9aa6b2";
  ctx.lineWidth = 1;
  const plotBottom = height - margin.bottom;
  ctx.beginPath();
  ctx.moveTo(margin.left, margin.top);
  ctx.lineTo(margin.left, plotBottom);
  ctx.lineTo(width - margin.right, plotBottom);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(width - margin.right, margin.top);
  ctx.lineTo(width - margin.right, plotBottom);
  ctx.stroke();
  ctx.fillStyle = "#5d6975";
  ctx.font = "11px Arial";
  ctx.textAlign = "right";
  for (let i = 0; i < rtScale.ticks.length; i++) {
    const tick = rtScale.ticks[i];
    const y = plotBottom - (tick / rtScale.max) * (plotBottom - margin.top);
    ctx.fillText(formatAxisTick(tick), margin.left - 6, y + 4);
  }
  ctx.textAlign = "left";
  for (let i = 0; i < peScale.ticks.length; i++) {
    const tick = peScale.ticks[i];
    const y = plotBottom - (tick / peScale.max) * (plotBottom - margin.top);
    ctx.fillText(formatAxisTick(tick), width - margin.right + 6, y + 4);
  }
  ctx.textAlign = "center";
  const xTickCount = 5;
  for (let i = 0; i <= xTickCount; i++) {
    const speedTick = minSpeed + (maxSpeed - minSpeed) * i / xTickCount;
    const x = margin.left + i / xTickCount * (width - margin.left - margin.right);
    ctx.fillText(speedTick.toFixed(1), x, plotBottom + 16);
  }
  ctx.font = "12px Arial";
  ctx.fillText("Speed, kn", width / 2, height - 14);
  ctx.save();
  ctx.translate(18, height / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillStyle = "#0f766e";
  ctx.fillText("RT, N", 0, 0);
  ctx.restore();
  ctx.save();
  ctx.translate(width - 18, height / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillStyle = "#334155";
  ctx.fillText("PE, kW", 0, 0);
  ctx.restore();
}

function formatAxisTick(value) {
  if (value === 0) {
    return "0";
  }
  if (Math.abs(value) >= 1000) {
    return formatNumber(value);
  }
  return value.toFixed(1);
}

function drawLegend(ctx, width) {
  ctx.font = "12px Arial";
  ctx.textAlign = "left";
  ctx.fillStyle = "#0f766e";
  ctx.fillText("— RT", width / 2 - 50, 20);
  ctx.fillStyle = "#334155";
  ctx.fillText("--- PE", width / 2 + 4, 20);
}

function drawLine(ctx, rows, margin, width, height, minSpeed, maxSpeed, maxValue, key, color, dashed = false) {
  const xSpan = Math.max(maxSpeed - minSpeed, 1);
  const ySpan = Math.max(maxValue, 1);
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;
  ctx.setLineDash(dashed ? [7, 5] : []);
  ctx.beginPath();
  rows.forEach((row, index) => {
    const x = margin.left + (row.speed_knots - minSpeed) / xSpan * (width - margin.left - margin.right);
    const y = height - margin.bottom - row[key] / ySpan * (height - margin.top - margin.bottom);
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();
  ctx.setLineDash([]);
  rows.forEach(row => {
    const x = margin.left + (row.speed_knots - minSpeed) / xSpan * (width - margin.left - margin.right);
    const y = height - margin.bottom - row[key] / ySpan * (height - margin.top - margin.bottom);
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
  });
}

plot.addEventListener("mousemove", event => {
  if (!lastPlotState) {
    return;
  }
  const rect = plot.getBoundingClientRect();
  const scaleX = plot.width / rect.width;
  const scaleY = plot.height / rect.height;
  const mx = (event.clientX - rect.left) * scaleX;
  const my = (event.clientY - rect.top) * scaleY;
  const {rows, margin, width, height, minSpeed, maxSpeed, rtMax, peMax} = lastPlotState;
  const xSpan = Math.max(maxSpeed - minSpeed, 1);
  let nearest = null;
  let nearestDx = Infinity;
  for (const row of rows) {
    const x = margin.left + (row.speed_knots - minSpeed) / xSpan * (width - margin.left - margin.right);
    const dx = Math.abs(mx - x);
    if (dx < nearestDx) {
      nearestDx = dx;
      nearest = {row, x};
    }
  }
  if (!nearest || nearestDx > 40 || my < margin.top || my > height - margin.bottom) {
    renderPlot({speeds: lastPlotState.rows});
    return;
  }
  renderPlot({speeds: lastPlotState.rows});
  const ctx = plot.getContext("2d");
  ctx.strokeStyle = "#94a3b8";
  ctx.setLineDash([3, 3]);
  ctx.beginPath();
  ctx.moveTo(nearest.x, margin.top);
  ctx.lineTo(nearest.x, height - margin.bottom);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "rgba(23, 33, 43, 0.92)";
  const label = `${nearest.row.speed_knots.toFixed(1)} kn  RT ${formatNumber(nearest.row.total_resistance_n)} N  PE ${formatNumber(nearest.row.effective_power_kw)} kW`;
  ctx.font = "11px Arial";
  ctx.textAlign = "left";
  const textWidth = ctx.measureText(label).width + 12;
  const tooltipX = Math.min(nearest.x + 8, width - textWidth - 4);
  ctx.fillRect(tooltipX, margin.top + 4, textWidth, 20);
  ctx.fillStyle = "#ffffff";
  ctx.fillText(label, tooltipX + 6, margin.top + 18);
});

plot.addEventListener("mouseleave", () => {
  if (lastPlotState) {
    renderPlot({speeds: lastPlotState.rows});
  }
});

runCase();
