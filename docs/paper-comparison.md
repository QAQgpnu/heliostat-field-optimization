# Comparison with the 2023 team paper

## Evidence retained in the paper

The appendix contains a short Python plotting fragment and MATLAB fragments for annual power calculation, SQP (`fmincon`) constraints, and a genetic-algorithm example. It also records unsuccessful solver status:

- SQP: terminated at an infeasible point;
- genetic algorithm: no feasible point found.

Several variables are incomplete or inconsistent in the extracted appendix. The standalone source files were not found, so those fragments are treated as historical evidence rather than directly reused production code.

## What is reconstructed

| Topic | Paper | This repository |
|---|---|---|
| Solar position | Formula-driven model | Tested ENU vector implementation using contest-style declination |
| DNI | Empirical altitude formula | Implemented with explicit kW/m2 units |
| Mirror normal | Vector/reflection discussion | Normalized Sun/receiver bisector |
| Cosine efficiency | Reported monthly values | Per-mirror calculation at 60 sample times |
| Atmospheric loss | Distance polynomial | Implemented and clamped to physical bounds |
| Shadow/blocking | Random-point geometric discussion | Deterministic nearest-neighbour analytic proxy |
| Truncation | Reported/approximated values | Gaussian-spread circular-aperture proxy |
| Problem 2 optimization | SQP fragment; infeasible termination recorded | Small deterministic tower/size grid search |
| Problem 3 optimization | GA fragment; no feasible point recorded | Not claimed as reproduced |
| Retained layouts | `result2/result3` | Small derivatives and full-workbook aggregate audit |

## Numerical claims not reproduced

The paper reports, among other values, annual mean powers and specific powers that are dimensionally or internally inconsistent in places. This repository does not tune parameters to match them and does not treat them as test fixtures.

In particular:

- paper values labelled `kW/m2` sometimes exceed plausible DNI by orders of magnitude;
- the appendix divides scalar efficiencies by the number of mirrors in one annual-efficiency expression;
- solver logs record infeasible termination;
- retained layouts contain clearance and duplicate-coordinate anomalies.

These points do not invalidate the award evidence. They limit what can honestly be claimed about numerical reproduction.

## Correct claim for portfolio use

> Rebuilt a tested Python heliostat-field optical model from a 2023 team paper and retained result tables, documented model approximations and data-quality constraints, and added reproducible visualizations and a deterministic optimization example.

Avoid claims such as “fully reproduced the competition solution,” “original competition code,” or “validated a 60 MW optimal field.”
