# Holtrop and Mennen Source Notes

Version 1.0, May 10, 2026

## Purpose

This note records the source trail for reimplementing PPP's resistance and powering calculations. The current legacy strings prove that PPP uses Holtrop and Mennen methods, but the exact coefficient set must be tied to citable literature before the web application is treated as an engineering oracle.

## Primary Source Trail

The Fortran executable contains these visible source strings:

- `Source:1. Holtrop,J., & Mennen, G.G.J., "An`
- `Power Prediction Method," International Shipbuilding`
- `2. Holtrop,J., "A Statistical Reanalysis of`
- `Resistance and Propulsion Data," International`

The corresponding primary publication records are:

| Year | Citation Target | Publication Facts | Use In PPP |
|---:|---|---|---|
| 1978 | Holtrop and Mennen, `A statistical power prediction method` | International Shipbuilding Progress, volume 25, issue 290, pages 253-256, first published October 1, 1978, DOI `10.3233/ISP-1978-2529001`, official record: `https://journals.sagepub.com/doi/abs/10.3233/ISP-1978-2529001` | Background method and propulsion-factor formulas |
| 1982 | Holtrop and Mennen, `An approximate power prediction method` | International Shipbuilding Progress, volume 29, issue 335, pages 166-170, first published July 1, 1982, DOI `10.3233/ISP-1982-2933501`, official record: `https://journals.sagepub.com/doi/10.3233/ISP-1982-2933501` | Main approximate resistance and power prediction method |
| 1984 | Holtrop, `A Statistical Re-Analysis of Resistance and Propulsion Data` | International Shipbuilding Progress, cited directly by PPP strings | Later correction/reanalysis terms likely used by PPP 1.8 |

## Local Manual Evidence

The newly supplied `PPP-OLD/470Manuals.pdf` is a University of Michigan conceptual ship design software manual. It confirms the PPP program identity and intended behavior without requiring the legacy executables at runtime.

Recovered manual evidence:

- Program name/version: `Power Prediction Program (PPP1.8)`.
- Author/date: M. G. Parsons, January 1996.
- Method: Holtrop and Mennen resistance and hull/propeller interaction, with an explicit air-drag estimate added.
- GUI/software environment: Windows Visual C++ interfaces developed by Dr. Jun Li during 1997-1998 under the DARPA COMPASS project.
- Speed sweep: PPP calculates eight speeds from an initial speed and an increment.
- Applicability limits: `CP`, `L/B`, `B/T`, and `Fn`, matching the GUI strings already implemented as checks.
- Resistance structure: `RT` is built from frictional resistance with form factor, wave, appendage, bulb, transom, model-ship correlation, air resistance, and design margin.

The manual strengthens confidence in the output contract and work queue, but exact numerical parity still requires a captured legacy `OUT` oracle.

## Implementation Rule

Only implement a formula when at least one of these is true:

- The formula is directly recovered from a legacy oracle output.
- The formula is traceable to the primary Holtrop/Mennen source set.
- The formula is a standard naval architecture identity, such as Froude number, ITTC-1957 friction coefficient, or effective power.

When a formula is implemented before a legacy `OUT` oracle is available, mark it as source-derived and verify it later against PPP output.

## Already Implemented Source-Safe Terms

The current backend core implements only terms that are unambiguous:

- Ship speed conversion from knots to m/s.
- Mean draft.
- Prismatic coefficient `CP = CB / CM`.
- LCB converted from percent LWL relative to amidships into meters from forward perpendicular.
- Beam-draft ratio.
- LWL-beam ratio.
- Froude number.
- Speed-length ratio.
- Reynolds number using `V * LWL / nu`.
- ITTC-1957 friction coefficient.
- Frictional resistance `RF = 0.5 * rho * V^2 * S * CF` when wetted surface is user supplied.
- Percent appendage resistance when appendage drag is entered as percent of currently implemented bare-hull resistance.
- Equivalent-area appendage resistance using the visible legacy input `Appendage Total SAPP(1+K2)` and the same ITTC friction coefficient already computed for the hull.
- Design-margin resistance as a percentage applied to currently implemented resistance subtotal.
- Effective power from `PE = RT * V / 1000`.
- Legacy GUI applicability checks for `Fn`, `B/T`, `LWL/B`, and `CP`.

## Formula Recovery Work Queue

Recover and implement in this order:

1. Wetted-surface estimation.
2. Form factor `1 + k1`.
3. Frictional resistance `RF`.
4. Appendage resistance `RAPP`.
5. Wave resistance `RW`.
6. Bulbous-bow resistance `RB`.
7. Transom-stern resistance `RTR`.
8. Model-ship correlation allowance `RA`.
9. Air resistance `RAIR`.
10. Total resistance `RT`.
11. Effective power `PE`.
12. Wake fraction `w`.
13. Thrust deduction `t`.
14. Hull efficiency `etaH`.
15. Relative rotative efficiency `etaRR`.
16. Required thrust `REQ.THR`.

## Oracle Requirement

The web application should not be considered numerically equivalent to legacy PPP until a legacy `OUT` report is captured and parsed for the sample case. Until then, source-derived formulas should be tested against independent published examples and marked as provisional.
