# PPP Backend

This backend contains the first modern PPP calculation modules.

## Current Scope

Implemented:

- Legacy `.PPP` `Contents` stream import for the observed sample layout
- Candidate legacy `IN` generator for controlled oracle experiments
- Reproducible legacy oracle runner for isolated compatibility tests outside `PPP-NEW`
- Reusable legacy oracle option sweep helper for bounded `IN` format probes, including unresolved appendage fields
- Legacy oracle sweep CLI for JSON summaries and captured `OUT` artifacts from controlled probes
- Legacy `OUT` text parser for future oracle fixtures
- Representative legacy `OUT` text fixture for parser and comparison regression tests
- Legacy `OUT` to modern-result comparison diagnostics with status counts and max-delta summary
- Legacy `OUT` comparison CLI for JSON delta reports and optional pass/fail gates
- Pinned current modern sample result fixture for regression baselining
- Fixture manifest distinguishing source, representative, modern baseline, and future oracle artifacts
- Minimal OLE Compound Document stream extraction
- Hull derivations
- Speed sweep terms
- Default eight-point speed runs matching PPP 1.8 behavior
- Displacement volume and mass
- LCB in meters and percent LWL from forward perpendicular
- ITTC-1957 friction coefficient
- Frictional resistance `RF`
- Percent appendage resistance based on currently implemented bare-hull resistance
- Equivalent-area appendage resistance from `SAPP(1+K2)`
- Design-margin resistance
- Total resistance, effective power, propulsion factors, and required thrust for the captured sample workflow
- Explicit modeling source values for user-entered or estimated wetted surface and half angle of entrance
- Engineering review status note in browser and printed report output
- Legacy applicability checks
- CSV export for speed rows
- Markdown engineering report export
- Modern evaluation CLI for reproducible result fixture refreshes
- Dependency-free HTTP routes
- HTTP smoke CLI for deployed backend or NGINX route checks
- Automated HTTP smoke regression for the backend route surface
- API validation for invalid physical inputs
- API validation for supported user and estimated wetted-surface and half-angle modes
- API validation for unsupported stern, propulsion, and water types
- API validation for hull coefficients greater than 1
- API validation for invalid feature, propulsion, and modeling dimensions
- API validation for non-finite numeric inputs
- API validation for non-boolean air-drag values
- API validation for point count as an integer from 1 to 20
- API validation for non-positive waterplane coefficient inputs
- Twin-screw propulsion-factor formulas from the 1982 Holtrop & Mennen paper (wake fraction, thrust deduction, relative rotative efficiency, required thrust)
- Single-screw open-stern propulsion-factor formulas from the 1982 paper (paper itself labels these tentative)
- Per-propulsion-type `resistance_status` labels distinguishing oracle-validated single-screw conventional from formula-only twin-screw and open-stern
- Pitch-diameter ratio input with safe default of 1.0; active value surfaced in `result.propulsion.active_pitch_diameter_ratio`
- Configurable air-drag coefficient (`modeling.air_drag_coefficient`) defaulting to the legacy `0.737223`
- Pram-with-gondola `C_stern` aligned to -25 per the 1984 paper
- Draft-aft (`T_A`) used in the single-screw conventional wake fraction and in `c_8` / `c_11` per the 1982 paper
- `pyproject.toml` with ruff and mypy strict on the new `ppp_core/types.py` (TypedDicts for the public API surface)
- Content-Security-Policy response header (strict `default-src 'self'`)
- 16 MB POST body cap; 1 MB OLE upload cap; path-traversal-safe static serving
- One-line-per-request JSON logging to stdout via `Handler.log_message` override
- Dedicated `healthcheck.py` script honoring `PPP_PORT`
- Synthetic regression fixtures for additional geometry and for twin-screw and open-stern propulsion types
- Frontend pure-helper test suite at `frontend/tests/pure.test.js` runs under `unittest discover`

Not yet implemented:

- Captured PPPFTRN.EXE oracles for twin-screw and open-stern propulsion types (synthetic fixtures only)
- Literature-oracle fixtures encoding the 1982 §5 and 1984 §5 worked examples
- Estimated-mode oracle at varied geometry

## Run Tests

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```

## Run Development Server

From the repository root:

```sh
PYTHONPATH=PPP-NEW/app/backend python3 PPP-NEW/app/backend/server.py
```

Default URL:

```text
http://127.0.0.1:8000/health
```

## Run HTTP Smoke Test

With the development server or NGINX proxy already running:

```sh
python3 PPP-NEW/tools/smoke_http.py --base-url http://127.0.0.1:8000
```

## Run Legacy Oracle Sweep

Use only copied legacy executables outside `PPP-NEW`:

```sh
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.legacy_sweep_cli PPP-NEW/tests/fixtures/pppin_sample_import.json /tmp/PPPFTRN.EXE /tmp/ppp-sweep --appendage-primary-value 0.05 --appendage-primary-value 5 --appendage-model-total 0 --appendage-model-total 0.05 --capture-out /tmp/ppp-oracle.OUT --capture-parsed-out /tmp/ppp-oracle-parsed.json --output /tmp/ppp-sweep-summary.json
```

## Run Modern Evaluation

```sh
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.evaluate_cli PPP-NEW/tests/fixtures/pppin_sample_import.json --point-count 2 --output /tmp/ppp-modern-result.json
```

## Compare Legacy OUT

```sh
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.legacy_compare_cli PPP-NEW/tests/fixtures/pppin_sample_import.json PPP-NEW/tests/fixtures/representative_legacy.OUT --point-count 2 --require-matched-speed-count 2 --max-absolute-delta 100000 --output /tmp/ppp-out-comparison.json
```

Current routes:

- `GET /` — serves `index.html`
- `GET /app.js`, `GET /pure.js`, `GET /styles.css` — frontend static assets
- `GET /health`
- `POST /api/evaluate`
- `POST /api/export/csv`
- `POST /api/export/json`
- `POST /api/export/report.md`
- `POST /api/export/legacy-in-candidate`
- `POST /api/import/ppp`
- `POST /api/import/out`
- `POST /api/compare/out`

The frontend is in `PPP-NEW/app/frontend` and is served by the backend. Pure helper functions live in `pure.js` and are loaded as a sibling `<script>` before `app.js`. The browser surface supports direct sample-case editing, water-property presets with mismatch detection, modern case JSON save/load with pre-population validation, legacy `.PPP` import for the observed sample layout, candidate legacy `IN` export, legacy `OUT` comparison upload, API-backed evaluation, applicability checks, user and estimated modes for wetted surface and half angle, air-drag on/off modeling with configurable coefficient, twin-screw P/D input, HTML min/max constraints aligned with backend validation, an engineering review status note, a speed table, a canvas plot with gridlines and dual-axis tick labels and hover tooltips, an aria-live status region, CSV/JSON/Markdown result download, and browser print/PDF output formatted for 8.5 by 11 inch paper with 1 inch margins.

## Run Frontend Pure-Helper Tests

The Python wrapper `tests/test_frontend_pure.py` invokes Node and runs the suite as part of `unittest discover`. To run the JavaScript tests directly:

```sh
node --test PPP-NEW/app/frontend/tests/pure.test.js
```

The test wrapper skips cleanly when Node isn't installed.
