# PPP Backend

This backend contains the first modern PPP calculation modules.

## Current Scope

Implemented:

- Legacy `.PPP` `Contents` stream import for the observed sample layout
- Minimal OLE Compound Document stream extraction
- Hull derivations
- Speed sweep terms
- ITTC-1957 friction coefficient
- Frictional resistance `RF`
- Percent appendage resistance based on currently implemented bare-hull resistance
- Design-margin resistance
- Partial total resistance and effective power
- Legacy applicability checks
- CSV export for speed rows
- Dependency-free HTTP routes
- API validation for invalid physical inputs

Not yet implemented:

- Full Holtrop and Mennen resistance components
- Propulsion factors
- Required thrust
- Legacy `OUT` oracle comparison

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

Current routes:

- `GET /`
- `GET /health`
- `POST /api/evaluate`
- `POST /api/export/csv`
- `POST /api/export/json`
- `POST /api/import/ppp`

The frontend is in `PPP-NEW/app/frontend` and is served by the backend. It currently supports direct sample-case editing, modern case JSON save/load, legacy `.PPP` import for the observed sample layout, API-backed evaluation, applicability checks, a speed table, a canvas plot, CSV/JSON result download, and browser print/PDF output formatted for 8.5 by 11 inch paper with 1 inch margins.
