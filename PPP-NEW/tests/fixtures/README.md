# PPP Test Fixtures

These fixtures are regression inputs for the modern implementation. None of them are legacy executables or files copied from `PPP-OLD`.

| Fixture | Role | Oracle Status |
|---|---|---|
| `pppin_sample_import.json` | Normalized modern case parsed from the observed legacy `.PPP` document | Source fixture |
| `pppin_sample_estimated_import.json` | Normalized sample with estimated wetted-surface and entrance-angle modes active | Source fixture variant |
| `pppin_sample_candidate.IN` | Current candidate legacy `IN` emitted from the normalized sample | Confirmed successful oracle input |
| `representative_legacy.OUT` | Representative legacy-style report text for parser and comparison tests | Not captured from `PPPFTRN.EXE` |
| `pppin_sample_legacy_oracle.OUT` | Captured `PPPFTRN.EXE` report from the normalized sample using PTY-backed Wine execution | Captured oracle |
| `pppin_sample_legacy_oracle.out.json` | Parsed JSON form of `pppin_sample_legacy_oracle.OUT` | Captured oracle derivative |
| `pppin_sample_oracle_compare.json` | Delta report comparing the captured oracle against the current modern partial implementation | Oracle comparison baseline |
| `pppin_sample_estimated_legacy_oracle.OUT` | Captured `PPPFTRN.EXE` report for the estimated-mode sample using PTY-backed Wine execution | Captured oracle |
| `pppin_sample_estimated_legacy_oracle.out.json` | Parsed JSON form of `pppin_sample_estimated_legacy_oracle.OUT` | Captured oracle derivative |
| `pppin_sample_estimated_oracle_compare.json` | Delta report comparing the estimated-mode oracle against the modern implementation | Oracle comparison baseline |
| `pppin_sample_modern_result.json` | Current modern partial-result baseline for the normalized sample, including derived hydrostatic terms and two speeds | Modern regression baseline |
| `pppin_sample_estimated_modern_result.json` | Current modern partial-result baseline for the estimated-mode sample, including active modeling terms and two speeds | Modern regression baseline |
| `synthetic_container_case.json` | Smaller, faster hull (LWL 150 m, B/T 2.75, Cp 0.64, Fn up to 0.28) used only to widen the geometry envelope covered by regression tests | Synthetic, **not** an oracle |
| `synthetic_container_result.json` | Pinned modern output for `synthetic_container_case.json`; locks the current implementation against silent drift outside the captured sample's geometry | Synthetic regression baseline |

Captured oracle fixtures are plain text or JSON only. Legacy executables remain in ignored archival folders and are not part of the modern product.

The only literature- or executable-validated cases today are the two captured PPP 1.8 oracles (user-mode and estimated-mode) at LWL 212 m. The synthetic fixtures lock additional geometries to the current implementation; they do **not** validate correctness against Holtrop & Mennen published values.
