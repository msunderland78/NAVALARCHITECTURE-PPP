# PPP Current Status

Version 1.0, May 10, 2026

## Implemented

- Legacy evidence notes for supplied files.
- Legacy inventory updated for the added manuals, spreadsheets, and Finder metadata.
- `470Manuals.pdf` reviewed for PPP 1.8 behavior, source, speed sweep, applicability, and resistance-component evidence.
- Legacy `.PPP` import for the observed OLE `Contents` stream layout.
- Modern case JSON save/load.
- Source-safe partial calculation core:
  - Hull derivations
  - Speed sweep
  - Froude number
  - Speed-length ratio
  - Displacement volume and mass
  - Inverse B/T and B/L ratios
  - Midship and waterplane areas
  - Length-displacement volume ratio
  - Reynolds number
  - ITTC-1957 friction coefficient
  - Frictional resistance
  - Holtrop form-factor resistance `RF*K1`
  - Holtrop correlation allowance coefficient `CA`
  - Holtrop correlation allowance resistance `RA`
  - PPP legacy air-drag resistance `RAIR`
  - Air-drag on/off modeling
  - Holtrop wave resistance `RW`
  - Holtrop bulb resistance `RB`
  - Holtrop transom resistance `RTR`
  - Percent appendage resistance
  - Equivalent-area appendage resistance from `SAPP(1+K2)`
  - Design margin resistance
  - Partial total resistance
  - Effective power
  - Holtrop wake fraction
  - Holtrop thrust deduction
  - Hull efficiency
  - Relative rotative efficiency
  - Required thrust
  - Explicit modeling source values for wetted surface and half angle of entrance
  - Estimated wetted surface
  - Estimated half angle of entrance
  - LCB converted to meters and percent LWL from forward perpendicular
- Captured oracle comparison now has numeric modern values for every compared legacy report field.
- Evaluation and JSON export include machine-readable engineering review status metadata.
- Markdown report export includes speed-sweep, water-property, propulsion, appendage, modeling-mode, air-drag, and margin input summary.
- Backend validation now rejects prismatic coefficient, LCB-derived factor, and half-angle values that would make the recovered Holtrop equations leave the real-number domain.
- Browser CSV export now reports API validation failures instead of downloading an error response as a result file.
- Non-conventional propulsion selections now surface an engineering warning because recovered wake, thrust-deduction, and relative-rotative-efficiency equations are still pinned to the captured single-screw conventional-stern workflow.
- The dependency-free HTTP server strips query strings before route and static asset matching for reverse-proxy and cache-busted requests.
- Legacy applicability checks:
  - `Fn`
  - `B/T`
  - `LWL/B`
  - `CP`
- API validation for invalid physical inputs.
- API validation accepts user and estimated wetted-surface and half-angle modes.
- API validation rejects unsupported stern, propulsion, and water types.
- API validation rejects hull coefficients greater than 1.
- API validation rejects non-positive waterplane coefficient inputs.
- API validation rejects invalid feature, propulsion, and modeling dimensions.
- API validation rejects non-boolean air-drag values.
- API validation rejects non-finite numeric inputs.
- Backend and deployment README files document current validation and HTTP smoke coverage.
- API validation rejects duplicate multi-point speed sweeps caused by zero speed increment.
- API point-count validation is capped at the same 20-point maximum exposed by the browser.
- API point-count validation rejects fractional values instead of truncating them.
- Default API, CLI, and browser speed-run point count is eight to match PPP 1.8 behavior.
- Browser workspace with:
  - Editable sample case
  - Water-property presets
  - Legacy `.PPP` import
  - Candidate legacy `IN` export
  - Legacy `OUT` comparison upload
  - Modern case JSON import/export
  - CSV and JSON result export
  - Markdown engineering report export
  - Applicability panel
  - Derived hydrostatic summary
  - Engineering review status note in browser and printed report output
  - Result table
  - Legacy `IN` oracle variant controls
  - Legacy `OUT` comparison speed tolerance control
  - Explicit user-mode controls for wetted surface and half angle
  - HTML min/max constraints aligned with backend numeric validation
  - Positive initial-speed browser constraint aligned with backend validation
  - Canvas plot
  - Letter-size print/PDF layout
- Dependency-free Python backend.
- Dockerfile, Docker Compose, and NGINX reverse-proxy scaffold.
- Docker image copies only runtime backend modules and frontend assets.
- Ubuntu/Docker Compose deployment guide for the NGINX container path.
- HTTP smoke CLI for backend or NGINX route verification.
- Automated HTTP smoke regression covering backend routes, frontend static serving, legacy export, and legacy `OUT` comparison.
- Static notes for the legacy temporary `IN` writer.
- Candidate legacy `IN` generator for controlled oracle experiments, including active estimated modeling values.
- Candidate legacy `IN` generator regression covers fresh-water preset water-code mapping.
- Candidate legacy `IN` generator regression covers open-flow and twin-screw propulsion type code mapping.
- Candidate legacy `IN` CLI for terminal-based oracle experiments.
- Candidate legacy `IN` matrix CLI for dry-run option audits without Wine.
- Candidate legacy `IN` propeller/wetted-surface record order corrected from direct writer disassembly.
- Pinned candidate legacy `IN` fixture for the normalized sample case.
- Pinned current modern sample result fixture for regression baselining.
- Pinned estimated-mode modern sample result fixture for regression baselining.
- Fresh-water preset numeric regression terms for density, viscosity, resistance, and powering behavior.
- Fixture manifest distinguishing source, representative, modern baseline, and future oracle artifacts.
- Reproducible legacy oracle runner that stages copied executables outside `PPP-NEW`.
- Reproducible legacy oracle runner records the exact Wine command and supports explicit Wine arguments.
- Reproducible legacy oracle runner supports PTY-backed execution for legacy console programs that write to `CONOUT$`.
- Reusable legacy oracle option sweep helper for bounded `IN` format probes, including unresolved appendage fields.
- Legacy oracle sweep options now include alternate first-record ordering probes.
- Legacy oracle sweep options now include alternate propeller/wetted-surface record ordering probes.
- Legacy oracle sweep attempt summaries now include generated `IN` SHA-256, line count, and first record.
- Legacy oracle sweep attempt summaries classify common Fortran runtime failure kinds.
- Legacy oracle sweep CLI for JSON summaries and captured `OUT` artifacts from controlled probes.
- Legacy oracle sweep CLI supports explicit Wine arguments for console-mode experiments.
- Captured legacy `OUT` oracle for the normalized `PPPIN.PPP` sample.
- Parsed captured oracle JSON fixture for the normalized sample.
- Oracle-to-modern comparison baseline for the current source-derived implementation.
- Captured oracle regression threshold requiring eight matched speeds and max absolute delta under 100 N.
- Captured estimated-mode oracle fixture and regression threshold for estimated wetted surface and half angle.
- Legacy `OUT` text parser for future oracle fixtures.
- Representative legacy `OUT` text fixture for parser and comparison regression tests.
- Legacy `OUT` to modern-result comparison diagnostics with status counts, max absolute delta, and max relative delta summaries.
- Legacy `OUT` comparison CLI for JSON delta reports and optional absolute/relative pass/fail gates.
- Legacy `OUT` comparison API accepts configurable speed matching tolerance.
- Modern evaluation CLI for reproducible result fixture refreshes.
- Candidate `IN` field map recovered from GUI writer/report cross-references.

## Verification

Current test command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```

Current result:

```text
99 tests OK
```

Automated HTTP smoke testing passes against an in-process backend for `/health`, `/`, `/api/evaluate`, `/api/export/csv`, `/api/export/json`, `/api/export/report.md`, `/api/export/legacy-in-candidate`, and `/api/compare/out`. Local HTTP smoke testing also passes with `PPP-NEW/tools/smoke_http.py` against a running server. The corrected legacy oracle candidate now runs successfully through PTY-backed Wine execution and produces `PPP-NEW/tests/fixtures/pppin_sample_legacy_oracle.OUT`. `docker-compose config` validates. Runtime Docker smoke testing is pending Docker socket permission.

## Known Limits

- Captured-sample resistance and propulsion fields now align with the legacy oracle to report-rounding scale.
- Current resistance totals remain marked `partial_source_safe_components` until additional oracle cases are captured.
- Captured legacy `OUT` oracles are available for the normalized user-mode sample and an estimated-mode variant.
- PPP's eight-speed run behavior is resolved from `470Manuals.pdf` and captured oracle fixtures.
- More oracle cases are needed before full formula equivalence can be trusted.
- `PPPFTRN.EXE` requires PTY-backed Wine execution because plain piped execution fails at Fortran unit 6 `CONOUT$`.

## Next Best Work

1. Add more oracle cases once additional valid legacy inputs are available.
2. Add more oracle cases when additional legacy source files are available.
3. Run Docker smoke tests from a Docker-enabled account.
