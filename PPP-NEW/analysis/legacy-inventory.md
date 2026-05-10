# Legacy Inventory

Version 1.0, May 10, 2026

## Scope

This inventory covers the current archival inputs in `PPP-OLD`. The files are preservation inputs only and must not be modified or required by the final web application.

## File Summary

| File | Size | Type | SHA-256 | Initial Role |
|---|---:|---|---|---|
| `PPP.EXE` | 88576 | PE32 Win32 GUI executable | `4e0808828d86fb241371e1c00dfd346b9b42376ee6e2412646b11d37c8df6304` | MFC GUI shell and report viewer |
| `PPPFTRN.EXE` | 257536 | PE32 Win32 console executable | `b859fb2fa4711f0fe21579235b058823cfe6d948ae71654df722a51e788eafcf` | Fortran calculation engine |
| `PPPIN.PPP` | 5120 | OLE Compound Document | `e0c3afe94335324737fa6915cb5c2a5b6eb4871724623ce5a01bd422b3f12591` | Saved Holtrop and Mennen sample document |
| `470Manuals.pdf` | 3198387 | PDF document, 52 pages | `53212238da3cfb20d4b0cd2be07722431947ed1ea37b03b44071e258d8aa3524` | University of Michigan conceptual ship design program manual |
| `FINDER.DAT` | 276 | Finder metadata/data file | `6de24001b67fe6535ca5fd43e50b34dec0e8a37ad1ea29318740cc45053d14d4` | Macintosh/archival metadata candidate |
| `Hollenbach (R3).xls` | 45568 | Excel workbook | `2d4bdb2f800c55ffa7276de2d13b8ee3bc82e3fae3bf28b5f8b5fc272eeca624` | Hollenbach resistance and hull-propeller interaction spreadsheet |
| `PowerEstimation(R5).xls` | 7045 | Excel workbook | `bd30703f3594005b3b002b3013d27561c40b9933779144aa1b265b17403ad43d` | Preliminary shaft power estimate spreadsheet |

## `PPP.EXE`

`PPP.EXE` is a PE32 executable for Intel 80386 with Windows GUI subsystem.

Important executable facts:

- Timestamp: February 26, 1998
- Linker version: 4.20
- Entry point: `0x00409420`
- Image base: `0x00400000`
- Sections: `.text`, `.rdata`, `.data`, `.idata`, `.rsrc`, `.reloc`
- Resource section present
- Debug symbols stripped
- Base relocations present

Imports:

- `MFC40.DLL`
- `MSVCRT40.dll`
- `KERNEL32.dll`
- `USER32.dll`
- `GDI32.dll`

Notable imported behavior:

- C++ iostream file I/O through `ifstream` and `ofstream`
- C runtime `system`
- `Sleep`
- Basic window and drawing APIs

Interpretation:

`PPP.EXE` is the document-oriented user interface. It most likely serializes `.PPP` documents, writes a temporary `IN` file, invokes `PPPFTRN.exe`, then reads `Out` for display and printing.

## `PPPFTRN.EXE`

`PPPFTRN.EXE` is a PE32 executable for Intel 80386 with Windows console subsystem.

Important executable facts:

- Timestamp: January 7, 1998
- Linker version: 5.0
- Entry point: `0x00424b40`
- Image base: `0x00400000`
- Sections: `.text`, `.rdata`, `.data`, `.idata`
- Debug symbols stripped
- Relocations stripped
- No resource section

Imports:

- `KERNEL32.dll`

Notable imported behavior:

- File open/read/write/delete APIs
- Process execution APIs
- Console and process APIs
- Heap and codepage APIs

Runtime evidence:

- `DEC Fortran RTL Message Catalog V1.1-14 07-Jan-1997`
- `DFORMSG.DLL`
- `FORTRAN`
- `CONOUT$`

Interpretation:

`PPPFTRN.EXE` is the numerical engine. It appears to be built with DEC Visual Fortran or an early related Visual Fortran toolchain. It reads legacy input, computes Holtrop and Mennen resistance and powering tables, and writes `OUT`.

## `PPPIN.PPP`

`PPPIN.PPP` is an OLE Compound Document file.

Important format facts:

- Header signature: `d0 cf 11 e0 a1 b1 1a e1`
- Sector size: 512 bytes
- Mini-sector size: 64 bytes
- Directory stream starts at sector 2
- FAT sector: 3
- Mini-FAT sector: 4
- Root mini-stream chain: sectors 5, 6, 7, 8
- Directory entries: `Root Entry`, `Contents`
- `Contents` stream size: 1880 bytes

Interpretation:

The `Contents` stream is an MFC-style serialized document. The first part contains binary values and short strings. The latter part contains a saved text report summary. The modern importer should parse this stream into JSON and never require the old MFC runtime.

## `470Manuals.pdf`

`470Manuals.pdf` is a 52-page manual for the University of Michigan conceptual ship design software environment. Dependency-free stream extraction recovered readable text from the PDF.

Important PPP evidence:

- Identifies `Power Prediction Program (PPP1.8)`.
- Attributes PPP to M. G. Parsons, January 1996.
- Confirms the method is Holtrop and Mennen with Holtrop's later statistical reanalysis.
- Confirms the Windows GUI work was developed during 1997-1998 by Dr. Jun Li for the DARPA COMPASS project.
- Confirms PPP was originally part of the NA470/NA475 conceptual ship design teaching toolset.
- Confirms PPP calculates eight speeds from initial speed and speed increment.
- Confirms the resistance composition used by PPP: frictional, form, appendage, wave, bulb, transom, model-ship correlation, air resistance, and design margin.
- Confirms the applicability checks already recovered from GUI strings: `CP`, `L/B`, `B/T`, and `Fn`.

This manual is useful for product behavior and formula-source context, but it is not a substitute for a captured `OUT` oracle from `PPPFTRN.EXE`.

## `Hollenbach (R3).xls`

`Hollenbach (R3).xls` is an Excel workbook authored by Michael G. Parsons. Visible strings identify it as Hollenbach's resistance and hull-propeller interaction prediction spreadsheet.

Important visible evidence:

- References Hollenbach's 1999 ICCAS method.
- Contains input/output labels for `LPP`, `LWL`, `LOS`, `Cb`, drafts, appendage factors, wetted surface, Reynolds number, ITTC-57 friction, correlation allowance, resistance, effective power, and hull-propeller interaction terms.
- It is relevant to the wider naval architecture conversion project but is not direct evidence for PPP's Holtrop/Mennen numerical engine.

## `PowerEstimation(R5).xls`

`PowerEstimation(R5).xls` is an Excel workbook for preliminary shaft power estimates.

Important visible evidence:

- References Harvald, Watson, and Silverleaf/Dawson methods.
- Contains labels for service margin, Admiralty coefficient, delivered horsepower, trials shaft power, and required shaft power.
- It is useful as a related preliminary powering reference but is not direct evidence for PPP's Holtrop/Mennen implementation.

## `FINDER.DAT`

`FINDER.DAT` appears to be a small metadata/data artifact associated with old Macintosh or archived spreadsheet files. It is not currently required for PPP conversion.

## Hardware Lock Check

No lock indicator was found in the current static pass.

Checked indicators:

- No visible `HASP`
- No visible `Sentinel`
- No visible `Rainbow`
- No visible `Wibu`
- No visible `CodeLock`
- No visible `Aladdin`
- No visible `SafeNet`
- No lock-driver DLL imports

No `BYPASS` folder is needed for the current artifacts.
