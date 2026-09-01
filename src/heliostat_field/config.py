from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SiteConfig:
    latitude_deg: float = 39.4
    longitude_deg: float = 98.5
    altitude_km: float = 3.0

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError("latitude_deg must be within [-90, 90]")
        if not -180.0 <= self.longitude_deg <= 180.0:
            raise ValueError("longitude_deg must be within [-180, 180]")
        if self.altitude_km < 0.0:
            raise ValueError("altitude_km must be non-negative")


@dataclass(frozen=True)
class ReceiverConfig:
    tower_x_m: float = 0.0
    tower_y_m: float = 0.0
    receiver_center_z_m: float = 84.0
    receiver_radius_m: float = 3.5
    receiver_height_m: float = 8.0

    def __post_init__(self) -> None:
        if self.receiver_center_z_m <= 0.0:
            raise ValueError("receiver_center_z_m must be positive")
        if self.receiver_radius_m <= 0.0 or self.receiver_height_m <= 0.0:
            raise ValueError("receiver dimensions must be positive")

    @property
    def center(self) -> np.ndarray:
        return np.array([self.tower_x_m, self.tower_y_m, self.receiver_center_z_m])


@dataclass(frozen=True)
class MirrorLayout:
    mirror_id: np.ndarray
    x_m: np.ndarray
    y_m: np.ndarray
    z_m: np.ndarray
    width_m: np.ndarray
    height_m: np.ndarray

    def __post_init__(self) -> None:
        arrays = [
            np.asarray(self.mirror_id),
            np.asarray(self.x_m, dtype=float),
            np.asarray(self.y_m, dtype=float),
            np.asarray(self.z_m, dtype=float),
            np.asarray(self.width_m, dtype=float),
            np.asarray(self.height_m, dtype=float),
        ]
        size = len(arrays[0])
        if size == 0 or any(len(item) != size for item in arrays):
            raise ValueError("layout arrays must have the same non-zero length")
        numeric = arrays[1:]
        if any(not np.all(np.isfinite(item)) for item in numeric):
            raise ValueError("layout values must be finite")
        if np.any(arrays[4] <= 0.0) or np.any(arrays[5] <= 0.0):
            raise ValueError("mirror dimensions must be positive")
        if np.any(arrays[3] <= 0.0):
            raise ValueError("mirror center heights must be positive")
        for field, value in zip(self.__dataclass_fields__, arrays):
            object.__setattr__(self, field, value)

    def __len__(self) -> int:
        return len(self.mirror_id)

    @property
    def centers(self) -> np.ndarray:
        return np.column_stack([self.x_m, self.y_m, self.z_m])

    @property
    def areas_m2(self) -> np.ndarray:
        return self.width_m * self.height_m
