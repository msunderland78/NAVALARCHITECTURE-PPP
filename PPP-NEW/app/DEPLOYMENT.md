# PPP Deployment

## Target

- Ubuntu Linux host
- Docker Compose
- NGINX reverse-proxy container
- PPP backend container serving the static frontend and JSON API

The deployed product uses only files under `PPP-NEW/app`. The ignored legacy `PPP-OLD` files and copied oracle executables are not required at runtime.

## Host Prerequisites

```sh
docker --version
docker-compose --version
```

The deployment user must be able to read and write `/var/run/docker.sock`.

## Configure

The default external HTTP port is `8080`. Override it with `PPP_HOST_PORT`:

```sh
cd PPP-NEW/app
PPP_HOST_PORT=9090 docker-compose config
```

The backend container listens on `PPP_PORT=8000` and NGINX proxies `/` and `/health` to that backend.

## Start

```sh
cd PPP-NEW/app
docker-compose up --build -d
```

Open:

```text
http://127.0.0.1:8080/
```

For a remote Ubuntu server, replace `127.0.0.1` with the server DNS name or IP address.

## Verify

```sh
curl http://127.0.0.1:8080/health
python3 ../tools/smoke_http.py --base-url http://127.0.0.1:8080
```

Expected health response:

```json
{"status": "ok"}
```

The smoke test checks the frontend, health route, sample evaluation, estimated modeling values, candidate legacy `IN` export, and captured legacy `OUT` comparison.

## Stop

```sh
cd PPP-NEW/app
docker-compose down
```

## Operational Notes

- Keep `PPP-OLD` out of the deployed artifact.
- Keep legacy oracle experiments outside the deployed container unless a controlled validation environment requires them.
- Treat current results as preliminary engineering estimates until additional independent oracle cases or published benchmark cases are captured.
- Browser print output is formatted for letter paper, 8.5 by 11 inches with 1 inch margins.
