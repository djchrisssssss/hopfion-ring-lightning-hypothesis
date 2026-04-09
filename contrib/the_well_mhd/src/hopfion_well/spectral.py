"""Spectral analysis of magnetic field topology.

Implements:
- Helicity power spectrum P_h(k)
- Cross-helicity spectrum H_c(k)
- Helical decomposition of magnetic energy E_B(k) = E⁺(k) + E⁻(k)
- Realizability bound check |H_m(k)| ≤ 2k E_B(k)

References:
    Moffatt (1978) Magnetic Field Generation in Electrically Conducting Fluids
    Biskamp (2003) Magnetohydrodynamic Turbulence, Ch. 8
    Brandenburg & Subramanian (2005) Phys. Rep. 417, 1-209
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class SpectralAnalysis:
    """Result of spectral topology analysis."""

    k_bins: NDArray[np.float64]  # Wavenumber bin centers
    E_B: NDArray[np.float64]  # Magnetic energy spectrum
    E_plus: NDArray[np.float64]  # Positive helicity energy spectrum
    E_minus: NDArray[np.float64]  # Negative helicity energy spectrum
    H_m_spectrum: NDArray[np.float64]  # Magnetic helicity spectrum
    H_c_spectrum: NDArray[np.float64]  # Cross-helicity spectrum (if v provided)
    P_h: NDArray[np.float64]  # Helicity density power spectrum
    realizability_ratio: NDArray[np.float64]  # |H_m(k)| / (2k E_B(k))


def compute_shell_spectrum(
    field_hat: NDArray,
    k_mag: NDArray[np.float64],
    n_bins: int | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Bin a spectral quantity into spherical shells.

    Args:
        field_hat: Spectral field values, shape matching k_mag.
        k_mag: Wavenumber magnitude array.
        n_bins: Number of bins. Defaults to N//2.

    Returns:
        k_bins: Bin center wavenumbers.
        spectrum: Binned spectrum values.
    """
    k_max = np.max(k_mag)
    if n_bins is None:
        n_bins = max(int(k_max / (2 * np.pi) * np.cbrt(np.prod(k_mag.shape))), 1)
        n_bins = min(n_bins, k_mag.shape[-1])

    dk = k_max / n_bins
    k_bins = np.arange(1, n_bins + 1) * dk - dk / 2
    spectrum = np.zeros(n_bins)

    for i in range(n_bins):
        k_lo = i * dk
        k_hi = (i + 1) * dk
        mask = (k_mag >= k_lo) & (k_mag < k_hi)
        if np.any(mask):
            spectrum[i] = np.sum(field_hat[mask].real)

    return k_bins, spectrum


def compute_magnetic_energy_spectrum(
    B: NDArray[np.float64],
    dx: float = 1.0,
    n_bins: int | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute isotropic magnetic energy spectrum E_B(k).

    E_B(k) = (1/2) Σ_{|k'|∈[k,k+dk)} |B̂(k')|²

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.
        n_bins: Number of wavenumber bins.

    Returns:
        k_bins: Wavenumber bin centers.
        E_B: Magnetic energy spectrum.
    """
    shape = B.shape[1:]
    N = np.prod(shape)

    kx = np.fft.fftfreq(shape[0], d=dx) * 2 * np.pi
    ky = np.fft.fftfreq(shape[1], d=dx) * 2 * np.pi
    kz = np.fft.rfftfreq(shape[2], d=dx) * 2 * np.pi
    kx_3d, ky_3d, kz_3d = np.meshgrid(kx, ky, kz, indexing="ij")
    k_mag = np.sqrt(kx_3d**2 + ky_3d**2 + kz_3d**2)

    Bx_hat = np.fft.rfftn(B[0]) / N
    By_hat = np.fft.rfftn(B[1]) / N
    Bz_hat = np.fft.rfftn(B[2]) / N

    E_k = 0.5 * (np.abs(Bx_hat) ** 2 + np.abs(By_hat) ** 2 + np.abs(Bz_hat) ** 2)

    return compute_shell_spectrum(E_k, k_mag, n_bins)


def compute_helical_decomposition(
    B: NDArray[np.float64],
    dx: float = 1.0,
    n_bins: int | None = None,
) -> SpectralAnalysis:
    """Compute helical decomposition of magnetic field.

    Decomposes B into positive and negative helicity modes:
        B̂(k) = B̂⁺(k) + B̂⁻(k)

    where B̂±(k) = (1/2)(B̂ ± i k̂ × B̂) are the helical projections.

    The magnetic helicity spectrum is:
        H_m(k) = (E⁺(k) - E⁻(k)) / k

    The realizability condition is:
        |H_m(k)| ≤ 2k E_B(k)  ↔  |E⁺(k) - E⁻(k)| ≤ E⁺(k) + E⁻(k)

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.
        n_bins: Number of wavenumber bins.

    Returns:
        SpectralAnalysis with all computed spectra.
    """
    shape = B.shape[1:]
    N = np.prod(shape)

    kx = np.fft.fftfreq(shape[0], d=dx) * 2 * np.pi
    ky = np.fft.fftfreq(shape[1], d=dx) * 2 * np.pi
    kz = np.fft.rfftfreq(shape[2], d=dx) * 2 * np.pi
    kx_3d, ky_3d, kz_3d = np.meshgrid(kx, ky, kz, indexing="ij")
    k_mag = np.sqrt(kx_3d**2 + ky_3d**2 + kz_3d**2)
    k_safe = np.where(k_mag > 0, k_mag, 1.0)

    # Unit wavevector
    khat_x = kx_3d / k_safe
    khat_y = ky_3d / k_safe
    khat_z = kz_3d / k_safe

    # FFT of B
    Bx_hat = np.fft.rfftn(B[0]) / N
    By_hat = np.fft.rfftn(B[1]) / N
    Bz_hat = np.fft.rfftn(B[2]) / N

    # k̂ × B̂
    cross_x = khat_y * Bz_hat - khat_z * By_hat
    cross_y = khat_z * Bx_hat - khat_x * Bz_hat
    cross_z = khat_x * By_hat - khat_y * Bx_hat

    # Helical projections: B̂± = (1/2)(B̂ ± i k̂ × B̂)
    Bp_x = 0.5 * (Bx_hat + 1j * cross_x)
    Bp_y = 0.5 * (By_hat + 1j * cross_y)
    Bp_z = 0.5 * (Bz_hat + 1j * cross_z)

    Bm_x = 0.5 * (Bx_hat - 1j * cross_x)
    Bm_y = 0.5 * (By_hat - 1j * cross_y)
    Bm_z = 0.5 * (Bz_hat - 1j * cross_z)

    # Energy in each helical mode
    E_plus_k = 0.5 * (np.abs(Bp_x) ** 2 + np.abs(Bp_y) ** 2 + np.abs(Bp_z) ** 2)
    E_minus_k = 0.5 * (np.abs(Bm_x) ** 2 + np.abs(Bm_y) ** 2 + np.abs(Bm_z) ** 2)
    E_total_k = E_plus_k + E_minus_k

    # Helicity spectrum: H_m(k) = (E⁺ - E⁻) / k
    H_m_k = np.where(k_mag > 0, (E_plus_k - E_minus_k) / k_safe, 0.0)

    # Realizability ratio: |H_m(k)| / (2 E_B(k) / k) = |E⁺ - E⁻| / (E⁺ + E⁻)
    realizability_k = np.where(
        E_total_k > 1e-30,
        np.abs(E_plus_k - E_minus_k) / (2.0 * E_total_k),
        0.0,
    )

    # Bin into shells
    k_bins, E_B = compute_shell_spectrum(E_total_k, k_mag, n_bins)
    _, E_plus = compute_shell_spectrum(E_plus_k, k_mag, n_bins)
    _, E_minus = compute_shell_spectrum(E_minus_k, k_mag, n_bins)
    _, H_m_spectrum = compute_shell_spectrum(H_m_k, k_mag, n_bins)
    _, realizability = compute_shell_spectrum(realizability_k, k_mag, n_bins)

    # Normalize realizability by bin count
    _, bin_count = compute_shell_spectrum(np.ones_like(k_mag), k_mag, n_bins)
    bin_count = np.where(bin_count > 0, bin_count, 1.0)
    realizability = realizability / bin_count

    # Helicity density power spectrum
    from .helicity import compute_vector_potential, compute_helicity_density

    A = compute_vector_potential(B, dx)
    h = compute_helicity_density(A, B)
    h_hat = np.fft.rfftn(h) / N
    P_h_k = np.abs(h_hat) ** 2
    _, P_h = compute_shell_spectrum(P_h_k, k_mag, n_bins)

    return SpectralAnalysis(
        k_bins=k_bins,
        E_B=E_B,
        E_plus=E_plus,
        E_minus=E_minus,
        H_m_spectrum=H_m_spectrum,
        H_c_spectrum=np.zeros_like(k_bins),  # populated if v provided
        P_h=P_h,
        realizability_ratio=realizability,
    )


def compute_cross_helicity_spectrum(
    v: NDArray[np.float64],
    B: NDArray[np.float64],
    dx: float = 1.0,
    n_bins: int | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute cross-helicity spectrum H_c(k) = Re(v̂* · B̂).

    Measures scale-dependent alignment between velocity and magnetic field.
    Non-zero H_c indicates Alfvénic correlation.

    Args:
        v: Velocity field, shape (3, Nx, Ny, Nz).
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        dx: Grid spacing.
        n_bins: Number of wavenumber bins.

    Returns:
        k_bins: Wavenumber bin centers.
        H_c: Cross-helicity spectrum.
    """
    shape = B.shape[1:]
    N = np.prod(shape)

    kx = np.fft.fftfreq(shape[0], d=dx) * 2 * np.pi
    ky = np.fft.fftfreq(shape[1], d=dx) * 2 * np.pi
    kz = np.fft.rfftfreq(shape[2], d=dx) * 2 * np.pi
    kx_3d, ky_3d, kz_3d = np.meshgrid(kx, ky, kz, indexing="ij")
    k_mag = np.sqrt(kx_3d**2 + ky_3d**2 + kz_3d**2)

    vx_hat = np.fft.rfftn(v[0]) / N
    vy_hat = np.fft.rfftn(v[1]) / N
    vz_hat = np.fft.rfftn(v[2]) / N

    Bx_hat = np.fft.rfftn(B[0]) / N
    By_hat = np.fft.rfftn(B[1]) / N
    Bz_hat = np.fft.rfftn(B[2]) / N

    H_c_k = np.real(
        np.conj(vx_hat) * Bx_hat
        + np.conj(vy_hat) * By_hat
        + np.conj(vz_hat) * Bz_hat
    )

    return compute_shell_spectrum(H_c_k, k_mag, n_bins)


def detect_inverse_cascade(
    H_m_spectra: list[NDArray[np.float64]],
    k_bins: NDArray[np.float64],
) -> dict[str, float | bool]:
    """Detect inverse helicity cascade from time series of helicity spectra.

    In an inverse cascade, helicity migrates from small scales (high k)
    to large scales (low k) over time. This is detected by:
    1. Tracking the peak wavenumber k_peak(t) of |H_m(k)|
    2. Measuring the growth rate of large-scale helicity

    Args:
        H_m_spectra: List of H_m(k) arrays, one per timestep.
        k_bins: Wavenumber bin centers.

    Returns:
        Dictionary with:
            cascade_detected: Whether inverse cascade signature is found
            k_peak_trend: Slope of k_peak(t) (negative = inverse cascade)
            large_scale_growth: Growth rate of helicity at k < k_max/4
    """
    if len(H_m_spectra) < 3:
        return {
            "cascade_detected": False,
            "k_peak_trend": 0.0,
            "large_scale_growth": 0.0,
        }

    T = len(H_m_spectra)
    k_peaks = np.zeros(T)
    large_scale_H = np.zeros(T)

    k_quarter = np.max(k_bins) / 4
    large_mask = k_bins < k_quarter

    for t, H_m in enumerate(H_m_spectra):
        abs_H = np.abs(H_m)
        if np.max(abs_H) > 0:
            k_peaks[t] = k_bins[np.argmax(abs_H)]
        large_scale_H[t] = np.sum(np.abs(H_m[large_mask])) if np.any(large_mask) else 0.0

    # Linear fit for k_peak trend
    times = np.arange(T, dtype=float)
    valid = k_peaks > 0
    if np.sum(valid) > 2:
        coeffs = np.polyfit(times[valid], k_peaks[valid], 1)
        k_peak_trend = float(coeffs[0])
    else:
        k_peak_trend = 0.0

    # Large-scale growth rate
    if np.sum(large_scale_H > 0) > 2:
        coeffs = np.polyfit(times, large_scale_H, 1)
        large_scale_growth = float(coeffs[0])
    else:
        large_scale_growth = 0.0

    # Inverse cascade: k_peak decreasing AND large-scale helicity growing
    cascade_detected = k_peak_trend < -0.01 and large_scale_growth > 0

    return {
        "cascade_detected": bool(cascade_detected),
        "k_peak_trend": k_peak_trend,
        "large_scale_growth": large_scale_growth,
    }
