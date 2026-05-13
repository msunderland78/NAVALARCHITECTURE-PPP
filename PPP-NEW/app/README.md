# PPP Web Application

## Run Without Docker

From the repository root:

```sh
PYTHONPATH=PPP-NEW/app/backend python3 PPP-NEW/app/backend/server.py
```

Open:

```text
http://127.0.0.1:8000/
```

## Run With Docker Compose

From this folder:

```sh
cd PPP-NEW/app
docker-compose up --build
```

The shell user must have permission to access the Docker socket. If `docker-compose` reports `PermissionError: [Errno 13] Permission denied`, run from a Docker-enabled account or adjust host Docker group permissions.

Open:

```text
http://127.0.0.1:8080/
```

Detailed deployment notes are in `DEPLOYMENT.md`.

Use another host port:

```sh
PPP_HOST_PORT=9090 docker-compose up --build
```

## Health Check

```text
http://127.0.0.1:8080/health
```

Expected response:

```json
{"status": "ok"}
```

## HTTP Smoke Test

Against a local backend:

```sh
python3 PPP-NEW/tools/smoke_http.py --base-url http://127.0.0.1:8000
```

Against Docker Compose through NGINX:

```sh
python3 PPP-NEW/tools/smoke_http.py --base-url http://127.0.0.1:8080
```

## Current Scope

The app imports the observed legacy `.PPP` sample layout, evaluates the recovered PPP resistance and propulsion workflow, defaults to the confirmed eight-point legacy speed run, reports applicability checks, displays tables and an interactive canvas plot, exports CSV/JSON/Markdown reports, exports candidate legacy `IN`, and compares legacy `OUT` reports.

Propulsion factors compute for all three propulsion types using the 1982 and 1984 Holtrop and Mennen formulas. Single-screw conventional stern is oracle-validated against `PPPFTRN.EXE` (max delta 53 N across the eight-speed sample). Twin-screw and single-screw open-stern compute from the 1982 paper but are not yet captured-oracle-validated; their `resistance_status` fields make this explicit.

User and estimated wetted-surface and half-angle modes plus air-drag on/off modeling (with configurable coefficient) are supported. Twin-screw cases can supply a pitch-diameter ratio; if omitted, P/D defaults to 1.0 with the active value surfaced in the result.

The Docker image copies only the runtime backend modules and frontend assets, runs the backend as the unprivileged `ppp` user under `init: true` (tini as PID 1), and reports health through a dedicated `healthcheck.py`. The NGINX proxy adds `Content-Security-Policy`, rate-limits `/api/evaluate`, and applies standard timeouts.

Source papers for cross-checking the formulas are committed under `PPP-NEW/Paper/`; the design plan that drove the non-conventional propulsion-factor work is at `PPP-NEW/HOLTROP-PAPER-PLAN.md`.
