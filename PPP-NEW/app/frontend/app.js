const form = document.getElementById("case-form");
const statusBox = document.getElementById("status");
const summary = document.getElementById("summary");
const table = document.getElementById("results-table");
const plot = document.getElementById("plot");
const csvButton = document.getElementById("csv-button");

let lastPayload = null;

form.addEventListener("submit", async event => {
  event.preventDefault();
  await runCase();
});

csvButton.addEventListener("click", async () => {
  const payload = buildPayload();
  const response = await fetch("/api/export/csv", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  const text = await response.text();
  const blob = new Blob([text], {type: "text/csv"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ppp-results.csv";
  link.click();
  URL.revokeObjectURL(url);
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
  lastPayload = payload;
  renderSummary(result);
  renderTable(result);
  renderPlot(result);
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
        mode: "percent_bare_hull_resistance",
        percent_bare_hull_resistance: numberValue(data, "appendages.percent_bare_hull_resistance")
      },
      modeling: {
        air_drag: data.get("modeling.air_drag") === "true",
        depth_at_bow_m: numberValue(data, "modeling.depth_at_bow_m"),
        deckhouse_cargo_frontal_area_m2: numberValue(data, "modeling.deckhouse_cargo_frontal_area_m2"),
        wetted_surface_mode: "user",
        wetted_surface_m2: numberValue(data, "modeling.wetted_surface_m2"),
        half_angle_entrance_mode: "user",
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

function numberValue(data, key) {
  return Number(data.get(key));
}

function renderSummary(result) {
  const last = result.speeds[result.speeds.length - 1];
  const failed = result.applicability.filter(item => !item.ok);
  summary.innerHTML = [
    metric("CP", result.derived.prismatic_coefficient.toFixed(4)),
    metric("B/T", result.derived.beam_draft_ratio.toFixed(2)),
    metric("Last RT", `${formatNumber(last.total_resistance_n / 1000)} kN`),
    metric("Applicability", failed.length === 0 ? "OK" : `${failed.length} warning`)
  ].join("");
}

function metric(label, value) {
  return `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`;
}

function renderTable(result) {
  const columns = [
    ["speed_knots", "V kn"],
    ["froude_number", "Fn"],
    ["friction_coefficient", "CF"],
    ["frictional_resistance_n", "RF N"],
    ["appendage_resistance_n", "RAPP N"],
    ["total_resistance_n", "RT N"],
    ["effective_power_kw", "PE kW"],
    ["resistance_status", "Status"]
  ];
  table.tHead.innerHTML = `<tr>${columns.map(column => `<th>${column[1]}</th>`).join("")}</tr>`;
  table.tBodies[0].innerHTML = result.speeds.map(row => {
    return `<tr>${columns.map(column => `<td>${formatCell(row[column[0]])}</td>`).join("")}</tr>`;
  }).join("");
}

function formatCell(value) {
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
