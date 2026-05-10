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

## Current Scope

The current app is a working modernization scaffold. It imports the observed legacy `.PPP` sample layout, evaluates source-safe partial resistance terms, reports applicability checks, displays tables and a plot, and exports CSV. Full Holtrop and Mennen wave, form, bulb, transom, correlation, propulsion-factor, and required-thrust terms remain under formula recovery.
