const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

const {validateImportedCase, waterPresetMismatch, niceScale, WATER_PRESETS} = require(path.join(__dirname, "..", "pure.js"));

function validCase() {
  return {
    project: {name: "Example", run_id: "Run-1"},
    speed_sweep: {initial_speed_knots: 15, speed_increment_knots: 2},
    hull: {lwl_m: 212},
    features: {stern_type: "normal_shaped_sections"},
    propulsion: {type: "single_screw_conventional_stern"},
    appendages: {mode: "percent_bare_hull_resistance"},
    modeling: {air_drag: true},
    water: {type: "salt_water_15_c", density_kg_m3: 1025.87, kinematic_viscosity_m2_s: 1.18831e-6},
    margin: {design_margin_percent: 5}
  };
}

test("validateImportedCase accepts a complete case", () => {
  assert.equal(validateImportedCase(validCase()), null);
});

test("validateImportedCase rejects non-object input", () => {
  assert.equal(validateImportedCase(null), "case must be a JSON object");
  assert.equal(validateImportedCase("not an object"), "case must be a JSON object");
  assert.equal(validateImportedCase([]), "case must be a JSON object");
});

test("validateImportedCase rejects missing sections", () => {
  for (const section of ["project", "hull", "modeling", "water", "margin"]) {
    const caseData = validCase();
    delete caseData[section];
    assert.equal(validateImportedCase(caseData), `case.${section} must be an object`);
  }
});

test("validateImportedCase rejects bad section types", () => {
  const caseData = validCase();
  caseData.hull = "not an object";
  assert.equal(validateImportedCase(caseData), "case.hull must be an object");
});

test("validateImportedCase rejects missing project strings", () => {
  const caseData = validCase();
  caseData.project.name = 42;
  assert.equal(validateImportedCase(caseData), "case.project.name and case.project.run_id must be strings");
});

test("validateImportedCase rejects non-boolean air_drag", () => {
  const caseData = validCase();
  caseData.modeling.air_drag = "yes";
  assert.equal(validateImportedCase(caseData), "case.modeling.air_drag must be a boolean");
});

test("waterPresetMismatch returns null for matching preset", () => {
  const water = {type: "salt_water_15_c", density_kg_m3: 1025.87, kinematic_viscosity_m2_s: 0.00000118831};
  assert.equal(waterPresetMismatch(water), null);
});

test("waterPresetMismatch returns null for custom water type", () => {
  const water = {type: "custom", density_kg_m3: 1000, kinematic_viscosity_m2_s: 1e-6};
  assert.equal(waterPresetMismatch(water), null);
});

test("waterPresetMismatch flags density drift", () => {
  const water = {type: "salt_water_15_c", density_kg_m3: 1010.0, kinematic_viscosity_m2_s: 0.00000118831};
  const result = waterPresetMismatch(water);
  assert.ok(result);
  assert.match(result, /salt_water_15_c/);
});

test("waterPresetMismatch flags viscosity drift", () => {
  const water = {type: "fresh_water_15_c", density_kg_m3: 999.1026, kinematic_viscosity_m2_s: 1.5e-6};
  const result = waterPresetMismatch(water);
  assert.ok(result);
});

test("niceScale handles a typical resistance magnitude", () => {
  const scale = niceScale(610052);
  assert.equal(scale.max, 1000000);
  assert.deepEqual(scale.ticks, [0, 200000, 400000, 600000, 800000, 1000000]);
});

test("niceScale handles small numbers", () => {
  const scale = niceScale(0.04);
  assert.equal(scale.max, 0.05);
  assert.equal(scale.ticks.length, 6);
});

test("niceScale handles zero gracefully", () => {
  const scale = niceScale(0);
  assert.equal(scale.max, 1);
  assert.equal(scale.ticks.length, 5);
});

test("niceScale handles non-finite input gracefully", () => {
  const scale = niceScale(Infinity);
  assert.equal(scale.max, 1);
  const nan = niceScale(NaN);
  assert.equal(nan.max, 1);
});

test("WATER_PRESETS exports salt and fresh water entries", () => {
  assert.ok(WATER_PRESETS.salt_water_15_c);
  assert.ok(WATER_PRESETS.fresh_water_15_c);
});
