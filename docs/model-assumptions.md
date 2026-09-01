# Model assumptions and equations

## Coordinate system and sampling

The model uses an east-north-up Cartesian frame. The site defaults are latitude `39.4° N`, longitude `98.5° E`, and altitude `3.0 km`. Longitude is retained as provenance metadata; because the contest sampling times are treated as local solar time, it is not used for a civil-time correction.

Annual summaries use the 21st day of each month at local solar times `09:00`, `10:30`, `12:00`, `13:30`, and `15:00` (60 samples).

## Solar position

The declination approximation follows the contest-style formula:

```text
sin(delta) = sin(2*pi*D/365) * sin(23.45 degrees)
omega = pi * (solar_time - 12) / 12
```

The Sun vector is then constructed directly in east-north-up coordinates and normalized. DNI follows the altitude-dependent empirical expression supplied with the 2023 problem, using a solar constant of `1.366 kW/m2`.

## Mirror normal and cosine efficiency

For each mirror, `s` is the unit vector toward the Sun and `r` is the unit vector toward the receiver center. The specular normal is the normalized bisector:

```text
n = (s + r) / ||s + r||
eta_cos = clamp(n dot s, 0, 1)
```

## Atmospheric transmittance

For mirror-to-receiver distance `d` in metres:

```text
eta_at = clamp(0.99321 - 0.0001176*d + 1.97e-8*d^2, 0, 1)
```

## Shadowing and blocking proxy

This implementation deliberately avoids claiming exact ray tracing. It finds up to eight nearest neighbours in the ground plane, represents each mirror by an equivalent-area circular footprint, and checks whether a neighbour lies:

1. upstream in the projected Sun direction (shadowing), or
2. toward the receiver (blocking).

Loss decreases linearly with longitudinal and lateral clearance and is capped at 65%. The weights are `0.45` for shadowing and `0.30` for blocking. This produces a deterministic, bounded diagnostic that is easy to inspect, but it does not model oriented rectangular polygons or multiple-overlap unions.

## Receiver truncation proxy

The receiver is approximated as a circular aperture. Reflected energy uses an isotropic Gaussian angular spread with sigma `4.65 mrad`:

```text
sigma_receiver = distance * angular_sigma
eta_trunc = 1 - exp(-0.5 * (receiver_radius / sigma_receiver)^2)
```

This is not a cylindrical-receiver Monte Carlo model and does not include mirror slope-error calibration from measurements.

## Optical efficiency and thermal power

```text
eta_optical = reflectivity * eta_cos * eta_sb * eta_at * eta_trunc
mirror_power_kW = DNI_kW_m2 * mirror_area_m2 * eta_optical
```

Reflectivity defaults to `0.92`. Values are computed independently for each mirror before aggregation.

## Optimization example

The example performs a deterministic grid search over tower offsets `{-20, 0, 20} m` in each horizontal axis and mirror dimension scales `{0.9, 1.0, 1.1}`. It ranks 27 candidates by mean specific power, with mean field power as a secondary key.

It is intentionally a small verifiable reconstruction. It is not the paper's SQP or genetic algorithm, and it does not claim a feasible 60 MW design.
