from __future__ import annotations

import numpy as np

from .config import MirrorLayout, ReceiverConfig


def unit_vectors(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    if np.any(norms == 0.0):
        raise ValueError("zero-length vector is not allowed")
    return vectors / norms


def receiver_directions(
    layout: MirrorLayout, receiver: ReceiverConfig
) -> tuple[np.ndarray, np.ndarray]:
    offsets = receiver.center - layout.centers
    distances = np.linalg.norm(offsets, axis=1)
    return offsets / distances[:, None], distances


def mirror_normals(sun_vector: np.ndarray, receiver_vectors: np.ndarray) -> np.ndarray:
    sun = np.asarray(sun_vector, dtype=float)
    if sun.shape != (3,):
        raise ValueError("sun_vector must have shape (3,)")
    return unit_vectors(receiver_vectors + sun[None, :])


def cosine_efficiency(sun_vector: np.ndarray, normals: np.ndarray) -> np.ndarray:
    values = np.einsum("ij,j->i", normals, np.asarray(sun_vector, dtype=float))
    return np.clip(values, 0.0, 1.0)


def atmospheric_transmittance(distance_m: np.ndarray) -> np.ndarray:
    distance = np.asarray(distance_m, dtype=float)
    eta = 0.99321 - 0.0001176 * distance + 1.97e-8 * distance**2
    return np.clip(eta, 0.0, 1.0)


def truncation_efficiency(
    distance_m: np.ndarray,
    receiver_radius_m: float,
    angular_sigma_rad: float = 0.00465,
) -> np.ndarray:
    """Circular-aperture Gaussian-spread approximation, not ray tracing."""
    if receiver_radius_m <= 0.0 or angular_sigma_rad <= 0.0:
        raise ValueError("receiver radius and angular spread must be positive")
    sigma_on_receiver = np.maximum(np.asarray(distance_m, dtype=float) * angular_sigma_rad, 1e-9)
    ratio = receiver_radius_m / sigma_on_receiver
    return np.clip(1.0 - np.exp(-0.5 * ratio**2), 0.0, 1.0)


def nearest_neighbour_vectors(
    layout: MirrorLayout, neighbours: int = 8
) -> tuple[np.ndarray, np.ndarray]:
    """Return vectors from each mirror to its nearest ground-plane neighbours."""
    count = len(layout)
    if count < 2:
        return np.empty((count, 0, 2)), np.empty((count, 0), dtype=int)
    k = min(neighbours, count - 1)
    xy = np.column_stack([layout.x_m, layout.y_m])
    delta = xy[None, :, :] - xy[:, None, :]
    distance_sq = np.einsum("ijk,ijk->ij", delta, delta)
    np.fill_diagonal(distance_sq, np.inf)
    indices = np.argpartition(distance_sq, kth=k - 1, axis=1)[:, :k]
    vectors = np.take_along_axis(delta, indices[:, :, None], axis=1)
    return vectors, indices


def shadow_blocking_efficiency(
    layout: MirrorLayout,
    sun_vector: np.ndarray,
    receiver_vectors: np.ndarray,
    neighbour_vectors: np.ndarray | None = None,
    neighbour_indices: np.ndarray | None = None,
) -> np.ndarray:
    """Deterministic nearest-neighbour proxy for shadowing and blocking.

    Mirrors are represented by equivalent circular footprints. A neighbour can
    reduce efficiency when it lies upstream toward the Sun or toward the
    receiver. Loss decreases linearly with lateral and longitudinal clearance.
    The model is intentionally bounded and explainable; it is not polygonal ray
    tracing and is documented as such.
    """
    sun = np.asarray(sun_vector, dtype=float)
    if neighbour_vectors is None or neighbour_indices is None:
        neighbour_vectors, neighbour_indices = nearest_neighbour_vectors(layout)
    if neighbour_vectors.shape[1] == 0:
        return np.ones(len(layout))
    neighbour_radius = np.sqrt(layout.areas_m2[neighbour_indices] / np.pi)
    own_radius = np.sqrt(layout.areas_m2 / np.pi)[:, None]
    span = own_radius + neighbour_radius

    def directional_loss(directions: np.ndarray, reach_scale: float) -> np.ndarray:
        direction_xy = directions[:, :2]
        direction_xy = direction_xy / np.maximum(
            np.linalg.norm(direction_xy, axis=1, keepdims=True), 1e-9
        )
        along = np.einsum("ijk,ik->ij", neighbour_vectors, direction_xy)
        lateral_vec = neighbour_vectors - along[:, :, None] * direction_xy[:, None, :]
        lateral = np.linalg.norm(lateral_vec, axis=2)
        reach = span * reach_scale
        candidate = (along > 0.0) & (along < reach) & (lateral < span)
        overlap = (1.0 - lateral / np.maximum(span, 1e-9)) * (1.0 - along / np.maximum(reach, 1e-9))
        return np.max(np.where(candidate, overlap, 0.0), axis=1)

    # A shadowing neighbour lies between the target mirror and the Sun.
    incoming_ground = np.repeat(sun[None, :], len(layout), axis=0)
    altitude_factor = 1.0 + 1.0 / max(abs(sun[2]), 0.15)
    shadow_loss = directional_loss(incoming_ground, reach_scale=altitude_factor)
    blocking_loss = directional_loss(receiver_vectors, reach_scale=2.0)
    combined_loss = np.clip(0.45 * shadow_loss + 0.30 * blocking_loss, 0.0, 0.65)
    return 1.0 - combined_loss
