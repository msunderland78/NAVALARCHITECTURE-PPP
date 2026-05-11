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
const legacyInButton = document.getElementById("legacy-in-button");
const printButton = document.getElementById("print-button");
const importFile = document.getElementById("import-file");
const importJsonFile = document.getElementById("import-json-file");
const importOutFile = document.getElementById("import-out-file");
const waterType = form.elements["water.type"];

const WATER_PRESETS = {
  salt_water_15_c: {
    density_kg_m3: 1025.87,
    kinematic_viscosity_m2_s: 0.00000118831
  },
  fresh_water_15_c: {
    density_kg_m3: 999.1026,
    kinematic_viscosity_m2_s: 0.0000011386
  }
};

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
  const payload = JSON.parse(await file.text());
  applyCase(payload.case || payload);
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
  oracle.innerHTML = "";
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
        pitch_diameter_ratio: null
      },
      appendages: {
        mode: data.get("appendages.mode"),
        percent_bare_hull_resistance: numberValue(data, "appendages.percent_bare_hull_resistance"),
        equivalent_wetted_area_form_factor_m2: numberValue(data, "appendages.equivalent_wetted_area_form_factor_m2")
      },
      modeling: {
        air_drag: data.get("modeling.air_drag") === "true",
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
  setValue("appendages.mode", caseData.appendages.mode || "percent_bare_hull_resistance");
  setValue("appendages.percent_bare_hull_resistance", caseData.appendages.percent_bare_hull_resistance);
  setValue("appendages.equivalent_wetted_area_form_factor_m2", caseData.appendages.equivalent_wetted_area_form_factor_m2 || 0);
  setValue("modeling.air_drag", String(caseData.modeling.air_drag));
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
  summary.innerHTML = [
    metric("CP", result.derived.prismatic_coefficient.toFixed(4)),
    metric("B/T", result.derived.beam_draft_ratio.toFixed(2)),
    metric("L/B", result.derived.lwl_beam_ratio.toFixed(2)),
    metric("LCB FP", `${formatNumber(result.derived.lcb_m_from_fp)} m`),
    metric("Disp", `${formatNumber(result.derived.displacement_mass_tonnes)} t`),
    metric("Awp", `${formatNumber(result.derived.waterplane_area_m2)} m2`),
    metric("Am", `${formatNumber(result.derived.midship_area_m2)} m2`),
    metric("L/V^(1/3)", result.derived.length_displacement_ratio.toFixed(2)),
    metric("Last RT", `${formatNumber(last.total_resistance_n / 1000)} kN`),
    metric("Applicability", failed.length === 0 ? "OK" : `${failed.length} warning`)
  ].join("");
}

function metric(label, value) {
  return `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`;
}

function renderEngineeringNote(result) {
  const statuses = [...new Set(result.speeds.map(row => row.resistance_status).filter(Boolean))];
  const statusText = statuses.length > 0 ? statuses.join(", ") : "not reported";
  engineeringNote.innerHTML = `
    <strong>Engineering review status</strong>
    <span>Preliminary resistance and powering estimate. Current calculation status: ${statusText}. Use with naval architect review and project-specific validation before design, procurement, or operational decisions.</span>
  `;
}

function renderChecks(result) {
  checks.innerHTML = result.applicability.map(item => {
    const className = item.ok ? "ok" : "warn";
    return `<div class="check ${className}"><strong>${item.label}</strong><span>${item.value.toFixed(4)} within ${item.lower} to ${item.upper}</span></div>`;
  }).join("");
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
    ["relative_rotative_efficiency", "etaRR"],
    ["resistance_status", "Status"]
  ];
  table.tHead.innerHTML = `<tr>${columns.map(column => `<th>${column[1]}</th>`).join("")}</tr>`;
  table.tBodies[0].innerHTML = result.speeds.map(row => {
    return `<tr>${columns.map(column => `<td>${formatCell(row[column[0]])}</td>`).join("")}</tr>`;
  }).join("");
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
    oracle.innerHTML = `<div class="oracle-empty">No matching speeds. Legacy: ${comparison.unmatched_legacy_speeds.join(", ")} Modern: ${comparison.unmatched_modern_speeds.join(", ")}</div>`;
    return;
  }
  const counts = comparison.summary ? comparison.summary.status_counts : {};
  const maxDelta = comparison.summary ? comparison.summary.max_absolute_delta : null;
  const maxRelativeDelta = comparison.summary ? comparison.summary.max_relative_delta : null;
  const maxDeltaText = maxDelta ? `${maxDelta.field} at ${formatCell(maxDelta.speed_knots)} kn: ${formatCell(maxDelta.absolute_delta)}` : "";
  const maxRelativeText = maxRelativeDelta ? `${maxRelativeDelta.field}: ${formatCell(maxRelativeDelta.absolute_relative_delta)}` : "";
  oracle.innerHTML = `
    <h2>Legacy OUT Comparison</h2>
    <div class="oracle-meta">
      <span>${comparison.matched_speed_count} matched speeds</span>
      <span>${counts.numeric_delta || 0} numeric deltas</span>
      <span>${counts.missing_modern || 0} missing modern fields</span>
      <span>${maxDeltaText}</span>
      <span>${maxRelativeText}</span>
    </div>
    <div class="oracle-table">
      <table>
        <thead><tr><th>V kn</th><th>Field</th><th>Legacy</th><th>Modern</th><th>Abs delta</th><th>Status</th></tr></thead>
        <tbody>${rows.map(row => `
          <tr>
            <td>${formatCell(row.speed_knots)}</td>
            <td>${row.field}</td>
            <td>${formatCell(row.legacy)}</td>
            <td>${formatCell(row.modern)}</td>
            <td>${formatCell(row.delta)}</td>
            <td>${row.status}</td>
          </tr>
        `).join("")}</tbody>
      </table>
    </div>
  `;
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

function renderPlot(result) {
  const ctx = plot.getContext("2d");
  const width = plot.width;
  const height = plot.height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, width, height);
  const margin = {left: 68, right: 28, top: 24, bottom: 46};
  const rows = result.speeds;
  const maxRt = Math.max(...rows.map(row => row.total_resistance_n));
  const maxPe = Math.max(...rows.map(row => row.effective_power_kw));
  const minSpeed = Math.min(...rows.map(row => row.speed_knots));
  const maxSpeed = Math.max(...rows.map(row => row.speed_knots));
  drawAxes(ctx, width, height, margin);
  drawLine(ctx, rows, margin, width, height, minSpeed, maxSpeed, maxRt, "total_resistance_n", "#0f766e");
  drawLine(ctx, rows, margin, width, height, minSpeed, maxSpeed, maxPe, "effective_power_kw", "#334155", true);
  ctx.fillStyle = "#0f766e";
  ctx.fillText("RT N", width - 110, 26);
  ctx.fillStyle = "#334155";
  ctx.fillText("PE kW", width - 58, 26);
}

function drawAxes(ctx, width, height, margin) {
  ctx.strokeStyle = "#9aa6b2";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(margin.left, margin.top);
  ctx.lineTo(margin.left, height - margin.bottom);
  ctx.lineTo(width - margin.right, height - margin.bottom);
  ctx.stroke();
  ctx.fillStyle = "#5d6975";
  ctx.font = "12px Arial";
  ctx.fillText("Speed, kn", width / 2 - 28, height - 12);
}

function drawLine(ctx, rows, margin, width, height, minSpeed, maxSpeed, maxValue, key, color, dashed = false) {
  const xSpan = Math.max(maxSpeed - minSpeed, 1);
  const ySpan = Math.max(maxValue, 1);
  ctx.strokeStyle = color;
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
}

runCase();
