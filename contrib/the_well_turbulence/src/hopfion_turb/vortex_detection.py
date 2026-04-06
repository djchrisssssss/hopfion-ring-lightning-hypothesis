"""Coherent vortex structure detection for turbulence fields.

Implements multiple vortex identification criteria:
- Q-criterion: Q = (1/2)(|Ω|² - |S|²)
- Enstrophy: ξ = |ω|² = |∇×v|²
- Lambda-2 criterion (Jeong & Hussain 1995)
- Pressure minima cross-validation

References:
    Hunt et al. (1988) CTR Report S88, 193-208 (Q-criterion)
    Jeong & Hussain (1995) J. Fluid Mech. 285, 69-94 (λ₂)
    Haller (2005) J. Fluid Mech. 525, 1-26 (objective vortex detection)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage


@dataclass
class VortexField:
    """Computed vortex identification fields."""

    Q_criterion: NDArray[np.float64]  # Q = (|Ω|² - |S|²) / 2
    enstrophy: NDArray[np.float64]  # ξ = |ω|²
    vorticity: NDArray[np.float64]  # ω = ∇×v, shape (3, Nx, Ny, Nz)
    strain_rate: float  # <|S|²> volume average
    rotation_rate: float  # <|Ω|²> volume average


def compute_velocity_gradient(
    v: NDArray[np.float64],
    dx: float = 1.0,
    periodic: bool = True,
) -> NDArray[np.float64]:
    """Compute velocity gradient tensor ∂v_i/∂x_j.

    Args:
        v: Velocity field, shape (ndim, N1, N2, ...).
        dx: Grid spacing.
        periodic: Whether to use periodic boundary conditions.

    Returns:
        grad_v: Velocity gradient tensor, shape (ndim, ndim, N1, N2, ...).
    """
    ndim = v.shape[0]
    spatial_shape = v.shape[1:]
    grad_v = np.zeros((ndim, ndim) + spatial_shape)

    for i in range(ndim):
        for j in range(ndim):
            if periodic:
                grad_v[i, j] = np.roll(v[i], -1, axis=j) - np.roll(v[i], 1, axis=j)
                grad_v[i, j] /= 2.0 * dx
            else:
                grad_v[i, j] = np.gradient(v[i], dx, axis=j)

    return grad_v


def compute_q_criterion(
    v: NDArray[np.float64],
    dx: float = 1.0,
    periodic: bool = True,
) -> VortexField:
    """Compute Q-criterion and related vortex identification fields.

    Q = (1/2)(|Ω|² - |S|²)

    where Ω = (∇v - ∇vᵀ)/2 (rotation tensor)
    and S = (∇v + ∇vᵀ)/2 (strain rate tensor)

    Vortex core: Q > 0 (rotation dominates strain)

    Args:
        v: Velocity field, shape (ndim, N1, N2, ...) where ndim is 2 or 3.
        dx: Grid spacing.
        periodic: Whether to use periodic BC.

    Returns:
        VortexField with Q-criterion and enstrophy fields.
    """
    ndim = v.shape[0]
    grad_v = compute_velocity_gradient(v, dx, periodic)

    # Symmetric (strain) and antisymmetric (rotation) parts
    S = 0.5 * (grad_v + np.swapaxes(grad_v, 0, 1))
    Omega = 0.5 * (grad_v - np.swapaxes(grad_v, 0, 1))

    # |S|² = S_ij S_ij
    S2 = np.sum(S * S, axis=(0, 1))
    # |Ω|² = Ω_ij Ω_ij
    Omega2 = np.sum(Omega * Omega, axis=(0, 1))

    Q = 0.5 * (Omega2 - S2)

    # Vorticity ω = ∇ × v
    if ndim == 3:
        wx = grad_v[2, 1] - grad_v[1, 2]
        wy = grad_v[0, 2] - grad_v[2, 0]
        wz = grad_v[1, 0] - grad_v[0, 1]
        vorticity = np.stack([wx, wy, wz])
    elif ndim == 2:
        wz = grad_v[1, 0] - grad_v[0, 1]
        vorticity = wz[np.newaxis]  # shape (1, Nx, Ny)
    else:
        raise ValueError(f"Expected 2D or 3D velocity field, got {ndim}D")

    enstrophy = np.sum(vorticity**2, axis=0)

    return VortexField(
        Q_criterion=Q,
        enstrophy=enstrophy,
        vorticity=vorticity,
        strain_rate=float(np.mean(S2)),
        rotation_rate=float(np.mean(Omega2)),
    )


def compute_lambda2(
    v: NDArray[np.float64],
    dx: float = 1.0,
    periodic: bool = True,
) -> NDArray[np.float64]:
    """Compute λ₂ criterion (Jeong & Hussain 1995).

    λ₂ is the second eigenvalue of S² + Ω².
    Vortex core: λ₂ < 0.

    Args:
        v: Velocity field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.
        periodic: Whether to use periodic BC.

    Returns:
        lambda2: Second eigenvalue field, shape (Nx, Ny, Nz).
    """
    if v.shape[0] != 3:
        raise ValueError(f"λ₂ criterion requires 3D velocity field, got {v.shape[0]}D")
    grad_v = compute_velocity_gradient(v, dx, periodic)

    S = 0.5 * (grad_v + np.swapaxes(grad_v, 0, 1))
    Omega = 0.5 * (grad_v - np.swapaxes(grad_v, 0, 1))

    spatial_shape = v.shape[1:]
    lambda2 = np.zeros(spatial_shape)

    # S² + Ω² at each grid point
    # For efficiency, compute the 3x3 symmetric matrix and find eigenvalues
    for idx in np.ndindex(*spatial_shape):
        S_local = S[(slice(None), slice(None)) + idx]
        O_local = Omega[(slice(None), slice(None)) + idx]
        M = S_local @ S_local + O_local @ O_local
        eigvals = np.sort(np.linalg.eigvalsh(M))
        lambda2[idx] = eigvals[1]  # second eigenvalue

    return lambda2


def detect_vortex_cores(
    Q: NDArray[np.float64],
    sigma_threshold: float = 2.0,
    min_volume: int = 4,
) -> tuple[NDArray[np.int32], int]:
    """Detect vortex cores from Q-criterion field.

    Args:
        Q: Q-criterion field, shape (N1, N2, ...).
        sigma_threshold: Threshold in std deviations above mean.
        min_volume: Minimum core volume in grid cells.

    Returns:
        labeled: Labeled array with vortex core IDs.
        n_cores: Number of detected cores.
    """
    mu = np.mean(Q)
    sigma = np.std(Q)

    if sigma < 1e-30:
        return np.zeros_like(Q, dtype=np.int32), 0

    threshold = mu + sigma_threshold * sigma
    mask = Q > threshold

    # Connected-component labeling
    structure = ndimage.generate_binary_structure(Q.ndim, 1)
    labeled, n_features = ndimage.label(mask, structure=structure)

    # Remove small components
    if min_volume > 1:
        for i in range(1, n_features + 1):
            if np.sum(labeled == i) < min_volume:
                labeled[labeled == i] = 0

        # Re-label
        unique_labels = np.unique(labeled)
        unique_labels = unique_labels[unique_labels > 0]
        new_labeled = np.zeros_like(labeled)
        for new_id, old_id in enumerate(unique_labels, 1):
            new_labeled[labeled == old_id] = new_id
        labeled = new_labeled
        n_features = len(unique_labels)

    return labeled, n_features


@dataclass
class VortexCore:
    """Detected vortex core properties."""

    core_id: int
    volume: int  # grid cells
    centroid: tuple[float, ...]
    peak_Q: float
    mean_Q: float
    peak_enstrophy: float
    mean_enstrophy: float
    circulation: float  # Γ = ∫ ω · dA (approximate)
    bbox: tuple[int, ...]


def extract_vortex_properties(
    labeled: NDArray[np.int32],
    Q: NDArray[np.float64],
    enstrophy: NDArray[np.float64],
    vorticity: NDArray[np.float64],
    dx: float = 1.0,
) -> list[VortexCore]:
    """Extract properties of detected vortex cores.

    Args:
        labeled: Labeled vortex core array.
        Q: Q-criterion field.
        enstrophy: Enstrophy field.
        vorticity: Vorticity field, shape (ndim, N1, N2, ...).
        dx: Grid spacing.

    Returns:
        List of VortexCore objects sorted by peak Q.
    """
    n_cores = np.max(labeled)
    cores = []

    for core_id in range(1, n_cores + 1):
        mask = labeled == core_id
        if not np.any(mask):
            continue

        coords = np.argwhere(mask)
        centroid = tuple(float(c) for c in np.mean(coords, axis=0))

        Q_values = Q[mask]
        ens_values = enstrophy[mask]

        # Approximate circulation: Γ ≈ Σ |ω| * dA
        omega_mag = np.sqrt(np.sum(vorticity[:, mask] ** 2, axis=0))
        dA = dx ** 2  # area element (2D area for both 2D and 3D flows)
        circulation = float(np.sum(omega_mag) * dA)

        # Bounding box
        mins = tuple(int(c) for c in coords.min(axis=0))
        maxs = tuple(int(c) for c in coords.max(axis=0))
        bbox = mins + maxs

        cores.append(
            VortexCore(
                core_id=core_id,
                volume=int(np.sum(mask)),
                centroid=centroid,
                peak_Q=float(np.max(Q_values)),
                mean_Q=float(np.mean(Q_values)),
                peak_enstrophy=float(np.max(ens_values)),
                mean_enstrophy=float(np.mean(ens_values)),
                circulation=circulation,
                bbox=bbox,
            )
        )

    cores.sort(key=lambda c: c.peak_Q, reverse=True)
    return cores


def compute_vortex_census(
    v: NDArray[np.float64],
    dx: float = 1.0,
    periodic: bool = True,
    sigma_threshold: float = 2.0,
    min_volume: int = 4,
) -> tuple[list[VortexCore], VortexField]:
    """Full vortex detection pipeline: compute fields → detect → extract properties.

    Args:
        v: Velocity field, shape (ndim, N1, N2, ...).
        dx: Grid spacing.
        periodic: Whether to use periodic BC.
        sigma_threshold: Detection threshold.
        min_volume: Minimum core volume.

    Returns:
        cores: List of VortexCore objects.
        fields: VortexField with computed identification fields.
    """
    fields = compute_q_criterion(v, dx, periodic)

    labeled, n_cores = detect_vortex_cores(
        fields.Q_criterion, sigma_threshold, min_volume
    )

    if n_cores == 0:
        return [], fields

    cores = extract_vortex_properties(
        labeled, fields.Q_criterion, fields.enstrophy, fields.vorticity, dx
    )

    return cores, fields
