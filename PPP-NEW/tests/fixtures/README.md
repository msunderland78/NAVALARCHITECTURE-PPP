# PPP Test Fixtures

These fixtures are regression inputs for the modern implementation. None of them are legacy executables or files copied from `PPP-OLD`.

| Fixture | Role | Oracle Status |
|---|---|---|
| `pppin_sample_import.json` | Normalized modern case parsed from the observed legacy `.PPP` document | Source fixture |
| `pppin_sample_candidate.IN` | Current candidate legacy `IN` emitted from the normalized sample | Not a successful oracle input yet |
| `representative_legacy.OUT` | Representative legacy-style report text for parser and comparison tests | Not captured from `PPPFTRN.EXE` |
| `pppin_sample_modern_result.json` | Current modern partial-result baseline for the normalized sample, including derived hydrostatic terms and two speeds | Modern regression baseline |

When a real `PPPFTRN.EXE` run produces `OUT`, add it as a separate fixture with an explicit captured-oracle name and preserve the sweep summary that produced it.
