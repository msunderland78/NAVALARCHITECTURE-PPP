# PPP Conversion Plan

Version 1.0, May 10, 2026

## Executive Summary

The legacy Performance Prediction Program in `PPP-OLD` appears to be a small Win32 MFC graphical shell coupled to a separate Win32 DEC Visual Fortran calculation engine. The correct modernization path is a clean reimplementation of the Holtrop and Mennen resistance and powering workflow in `PPP-NEW`, using the old executables only as investigation inputs and temporary oracle references.

The recommended first product is a browser-based preliminary resistance and powering application. It should accept hull geometry, hull-form coefficients, bulb/transom/stern inputs, propulsion-factor model choices, appendage drag, air drag, water properties, design margin, and a speed sweep. It should report resistance components, coefficients, effective power, wake fraction, thrust deduction, required thrust, hull efficiency, and relative rotative efficiency.

No obvious hardware-lock or dongle dependency was found in the current artifacts. There are no visible HASP, Sentinel, Rainbow, Wibu, CodeLock, Aladdin, or SafeNet strings/imports in the supplied executables. No `BYPASS` folder is needed at this stage.

## Implementation Status

Current status as of May 10, 2026:

- Repository setup is complete with `PPP-OLD/` ignored by git and `PPP-NEW/` available for documentation and implementation.
- Initial static inventory is complete for `PPP.EXE`, `PPPFTRN.EXE`, and `PPPIN.PPP`.
- `PPP.EXE` has been identified as a PE32 Win32 GUI executable using MFC 4.0 and Visual C++ runtime imports.
- `PPPFTRN.EXE` has been identified as a PE32 Win32 console executable with DEC Visual Fortran runtime strings.
- `PPPIN.PPP` has been identified as an OLE Compound Document containing one `Contents` stream with an MFC-style serialized document.
- The sample saved case is the `Holtrop and Mennen Example` run `Test 1.0`.
- The likely legacy run flow has been recovered: GUI writes `IN`, deletes stale `In`/`Out`, launches `PPPFTRN.exe`, then reads the generated `OUT`/`Out` report.
- No hardware-lock work is required from the currently supplied files.
- Phase 1 evidence preservation is complete for the currently supplied files.
- `PPPIN.PPP` has been normalized into `PPP-NEW/tests/fixtures/pppin_sample_import.json` for future importer and calculation tests.
- The first backend calculation core scaffold exists in `PPP-NEW/app/backend/ppp_core` with hull derivations, speed sweep terms, ITTC friction coefficient, and legacy applicability checks.
- The core now computes the source-safe `RF` frictional resistance column from water density, speed, wetted surface, and ITTC-1957 `CF`.
- The core now reports partial resistance components, percent appendage resistance, equivalent-area appendage resistance from `SAPP(1+K2)`, design margin resistance, partial total resistance, and effective power with `resistance_status` marking the result as incomplete until Holtrop-specific components are implemented.
- Result rows now expose the visible legacy report columns, using explicit `null` placeholders for unrecovered Holtrop and propulsion terms.
- A reusable legacy `.PPP` importer exists in `PPP-NEW/app/backend/ppp_core/legacy_ppp.py` and has been manually checked against the ignored `PPP-OLD/PPPIN.PPP`.
- The HTTP API exposes `POST /api/import/ppp` for raw legacy `.PPP` uploads, and the browser workspace has an `Import .PPP` control.
- A CSV exporter exists for current speed rows.
- JSON result export is available through `POST /api/export/json` and the browser workspace.
- Modern case JSON save/load is available in the browser workspace as the replacement path for MFC `.PPP` saving.
- Browser print/PDF output is available for the current report view.
- Browser legacy `OUT` comparison upload is available for oracle delta review.
- API validation rejects invalid physical inputs before calculation and the browser displays returned errors in the status area.
- Browser water-property presets update density and viscosity for salt water and fresh water at 15 C.
- A dependency-free HTTP layer exists with `GET /health`, `POST /api/evaluate`, and `POST /api/export/csv`.
- A first browser interface exists in `PPP-NEW/app/frontend` and is served by the backend at `/`.
- Container deployment files exist in `PPP-NEW/app`, including a backend Dockerfile, `docker-compose.yml`, and an NGINX reverse-proxy config.
- `docker-compose config` validates. Runtime compose smoke testing is pending because the current shell user cannot access the Docker socket.
- Legacy oracle notes exist in `PPP-NEW/analysis/oracle-notes.md`. A copied `PPPFTRN.EXE` starts under Wine and attempts to read working-directory file `IN` on Fortran unit 4; exact `IN` layout recovery is now the oracle blocker.
- Static `IN` writer notes exist in `PPP-NEW/analysis/in-format-notes.md`; the GUI opens uppercase `IN`, invokes `PPPFTRN.exe`, and reads `Out`, while the Fortran engine writes `OUT`.
- The candidate `IN` field map now reaches the Fortran calculation path under Wine but still fails with a `DOMAIN error`; a bounded enum/value sweep did not produce `OUT`, so exact record ordering and appendage/model candidate fields remain unresolved.
- A candidate legacy `IN` generator exists so oracle attempts can be reproduced from modern case JSON.
- Browser candidate legacy `IN` export is available for controlled oracle experiments.
- The normalized sample candidate `IN` is pinned as a fixture so static recovery changes are regression-visible.
- A legacy oracle runner exists for isolated `/tmp` Wine runs with captured stdout, stderr, and optional parsed `OUT`.
- A reusable oracle option sweep helper exists for bounded `IN` format probes without hand-managed temp directories, including unresolved appendage fields around the current oracle blocker.
- A legacy oracle sweep CLI exists for repeatable JSON summaries of controlled probes.
- A legacy `OUT` text parser exists for future oracle fixtures.
- A representative, non-oracle `OUT` fixture is pinned for parser and comparison regression tests until a real legacy `OUT` is captured.
- Legacy `OUT` to modern-result comparison diagnostics now merge the coefficient, component, and powering tables by speed and report numeric deltas or missing modern fields.
- A legacy `OUT` comparison CLI exists for repeatable JSON delta reports.
- Initial backend unit tests exist in `PPP-NEW/app/backend/tests` and pass with `PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests`.
- Holtrop and Mennen source tracking has started in `PPP-NEW/analysis/holtrop-mennen-sources.md`.

The next milestone is to recover the exact `IN` file format and produce a real legacy `OUT` oracle, then implement source-derived Holtrop and Mennen components against the oracle comparison deltas.

## Legacy File Inventory

| File | Size | Type | SHA-256 | Role |
|---|---:|---|---|---|
| `PPP.EXE` | 88576 | PE32 Win32 GUI executable | `4e0808828d86fb241371e1c00dfd346b9b42376ee6e2412646b11d37c8df6304` | MFC user interface, document shell, input writer, report reader |
| `PPPFTRN.EXE` | 257536 | PE32 Win32 console executable | `b859fb2fa4711f0fe21579235b058823cfe6d948ae71654df722a51e788eafcf` | DEC Visual Fortran numerical engine |
| `PPPIN.PPP` | 5120 | OLE Compound Document | `e0c3afe94335324737fa6915cb5c2a5b6eb4871724623ce5a01bd422b3f12591` | Saved sample input/document state |

These files are archival investigation inputs only. They must remain in `PPP-OLD` and must not be required by the final web application.

## Static Analysis Findings

### `PPP.EXE`

`PPP.EXE` is a PE32 GUI executable for Intel 80386.

Important PE clues:

- Timestamp: February 26, 1998
- Linker: version 4.20
- Subsystem: Windows GUI
- Sections: `.text`, `.rdata`, `.data`, `.idata`, `.rsrc`, `.reloc`
- Imports: `MFC40.DLL`, `MSVCRT40.dll`, `KERNEL32.dll`, `USER32.dll`, `GDI32.dll`
- Visible C++/MFC classes: `CPPPDoc`, `CPPPView`, `CPPPCntrItem`, `CChildFrame`, `CMainFrame`
- Version resource: `PPP MFC Application`, version `1, 0, 0, 1`
- Program title string: `Power Prediction Program`
- UI credit: `PPP Interface 1.0 - Visual C++ by Dr. Jun Li`
- Project credit: `Developed under the COMPASS Project Sponsored by DARPA through Intergraph Federal Systems`
- Academic affiliation: `Department of Naval Architecture and Marine Engineering University of Michigan`

The import table and visible strings are consistent with Microsoft Visual C++ 4.x or 5.x era MFC development.

The GUI contains menus and dialogs for:

- Project name
- Hull characteristics
- Hull features
- Propulsion factors model
- Appendage drag as percent bare-hull resistance
- Appendage drag as model calculation from appendage wetted areas and form factors
- Air drag, wetted surface, and half angle of entrance modeling
- Design margin
- Water properties
- Analysis run
- Report display
- Font selection
- Microsoft Excel and Word report commands

Important execution strings:

- `del Out`
- `del In`
- `PPPFTRN.exe`
- `PPP failed. Please check your input data, or whether you have a PPPFTRN.exe file in the folder.`
- `Please check and adjust relevant data before running PPP.`

These strings and the C runtime `system` import indicate that the MFC shell writes an `IN` file, deletes stale `In`/`Out`, invokes `PPPFTRN.exe`, waits briefly, reads generated output, and displays or prints the report.

Important validation strings:

- `Fn(Vk = %.2f) = %.4f is out of bounds (0.00 < Fn < 1.00).`
- `B/T = %.2f is out of bounds (2.10 < B/T < 4.00).`
- `LWL/B = %.2f is out of bounds (3.90 < LWL/B < 14.9).`
- `Cp(= CB/CM) = %.4f is out of bounds (0.55 < Cp <0.85).`

These bounds should be carried into the modern validation layer because they describe the intended Holtrop and Mennen applicability range enforced by the original UI.

### `PPPFTRN.EXE`

`PPPFTRN.EXE` is a PE32 console executable for Intel 80386.

Important PE clues:

- Timestamp: January 7, 1998
- Linker: version 5.0
- Subsystem: Windows CUI
- Sections: `.text`, `.rdata`, `.data`, `.idata`
- Imports: `KERNEL32.dll`
- Runtime strings: `DEC Fortran RTL Message Catalog V1.1-14 07-Jan-1997`
- Runtime DLL string: `DFORMSG.DLL`
- Output file string: `OUT`

The executable is consistent with DEC Visual Fortran or early Compaq Visual Fortran with runtime support linked into the executable and message lookup through `DFORMSG.DLL` when needed.

Visible program identity:

- `Power Prediction Program (PPP-1.8) by M. G. Parsons`
- `Source:1. Holtrop,J., & Mennen, G.G.J., "An ... Power Prediction Method," International Shipbuilding`
- `2. Holtrop,J., "A Statistical Reanalysis of Resistance and Propulsion Data," International ...`

Visible output report sections:

- `Input Verification:`
- `Speed, Resistance Coefficients and Frictional Resistance RF(N):`
- `Remaining Resistance Components (N):`
- `Resistance, Effective Power, Propulsion Factors and Required Thrust`

Visible output table columns:

- `V(kts)`
- `V(m/s)`
- `FN`
- `SLRATIO`
- `CF`
- `CR`
- `CA`
- `RF`
- `RF*K1`
- `RAPP`
- `RW`
- `RB`
- `RTR`
- `RA`
- `RAIR`
- `RT(N)`
- `PE(kW)`
- `w`
- `t`
- `REQ.THR(N)`
- `etaH`
- `etaRR`

Visible input verification fields:

- `Length of Waterline LWL (m)`
- `Maximum Beam on LWL (m)`
- `Mean Draft (m)`
- `Draft Forward (m)`
- `Draft Aft (m)`
- `Block Coefficient on LWL CB`
- `Prismatic Coefficient on LWL CP`
- `Midship Coefficient to LWL CM=CX`
- `Waterplane Coefficient on LWL CWP`
- `Center of Buoyancy LCB (% LWL; + Fwd)`
- `Center of Buoyancy LCB (m from FP)`
- `Bulb Section Area at Station 0 (m^2)`
- `Vertical Center of Bulb Area (m)`
- `Transom Immersed Area (m^2)`
- `Stern Type`
- `Propulsion Type`
- `Appen. Drag (% Bare Hull Resistance)`
- `Bow Thruster Tunnel CBTO*DT^2 (m^2)`
- `Water Type`
- `Design Margin on RT,PE,REQ.THR (%)`
- `Deck House/Cargo Frontal Area (m^2)`
- `Appendage Total SAPP(1+K2) (m^2)`
- `Water Density (kg/m^3)`
- `Kinematic Viscosity (m^2/s)`

The engine contains calculation-specific error strings, including:

- `Check data for CB, CM and LCB.`
- `Error of taking sqare root of a negative number.`
- `TLOSS error`
- `SING error`
- `DOMAIN error`

### `PPPIN.PPP`

`PPPIN.PPP` is an OLE Compound Document.

Compound document structure:

- Sector size: 512 bytes
- Mini-sector size: 64 bytes
- Directory stream starts at sector 2
- FAT sector: 3
- Mini-FAT sector: 4
- Root mini-stream chain: sectors 5, 6, 7, 8
- Directory entries: `Root Entry`, `Contents`
- `Contents` stream size: 1880 bytes

The `Contents` stream is a compact MFC-style serialized document. It contains binary double-precision values followed by saved report text. It should be supported by a purpose-built importer in the modern app, not by depending on the old MFC runtime.

Recovered sample case:

| Field | Value |
|---|---|
| Project name | `Holtrop and Mennen Example` |
| Run identification | `Test 1.0` |
| LWL | `212.00 m` |
| Beam on LWL | `32.00 m` |
| Draft forward | `11.00 m` |
| Draft aft | `11.00 m` |
| Block coefficient | `0.6000` |
| Midship coefficient | `0.9800` |
| Waterplane coefficient | `0.7500` |
| LCB | `-0.75 percent LWL from amidships, + forward` |
| Bulb area at Station 0 | `21.00 m^2` |
| Vertical center of bulb area | `4.00 m` |
| Immersed transom area at zero speed | `16.00 m^2` |
| Stern type | `normal shaped sections` |
| Propulsion type | `single-screw with "conventional" stern` |
| Propeller diameter | `8.00 m` |
| Expanded area ratio | `0.8000` |
| Air drag | `yes` |
| Depth at bow | `21.00 m` |
| Deck house/cargo frontal area | `321.00 m^2` |
| Wetted surface | `7890.00 m^2` |
| Half angle of entrance | `12.11 degrees` |
| Design margin | `5.00 percent` |
| Water type | `Salt Water at 15 degrees Celsius` |
| Water density | `1025.870 kg/m^3` |
| Kinematic viscosity | `1.188310e-006 m^2/s` |
| Appendage drag | `5.00 percent bare-hull resistance` |

Binary values near the end of the serialized state suggest speed-run inputs including `15` and `2`, likely initial ship speed and speed increment, but this must be confirmed by recovering the exact `IN` file layout or running the legacy executable under an isolated Windows/Wine environment.

## Inferred Legacy Architecture

The legacy application likely follows this flow:

1. `PPP.EXE` launches as an MFC/OLE document application.
2. The user enters hull, feature, propulsion, appendage, water, margin, and run inputs through dialogs.
3. `PPP.EXE` serializes document state into a `Contents` stream when saving `.PPP` files.
4. On run, `PPP.EXE` validates hull ratios and coefficient ranges.
5. `PPP.EXE` deletes stale `In` and `Out` files through Windows shell commands.
6. `PPP.EXE` writes current inputs to an `IN` file.
7. `PPP.EXE` invokes `PPPFTRN.exe` through the C runtime `system` call.
8. `PPPFTRN.EXE` reads `IN`, performs Holtrop and Mennen resistance and powering calculations over the requested speed range, and writes `OUT`.
9. `PPP.EXE` reads `Out`/`OUT` into the document report view.
10. `PPP.EXE` can print the report and may expose report export workflows for Microsoft Word or Excel.

Windows case-insensitivity likely hid the difference between `Out` and `OUT`. The Linux web application should use explicit structured result objects and avoid case-dependent temporary filenames.

## Hardware Lock Assessment

No current evidence indicates a hardware dongle or software license lock.

Checked indicators:

- No visible `HASP`, `Sentinel`, `Rainbow`, `Wibu`, `CodeLock`, `Aladdin`, `SafeNet`, `dongle`, or license-driver strings.
- No visible lock-driver DLL imports.
- `PPP.EXE` imports standard MFC, C runtime, Win32 user, and GDI libraries.
- `PPPFTRN.EXE` imports only `KERNEL32.dll`; its visible non-Kernel strings are consistent with DEC Fortran runtime support.
- The observed failure string points to missing `PPPFTRN.exe` or invalid input, not license failure.

Conversion action:

- Do not create a `BYPASS` folder now.
- If later artifacts reveal a lock, isolate lock research in a root-level `BYPASS` folder.
- The production web app must not depend on an original dongle, original lock driver, patched executable, copied license state, or emulator.

## Reimplementation Scope

### Version 1 Scope

Implement the behavior proven by the current files:

- Holtrop and Mennen displacement-hull resistance and powering workflow.
- Metric input and output units.
- Speed sweep from initial speed and increment.
- Hull characteristics: LWL, B, TF, TA, CB, CM, CWP, LCB.
- Derived hull values: mean draft, CP, LCB from forward perpendicular, Froude number, slenderness ratio.
- Hull features: bulb area, bulb vertical center, transom immersed area, stern type.
- Stern types: pram with gondola, V-shaped sections, normal shaped sections, U-shaped sections with Hogner stern.
- Propulsion types: single-screw conventional stern, single-screw open-flow stern, twin screw.
- Propeller values: diameter, expanded area ratio, pitch-diameter ratio when required by selected propulsion model.
- Appendage drag by percent bare-hull resistance.
- Appendage drag by individual appendage areas and `(1+K2)` factors.
- Bow-thruster tunnel factor through `CBTO*DT^2`.
- Air drag from depth at bow and deckhouse/cargo frontal area.
- User-entered or estimated wetted surface.
- User-entered or estimated half angle of entrance.
- Salt water at 15 degrees Celsius.
- Fresh water at 15 degrees Celsius.
- User-entered density and kinematic viscosity.
- Design margin applied to total resistance, effective power, and required thrust.
- Report tables matching the legacy report sections.
- Import of the known `.PPP` sample case.
- JSON and CSV export of structured inputs and results.
- Browser print/PDF-friendly report.

### Deferred Scope

Defer until more legacy evidence or user demand exists:

- English-unit input mode if it was only partially implemented in the GUI.
- Direct Microsoft Word or Excel automation. Replace this with CSV, XLSX if required, and browser/PDF reports.
- Exact MFC OLE round-trip saving. The modern app should import legacy `.PPP` files and save modern JSON.
- Running the original executables in production.
- Any dongle or license bypass work unless new artifacts require it for authorized oracle generation.

## Engineering Model

The new calculation core should implement Holtrop and Mennen using a transparent, testable model rather than wrapping the Fortran executable.

Core calculation modules should cover:

- Input normalization and unit conversion.
- Hull geometry derivations.
- Applicability checks.
- ITTC-1957 friction coefficient.
- Form factor and frictional resistance.
- Appendage resistance.
- Wave-making resistance.
- Bulbous bow resistance.
- Transom-stern resistance.
- Model-ship correlation allowance.
- Air drag.
- Total resistance.
- Effective power.
- Wake fraction.
- Thrust deduction.
- Hull efficiency.
- Relative rotative efficiency.
- Required thrust.
- Design-margin application.

The implementation should expose intermediate values because PPP is an engineering tool, not just a final-power calculator. Users need to see why a result changed.

## Web Application Target

Use the POP project at `/home/sundema/CLAUDE-AI-PROJECTS/CODEX-NAVARCH-POP` as the deployment and structure reference.

Recommended initial structure:

```text
PPP-NEW/
  PPP-COVERSION-PLAN.md
  PROJECT_BRIEF.md
  analysis/
    legacy-inventory.md
    file-format-notes.md
    string-findings.md
    holtrop-mennen-sources.md
  app/
    backend/
      ppp_core/
      tests/
    frontend/
    nginx/
    docker-compose.yml
    README.md
```

Recommended stack:

- Backend: Python with FastAPI for clear numerical code and fast iteration.
- Numerical core: plain Python dataclasses and math functions first; move to Rust or WebAssembly only if performance becomes a real issue.
- Frontend: plain HTML, CSS, and JavaScript or a small React app, following the scale of the final workflow.
- Deployment: Docker Compose with a backend container and NGINX reverse proxy.

The application should be self-contained and should not require `PPP.EXE`, `PPPFTRN.EXE`, `PPPIN.PPP`, Wine, Windows, MFC, DEC Fortran runtime files, or Office automation.

## User Interface Plan

The first screen should be the actual PPP working interface, not a marketing page.

Primary panels:

- Project: project name, run ID.
- Speed range: initial speed, increment, number of speeds or final speed once confirmed.
- Hull characteristics: LWL, B, TF, TA, CB, CM, CWP, LCB.
- Hull features: bulb, transom, stern shape.
- Propulsion factors: propulsion type, Dp, Ae/Ao, P/Dp where applicable.
- Appendages: percent mode and model-calculation mode.
- Modeling: air drag, wetted surface source, half-angle source.
- Water and margin: density, viscosity, preset water types, design margin.
- Results: report tables, coefficient plots, resistance component stacked chart, speed-power curve.

Expected controls:

- Segmented controls for input modes.
- Select menus for stern type, propulsion type, and water type.
- Numeric inputs with units shown near the field.
- Toggle for air drag.
- Tabs for inputs, report, plots, and import/export.
- Import button for legacy `.PPP`.
- Export buttons for JSON, CSV, and print/PDF.

Validation should be visible at the relevant input and in a compact run-status area. The legacy range checks should be warnings or blocking errors depending on whether they make the Holtrop method invalid.

## API Plan

Initial backend endpoints:

- `GET /health`
- `POST /api/evaluate`
- `POST /api/import/ppp`
- `POST /api/export/csv`

`POST /api/evaluate` should accept one structured JSON object containing:

- Project metadata.
- Hull characteristics.
- Hull features.
- Propulsion model.
- Appendage model.
- Air and modeling settings.
- Water properties.
- Design margin.
- Speed sweep.

The response should return:

- Normalized inputs.
- Derived values.
- Applicability checks.
- Per-speed result rows.
- Resistance component rows.
- Summary values.
- Plot-ready arrays.

## Legacy Oracle Plan

The immediate oracle target is the supplied Holtrop and Mennen sample.

Oracle tasks:

1. Recover or synthesize the legacy `IN` file corresponding to `PPPIN.PPP`.
2. Run `PPPFTRN.EXE` in an isolated compatibility environment if feasible.
3. Capture the generated `OUT` file without modifying `PPP-OLD`.
4. Store copied oracle text and parsed expected values under `PPP-NEW/tests/fixtures/`.
5. Write a parser for the legacy `OUT` report.
6. Create golden tests comparing the new core against legacy values within documented tolerances.

If running the binary is not feasible, use published Holtrop and Mennen benchmark examples and the visible sample input as the first regression suite, then add legacy oracle data when available.

## Legacy `.PPP` Import Plan

The importer should support the known OLE Compound Document pattern first:

1. Parse the OLE directory and locate `Contents`.
2. Extract MFC-style string and double fields from the binary prefix.
3. Parse the embedded report text as a fallback for fields with visible labels.
4. Convert legacy labels and enum strings to modern enum values.
5. Return a normalized JSON input object.
6. Preserve the original labels in import metadata for auditability.

Initial importer can support only the observed `PPPIN.PPP` stream layout. Broaden it only when more `.PPP` files are found.

## Testing Strategy

Testing should scale with risk.

Core tests:

- Unit tests for hull derivations.
- Unit tests for friction coefficient and Reynolds/Froude calculations.
- Unit tests for each resistance component.
- Applicability-bound tests for `Fn`, `B/T`, `LWL/B`, and `CP`.
- Sample Holtrop and Mennen regression test.
- Legacy `.PPP` import test for `PPPIN.PPP` copied into fixtures only as parsed JSON, not by depending on `PPP-OLD`.

API tests:

- Valid evaluation request.
- Invalid physical inputs.
- Out-of-range applicability warnings.
- Legacy import request.
- CSV export shape and values.

Frontend tests:

- Static load test.
- Calculation smoke test.
- Import smoke test.
- Plot nonblank test.
- Mobile and desktop layout screenshots.

Deployment tests:

- Docker build.
- Compose startup.
- `GET /health`.
- Browser smoke test through NGINX.

## Implementation Phases

### Phase 1: Evidence Preservation

Status: complete for current artifacts.

Deliverables:

- `PPP-NEW/analysis/legacy-inventory.md`
- `PPP-NEW/analysis/string-findings.md`
- `PPP-NEW/analysis/file-format-notes.md`
- Parsed JSON representation of the known `PPPIN.PPP` sample

Exit criteria:

- Every current legacy file is documented.
- No files in `PPP-OLD` are modified.
- No production code depends on `PPP-OLD`.

### Phase 2: Formula Recovery

Status: started.

Deliverables:

- `PPP-NEW/analysis/holtrop-mennen-sources.md`
- Formula map from legacy output terms to implemented calculations
- Applicability-range note
- First hand-calculated or reference benchmark case

Exit criteria:

- Each output column has a documented formula source.
- Unit conventions are explicit.
- Open questions are isolated to known terms.

### Phase 3: Core Calculation Library

Status: started.

Deliverables:

- `PPP-NEW/app/backend/ppp_core`
- Typed input and result structures
- Calculation functions
- Unit tests

Exit criteria:

- The sample case can be evaluated over a speed range.
- Result rows include all visible legacy table columns.
- Tests pass locally.

### Phase 4: Legacy Import and Oracle

Status: importer started; Wine startup confirmed; legacy `IN` layout pending.

Deliverables:

- `.PPP` importer for the observed OLE `Contents` stream
- Parsed sample fixture
- Legacy `OUT` parser if oracle output is produced
- Golden regression test

Exit criteria:

- `PPPIN.PPP` can be imported into modern JSON.
- Imported JSON can run through the new core.
- New output can be compared against either legacy output or documented Holtrop and Mennen benchmark values.

### Phase 5: Web Interface

Status: started.

Deliverables:

- Working browser UI
- Input forms
- Validation display
- Result tables
- Resistance and power plots
- JSON and CSV export
- Print/PDF-friendly report

Exit criteria:

- A user can reproduce the sample case from the browser.
- Desktop and mobile layouts are usable.
- Result plots render and are nonblank.

### Phase 6: Container Deployment

Status: started; config validated; runtime smoke pending Docker socket access.

Deliverables:

- Backend Dockerfile
- NGINX config
- `docker-compose.yml`
- Deployment README
- Health check

Exit criteria:

- Compose stack runs locally.
- App is reachable through NGINX.
- Health endpoint returns `{"status":"ok"}`.

### Phase 7: Product Hardening

Deliverables:

- More regression cases.
- Clear engineering disclaimers in README/report output.
- Improved export formatting.
- Host-specific deployment notes.

Exit criteria:

- Results are defensible against multiple references.
- Deployment steps are reproducible on the target Ubuntu/NGINX server.

## Open Questions

These questions should be answered before declaring the app complete:

- What is the exact legacy `IN` file layout written by `PPP.EXE`?
- How many speed points does PPP run from the `Run ...` dialog?
- Does the legacy run dialog store final speed, count, or only initial speed plus increment?
- Are English units actually implemented or only exposed in command strings?
- What exact formulas or coefficients did Parsons use for each Holtrop and Mennen term?
- How does PPP estimate wetted surface when the user selects estimated mode?
- How does PPP estimate half angle of entrance when the user selects estimated mode?
- Does PPP use the 1978 Holtrop and Mennen paper, the 1984 statistical reanalysis, or a hybrid coefficient set?
- How exactly are wake fraction, thrust deduction, and relative rotative efficiency selected for SSC, SSOF, and TS propulsion types?
- What does the Fortran `TLOSS error` path represent?
- Are Word and Excel commands dead UI, automation hooks, or planned features?

## Maintenance Rules

This plan is a living project document. Update it when:

- A new legacy artifact is added.
- A new file format is recovered.
- A formula assumption is confirmed or rejected.
- A milestone phase starts or finishes.
- A test oracle is added.
- Deployment requirements change.

Keep updates in `PPP-NEW/PPP-COVERSION-PLAN.md`. Do not edit `PPP-OLD`.
