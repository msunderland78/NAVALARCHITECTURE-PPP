# CLAUDE-PLAN.md — Review and Upgrade Plan for PPP-NEW

Date: 2026-05-13
Author: Claude (Opus 4.7)
Scope reviewed: every file under `PPP-NEW/` (~6,000 lines across backend, frontend, deployment, tests, fixtures, analysis docs). Tests run clean: `132 tests OK` in 0.71s.

The project is in genuinely good shape. The Holtrop and Mennen workflow is recovered, the captured oracle agrees to report-rounding scale, validation is thorough, exports are exercised, the Docker stack builds and `docker-compose config` validates, and the test suite is comprehensive against the single captured sample. What follows is everything I would change before calling this product done, organized so you can stop at any phase and still ship something meaningfully better.

---

## Section A — Real Bugs (Fix Before Anything Else)

### A1. Legacy `.PPP` importer reads two different fields from the same offset

`PPP-NEW/app/backend/ppp_core/legacy_ppp.py:65` and `:83` both read `read_double(contents, 0x01da) * 100`. One assigns to `appendages.percent_bare_hull_resistance`, the other to `margin.design_margin_percent`. The captured `PPPIN.PPP` happens to have both equal to 5.0%, so the unit test passes by coincidence (see `test_legacy_ppp.py:58` where the fixture stores 0.05 at offset `0x01da` only). For any other saved `.PPP` file with `appendage % ≠ design margin %`, one of the two imported values will be wrong.

Fix:
- Re-scan the binary near `0x01da` for the second of the two values. The MFC serialization in the captured stream is sequential doubles, so look for `0.05` (5%) at a distinct offset.
- Add a deliberate fixture variant with `appendage_percent = 3.0`, `design_margin_percent = 7.0` and a unit test that distinguishes them. Once that test fails for the right reason, fix the offset.
- Document the resolved offset in `analysis/file-format-notes.md`.

### A2. `pram_with_gondola` stern correction disagrees between modules

`core.py:8` maps `pram_with_gondola → +10`. `legacy_in.py:21` maps it to `0` in `STERN_CORRECTION_CANDIDATES`. These are the same coefficient (Holtrop's `Cstern`) but the legacy-IN writer uses a different default than the core. Holtrop's published value is `+10`. Either the legacy-IN writer is intentionally probing an alternative encoding (defensible during oracle sweeps) or it is a copy-paste error.

Fix: confirm the intent in a one-line comment, or align both tables to `+10`. If the value is intentionally configurable during oracle probing, expose it via `legacy_options.stern_correction` (already exposed) and leave the core's published Holtrop value alone.

### A3. Server runs a dependency-free `ThreadingHTTPServer` with no body-size cap

`server.py:59` reads the full POST body with `self.rfile.read(length)` where `length` is whatever the client sent in `Content-Length`. NGINX caps requests to 10MB but anyone hitting the backend directly (the documented "Run Without Docker" path on port 8000) has no cap. A malicious or accidental gigabyte POST allocates that gigabyte in memory.

Fix: add a constant like `MAX_REQUEST_BYTES = 16 * 1024 * 1024`, reject larger `Content-Length` with `413 Payload Too Large`, and `read()` with a hard limit so chunked transfer encoding cannot lie about the size either.

### A4. Frontend builds HTML with `innerHTML` for values it does not own

`app.js:395-399` renders `review.note`, `review.status`, and `review.warnings` via `innerHTML`. These currently come from server-side constants, so there is no live XSS. But the same pattern is used in `renderOracleComparison` (`app.js:463`) for legacy OUT content. If any future code path bubbles user-supplied or imported text into one of these slots — for example, project name on the print page, or labels parsed from a legacy OUT — it becomes an injection. The render path should not depend on "no one ever puts user data here later."

Fix: replace `innerHTML = string` with `textContent` for any field where the value originates outside our constant set. Build any structural HTML with `createElement`/`append`, or pass user values through a small `escape()` helper.

### A5. `result["engineering_review"]["status"]` joins distinct status strings with `", "`

`core.py:118`: `", ".join(statuses)`. The CSV path then puts this into a column. If the model later returns multiple statuses, the comma will collide with CSV separators. Today `resistance_status` is always the same string, so this is latent, not active.

Fix: pick one of (a) a JSON list field rather than a joined string, or (b) quote the value through `csv.writer` and never break out of that helper. The current code path goes through `csv.DictWriter` which does quote, so this is mostly cosmetic — but using a list is the cleaner data model.

---

## Section B — Quality / Maintainability Issues

### B1. No type hints, no linter, no formatter config

Zero `def f(x: float) -> float`. Zero `mypy`, `ruff`, or `black` config. The code is consistent enough that this rarely bites today, but the math layer is the kind of code where types prevent silent unit confusions (m vs mm, percent vs fraction, knots vs m/s). The codebase calls `appendages.get("percent_bare_hull_resistance", 0) / 100` in several places and getting that "/100" wrong somewhere would be invisible without types.

Fix: add `pyproject.toml` with `ruff` + `black`, add `mypy` in `--strict` mode for `ppp_core` only, and type the public API (`evaluate_case`, `compare_legacy_out_to_result`, `generate_candidate_legacy_in`, the OLE reader) with `TypedDict`s for the case shape.

### B2. Two output fields point at the same value

`core.py:511-512`: `rf_form_resistance_n` and `form_resistance_n` are both set to `rf * form_factor`. The export schema and tests reference one or the other inconsistently. Pick one canonical name and delete the alias. The legacy oracle parser column is `RF*K1`, so `rf_form_resistance_n` is the better name; drop `form_resistance_n`.

### B3. `legacy_in.py:41` calls `evaluate_case(case, 1)` just to read back active modeling values

The candidate IN writer re-runs the entire Holtrop pipeline to pick up estimated wetted-surface and half-angle values. This works but couples two unrelated paths and pays the full cost of `evaluate_case` for an export operation. Factor `modeling_values(...)` (`core.py:126`) out of `evaluate_case` and call only that helper from `legacy_in`. Same intent, no validation duplication, no resistance math run for an export.

### B4. `applicability()` runs the Froude check once per speed but produces one row per speed in the output

`core.py:530-543`. For an eight-speed run you get eight `froude_number` rows in `applicability` plus three other checks — 11 rows total. The HTML renders them all as separate cards. That makes the panel grow with point count and adds noise. A single applicability check at min and max Fn is enough, or one row that reports the worst case.

### B5. The dependency-free server returns the C runtime banner suppressed but still emits `Server:` from `BaseHTTPRequestHandler`

`server.py:23-24` sets `server_version = "PPPBackend"` and `sys_version = ""`. That replaces the Python banner with `PPPBackend`. Good. But the framework still emits `Date:` headers that disclose server clock and `Server:` discloses the framework. Either drop both headers via `BaseHTTPRequestHandler.protocol_version` overrides, or accept them as fine — they are not sensitive. Note this only as a posture choice, not a fix.

### B6. `request_path` does not normalize `..` or duplicate slashes

`server.py:102-103`. `urlsplit` only splits — it does not resolve `..`. Then `serve_static` builds a path with `FRONTEND / request_path_value.lstrip("/")` and checks `path.parent == FRONTEND`. That check defeats `..` traversal because `Path("/x/../../etc/passwd").parent` is not `/x` — but the resolution rules are subtle and the safety bet depends on the OS. Use `Path.resolve(strict=False)` and then `is_relative_to(FRONTEND)` for an explicit, OS-agnostic check.

### B7. `legacy_oracle.py:103` calls `os.execvpe` in the child without an `else:` exit

After `os.execvpe(command[0], command, child_env)`, if exec fails (binary missing, exec permission), the child returns to the parent's code path and starts running the parent logic with the child PID. `execvpe` raises on failure, so this is OK in practice — but wrap in a `try/except SystemExit, OSError → os._exit(1)` for safety. The Wine subprocess path is already a quirky surface; harden it.

### B8. The numeric value parser in `legacy_out.py:118` does a `replace("D", "E")` over the whole match

This is correct for Fortran-style `1.5D6` but will eat any `D` mid-token. The regex prevents real harm because `[deDE]` is restricted to the exponent slot — fine. Just worth a one-line comment so a future reader does not "fix" the perceived bug.

### B9. `tests/fixtures/` is committed to the repo with `__pycache__/` siblings present

`tools/__pycache__/` and `app/backend/__pycache__/` are visible in the working tree. Add `__pycache__/` to `.gitignore` (the README claims `*-OLD/` is excluded but does not list bytecode dirs).

### B10. No license file, no `pyproject.toml`, no setup metadata

Not a bug — but every modern Python project of this size includes them, and the lack makes pip-installable distribution impossible. If "deploy to an Ubuntu host" stays the long-term plan, this is fine; if anyone else ever runs the code, this hurts.

---

## Section C — Security Posture Beyond A3/A4

### C1. Missing `Content-Security-Policy` header

The server returns `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer`. Add a strict CSP for the frontend page: `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'`. The current page uses no inline scripts or styles, so `'self'`-only works.

### C2. NGINX does not pin `Strict-Transport-Security`

This is HTTP-only today (TLS is documented as out-of-scope for the included compose stack). When TLS is added, an `add_header Strict-Transport-Security "max-age=31536000" always;` belongs in the nginx config.

### C3. No rate limiting

The single backend instance answers every request. A simple `limit_req_zone` in nginx for `/api/evaluate` (CPU-bound) prevents trivial DoS. Optional for a single-user tool; standard for anything multi-tenant.

### C4. `/api/import/ppp` accepts arbitrary bytes and parses them as OLE

OLE parsing is a historically rough surface. The current parser is short and bounded but has no explicit size limit on the body or on the stream allocations. Combined with A3 (no body cap), a malformed compound document can drive memory use. Add a cap on `len(data)` (e.g. 1 MB — the captured sample is 5 KB) and reject anything larger up front.

### C5. `legacy_ppp.py:108` uses `next(... for entry in entries if entry["type"] == 5)` without a default

If the directory entry list is corrupt or empty (uploaded garbage), this raises `StopIteration` which then surfaces as a 500 because `api.py:106` does not catch it. Catch `StopIteration` in the route or change to `next(..., None)` plus a `ValueError`.

### C6. Wine oracle runner writes user-supplied path to `os.chdir`

`legacy_oracle.py:101` — the workdir is passed through from CLI args. This is a developer tool used outside the production container, so the blast radius is small, but the path argument should still be validated as "exists and is a directory we created."

---

## Section D — Engineering / Domain Issues

### D1. Captured oracle is one case

`CURRENT_STATUS.md` is explicit: `partial_source_safe_components` because only one user-mode case and one estimated-mode variant of that same hull have been validated against the legacy OUT. The Parsons PPP 1.8 user manual (`470Manuals.pdf` per the analysis notes) covers the Holtrop method's intended applicability range broadly. The single captured case sits at:
- `Fn` 0.17 to 0.32 (the eight-speed run from 15 to 29 knots on a 212 m hull)
- `B/T = 2.91`, near the lower end of `2.10 < B/T < 4.00`
- `Cp ≈ 0.612`, near the lower end of `0.55 < Cp < 0.85`
- `LWL/B = 6.625`, well inside `3.90 < LWL/B < 14.9`

We have effectively zero validation at the upper end of any range, at twin-screw or open-flow propulsion (the warning surfaces, but the math is unvalidated), or with the equivalent-area appendage model. The product is honest about this in the engineering-review status, but it limits what the tool can defensibly produce.

Fix: build a second-tier oracle from **published** Holtrop and Mennen benchmark cases (Series 60 hulls, the 1982 paper's worked examples, the 1984 reanalysis examples) rather than waiting for more captured `.PPP` documents. The expected values are in the literature; the comparison framework already exists; the missing artifact is a few JSON fixtures and a regression test. This is the single highest-impact engineering improvement we can make without depending on outside material.

### D2. Air-drag coefficient is hard-coded to `0.737223`

`core.py:7`: `LEGACY_AIR_DRAG_PRESSURE_COEFFICIENT = 0.737223`. This is the recovered PPP 1.8 coefficient. For a project that wants to be a general preliminary tool (not "exact reproduction of one 1998 Fortran program"), this should be exposed as an input (default = the recovered value, override = user-set), with the standard ITTC air-drag formula `0.5 * ρ_air * V² * A * Cd` available as an alternative model. Holtrop's own ITTC-style air drag uses ρ_air directly; the `0.737223` constant rolls density into the coefficient.

### D3. Wave-resistance interpolation discontinuity

`core.py:383-393`: between `Fn = 0.4` and `Fn = 0.55`, wave resistance is linearly interpolated between the low-Fn and high-Fn formulas (the Holtrop approach). At the endpoints, the result is continuous but the first derivative is not — so the residual-resistance coefficient curve has kinks at exactly those speeds. For most preliminary work this is fine; for plotting smooth curves it shows. The standard fix is a smooth blend (cubic Hermite). Optional, not a defect.

### D4. `holtrop_propulsion_factors` is conditional on `propulsion["type"]` only through the warning

The function applies the Holtrop single-screw conventional-stern wake-fraction equation regardless of `propulsion["type"]`. The `engineering_review` warning is the user-facing signal. For open-flow and twin-screw, Holtrop gives different `c11`, `c19`, `c20` and a different wake formula entirely. The right path is to either (a) refuse to compute for non-conventional types until the formulas are added, or (b) implement them — the 1984 paper has them. Today we silently produce numbers that look right but are not validated.

### D5. `validate_case` mixes hard validation with bounds enforcement

The function mixes "this would crash the math" checks (e.g. `cp >= 1`) with "this is outside Holtrop's applicability" checks (which are presented separately as `applicability` warnings). Pulling the "applicability bound" set out of validation and into `applicability()` would let users compute resistance at, say, `Fn = 0.45` (outside Holtrop) and see the warning, which is the published behavior of the original PPP 1.8 too.

### D6. `estimated_wetted_surface` and `estimated_half_angle_entrance` need their own oracle case at varied geometry

The estimated-mode oracle is also one case, the same hull with `wetted_surface_mode=estimated`. We have zero validation that the estimated formulas reproduce the legacy estimates at other geometries.

### D7. The CSV export emits all 29 columns including internal state

`export.py:6-36` lists `SPEED_COLUMNS` with every internal value. For a user-facing CSV, this is fine; for downstream tooling it would be cleaner to either (a) emit a stable subset that matches the legacy OUT columns by default plus a `--full` switch, or (b) split into two CSVs (coefficients and components, like the legacy OUT does).

---

## Section E — UX / Frontend

### E1. Form labels wrap the input element, which is semantically OK but lacks `for`/`id`

Screen readers will work but tab order and focus management could be tighter. Add `id` to inputs and convert to `<label for="...">` so each form control has a stable target.

### E2. `Status` box is not a live region

`app.js:34`: `statusBox.textContent = "Running"` does not announce to assistive tech. Add `role="status"` and `aria-live="polite"` to the `#status` element in `index.html:15`.

### E3. The canvas plot has no fallback and no tooltips

Decent for preliminary work, but it lacks: axis tick labels, gridlines, a second y-axis label for PE, and any way to hover-inspect a point. For an engineering report, two y-axes and tick labels are standard. Two options: (a) keep raw canvas but draw the missing pieces, (b) drop the canvas for a tiny SVG renderer that does it natively. SVG also prints sharper.

### E4. Print layout hides oracle comparison entirely

`styles.css:377`: `.oracle { display: none; }` inside `@media print`. If the user just compared against a legacy OUT and prints, that comparison disappears. That is probably a choice — engineering reports should not embed legacy diagnostics — but say so in the UI so users do not get surprised.

### E5. Imported case JSON does not validate before populating the form

`app.js:127-147`: parse, `applyCase(payload.case || payload)`, then run. If the JSON parses but is missing fields, `applyCase` accesses `caseData.project.name` and throws. Caught by the outer try, status box says "Import JSON failed", but the form is partially overwritten. Either validate the shape first or snapshot the form values and restore on failure.

### E6. The water-property preset only triggers on user-driven change

`app.js:38-45`: if the imported case JSON sets `water.type` to `salt_water_15_c` but the imported density does not match the preset, no warning fires. Optional: detect mismatch and show a hint.

### E7. No unit tests for `app.js`

The frontend is a single 559-line script with no test runner. For a vanilla-JS project this is normal, but it means the form-payload mapping in `buildPayload`/`applyCase` is the largest untested surface in the repo. A few tests covering the round-trip (form → JSON → applyCase → form) using `jsdom` or just `node --experimental-vm-modules` would catch field-rename regressions.

---

## Section F — Deployment / Ops

### F1. `docker-compose.yml` declares `version: "3.8"`

Compose v2 ignores `version:` and warns about it. Drop the field.

### F2. The backend healthcheck uses an inline Python one-liner

`docker-compose.yml:15`: `python -c "import urllib.request; urllib.request.urlopen(...)"` works but is fragile. Add `/healthz` semantics later if needed; for now, a `curl -fsS` (after installing curl) or a dedicated `healthcheck.py` is more readable.

### F3. No CI

There is no `.github/workflows/` or equivalent. The 132-test suite is the single highest-leverage automation in the repo and it is not gated on PRs. Add a GitHub Actions workflow that runs `unittest`, `ruff check`, and `mypy` on push.

### F4. No reproducible Python version pin for local development

The Dockerfile pins `python:3.12-slim`. Local development on Matt's host can run any Python 3.x. Add a `.python-version` (pyenv) or a clear note in the README that 3.10+ is required (the `match`-free code suggests anything ≥ 3.6 works, but the test suite implicitly relies on dict ordering and `urllib.parse.urlsplit`, both stable from 3.6).

### F5. No log format or log-to-stdout discipline beyond default

`BaseHTTPRequestHandler.log_message` writes formatted requests to stderr. For Docker, stdout is the conventional log surface. Override `log_message` to emit one JSON line per request — easier to scrape and forward.

### F6. The Dockerfile does not run as PID 1 cleanly

`CMD ["python", "backend/server.py"]` runs Python as PID 1, which means signal handling and zombie reaping fall on Python. For a Python HTTP server this is usually fine, but adding `tini` or `dumb-init` as an entrypoint is the conventional fix.

### F7. NGINX config has no `gzip on;` or static caching

Tiny project, tiny page (frontend totals ~1100 lines), so gains are small — but `gzip on; gzip_types text/css application/javascript text/html;` is one line and meaningful for `app.js` (559 lines uncompressed). Also `expires 1h;` on `/app.js` and `/styles.css` would prevent revalidation thrash.

### F8. No production HTTPS path is wired up

The README describes the manual flow ("put a TLS-terminating proxy in front"). For a project that targets "an Ubuntu Linux server," this is the last mile. A second nginx config or a documented Caddy alternative would land it. Optional, depending on how this gets used.

---

## Section G — Recommended Priority Order

Roll these up by impact-to-effort:

**Tier 1 (do first, half a day of work):**
- A1: fix the duplicate-offset bug in the importer (this is a correctness defect on user-mode `.PPP` files other than the captured sample).
- A3: cap request body size in `server.py`.
- A4: replace `innerHTML` with `textContent` everywhere user-controllable strings could land.
- F1: drop `version:` from `docker-compose.yml`.
- F3: add a CI workflow (1 file, ~30 lines).
- B9: add `__pycache__/` to `.gitignore`.

**Tier 2 (one or two days, materially improves the product):**
- D1: add 3–5 published Holtrop benchmark fixtures and regression tests. This is the single biggest engineering credibility win available.
- D4: either refuse to compute or properly implement open-flow / twin-screw propulsion factors.
- B1: introduce `ruff` + `mypy --strict` for `ppp_core`, type the public API surface.
- C1: add `Content-Security-Policy`.
- A2: pin the `pram_with_gondola` stern correction across modules.

**Tier 3 (polish, several more days):**
- E1, E2, E3: accessibility + plot quality.
- D2: parameterize the air-drag coefficient.
- D5: move applicability-only checks out of `validate_case`.
- B3: factor `modeling_values` out so `legacy_in` doesn't run the full pipeline.
- F5, F7: log discipline and gzip.

**Tier 4 (when it becomes a real product, weeks):**
- D3: smooth wave-resistance blend.
- D6: estimated-mode oracle at varied geometries.
- F8: end-to-end HTTPS with cert renewal.
- E7: introduce a JS test runner for the frontend.

---

## Section H — Concrete First-Pass Diffs (Tier 1 Sketches)

These are not meant as final code; they are concrete enough that anyone picking this up can move on Tier 1 in an afternoon.

### A1 — duplicate-offset fix in `legacy_ppp.py`

```python
# Before
"appendages": {
    ...,
    "percent_bare_hull_resistance": read_double(contents, 0x01da) * 100,
    ...
},
"margin": {
    "design_margin_percent": read_double(contents, 0x01da) * 100
}

# After (with the resolved offset for the second field, TBD by re-scan)
"appendages": {
    ...,
    "percent_bare_hull_resistance": read_double(contents, 0x01d2) * 100,  # offset to confirm
    ...
},
"margin": {
    "design_margin_percent": read_double(contents, 0x01da) * 100
}
```

Plus a regression test with `appendage_percent = 3.0`, `design_margin = 7.0`.

### A3 — request body cap in `server.py`

```python
MAX_REQUEST_BYTES = 16 * 1024 * 1024

def request_content_length(value):
    try:
        length = int(value)
    except (TypeError, ValueError):
        raise ValueError("Content-Length must be a non-negative integer")
    if length < 0:
        raise ValueError("Content-Length must be a non-negative integer")
    if length > MAX_REQUEST_BYTES:
        raise ValueError("Content-Length exceeds maximum request size")
    return length
```

Return 413 in `do_POST` when this raises that specific message — or keep it as 400 for simplicity.

### A4 — escape helper in `app.js`

```javascript
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}
```

Then replace `${review.note}` with `${escapeHtml(review.note)}` (and similarly for `status`, the warning items, oracle row fields). Or rewrite `renderEngineeringNote` / `renderOracleComparison` to build DOM nodes with `createElement` and skip `innerHTML` entirely.

### F1 — drop the version key

```yaml
# docker-compose.yml — delete the first two lines
# version: "3.8"
services:
  ppp-backend:
    ...
```

### F3 — minimal CI

`.github/workflows/test.yml`:

```yaml
name: test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python -m unittest discover PPP-NEW/app/backend/tests
```

Three more lines after `ruff` and `mypy` are added.

---

## Section I — What I'd Leave Alone

Worth saying out loud, because Codex got these right:

- The dependency-free backend choice. Adding FastAPI would not pay back the new runtime dependency for a project this size.
- The single-file frontend. No SPA framework, no build step, easy to read.
- The validation-first approach in `core.py:validate_case` — domain-aware checks are exactly right for an engineering tool.
- The oracle harness (`legacy_oracle.py`, `legacy_sweep.py`, the PTY workaround for Fortran `CONOUT$`). That is genuinely good investigative work.
- The fixture manifest distinguishing source / representative / modern baseline / future oracle. That is the right taxonomy.
- The print layout. Letter paper, 1-inch margins, hide the form — a real engineering report shape.
- The `partial_source_safe_components` status label. It tells users exactly what they have.

---

## Closing Note

If I had to pick one thing to do first, it would be D1: get a half-dozen published Holtrop and Mennen benchmark cases into `tests/fixtures/` with comparison regressions. Every other item on this list improves the code or the deploy; that item improves what the tool is actually allowed to claim. A naval architect cannot defend "preliminary engineering estimate" to a project review if the validation set is a single 212-meter hull at eight Froude numbers.

A1 (the importer bug) is the only item that produces wrong answers today for any input that diverges from the captured sample. Everything else is correctness in expansion, hardening, or polish.
