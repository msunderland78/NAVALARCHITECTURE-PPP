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
