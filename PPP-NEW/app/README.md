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

The current app imports the observed legacy `.PPP` sample layout, evaluates the captured PPP resistance and propulsion workflow, defaults to the confirmed eight-point legacy speed run, reports applicability checks, displays tables and a plot, exports CSV/JSON/Markdown reports, exports candidate legacy `IN`, and compares legacy `OUT` reports. User and estimated wetted-surface and half-angle modes plus air-drag on/off modeling are supported. The Docker image copies only the runtime backend modules and frontend assets.
