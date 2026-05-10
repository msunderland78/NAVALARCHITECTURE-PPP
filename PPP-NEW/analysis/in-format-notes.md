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

The current static pass recovers this broad record structure:

| Writer address range | Observed output shape |
|---|---|
| `0x00404050` to `0x0040409e` | Six floating-point values separated by spaces, then newline |
| `0x004040c6` to `0x00404132` | Four floating-point values separated by spaces, then newline |
| `0x0040414b` to `0x00404218` | Six floating-point values, one integer value, then newline |
| `0x0040423c` to `0x0040425b` | One floating-point value, then a precision or format change |
| `0x0040427b` to `0x004042ca` | Three floating-point values, then a precision or format change |
| `0x004042f4` to `0x0040433a` | Two floating-point values, one integer value, then newline |
| `0x0040435f` to `0x00404397` | Two floating-point values, then a precision or format change |
| `0x004043be` to `0x0040440d` | Two floating-point values, then newline |

The exact semantic mapping of every `CPPPDoc` object offset is not fully recovered. The values align with the legacy dialogs and the serialized `.PPP` document, but assigning each stream column still needs either dynamic tracing under Wine/Windows or a successful `PPPFTRN.EXE` oracle run.

## Strong Inferences

- The temporary input filename is uppercase `IN`, not lowercase `In`.
- The report reader opens `Out`, while the Fortran engine writes `OUT`.
- The format is whitespace-delimited text produced by iostream insertion operators.
- The first records are numeric and likely cover hull characteristics, hull features, propulsion, appendage mode data, water properties, speed sweep, and design margin.
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
