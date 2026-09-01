# Heliostat Field Optical Model Reconstruction

[中文](README.md) | [Model assumptions](docs/model-assumptions.md) | [Data provenance](docs/data-provenance.md) | [Paper comparison](docs/paper-comparison.md)

This repository is an evidence-bounded reconstruction inspired by Problem A of the 2023 China Undergraduate Mathematical Contest in Modeling. It was rebuilt from the team paper *Research on Heliostat Parameters Based on a Multi-objective Programming Model* and retained `result2.xlsx` / `result3.xlsx` outputs.

It is **not the original contest code and does not claim numerical reproduction of the paper**.

## Scope

- Solar declination, hour angle, ENU Sun vector, and direct normal irradiance;
- Heliostat normal vectors and cosine efficiency;
- Atmospheric transmittance;
- A documented nearest-neighbour proxy for shadowing and blocking;
- A documented Gaussian-spread approximation for receiver truncation;
- Optical efficiency and field thermal-power summaries at 60 annual sample times;
- A comparison of small public derivatives from the retained result workbooks;
- A deterministic small grid-search example with seed `20230910`.

## Run

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
.venv\Scripts\python -m heliostat_field --output-dir artifacts/demo
```

The demo uses a generated ring layout and does not require the private retained workbooks. Committed figures were produced by the same command.

## Evidence boundary

The original paper, certificate, archive, and Excel files are not published. Because redistribution permission for full team-result workbooks is unclear, this repository contains only deterministic 96-row samples and aggregate statistics. No official contest attachment is included.

The retained workbooks also contain constraint anomalies, so they are treated as historical outputs rather than validated optima. See [data provenance](docs/data-provenance.md) and [paper comparison](docs/paper-comparison.md).

## Award statement

The retained certificate supports this limited statement: Undergraduate Group, Second Prize, Guangdong Division, 2023 China Undergraduate Mathematical Contest in Modeling; Problem A, “Optimization Design of a Heliostat Field.” The certificate image is withheld because it contains personal identifiers and a QR code.

## Limitations

- No standalone original MATLAB/Python project was found.
- Appendix snippets are incomplete and include infeasible-termination logs.
- Shadowing/blocking is not polygonal ray tracing.
- Truncation is not Monte Carlo ray tracing.
- The paper's 60 MW feasibility and reported power values are not validated.
- No plant, hardware, or field measurements were performed.

Reconstruction code is MIT-licensed. Data provenance and reuse limits are documented separately in `data/README.md`.
