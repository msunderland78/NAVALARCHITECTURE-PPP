# PPP Test Fixtures

These fixtures are regression inputs for the modern implementation. None of them are legacy executables or files copied from `PPP-OLD`.

| Fixture | Role | Oracle Status |
|---|---|---|
| `pppin_sample_import.json` | Normalized modern case parsed from the observed legacy `.PPP` document | Source fixture |
| `pppin_sample_candidate.IN` | Current candidate legacy `IN` emitted from the normalized sample | Confirmed successful oracle input |
| `representative_legacy.OUT` | Representative legacy-style report text for parser and comparison tests | Not captured from `PPPFTRN.EXE` |
| `pppin_sample_legacy_oracle.OUT` | Captured `PPPFTRN.EXE` report from the normalized sample using PTY-backed Wine execution | Captured oracle |
| `pppin_sample_legacy_oracle.out.json` | Parsed JSON form of `pppin_sample_legacy_oracle.OUT` | Captured oracle derivative |
| `pppin_sample_oracle_compare.json` | Delta report comparing the captured oracle against the current modern partial implementation | Oracle comparison baseline |
| `pppin_sample_modern_result.json` | Current modern partial-result baseline for the normalized sample, including derived hydrostatic terms and two speeds | Modern regression baseline |

Captured oracle fixtures are plain text or JSON only. Legacy executables remain in ignored archival folders and are not part of the modern product.
