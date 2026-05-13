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

const REQUIRED_CASE_SECTIONS = ["project", "speed_sweep", "hull", "features", "propulsion", "appendages", "modeling", "water", "margin"];

function validateImportedCase(caseData) {
  if (!caseData || typeof caseData !== "object" || Array.isArray(caseData)) {
    return "case must be a JSON object";
  }
  for (const section of REQUIRED_CASE_SECTIONS) {
    if (!caseData[section] || typeof caseData[section] !== "object" || Array.isArray(caseData[section])) {
      return `case.${section} must be an object`;
    }
  }
  if (typeof caseData.project.name !== "string" || typeof caseData.project.run_id !== "string") {
    return "case.project.name and case.project.run_id must be strings";
  }
  if (typeof caseData.modeling.air_drag !== "boolean") {
    return "case.modeling.air_drag must be a boolean";
  }
  return null;
}

function waterPresetMismatch(water, presets) {
  presets = presets || WATER_PRESETS;
  const preset = presets[water.type];
  if (!preset) {
    return null;
  }
  const densityOff = Math.abs(water.density_kg_m3 - preset.density_kg_m3) > 1e-3;
  const viscosityOff = Math.abs(water.kinematic_viscosity_m2_s - preset.kinematic_viscosity_m2_s) > 1e-3 * preset.kinematic_viscosity_m2_s;
  if (!densityOff && !viscosityOff) {
    return null;
  }
  return `Imported water.type "${water.type}" but density or viscosity differs from preset; using the imported values.`;
}

function niceScale(maxValue) {
  if (!isFinite(maxValue) || maxValue <= 0) {
    return {max: 1, ticks: [0, 0.25, 0.5, 0.75, 1]};
  }
  const exponent = Math.floor(Math.log10(maxValue));
  const fraction = maxValue / Math.pow(10, exponent);
  let niceFraction;
  if (fraction <= 1) {
    niceFraction = 1;
  } else if (fraction <= 2) {
    niceFraction = 2;
  } else if (fraction <= 5) {
    niceFraction = 5;
  } else {
    niceFraction = 10;
  }
  const niceMax = niceFraction * Math.pow(10, exponent);
  const tickCount = 5;
  const ticks = [];
  for (let i = 0; i <= tickCount; i++) {
    ticks.push(niceMax * i / tickCount);
  }
  return {max: niceMax, ticks};
}

if (typeof module !== "undefined") {
  module.exports = {validateImportedCase, waterPresetMismatch, niceScale, WATER_PRESETS, REQUIRED_CASE_SECTIONS};
}
