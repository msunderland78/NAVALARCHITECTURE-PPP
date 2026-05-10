# File Format Notes

Version 1.0, May 10, 2026

## Overview

The current legacy file set exposes three important formats:

- Win32 MFC executable shell: `PPP.EXE`
- Win32 DEC Visual Fortran calculation executable: `PPPFTRN.EXE`
- OLE Compound Document saved case: `PPPIN.PPP`

The modern web application should not preserve the executable formats. It should preserve the engineering data and calculation behavior.

## `.PPP` Compound Document

`PPPIN.PPP` uses Microsoft Compound File Binary Format.

Observed header and allocation values:

| Item | Value |
|---|---|
| Signature | `d0 cf 11 e0 a1 b1 1a e1` |
| Sector size | 512 bytes |
| Mini-sector size | 64 bytes |
| Number of FAT sectors | 1 |
| Directory start sector | 2 |
| Mini stream cutoff | 4096 bytes |
| Mini-FAT start sector | 4 |
| Mini-FAT sector count | 1 |
| DIFAT start | `ENDOFCHAIN` |
| DIFAT sector count | 0 |

Directory entries:

| Entry | Type | Start | Size |
|---|---:|---:|---:|
| `Root Entry` | root storage | 5 | 1920 |
| `Contents` | stream | 0 | 1880 |

Chains:

| Chain | Sectors |
|---|---|
| Directory | `2` |
| FAT | `3` |
| Mini-FAT | `4` |
| Root mini-stream | `5, 6, 7, 8` |
| `Contents` mini-stream | mini sectors `0` through `29` |

## `Contents` Stream

The `Contents` stream contains:

- An initial binary state block.
- Inline counted strings.
- Little-endian IEEE-754 double values for the main numeric inputs.
- Later text matching the report strings shown by the GUI.

Known binary prefix values:

| Offset | Type | Value | Meaning |
|---:|---|---:|---|
| `0x0004` | counted string | `Holtrop and Mennen Example` | Project name, text starts at `0x0005` |
| `0x001f` | counted string | `Test 1.0` | Run identification, text starts at `0x0020` |
| `0x0028` | double | `212.0` | LWL, m |
| `0x0030` | double | `32.0` | Beam on LWL, m |
| `0x0038` | double | `11.0` | Draft forward, m |
| `0x0040` | double | `11.0` | Draft aft, m |
| `0x0048` | double | `0.6` | CB |
| `0x0050` | double | `0.98` | CM |
| `0x0058` | double | `0.75` | CWP |
| `0x0060` | double | `-0.75` | LCB, percent LWL from amidships |
| `0x0068` | double | `16.0` | Transom immersed area, m^2 |
| `0x0070` | double | `4.0` | Vertical center of bulb area, m |
| `0x0078` | double | `21.0` | Bulb area, m^2 |
| `0x0088` | int32 | `2` | Stern enum candidate |
| `0x008c` | counted string | `normal shaped sections` | Stern label, text starts at `0x008d` |
| `0x00a3` | double | `8.0` | Propeller diameter, m |
| `0x00ab` | double | `0.8` | Expanded area ratio |
| `0x00bf` | counted string | `single-screw with "conventional" stern` | Propulsion label, text starts at `0x00c0` |
| `0x00e6` | double | `0.05` | Propulsion or margin fraction candidate |
| `0x00ee` | double | `0.05` | Propulsion or appendage fraction candidate |
| `0x01ae` | double | `21.0` | Depth at bow, m |
| `0x01b6` | double | `321.0` | Deckhouse/cargo frontal area, m^2 |
| `0x01be` | double | `7890.0` | Wetted surface, m^2 |
| `0x01c6` | double | `12.11` | Half angle of entrance, degrees |
| `0x01da` | double | `0.05` | Design margin or appendage fraction candidate |
| `0x01e2` | double | `1025.87` | Water density, kg/m^3 |
| `0x01ea` | double | `1.18831e-6` | Kinematic viscosity, m^2/s |
| `0x01f6` | double | `15.0` | Speed-run value candidate |
| `0x01fe` | double | `2.0` | Speed-run value candidate |

Some offset meanings are confirmed by adjacent report labels; others are candidates until the original `In` file layout or a legacy `OUT` oracle is recovered.

## Modern Import Strategy

Implement legacy import as a narrow converter:

1. Detect OLE signature.
2. Parse the FAT, mini-FAT, directory, and `Contents` stream.
3. Extract known binary values by offset for the observed layout.
4. Parse visible report text labels as a fallback.
5. Return normalized JSON for the modern application.
6. Preserve import metadata including source filename, stream size, and parser version.

The importer should fail clearly on unknown layouts instead of pretending to support every possible MFC serialization variant.

## Modern Save Format

The modern application should save JSON, not `.PPP`.

Recommended modern case format:

```json
{
  "schema": "navarch.ppp.case",
  "version": 1,
  "project": {},
  "speed_sweep": {},
  "hull": {},
  "features": {},
  "propulsion": {},
  "appendages": {},
  "modeling": {},
  "water": {},
  "metadata": {}
}
```

Legacy `.PPP` import is a one-way migration path.
