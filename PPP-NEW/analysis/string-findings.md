# String Findings

Version 1.0, May 10, 2026

## Purpose

This note records the important static strings recovered from the current PPP binaries and sample file. It separates observed evidence from implementation inference.

## `PPP.EXE` Identity Strings

Observed:

- `Power Prediction Program`
- `PPP Version 1.0`
- `PPP Interface 1.0 - Visual C++ by Dr. Jun Li`
- `Developed under the COMPASS Project Sponsored`
- `by DARPA through Intergraph Federal Systems`
- `Department of Naval Architecture and Marine Engineering`
- `University of Michigan`
- `PPP MFC Application`
- `PPP Application`
- `PPP.Document`
- `PPP Document`

Inference:

The GUI was built as an MFC document/view application with OLE document support.

## `PPP.EXE` Execution Strings

Observed:

- `del Out`
- `del In`
- `PPPFTRN.exe`
- `PPP failed. Please check your input data,`
- ` or whether you have a PPPFTRN.exe file in the folder.`
- `Please check and adjust relevant data before running PPP.`

Inference:

The GUI deletes stale temporary files, writes a temporary input file, invokes the Fortran executable, then reads the generated report file.

## `PPP.EXE` Menu and Dialog Strings

Observed menu areas:

- `Project Name`
- `Hull Characters`
- `Hull Features`
- `Propulsion Factors Model`
- `Appendages`
- `% Bare Hull Resistance`
- `Model Calculation`
- `Modeling`
- `Design Margin`
- `Water Properties`
- `Run...`
- `Report`
- `MS Excel`
- `MS Word`

Observed hull-characteristic fields:

- `Length on waterline (LWL):`
- `Maximum beam on LWL (B):`
- `Draft forward (TF):`
- `Draft aft (TA):`
- `Block coefficient on LWL (CB):`
- `Midship coefficient to LWL (CM):`
- `Waterplane coefficient on LWL (CWP):`
- `Longitudinal center of buoyancy (LCB):`
- `(in % LWL from amidships; + forward)`

Observed hull-feature fields:

- `Pram with gondola`
- `V-shaped sections`
- `Normally shaped sections`
- `U-shaped sections with Hogner stern`
- `Transverse bulb area at Station 0 (ABT):`
- `Vertical center of bulb area at Station 0 (HB):`
- `Immersed transverse area of transom at zero speed (ATR):`

Observed propulsion fields:

- `Single-screw with "conventional" stern (SSC)`
- `Single-screw with "open" flow stern (SSOF)`
- `Twin screw (TS)`
- `Propeller diameter (Dp):`
- `Propeller expanded area ratio (Ae/Ao):`
- `Propeller pitch diameter ratio (P/Dp):`

Observed appendage fields:

- `Appendage drag =`
- `% bare hull resistance`
- `sum((1+K2[i])*SAPP[i])`
- `Rudder behind stern (skeg):`
- `Twin-screw balance rudders:`
- `Shaft brackets:`
- `Skeg:`
- `Strut (hull) bossings:`
- `Exposed shafts:`
- `Stabilizer fins:`
- `Sonar dome:`
- `Bilge keels:`
- `Other:`
- `Tunnel diameter:`
- `Tunnel drag coefficient:`

Observed modeling fields:

- `Air Drag?`
- `Depth at the bow:`
- `Frontal area of the deckhouse`
- `and cargo above the hull:`
- `Hull wetted surface:`
- `Half angle of entrance:`
- `Estimated by PPP`
- `Input by user`

Observed water and margin fields:

- `Salt water at 15 degrees Celsius`
- `Fresh water at 15 degrees Celsius`
- `Input other values`
- `Water density (Rho):`
- `Kinematic Viscosity (Nu):`
- `Design margin as percent (DMAR):`

Observed run fields:

- `Initial ship speed:`
- `Speed Increment:`
- `Run identifier:`
- `knots`

## `PPP.EXE` Validation Strings

Observed:

- `Fn(Vk = %.2f) = %.4f is out of bounds (0.00 < Fn < 1.00).`
- `B/T = %.2f is out of bounds (2.10 < B/T < 4.00).`
- `LWL/B = %.2f is out of bounds (3.90 < LWL/B < 14.9).`
- `Cp(= CB/CM) = %.4f is out of bounds (0.55 < Cp <0.85).`

Implementation action:

The modern validation layer should reproduce these applicability checks.

## `PPPFTRN.EXE` Identity Strings

Observed:

- `Power Prediction Program (PPP-1.8) by M. G. Parsons`
- `Source:1. Holtrop,J., & Mennen, G.G.J., "An`
- `Power Prediction Method," International Shipbuilding`
- `2. Holtrop,J., "A Statistical Reanalysis of`
- `Resistance and Propulsion Data," International`

Inference:

The calculation method is Holtrop and Mennen resistance and powering prediction, likely with later statistical reanalysis terms.

## `PPPFTRN.EXE` Report Strings

Observed report sections:

- `Input Verification:`
- `Speed, Resistance Coefficients`
- `and Frictional Resistance RF(N):`
- `Remaining Resistance Components (N):`
- `Resistance, Effective Power, Propulsion Factors`
- `and Required Thrust`

Observed result columns:

- `V(kts)`
- `V(m/s)`
- `FN`
- `SLRATIO`
- `CF`
- `CR`
- `CA`
- `RF`
- `RF*K1`
- `RAPP`
- `RW`
- `RB`
- `RTR`
- `RA`
- `RAIR`
- `RT(N)`
- `PE(kW)`
- `w`
- `t`
- `REQ.THR(N)`
- `etaH`
- `etaRR`

Implementation action:

The first calculation core should return every visible report column, even when some values are also used only as intermediate checks.

## `PPPFTRN.EXE` Runtime and Error Strings

Observed:

- `DEC Fortran RTL Message Catalog V1.1-14 07-Jan-1997`
- `DFORMSG.DLL`
- `FORTRAN`
- `Run time error. Hit Return to see error message ...`
- `Check data for CB, CM and LCB.`
- `Error of taking sqare root of a negative number.`
- `TLOSS error`
- `SING error`
- `DOMAIN error`
- `Calculation Completed Successfully!`

Inference:

The original numerical engine is Fortran with direct mathematical domain checks and broad runtime error paths. The modern implementation should make invalid-domain checks explicit at input validation or per-speed result generation.

## `PPPIN.PPP` Visible Strings

Observed:

- `Holtrop and Mennen Example`
- `Test 1.0`
- `Project Name:  Holtrop and Mennen Example`
- `Run Identification:  Test 1.0`
- `Length of Waterline LWL (meters) = 212.00`
- `Maximum Beam on LWL B (meters) = 32.00`
- `Draft Forward TF (meters) = 11.00`
- `Draft Aft TA (meters) = 11.00`
- `Block Coefficient on LWL CB = 0.6000`
- `Midship Coefficient to LWL CM = 0.9800`
- `Waterplane Coefficient on LWL CWP = 0.7500`
- `Center of Buoyancy LCB (percent LWL from amidships; + FWD) = -0.75`
- `Bulb Area at Station 0 (meters^2) = 21.00`
- `Vertical Center of Bulb Area at Station 0 (meters) = 4.00`
- `Immersed Transverse Area of Transom at Zero Speed (meters^2) = 16.00`
- `Stern Type = normal shaped sections`
- `Propulsion Type = single-screw with "conventional" stern`
- `Propeller Diameter Dp (meters) = 8.00`
- `Propeller Expanded Area Ratio Ae/Ao = 0.8000`
- `Consider Air Drag? Yes.`
- `Depth at the Bow (meters) = 21.00`
- `Deck House/Cargo Frontal Area (meters^2) = 321.00`
- `Wetted Surface (meters^2) = 7890.00`
- `Half Angle of Entrance (degrees) = 12.11`
- `Design Margin on RT, PE, REQ.THR (percent) = 5.00`
- `Water Properties: Salt Water at 15 degrees Celsius`
- `Water Density Rho (kg/m^3) = 1025.870`
- `Kinematic Viscosity Nu (m^2/sec) = 1.188310e-006`
- `Appendage Drag as Percent Bare Hull Resistance (percent) = 5.00`
