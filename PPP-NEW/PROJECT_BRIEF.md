# Power Prediction Program (PPP) Modernization Brief

Version 1.0, May 10, 2026

## Project Purpose

This project reviews the legacy Power Prediction Program (PPP), originally built for 32-bit Windows-era environments, and defines how to convert or reimplement it as a modern web application deployable on an Ubuntu Linux server behind an NGINX container.

The target result is a self-contained web application using a modern frontend and backend stack appropriate to the recovered computation model. Preferred targets include React, Next.js, plain HTML and JavaScript, Python, Node.js, Rust, or WebAssembly.

## Engineering Role

The work should be performed from the perspective of a naval architecture software engineer familiar with legacy engineering programs from the 1990s and early 2000s.

Expected domain knowledge includes:

- Hull design tools
- Hydrostatics and stability calculations
- Resistance and powering prediction
- Propeller and powering workflows
- Structural analysis
- Seakeeping analysis
- Legacy desktop engineering workflows

Expected legacy platform knowledge includes:

- DOS
- Windows 3.x
- Windows 95, 98, NT, and 32-bit Windows
- Fortran
- C
- C++
- Delphi
- Visual Basic
- Early Windows runtimes and installers

## Repository Layout Rules

Legacy files must remain in folders ending with `-OLD`.

New implementation files must be created only in folders ending with `-NEW`.

The current project layout is:

- `PPP-OLD`: original legacy PPP files
- `PPP-NEW`: new documentation, analysis, source code, tests, and web application files

Files in folders ending with `-OLD` are archival inputs only. They must not be changed and must not be required by the final software product.

Folders ending with `-OLD` should be ignored by git. If a git repository is initialized later, add an ignore rule for `*-OLD/`.

## Legacy Review Workflow

For each legacy program under review:

1. Identify the original programming language.
2. Identify the compiler, linker, and runtime dependencies.
3. Inspect executable format, imports, strings, resources, overlays, and installer artifacts.
4. Determine whether the application is DOS, Win16, Win32, or another runtime target.
5. Identify input files, output files, binary data formats, configuration files, and working directory assumptions.
6. Recover the calculation workflow and call graph.
7. Separate user interface behavior from core engineering computation.
8. Determine whether the computational core can be cleanly ported or should be wrapped temporarily.
9. Recreate required algorithms, file formats, and test cases in `PPP-NEW`.
10. Verify the new implementation against known legacy inputs and outputs.

## Hardware Lock Investigation

Some legacy engineering applications from this period used hardware locks or software license checks, including HASP, Sentinel, Rainbow, Wibu, CodeLock, and similar systems.

When a lock is encountered, document:

- Lock family and probable product generation, such as HASP HL, Sentinel SuperPro, Rainbow, Wibu, or CodeLock
- Evidence used for identification
- Relevant binaries, DLLs, drivers, installer artifacts, import names, and string references
- Where the check appears in the execution flow
- What the check gates, such as startup, file loading, calculation routines, export, print, or save
- Whether the check affects engineering computation or only license enforcement
- How the modern reimplementation replaces the licensing dependency with a clean internal interface

This work is authorized reverse engineering for preservation, analysis, and modernization of software owned or lawfully held for this project. The purpose is not piracy, redistribution, or use of unauthorized licensed software.

When testing requires lock analysis, create a root-level `BYPASS` folder and place all lock-analysis support code, notes, extracted call traces, emulator stubs, or oracle test harnesses there. Do not mix lock-analysis artifacts into the production web application.

The production replacement must not depend on the original dongle, original lock driver, copied license state, or patched legacy executable.

## Conversion Strategy

Prefer clean reimplementation of the mathematics and engineering workflow when the algorithms can be recovered or are documented.

Use wrapping or emulation only when it is necessary to preserve behavior while the algorithm is still being recovered.

Acceptable interim wrapping strategies include:

- Wine for Win32 binaries
- DOSBox for DOS binaries
- x86 emulation where needed
- Isolated backend execution behind a controlled API
- Legacy-output oracle comparison during reimplementation

Preferred final strategies include:

- Fortran to Python, Rust, or WebAssembly
- C or C++ numerical kernels to Rust, C++, Python extensions, or WebAssembly
- Visual Basic workflows to TypeScript and backend services
- Delphi workflows to TypeScript, Python, or Rust
- Plain HTML and JavaScript for small interactive tools
- React or Next.js for larger browser applications

## Web Application Target

The modern PPP application should be deployable on:

- Ubuntu Linux server
- NGINX container
- Static frontend or containerized frontend service
- Backend service only when required for computation, persistence, file conversion, or batch processing

The web application should be self-contained and should not require the original files in `PPP-OLD`.

Expected application capabilities may include:

- Vessel and operating-condition inputs
- Resistance and powering calculation execution
- Result tables
- Performance curves
- Import of recreated input formats
- Export of modern result formats
- Regression tests against known PPP outputs

## Coding Defaults

Use the existing project structure and keep changes scoped.

Do not change files in folders ending with `-OLD`.

Create new files in folders ending with `-NEW`.

Do not add comments unless the reason is non-obvious.

Do not add docstrings or multi-line comment blocks.

Do not add error handling or abstractions beyond what the task requires.

Prefer direct, readable implementation over speculative frameworks.

Use structured parsing for recovered file formats when practical.

Keep legacy compatibility tests focused on known inputs and outputs.

## Analysis Deliverables

For each reviewed executable or module, produce documentation in `PPP-NEW` covering:

- Program identity
- File inventory
- Platform and executable format
- Compiler or runtime clues
- Dependency list
- Input and output files
- Calculation workflow
- Recovered formulas or algorithms
- Hardware or software lock findings
- Reimplementation recommendation
- Test oracle plan
- Web application integration plan

## Current Legacy Inputs

The current archival folder contains:

| File | Size | Type | SHA-256 | Role |
|---|---:|---|---|---|
| `PPP.EXE` | 88576 | PE32 Win32 GUI executable | `4e0808828d86fb241371e1c00dfd346b9b42376ee6e2412646b11d37c8df6304` | Legacy PPP user interface or shell |
| `PPPFTRN.EXE` | 257536 | PE32 Win32 console executable | `b859fb2fa4711f0fe21579235b058823cfe6d948ae71654df722a51e788eafcf` | Legacy PPP numerical engine candidate |
| `PPPIN.PPP` | 5120 | OLE Compound Document | `e0c3afe94335324737fa6915cb5c2a5b6eb4871724623ce5a01bd422b3f12591` | Legacy PPP input or saved document candidate |

These files are investigation inputs only. They must remain in `PPP-OLD` and must not be modified.

## Reference Project

Use `/home/sundema/CLAUDE-AI-PROJECTS/CODEX-NAVARCH-POP` as the completed reference project for structure, documentation style, analysis workflow, test strategy, and final web deployment pattern.
