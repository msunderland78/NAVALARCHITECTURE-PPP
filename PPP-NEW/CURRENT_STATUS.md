# PPP Current Status

Version 1.1, May 13, 2026

## Implemented

- Public project, documentation, browser, and test references use the corrected name `Power Prediction Program (PPP)`.
- Legacy evidence notes for supplied files.
- Legacy inventory updated for the added manuals, spreadsheets, and Finder metadata.
- `470Manuals.pdf` reviewed for PPP 1.8 behavior, source, speed sweep, applicability, and resistance-component evidence.
- `470Manuals.pdf` is tracked under `PPP-NEW/` for GitHub reference access.
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
- CSV result export now validates result and speed-row shapes before writing output.
- CSV result export now validates numeric speed-row values are finite before writing output.
- Markdown report export now validates rendered result sections and row shapes before writing output.
- Markdown report export now validates rendered numeric values are finite before formatting output.
- Markdown report export now validates rendered case-summary values before formatting output.
- Point-count and legacy comparison tolerance validation now rejects boolean values instead of accepting Python's integer coercion.
- Backend validation now rejects prismatic coefficient, LCB-derived factor, and half-angle values that would make the recovered Holtrop equations leave the real-number domain.
- API routes now return controlled 400 responses for malformed JSON shapes and invalid UTF-8 request bodies.
- JSON API routes now reject non-object request bodies with a controlled 400 response.
- The dependency-free HTTP server now rejects invalid `Content-Length` values with controlled 400 responses.
- The dependency-free HTTP server now emits basic response hardening headers.
- The dependency-free HTTP server now returns JSON 405 and OPTIONS responses with stable `Allow` headers.
- The dependency-free HTTP server now suppresses the default Python runtime banner.
- CLI and oracle case-file entry points now share a JSON case loader with object-shape validation.
- Legacy `OUT` comparison now validates speed tolerance and field-list options before producing diagnostics.
- Legacy comparison option validation now lives in the comparison helper so API and CLI callers share the same checks.
- Legacy `OUT` comparison now validates legacy and modern speed-row shapes before matching rows.
- Legacy `IN` export now validates option object shape and finite numeric override values before generating candidate oracle input.
- Legacy `IN` export now validates candidate record-order options before evaluating the case.
- Legacy `IN` export option validation now lives in the candidate generator so API, CLI, and oracle paths share the same checks.
- Browser CSV export now reports API validation failures instead of downloading an error response as a result file.
- Browser JSON case import now reports malformed files instead of leaving an unhandled import failure.
- Non-conventional propulsion selections now surface an engineering warning because recovered wake, thrust-deduction, and relative-rotative-efficiency equations are still pinned to the captured single-screw conventional-stern workflow.
- The dependency-free HTTP server strips query strings before route and static asset matching for reverse-proxy and cache-busted requests.
- Compose services now use `restart: unless-stopped` for basic host reboot and transient process recovery.
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
  - Result table without the internal `resistance_status` column
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
- Docker backend image runs as an unprivileged `ppp` user.
- Docker backend image disables Python bytecode writes for the unprivileged runtime filesystem.
- NGINX proxy configuration now pins basic response hardening headers and proxy timeouts.
- Docker Compose starts NGINX after the backend healthcheck reports healthy.
- Ubuntu/Docker Compose deployment guide for the NGINX container path.
- HTTP smoke CLI for backend or NGINX route verification.
- Automated HTTP smoke regression covering backend routes, frontend static serving, legacy export, and legacy `OUT` comparison.
- Static notes for the legacy temporary `IN` writer.
- Candidate legacy `IN` generator for controlled oracle experiments, including active estimated modeling values.
- Candidate legacy `IN` generator regression covers fresh-water preset water-code mapping.
- Candidate legacy `IN` generator regression covers open-flow and twin-screw propulsion type code mapping.
- Candidate legacy `IN` CLI for terminal-based oracle experiments.
- Candidate legacy `IN` matrix CLI for dry-run option audits without Wine.
- Legacy oracle runner now validates positive finite timeout values before staging and launching Wine.
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
- Legacy oracle sweep helpers now validate option list shapes before creating attempt directories.
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
- Legacy `OUT` parser now rejects non-finite numeric report values before comparison.
- Representative legacy `OUT` text fixture for parser and comparison regression tests.
- Legacy `OUT` to modern-result comparison diagnostics with status counts, max absolute delta, and max relative delta summaries.
- Legacy `OUT` comparison CLI for JSON delta reports and optional absolute/relative pass/fail gates.
- Legacy `OUT` comparison API accepts configurable speed matching tolerance.
- Modern evaluation CLI for reproducible result fixture refreshes.
- Candidate `IN` field map recovered from GUI writer/report cross-references.
- Twin-screw and single-screw open-stern propulsion-factor formulas implemented from the 1982 Holtrop & Mennen paper. Wake fraction, thrust deduction, hull efficiency, relative rotative efficiency, and required thrust now compute for all three propulsion types.
- `resistance_status` splits three ways by propulsion type: `partial_source_safe_components` for oracle-validated single-screw conventional stern, `partial_source_safe_unvalidated_propulsion_twin_screw` for twin-screw, and `partial_source_safe_unvalidated_propulsion_open_stern` for open-stern.
- Pitch-diameter ratio is now an input. Defaults to 1.0 for twin-screw cases that don't supply it; active value surfaced in `result.propulsion.active_pitch_diameter_ratio`.
- Air drag coefficient is now a configurable input (`modeling.air_drag_coefficient`); legacy `0.737223` is the default.
- Pram-with-gondola `C_stern` corrected to -25 per the 1984 paper.
- Single-screw conventional stern wake fraction and `c_8` / `c_11` now use draft aft, matching the 1982 paper. Captured oracle still matches to 53 N max delta.
- Both Holtrop & Mennen papers (1982 and 1984) committed under `PPP-NEW/Paper/` as OCR'd markdown for reference; `PPP-NEW/HALTROP-PAPER-PLAN.md` documents the design plan that drove D4.
- Synthetic regression fixtures added for additional geometry (`synthetic_container_*`), twin-screw (`synthetic_twin_screw_*`), and open-stern (`synthetic_open_stern_*`) cases.
- Backend hardening: 16 MB POST body cap, 1 MB OLE upload cap, path-traversal-safe static serving via `safe_static_path()`, `Content-Security-Policy` header (strict `default-src 'self'`), JSON request logs to stdout.
- NGINX hardening: rate limit on `/api/evaluate` (10 r/s + burst 20), Content-Security-Policy header.
- Docker deployment: `init: true` runs tini as PID 1; dedicated `backend/healthcheck.py` honors `PPP_PORT`.
- Code-quality tooling: `pyproject.toml` with ruff and mypy strict on `ppp_core/types.py` (new TypedDict definitions); public API surface type-annotated.
- GitHub Actions CI runs unittest discover, ruff, mypy, and `docker compose config` on push and pull request.
- Frontend hardening: every form control has explicit `for`/`id`; `#status` is an aria-live region; canvas plot has gridlines, dual-axis tick labels, hover tooltips, and an aria-label; print-exclusion notice on the oracle comparison panel; import-JSON validator runs before form population; water-preset density/viscosity mismatch warning.
- Frontend test suite: `pure.js` extracted with pure helpers; 15 Node tests via `node:test` (no npm); Python wrapper runs them under `unittest discover`.
- `.python-version` pinned to 3.12.

## Verification

Current test command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```

Current result:

```text
Ran 156 tests in ~0.9s — OK
```

Frontend pure-helper tests run under the same `unittest discover` via `tests/test_frontend_pure.py`, which spawns Node and asserts on the `node:test` output. 15 additional checks. The Python wrapper skips cleanly when Node isn't installed.

Automated HTTP smoke testing passes against an in-process backend for `/health`, `/`, `/api/evaluate`, `/api/export/csv`, `/api/export/json`, `/api/export/report.md`, `/api/export/legacy-in-candidate`, and `/api/compare/out`. The smoke harness now also verifies the `Content-Security-Policy` response header. Local HTTP smoke testing also passes with `PPP-NEW/tools/smoke_http.py` against a running server. The corrected legacy oracle candidate now runs successfully through PTY-backed Wine execution and produces `PPP-NEW/tests/fixtures/pppin_sample_legacy_oracle.OUT`. `docker-compose config` validates. Runtime Docker smoke testing is pending Docker socket permission.

## Known Limits

- Captured-sample resistance and propulsion fields align with the legacy oracle to report-rounding scale; max absolute delta 53 N at 27 kn after the draft-aft propulsion-factor fix.
- The single-screw conventional stern result is the only propulsion type with captured-oracle validation. Twin-screw and open-stern propulsion factors compute via the 1982 paper formulas and carry `..._unvalidated_propulsion_*` status labels until a PPPFTRN.EXE oracle is captured for each.
- Captured legacy `OUT` oracles are available for the normalized user-mode sample and an estimated-mode variant.
- PPP's eight-speed run behavior is resolved from `470Manuals.pdf` and captured oracle fixtures.
- Synthetic regression fixtures lock additional geometries and propulsion types against silent drift but are not literature- or executable-validated.
- More oracle cases are needed before full formula equivalence can be trusted across the Holtrop applicability range.
- `PPPFTRN.EXE` requires PTY-backed Wine execution because plain piped execution fails at Fortran unit 6 `CONOUT$`.

## Next Best Work

1. Encode the 1982 paper §5 (single-screw, L=205 m) and 1984 paper §5 (twin-screw, L=50 m) worked numerical examples as literature-oracle fixtures with pinned expected values. The papers are at `PPP-NEW/Paper/`.
2. Capture twin-screw and open-stern `.OUT` files from `PPPFTRN.EXE` under Wine, then upgrade the `..._unvalidated_propulsion_*` status labels to validated.
3. Add an estimated-mode oracle case at a different geometry (D6 in `CLAUDE-PLAN.md`).
4. Run Docker smoke tests from a Docker-enabled account.
