# HALTROP-PAPER-PLAN.md — D4 Implementation Plan

Date: 2026-05-13
Owner: Claude (Opus 4.7)
Source papers: `PPP-NEW/Paper/Holtrop_Approximate_1982_OCR.md`, `PPP-NEW/Paper/Holtrop_Resistance_and_Propulsion_1984_OCR.md`

This plan covers CLAUDE-PLAN item **D4** (propulsion factors for non-conventional propulsion types) plus two genuine bug fixes the papers exposed during cross-check. It is the source-of-truth document for the work, including the resolved design decisions.

---

## 1. What the two papers together tell us

The 1984 reanalysis only updates **single-screw conventional stern** formulas. For multiple-screw ships and open-stern single-screw ships, the 1984 paper explicitly defers to the 1982 paper (Section 3, lines 286-288 of the OCR):

> "For multiple-screw ships and open-stern single-screw ships with open shafts the formulae of [1] were maintained."

Reference [1] is **Holtrop & Mennen, 1982** — `Holtrop_Approximate_1982_OCR.md`. That paper, Section 3 page 4, carries the formulas this codebase has been missing.

### Twin-screw (1982 paper, lines 444-449)

```
w   = 0.3095·C_B + 10·C_V·C_B - 0.23·D/√(B·T)
t   = 0.325·C_B - 0.1885·D/√(B·T)
η_R = 0.9737 + 0.111·(C_P - 0.0225·lcb) - 0.06325·(P/D)
```

### Single-screw open-stern (1982 paper, lines 434-435)

```
w   = 0.3·C_P + 10·C_V·C_P - 0.1
t   = 0.10        (constant)
η_R = 0.98        (constant)
```

The paper labels the open-stern formula "tentative" and "based on only a very limited number of model data" (lines 437-438). The twin-screw set is more established.

### Symbol reference

| Symbol | Meaning |
|---|---|
| `C_B` | Block coefficient |
| `C_P` | Prismatic coefficient |
| `C_V` | Viscous resistance coefficient = (1+k)·C_F + C_A |
| `D` | Propeller diameter |
| `B` | Beam on waterline |
| `T` | Mean moulded draught |
| `lcb` | Longitudinal centre of buoyancy, percent of L, + forward of amidships |
| `P/D` | Pitch-to-diameter ratio |

---

## 2. Design decisions

| # | Question | Decision | Rationale |
|---|---|---|---|
| 1 | How to handle missing `P/D` for twin-screw cases? | **Option (b): default to 1.0 silently** | Tool always produces a number. Default is mid-range for typical hulls. Active value surfaced in output so users can detect that they're seeing a defaulted result. |
| 2 | Split `resistance_status` to reflect validation level by propulsion type? | **Yes** | Carries the validation truth all the way to CSV/JSON/markdown. Captured-oracle case keeps its existing label so its pinned fixture doesn't shift. |

### Resistance status labels after this change

| Propulsion type | New `resistance_status` value | Validation source |
|---|---|---|
| `single_screw_conventional_stern` | `partial_source_safe_components` | Captured PPPFTRN.EXE oracle, <100 N at every speed |
| `twin_screw` | `partial_source_safe_unvalidated_propulsion_twin_screw` | 1982 paper formulas, no legacy oracle yet |
| `single_screw_open_flow_stern` | `partial_source_safe_unvalidated_propulsion_open_stern` | 1982 paper formulas, labelled tentative by the paper authors |

---

## 3. Implementation steps

### Step 1 — turn `holtrop_propulsion_factors` into a dispatcher

`core.py` currently has one branch for single-screw conventional stern and a guard that returns `None` for everything else. After this step:

- `single_screw_conventional_stern` → existing branch, unchanged. Already oracle-validated.
- `twin_screw` → new branch using the 1982 twin-screw formulas above.
- `single_screw_open_flow_stern` → new branch using the 1982 open-stern formulas above.

All three branches return numeric `wake_fraction`, `thrust_deduction`, `hull_efficiency`, `relative_rotative_efficiency`. `required_thrust_n` returns to being numeric for all three types.

### Step 2 — P/D default for twin-screw

```python
pitch_diameter_ratio = propulsion.get("pitch_diameter_ratio") or 1.0
```

Surface the active value in `result["propulsion"]["active_pitch_diameter_ratio"]` (new field) so users can tell when the default kicked in.

Validation stays as today: if user supplies P/D, it must be non-negative finite. If absent, the default applies.

### Step 3 — per-row `resistance_status` reflects validation level

`resistance_components()` in `core.py` currently hardcodes `"resistance_status": "partial_source_safe_components"`. Change to compute the status from the propulsion type (see table in §2).

This means `engineering_review.statuses` will also pick up the new labels via the existing aggregation path.

### Step 4 — engineering review wording

The current `NONCONVENTIONAL_PROPULSION_WARNING` says factors are "not reported for this propulsion type." Replace with type-specific wording:

- Twin-screw: "Twin-screw propulsion factors use the 1982 Holtrop & Mennen formulas. Numerical results are produced, but they have not yet been validated against a captured PPPFTRN.EXE oracle run."
- Open-stern: "Single-screw open-stern propulsion factors use the 1982 Holtrop & Mennen formulas. The paper itself describes these as tentative, based on a limited data set. Validation against a captured PPPFTRN.EXE oracle is pending."

### Step 5 — add the P/D field to the frontend

`index.html` Propulsion section gets a new input:

```html
<label>P/D<input name="propulsion.pitch_diameter_ratio" type="number" min="0" step="0.001" placeholder="auto"></label>
```

`app.js` `buildPayload` sends the parsed value when non-empty, omits it when empty. `applyCase` populates it when present in the incoming case JSON.

### Step 6 — tests

New regression tests in `test_ppp_core.py`:

- `test_twin_screw_propulsion_factors_numeric` — assert all four propulsion-factor fields and `required_thrust_n` are finite numbers; check `resistance_status == "partial_source_safe_unvalidated_propulsion_twin_screw"`.
- `test_twin_screw_uses_pitch_diameter_default_when_missing` — assert behavior with no P/D in case; check `result["propulsion"]["active_pitch_diameter_ratio"] == 1.0`.
- `test_twin_screw_uses_supplied_pitch_diameter` — assert behavior with explicit P/D = 1.2; check that value appears in active output and that η_R is the expected value.
- `test_open_stern_propulsion_factors_constants` — assert `t == 0.10` and `relative_rotative_efficiency == 0.98` exactly; assert `wake_fraction` matches the formula; check `resistance_status == "partial_source_safe_unvalidated_propulsion_open_stern"`.
- `test_open_stern_uses_open_stern_status_label`.

Plus synthetic regression fixtures:

- `tests/fixtures/synthetic_twin_screw_case.json` + `synthetic_twin_screw_result.json` — copy of the captured sample with `propulsion.type = "twin_screw"` and an explicit `pitch_diameter_ratio = 1.0`.
- `tests/fixtures/synthetic_open_stern_case.json` + `synthetic_open_stern_result.json` — same with `propulsion.type = "single_screw_open_flow_stern"`.

These pin the new code paths against future drift. Fixtures README updated to flag them as **synthetic, not oracle-validated**.

### Step 7 — non-goals for this pass

Deliberately out of scope:

- Propeller cavitation (1984 paper Section 4). Formulas exist in the paper; future feature.
- Partial propeller submergence (1984 paper Section 4). Same.
- Capturing twin-screw / open-stern oracles via `PPPFTRN.EXE` under Wine. That's a follow-up validation pass the user can run when ready. The status labels make it explicit which propulsion types are still pending oracle confirmation.

---

## 4. Separate bug fixes the papers exposed

Both verifiable against the existing captured single-screw oracle.

### 4a. Pram-with-gondola C_stern is wrong in our code

1984 paper line 88 shows the stern-correction table with progression `pram with gondola: -25`, `V-shaped: -10`, `normal: 0`, `U-shaped with Hogner: +10`. Our `core.py:8-13` STERN_CORRECTIONS maps `pram_with_gondola → +10`. That contradicts the paper.

The earlier CLAUDE-PLAN A2 fix mistakenly aligned legacy_in.py to the wrong value. Both files need to read `-25` for pram-with-gondola. The captured oracle is unaffected (sample uses `normal_shaped_sections`).

### 4b. T_A vs mean draft in propulsion factor formulas

1982 paper line 360 wake fraction formula uses `L/T_A` and `c_8` definition (line 374) uses `B/T_A`. Our `core.py` uses mean draft in both places. In the captured sample `T_F = T_A = 11 m`, so the discrepancy doesn't show up against the oracle. For any vessel with trim it would.

Fix: pass `draft_aft_m` into `holtrop_c8` and the wake-fraction call site instead of mean draft. Re-run the captured-oracle regression to confirm we still match to <100 N.

---

## 5. Validation strategy

| Layer | What it confirms |
|---|---|
| Existing oracle regression test | Single-screw conventional stern still agrees with `PPPFTRN.EXE` to <100 N after the T_A fix. If this drifts the fix is wrong. |
| New synthetic fixtures | Twin-screw and open-stern output is locked against silent code drift. Not a correctness oracle. |
| Hand-calculated assertions in unit tests | Spot-check at least one numerical value per propulsion-factor formula matches what the formula evaluates to with paper inputs. |
| Future work (not in this pass) | Run `PPPFTRN.EXE` under Wine for twin-screw and open-stern .IN files. Compare against the new modern output. On agreement, upgrade `resistance_status` labels from `..._unvalidated_propulsion_*` to fully validated. |

---

## 6. Expected impact

- D4 closes properly. Non-conventional propulsion types produce numeric output backed by published formulas, with honest validation status carried in the data model.
- A2 follow-up bug fix: pram-with-gondola stern correction now matches the published table.
- T_A vs mean-draft fix removes a latent bug that doesn't show on the current sample but would surface for any trimmed-by-the-stern hull.
- Test count grows by ~7 (5 new propulsion tests + 2 synthetic fixture regression tests).
- Three new fixture files. Two existing fixtures regenerated only at the field level (`resistance_status` rename was already done in Tier-2 work).

---

## 7. Out-of-band reference points for hand calcs

From the 1982 paper sample (Section 5, page 5):

- Single-screw, L=205 m, B=32 m, T=10 m, V=37500 m³, lcb=-0.75%, C_B=0.5717, C_M=0.980, C_WP=0.750, C_P=0.5833, A_T=16 m², D=8 m, Z=4
- Reported `w = 0.2584`, `t = 0.1747`, `η_R = 0.9931`

From the 1984 paper sample (Section 5, page 4):

- Twin-screw, L=50 m, B=12 m, T=3.3 m, lcb=-4.5%, C_P=0.7, P/D=1.136, A_E/A_O=0.763, D=3.21 m
- Reported `t = 0.054`, `w = 0.039`, `η_R = 0.980`

These are the two cross-check anchors for hand calcs in Step 6 tests.
