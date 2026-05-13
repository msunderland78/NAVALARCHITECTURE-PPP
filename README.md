# Power Prediction Program (PPP) for the Web

Power Prediction Program (PPP) for the Web is a browser-based modernization of the legacy PPP resistance and powering workflow. It is intended for preliminary naval architecture evaluation of displacement hull forms using the recovered Holtrop and Mennen based calculation path from the original Power Prediction Program artifacts.

The application runs from `PPP-NEW`. The legacy material in `PPP-OLD` is archival evidence only and is not required by the web application.

## Use the Program

Open the web application and work through the hull, appendage, propulsion, water, and speed-run inputs as a preliminary resistance and powering case.

### Hull and Hydrostatics

Enter the principal dimensions and hull-form coefficients for the vessel:

- Length on the waterline
- Beam on the waterline
- Forward and aft drafts
- Block coefficient
- Midship coefficient
- Waterplane coefficient
- Longitudinal center of buoyancy

The program derives mean draft, prismatic coefficient, displacement, length-displacement ratio, Froude number, speed-length ratio, Reynolds number, and related hydrostatic terms used by the resistance estimate.

### Hull Features

Define the bulb, transom, and stern form inputs used by the Holtrop and Mennen component estimates:

- Bulb section area at station 0
- Vertical center of bulb area
- Transom immersed area
- Stern type

Applicability checks are reported for key method ranges, including Froude number, beam-draft ratio, length-beam ratio, and prismatic coefficient.

### Propulsion Factors

Select the propulsion arrangement and enter the propeller and propulsive coefficient inputs:

- Single-screw conventional stern
- Single-screw open-flow stern
- Twin-screw arrangement
- Propeller diameter
- Expanded area ratio
- Pitch-diameter ratio (used by twin-screw; defaults to 1.0 when not supplied)

Wake fraction, thrust deduction, hull efficiency, relative rotative efficiency, and required thrust now compute for all three propulsion types using the formulas from the 1982 and 1984 Holtrop and Mennen papers. The single-screw conventional-stern path is validated against the captured PPP 1.8 oracle (max absolute delta 53 N across the eight-speed sample). Twin-screw and open-stern carry per-type `resistance_status` labels noting that a captured-oracle validation is still pending. Reference papers are committed under `PPP-NEW/Paper/` for traceability.

### Appendage and Air Resistance

Choose appendage resistance treatment:

- Percent of bare-hull resistance
- Equivalent wetted area and form-factor method

Air resistance can be included or disabled. When enabled, the deckhouse or cargo frontal area and air-drag coefficient contribute to the resistance build-up. The air-drag coefficient is an input (`modeling.air_drag_coefficient`); the default is the legacy PPP 1.8 value of `0.737223`.

### Wetted Surface and Entrance Angle

The program supports both user-specified and estimated values for:

- Wetted surface area
- Half angle of entrance

Use user-entered values when model-test, lines-plan, or trusted design data are available. Use estimated mode for early-stage comparative work when detailed data are not yet fixed.

### Water Properties

Select a preset or enter custom water properties:

- Salt water at 15 C
- Fresh water at 15 C
- Custom density and kinematic viscosity

These values directly affect Reynolds number, friction coefficient, and resistance magnitude.

### Speed Run

Enter initial speed and speed increment. The default run is eight speed points, matching the confirmed legacy PPP 1.8 behavior.

For each speed, the program reports resistance coefficients, resistance components, effective power, propulsion factors, and required thrust.

### Review Outputs

Use the report areas to review:

- Derived hull summary
- Applicability checks
- Speed table
- Resistance and powering plot
- Engineering review status
- Legacy OUT comparison diagnostics when an original report is available

Export options include:

- CSV result table
- JSON result package
- Markdown engineering report
- Candidate legacy IN file for controlled oracle comparison

Printed reports are formatted for letter paper: 8.5 inches wide by 11 inches high, with 1 inch margins.

## Engineering Status

The single-screw conventional-stern path is validated against the captured PPP 1.8 oracle to report-rounding scale (max absolute delta 53 N across the eight-speed sample). Single-screw open-stern and twin-screw paths compute via the 1982 Holtrop and Mennen formulas but do not yet have captured-oracle validation; results from those propulsion types carry `partial_source_safe_unvalidated_propulsion_*` status labels.

Use the output as a preliminary engineering estimate. Final hull resistance, powering, propulsion, procurement, and operating decisions should be reviewed by a qualified naval architect and supported by project-specific validation.

## Install

### Get the Code with HTTPS

Use the GitHub HTTPS address for this PPP repository:

```sh
git clone https://github.com/msunderland78/NAVALARCHITECTURE-PPP.git
cd NAVALARCHITECTURE-PPP
```

### Run Without Docker

Python 3.12 is the supported version (pinned in `.python-version` and the Docker image). The backend is dependency-free, so no virtual environment or `pip install` step is required.

From the repository root:

```sh
PYTHONPATH=PPP-NEW/app/backend python3 PPP-NEW/app/backend/server.py
```

Open:

```text
http://127.0.0.1:8000/
```

### Run With Docker Compose

From the repository root:

```sh
cd PPP-NEW/app
docker-compose up --build
```

Open:

```text
http://127.0.0.1:8080/
```

Use another host port:

```sh
PPP_HOST_PORT=9090 docker-compose up --build
```

The shell user must have Docker permission. If Docker reports a permission error for `/var/run/docker.sock`, run from a Docker-enabled account or add the user to the host Docker group.

### Check the Server

Health check:

```sh
curl http://127.0.0.1:8080/health
```

Expected response:

```json
{"status": "ok"}
```

Smoke test:

```sh
python3 PPP-NEW/tools/smoke_http.py --base-url http://127.0.0.1:8080
```

### Production HTTPS

The included Docker Compose stack exposes the application over HTTP through the NGINX container. For production HTTPS, place this stack behind a TLS-enabled reverse proxy or add a certificate-enabled NGINX front end on the host.

Basic flow:

1. Point the public DNS name to the Ubuntu server.
2. Install a TLS certificate for that DNS name.
3. Forward HTTPS traffic to the PPP NGINX service port.
4. Verify the site opens with `https://`.

Keep `PPP-OLD` out of the deployed product. The running web application only needs files under `PPP-NEW/app`.

## Repository Layout

```text
PPP-NEW/
  app/
    backend/       Python backend and calculation core
    frontend/      Browser interface, plus pure.js for testable helpers
    nginx/         NGINX reverse-proxy configuration
  analysis/        Legacy investigation notes
  Paper/           OCR'd Holtrop & Mennen 1982 and 1984 source papers
  tests/fixtures/  Normalized samples and oracle fixtures
  CLAUDE-PLAN.md   Code-review plan and implementation status
  HOLTROP-PAPER-PLAN.md  Design plan for the D4 propulsion-factor implementation

PPP-OLD/
  Legacy archival inputs, ignored by git
```
