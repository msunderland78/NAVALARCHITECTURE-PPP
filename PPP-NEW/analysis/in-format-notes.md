# Legacy `IN` Format Notes

Version 1.0, May 10, 2026

## Purpose

This note records static evidence about the temporary calculation input file written by `PPP.EXE` and read by `PPPFTRN.EXE`. It is evidence for oracle recovery only. The modern web application must not depend on `PPP.EXE`, `PPPFTRN.EXE`, Wine, or a generated legacy temporary file.

## Confirmed Run Path

`PPP.EXE` stores the temporary file and command strings in its `.data` section:

| String | File offset | Runtime address | Use |
|---|---:|---:|---|
| `IN` | `0x0000b59c` | `0x0040d39c` | Input file opened by the GUI writer |
| `Out` | `0x0000b560` | `0x0040d360` | Report file opened by the GUI reader |
| `PPPFTRN.exe` | `0x0000b564` | `0x0040d364` | External Fortran engine command |
| `del In` | `0x0000b4c4` | `0x0040d2c4` | Cleanup command |
| `del Out` | `0x0000b4bc` | `0x0040d2bc` | Cleanup command |

Important code references:

| Address | Evidence |
|---:|---|
| `0x00403f39` | Pushes `0x0040d39c`, the `IN` filename, before calling the imported `ofstream` constructor |
| `0x00404418` | Calls imported `ofstream::close` after writing the input stream |
| `0x00404466` | Pushes `0x0040d364`, then calls C runtime `system`, invoking `PPPFTRN.exe` |
| `0x004044a4` | Pushes `0x0040d360`, the `Out` filename, before calling the imported `ifstream` constructor |
| `0x004046bb` | Calls imported `ifstream::close` after reading the report |
| `0x004046c1` | Calls `system("del In")` |
| `0x004046cf` | Calls `system("del Out")` |

`PPPFTRN.EXE` contains the output string `OUT`. The GUI reads `Out`. This was harmless on 32-bit Windows because filenames were case-insensitive. Any Linux oracle tooling must account for this spelling difference.

## I/O Mechanism

`PPP.EXE` imports these C++ stream functions from `MSVCRT40.dll`:

- `??0ofstream@@QAE@PBDHH@Z`
- `?close@ofstream@@QAEXXZ`
- `??6ostream@@QAEAAV0@H@Z`
- `??6ostream@@QAEAAV0@PBD@Z`
- `??6ostream@@QAEAAV0@N@Z`
- `??0ifstream@@QAE@PBDHH@Z`
- `?get@istream@@IAEAAV1@PADHH@Z`
- `?close@ifstream@@QAEXXZ`

The writer uses the C++ `ostream << double`, `ostream << char const *`, `ostream << int`, and `endl` operators. The separator string at `0x0040d398` is a single space. The stream therefore appears to be text, not binary.

## Recovered Writer Shape

The `IN` writer begins at approximately `0x00403f30`. It opens `IN`, changes stream float formatting, writes numeric values from the `CPPPDoc` object, separates values with spaces, and ends records with `endl`.

The current static pass recovers this candidate record structure. Field names are mapped by cross-referencing the writer offsets with the GUI report-building code and visible report labels.

| Writer address range | Candidate output fields |
|---|---|
| `0x00404050` to `0x0040409e` | `LWL`, `B`, `depth_at_bow`, `TF`, `TA`, `deckhouse_cargo_frontal_area` |
| `0x004040c6` to `0x00404132` | `CB`, `CM`, `CWP`, `design_margin_fraction` |
| `0x0040414b` to `0x00404218` | `appendage_percent_or_total`, `appendage_model_total_candidate`, `ABT`, `HB`, `ATR`, `stern_correction_candidate`, `propulsion_type_code` |
| `0x0040423c` to `0x0040425b` | `LCB_percent_lwl_from_midships` |
| `0x0040427b` to `0x004042ca` | `Dp`, `wetted_surface`, `half_angle_entrance` |
| `0x004042f4` to `0x0040433a` | `Ae_Ao`, `P_Dp_candidate`, `water_type_code` |
| `0x0040435f` to `0x00404397` | `initial_speed_knots`, `speed_increment_knots` |
| `0x004043be` to `0x0040440d` | `water_density`, `kinematic_viscosity` |

The exact semantic mapping of every `CPPPDoc` object offset is not fully recovered. The values align with the legacy dialogs and the serialized `.PPP` document, but assigning each stream column still needs either dynamic tracing under Wine/Windows or a successful `PPPFTRN.EXE` oracle run.

## Recovered Document Field Offsets

The following offsets are within the `CPPPDoc` object used by the MFC GUI. Floating-point values are stored as adjacent 32-bit halves of a double.

| `CPPPDoc` offset | Field | Evidence |
|---:|---|---|
| `0x7b0` | `LWL` | Report label `Length of Waterline LWL` |
| `0x7b8` | `B` | Report label `Maximum Beam on LWL B` |
| `0x7c0` | `TF` | Report label `Draft Forward TF` |
| `0x7c8` | `TA` | Report label `Draft Aft TA` |
| `0x7d0` | `CB` | Report label `Block Coefficient on LWL CB` |
| `0x7d8` | `CM` | Report label `Midship Coefficient to LWL CM` |
| `0x7e0` | `CWP` | Report label `Waterplane Coefficient on LWL CWP` |
| `0x7e8` | `LCB` | Report label `Center of Buoyancy LCB` |
| `0x7f0` | `ATR` | Report label `Immersed Transverse Area of Transom` |
| `0x7f8` | `HB` | Report label `Vertical Center of Bulb Area` |
| `0x800` | `ABT` | Report label `Bulb Area at Station 0` |
| `0x808` | Stern correction candidate | Written to `IN`; not yet tied to a visible report label |
| `0x818` | `Dp` | Report label `Propeller Diameter Dp` |
| `0x820` | `Ae_Ao` | Report label `Propeller Expanded Area Ratio Ae/Ao` |
| `0x828` | `P_Dp` candidate | Propulsion dialog and writer position |
| `0x830` | Propulsion type enum | Writer emits `value + 1`; report selects SSC, SSOF, TS labels |
| `0x838` | Appendage percent candidate | Appendage percent dialog stores scaled value |
| `0x840` | Appendage percent or total candidate | Written to `IN` and report labels appendage drag percent |
| `0x8f8` | Appendage model total candidate | Written to `IN`; likely model-calculated `SAPP(1+K2)` path |
| `0x900` | `depth_at_bow` | Report label `Depth at the Bow` |
| `0x908` | `deckhouse_cargo_frontal_area` | Report label `Deck House/Cargo Frontal Area` |
| `0x910` | `wetted_surface` | Report label `Wetted Surface` |
| `0x918` | `half_angle_entrance` | Report label `Half Angle of Entrance` |
| `0x920` | Air-drag mode | Report selects `Consider Air Drag?` labels |
| `0x924` | Wetted-surface mode | Report selects estimated/user labels |
| `0x928` | Half-angle mode | Report selects estimated/user labels |
| `0x930` | Design margin | Report label `Design Margin on RT, PE, REQ.THR` |
| `0x938` | Water density | Report label `Water Density Rho` |
| `0x940` | Kinematic viscosity | Report label `Kinematic Viscosity Nu` |
| `0x948` | Water type enum | Writer emits `value + 1`; report selects user/fresh/salt labels |
| `0x950` | Initial speed | Run dialog stores values before invoking the writer |
| `0x958` | Speed increment | Run dialog stores values before invoking the writer |

## Candidate Oracle Attempt

A candidate `IN` was generated in `/tmp/ppp-oracle-candidate` from the recovered writer order and the normalized `PPPIN.PPP` sample. A copied `PPPFTRN.EXE` was run under Wine with a 20-second timeout. No files in `PPP-OLD` were modified, and no legacy executable was copied into `PPP-NEW`.

Observed result:

```text
forrtl: severe (6201): **: DOMAIN error
```

No `OUT` report was produced. This is still progress over the empty-file run, which failed with end-of-file on unit 4. The candidate file is text and is read far enough for the Fortran engine to enter a numerical calculation path. The remaining blocker is likely one or more field semantics or enum encodings, not the filename, text format, or gross record count.

## Strong Inferences

- The temporary input filename is uppercase `IN`, not lowercase `In`.
- The report reader opens `Out`, while the Fortran engine writes `OUT`.
- The format is whitespace-delimited text produced by iostream insertion operators.
- The first records are numeric and cover hull characteristics, modeling inputs, hull features, propulsion, appendage mode data, water properties, speed sweep, and design margin.
- The single-space string is reused as the delimiter between numeric values.
- The writer uses stream precision/format manipulation before or between records, so direct reproduction must preserve numeric formatting closely enough for DEC Fortran text reads.

## Next Oracle Step

Use a copied executable outside git, under a temporary working directory, and create candidate `IN` files from the recovered record order. Run `PPPFTRN.EXE` under Wine and compare failures:

1. Start with the normalized `PPPIN.PPP` sample values.
2. Emit whitespace-delimited text records matching the recovered writer shape.
3. Preserve Windows-style case by creating both `IN` and any expected `Out` cleanup target in the temp directory.
4. Run the copied Fortran executable under Wine.
5. If `OUT` is generated, copy only parsed oracle data or plain text fixtures into `PPP-NEW/tests/fixtures/`.

Do not copy legacy executables into `PPP-NEW`.
