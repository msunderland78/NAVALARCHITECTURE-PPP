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
- Legacy applicability checks
- CSV export for speed rows

Not yet implemented:

- Full Holtrop and Mennen resistance components
- Propulsion factors
- Required thrust
- HTTP API
- Legacy `OUT` oracle comparison

## Run Tests

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```
