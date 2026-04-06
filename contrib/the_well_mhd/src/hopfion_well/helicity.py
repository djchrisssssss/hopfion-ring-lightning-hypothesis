"""Magnetic helicity computation for MHD fields on periodic domains.

Implements spectral methods to compute:
- Vector potential A from magnetic field B (Coulomb gauge)
- Magnetic helicity density h(x) = A(x) · B(x)
- Global magnetic helicity H_m = ∫ h(x) d³x
- Normalized Hopf charge Q_H = H_m / (4π)²

References:
    Woltjer (1958) PNAS 44, 489-491
    Moffatt (1969) J. Fluid Mech. 35, 117-129
    Berger & Field (1984) J. Fluid Mech. 147, 133-148
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class HelicityResult:
    """Result of magnetic helicity computation for a single snapshot."""

    helicity_density: NDArray[np.float64]  # h(x) = A · B, shape (Nx, Ny, Nz)
    global_helicity: float  # H_m = ∫ h(x) d³x
    hopf_charge: float  # Q_H = H_m / (4π)²
    vector_potential: NDArray[np.float64]  # A(x), shape (3, Nx, Ny, Nz)
    magnetic_field: NDArray[np.float64]  # B(x), shape (3, Nx, Ny, Nz)


def build_k_grid(
    shape: tuple[int, int, int],
    dx: float = 1.0,
) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """Build wavenumber grid for a 3D periodic domain.

    Args:
        shape: Grid dimensions (Nx, Ny, Nz).
        dx: Grid spacing (uniform, isotropic).

    Returns:
        kx, ky, kz: Wavenumber arrays, each shape matching rfft output.
        k2: |k|² array with k=0 set to 1.0 to avoid division by zero.
    """
    nx, ny, nz = shape
    kx = np.fft.fftfreq(nx, d=dx) * 2 * np.pi
    ky = np.fft.fftfreq(ny, d=dx) * 2 * np.pi
    kz = np.fft.rfftfreq(nz, d=dx) * 2 * np.pi

    kx_3d, ky_3d, kz_3d = np.meshgrid(kx, ky, kz, indexing="ij")
    k2 = kx_3d**2 + ky_3d**2 + kz_3d**2
    k2[0, 0, 0] = 1.0  # avoid div-by-zero; A(k=0) = 0 anyway

    return kx_3d, ky_3d, kz_3d, k2


def compute_vector_potential(
    B: NDArray[np.float64],
    dx: float = 1.0,
) -> NDArray[np.float64]:
    """Compute vector potential A from magnetic field B in Coulomb gauge.

    Uses spectral method on periodic domain:
        B̂(k) = ik × Â(k)  →  Â(k) = -ik × B̂(k) / |k|²

    The Coulomb gauge (∇·A = 0) is automatically satisfied since
    k · Â(k) = 0 by construction.

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.

    Returns:
        A: Vector potential, shape (3, Nx, Ny, Nz).
    """
    assert B.ndim == 4 and B.shape[0] == 3, f"Expected shape (3, Nx, Ny, Nz), got {B.shape}"
    shape = B.shape[1:]

    kx, ky, kz, k2 = build_k_grid(shape, dx)

    # FFT each component of B
    Bx_hat = np.fft.rfftn(B[0])
    By_hat = np.fft.rfftn(B[1])
    Bz_hat = np.fft.rfftn(B[2])

    # From ik × Â = B̂ and Coulomb gauge k·Â = 0:
    #   Â = i(k × B̂) / |k|²
    # (k × B̂)_x = ky * Bz_hat - kz * By_hat
    # (k × B̂)_y = kz * Bx_hat - kx * Bz_hat
    # (k × B̂)_z = kx * By_hat - ky * Bx_hat
    Ax_hat = 1j * (ky * Bz_hat - kz * By_hat) / k2
    Ay_hat = 1j * (kz * Bx_hat - kx * Bz_hat) / k2
    Az_hat = 1j * (kx * By_hat - ky * Bx_hat) / k2

    # Zero mode: A(k=0) = 0 (no net flux)
    Ax_hat[0, 0, 0] = 0.0
    Ay_hat[0, 0, 0] = 0.0
    Az_hat[0, 0, 0] = 0.0

    A = np.stack([
        np.fft.irfftn(Ax_hat, s=shape),
        np.fft.irfftn(Ay_hat, s=shape),
        np.fft.irfftn(Az_hat, s=shape),
    ])

    return A


def compute_helicity_density(
    A: NDArray[np.float64],
    B: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute magnetic helicity density h(x) = A(x) · B(x).

    Args:
        A: Vector potential, shape (3, Nx, Ny, Nz).
        B: Magnetic field, shape (3, Nx, Ny, Nz).

    Returns:
        h: Helicity density, shape (Nx, Ny, Nz).
    """
    return np.sum(A * B, axis=0)


def compute_magnetic_helicity(
    B: NDArray[np.float64],
    dx: float = 1.0,
) -> HelicityResult:
    """Compute full magnetic helicity analysis for a single snapshot.

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.

    Returns:
        HelicityResult with all computed quantities.
    """
    A = compute_vector_potential(B, dx)
    h = compute_helicity_density(A, B)

    dV = dx**3
    H_m = float(np.sum(h) * dV)
    Q_H = H_m / (4 * np.pi) ** 2

    return HelicityResult(
        helicity_density=h,
        global_helicity=H_m,
        hopf_charge=Q_H,
        vector_potential=A,
        magnetic_field=B,
    )


def compute_helicity_timeseries(
    B_timeseries: NDArray[np.float64],
    dx: float = 1.0,
) -> dict[str, NDArray]:
    """Compute magnetic helicity over a time series of B-field snapshots.

    Args:
        B_timeseries: Magnetic field time series, shape (T, 3, Nx, Ny, Nz).
        dx: Grid spacing.

    Returns:
        Dictionary with:
            'H_m': Global helicity array, shape (T,)
            'Q_H': Hopf charge array, shape (T,)
            'h_rms': RMS helicity density, shape (T,)
    """
    T = B_timeseries.shape[0]
    H_m = np.zeros(T)
    Q_H = np.zeros(T)
    h_rms = np.zeros(T)

    for t in range(T):
        result = compute_magnetic_helicity(B_timeseries[t], dx)
        H_m[t] = result.global_helicity
        Q_H[t] = result.hopf_charge
        h_rms[t] = float(np.sqrt(np.mean(result.helicity_density**2)))

    return {"H_m": H_m, "Q_H": Q_H, "h_rms": h_rms}


def compute_cross_helicity(
    v: NDArray[np.float64],
    B: NDArray[np.float64],
    dx: float = 1.0,
) -> float:
    """Compute cross-helicity H_c = ∫ v · B d³x.

    Cross-helicity measures alignment between velocity and magnetic field.
    It is an ideal MHD invariant and indicates Alfvénic correlation.

    Args:
        v: Velocity field, shape (3, Nx, Ny, Nz).
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.

    Returns:
        H_c: Cross-helicity (scalar).
    """
    dV = dx**3
    return float(np.sum(v * B) * dV)


def compute_relative_helicity(
    B: NDArray[np.float64],
    dx: float = 1.0,
) -> float:
    """Compute relative magnetic helicity normalized by realizability bound.

    The realizability condition states |H_m(k)| ≤ 2k E_B(k) for each k.
    The relative helicity H_m / H_max measures how close the field is to
    being maximally helical.

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.

    Returns:
        H_rel: Relative helicity in [-1, 1]. |H_rel| → 1 means maximally helical.
    """
    shape = B.shape[1:]
    kx, ky, kz, k2 = build_k_grid(shape, dx)
    k_mag = np.sqrt(kx**2 + ky**2 + kz**2)
    k_mag[0, 0, 0] = 1.0  # avoid div-by-zero

    Bx_hat = np.fft.rfftn(B[0])
    By_hat = np.fft.rfftn(B[1])
    Bz_hat = np.fft.rfftn(B[2])

    # Magnetic energy spectrum (per mode), normalized
    N_total = np.prod(shape)
    Bx_hat_n = Bx_hat / N_total
    By_hat_n = By_hat / N_total
    Bz_hat_n = Bz_hat / N_total

    E_B_k = 0.5 * (np.abs(Bx_hat_n) ** 2 + np.abs(By_hat_n) ** 2 + np.abs(Bz_hat_n) ** 2)

    # Realizability bound: H_max = sum of 2 * E_B(k) / |k| over all modes
    H_max = float(2.0 * np.sum(E_B_k / k_mag).real) * N_total * dx**3

    result = compute_magnetic_helicity(B, dx)

    if abs(H_max) < 1e-30:
        return 0.0

    # Clamp to [-1, 1] — numerical errors can slightly exceed bounds
    return float(np.clip(result.global_helicity / H_max, -1.0, 1.0))


def verify_divergence_free(
    B: NDArray[np.float64],
    dx: float = 1.0,
) -> float:
    """Verify ∇·B = 0 constraint using spectral method.

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.

    Returns:
        max_div_B: Maximum |∇·B| normalized by max|B|.
    """
    shape = B.shape[1:]
    kx, ky, kz, _ = build_k_grid(shape, dx)

    Bx_hat = np.fft.rfftn(B[0])
    By_hat = np.fft.rfftn(B[1])
    Bz_hat = np.fft.rfftn(B[2])

    div_B_hat = 1j * (kx * Bx_hat + ky * By_hat + kz * Bz_hat)
    div_B = np.fft.irfftn(div_B_hat, s=shape)

    B_max = max(np.max(np.abs(B)), 1e-30)
    return float(np.max(np.abs(div_B))) / B_max


def generate_hopf_ranada_field(
    N: int,
    L: float = 2 * np.pi,
    a: float = 1.0,
    project_divfree: bool = True,
) -> NDArray[np.float64]:
    """Generate an analytic Hopf-Ranada magnetic field on a periodic grid.

    The Hopf-Ranada field is a force-free solution with non-trivial Hopf
    topology (Q_H = 1). It has the form:
        B = ∇α × ∇β / (1 + |x|²/a²)³

    where α, β are the Euler potentials derived from the Hopf map S³ → S².

    This is a simplified construction that places a Hopfion-like
    structure at the center of the domain. When project_divfree=True,
    the field is spectrally projected to satisfy ∇·B = 0 exactly on the
    periodic grid.

    Args:
        N: Grid points per dimension.
        L: Domain size.
        a: Hopfion scale parameter.
        project_divfree: If True, project to divergence-free field.

    Returns:
        B: Magnetic field, shape (3, N, N, N).
    """
    dx = L / N
    x = np.linspace(-L / 2, L / 2, N, endpoint=False) + dx / 2
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

    r2 = (X**2 + Y**2 + Z**2) / a**2
    denom = (1 + r2) ** 3

    # Hopf-Ranada field components (simplified)
    # Based on Ranada (1989) Lett. Math. Phys. 18, 97-106
    Bx = (2 * (X * Z / a**2 + Y / a)) / denom
    By = (2 * (Y * Z / a**2 - X / a)) / denom
    Bz = (1 - X**2 / a**2 - Y**2 / a**2 + Z**2 / a**2) / denom

    B = np.stack([Bx, By, Bz])

    # Project to divergence-free: B_df = B - ∇(∇⁻²(∇·B))
    if project_divfree:
        kx_arr = np.fft.fftfreq(N, d=dx) * 2 * np.pi
        ky_arr = np.fft.fftfreq(N, d=dx) * 2 * np.pi
        kz_arr = np.fft.rfftfreq(N, d=dx) * 2 * np.pi
        kx_3d, ky_3d, kz_3d = np.meshgrid(kx_arr, ky_arr, kz_arr, indexing="ij")
        k2 = kx_3d**2 + ky_3d**2 + kz_3d**2
        k2[0, 0, 0] = 1.0

        Bx_hat = np.fft.rfftn(B[0])
        By_hat = np.fft.rfftn(B[1])
        Bz_hat = np.fft.rfftn(B[2])

        # ∇·B in Fourier space
        div_hat = 1j * (kx_3d * Bx_hat + ky_3d * By_hat + kz_3d * Bz_hat)

        # Subtract gradient of scalar potential: B_df = B - ∇φ, where ∇²φ = ∇·B
        phi_hat = div_hat / k2
        phi_hat[0, 0, 0] = 0.0

        B[0] = np.fft.irfftn(Bx_hat - 1j * kx_3d * phi_hat, s=(N, N, N))
        B[1] = np.fft.irfftn(By_hat - 1j * ky_3d * phi_hat, s=(N, N, N))
        B[2] = np.fft.irfftn(Bz_hat - 1j * kz_3d * phi_hat, s=(N, N, N))

    # Normalize to unit maximum field strength
    B_max = np.max(np.sqrt(B[0]**2 + B[1]**2 + B[2]**2))
    if B_max > 0:
        B /= B_max

    return B


def extract_b_field_from_well(
    sample: dict,
    field_name: str = "magnetic_field",
) -> NDArray[np.float64]:
    """Extract magnetic field from a WellDataset sample in (3, Nx, Ny, Nz) format.

    The Well stores fields as (..., Nx, Ny, Nz, C) where C is the
    number of components. We reshape to (C, Nx, Ny, Nz).

    Args:
        sample: A sample dict from WellDataset.
        field_name: Name of the magnetic field in the dataset.

    Returns:
        B: Magnetic field array, shape (3, Nx, Ny, Nz).
    """
    # WellDataset returns tensors with shape (T, Nx, Ny, Nz, C)
    # For input_fields dict, keys are field names
    try:
        import torch
        has_torch = True
    except ImportError:
        has_torch = False

    if isinstance(sample, dict):
        if "input_fields" in sample:
            fields = sample["input_fields"]
            if isinstance(fields, dict) and field_name in fields:
                data = fields[field_name]
            elif isinstance(fields, np.ndarray) or (has_torch and isinstance(fields, torch.Tensor)):
                data = fields
            else:
                raise KeyError(f"Cannot find '{field_name}' in sample")
        elif field_name in sample:
            data = sample[field_name]
        else:
            raise KeyError(f"Cannot find '{field_name}' in sample keys: {list(sample.keys())}")
    else:
        data = sample

    if has_torch and isinstance(data, torch.Tensor):
        data = data.numpy()

    # Remove batch/time dimensions if present
    while data.ndim > 4:
        data = data[0]

    # If last dim is 3, it's channels-last: (Nx, Ny, Nz, 3) -> (3, Nx, Ny, Nz)
    if data.shape[-1] == 3 and data.ndim == 4:
        data = np.moveaxis(data, -1, 0)
    # If first dim is 3, already channels-first
    elif data.shape[0] == 3:
        pass
    else:
        raise ValueError(f"Cannot determine channel axis from shape {data.shape}")

    return data.astype(np.float64)
