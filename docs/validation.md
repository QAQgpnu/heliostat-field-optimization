# Validation strategy

## Automated tests

Tests cover:

- equinox declination and noon hour angle;
- unit-length Sun and mirror-normal vectors;
- morning/afternoon symmetry;
- DNI and efficiency physical bounds;
- atmospheric and truncation distance behaviour;
- deterministic shadow/blocking output;
- layout schema and parameter validation;
- 60-sample annual aggregation;
- deterministic optimization ranking;
- public-data row count, schema, and non-publication manifest.

## What passing tests mean

They show that the implemented formulas, bounds, file schema, and deterministic execution behave as declared. They do not validate the simplified optical model against a ray tracer, an operating solar plant, or the paper's reported power values.

## Reproducibility controls

- declared Python version and dependencies in `pyproject.toml`;
- fixed seed `20230910` even though the current grid search is deterministic;
- no network access in the demo;
- generated layouts and public derivatives have deterministic construction rules;
- CI runs tests, Ruff, the demo, and checks generated files exist.
- CI rejects common secret patterns, private source paths, blocked source-artifact types, and files larger than 2 MiB.
