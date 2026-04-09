"""Cooling-stability analysis for turbulent radiative mixing layers.

Analyzes how radiative cooling time affects:
- Mixing layer width evolution
- KH vortex lifetime
- Critical cooling time for structure survival
- Phase diagram construction (cooling time vs stability)

Designed for turbulent_radiative_layer_2D and _3D datasets from The Well.

References:
    Fielding et al. (2020) ApJ Letters 894, L24
    Tan et al. (2021) MNRAS 502, 3179-3199
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class MixingLayerAnalysis:
    """Results of mixing layer width analysis for one trajectory."""

    time: NDArray[np.float64]
    width: NDArray[np.float64]  # Mixing layer width h(t)
    growth_rate: float  # dh/dt (linear fit)
    entrainment_velocity: float  # v_e = dh/dt
    t_cool: float  # Cooling time parameter
    initial_width: float
    final_width: float
    width_ratio: float  # final/initial


@dataclass
class CoolingStabilityResult:
    """Results of cooling time vs vortex stability analysis."""

    t_cool_values: NDArray[np.float64]
    mean_lifetimes: NDArray[np.float64]
    std_lifetimes: NDArray[np.float64]
    max_lifetimes: NDArray[np.float64]
    n_vortices: NDArray[np.int64]
    t_cool_critical: float  # Optimal cooling time for longest structures
    critical_uncertainty: float


def compute_mixing_layer_width(
    density: NDArray[np.float64],
    axis: int = -1,
    rho_hot: float | None = None,
    rho_cold: float | None = None,
    threshold_lo: float = 0.2,
    threshold_hi: float = 0.8,
) -> float:
    """Compute mixing layer width from density field.

    The mixing layer is defined as the region where the normalized
    density falls between threshold_lo and threshold_hi.

    For radiative mixing layers:
        ρ_normalized = (ρ - ρ_hot) / (ρ_cold - ρ_hot)

    Args:
        density: Density field, shape (..., Nz) where z is the mixing axis.
        axis: Axis along which mixing occurs.
        rho_hot: Hot phase density. If None, uses min(density).
        rho_cold: Cold phase density. If None, uses max(density).
        threshold_lo: Lower normalized density threshold.
        threshold_hi: Upper normalized density threshold.

    Returns:
        width: Mixing layer width in grid cells.
    """
    if rho_hot is None:
        rho_hot = float(np.min(density))
    if rho_cold is None:
        rho_cold = float(np.max(density))

    delta_rho = rho_cold - rho_hot
    if abs(delta_rho) < 1e-30:
        return 0.0

    rho_norm = (density - rho_hot) / delta_rho

    # Average over non-mixing axes to get 1D profile
    axes_to_avg = list(range(density.ndim))
    if axis < 0:
        axis = density.ndim + axis
    axes_to_avg.remove(axis)
    if axes_to_avg:
        profile = np.mean(rho_norm, axis=tuple(axes_to_avg))
    else:
        profile = rho_norm

    # Width = number of cells where threshold_lo < rho_norm < threshold_hi
    in_mixing = (profile > threshold_lo) & (profile < threshold_hi)
    width = float(np.sum(in_mixing))

    return width


def analyze_mixing_layer_evolution(
    density_series: NDArray[np.float64],
    times: NDArray[np.float64],
    mixing_axis: int = -1,
    dx: float = 1.0,
    t_cool: float = 0.0,
) -> MixingLayerAnalysis:
    """Analyze mixing layer width evolution over time.

    Args:
        density_series: Density time series, shape (T, ...).
        times: Time values, shape (T,).
        mixing_axis: Axis along which mixing occurs.
        dx: Grid spacing.
        t_cool: Cooling time parameter (for labeling).

    Returns:
        MixingLayerAnalysis with width evolution and growth rate.
    """
    T = density_series.shape[0]
    widths = np.zeros(T)

    # Determine reference densities from first frame
    rho_hot = float(np.percentile(density_series[0], 5))
    rho_cold = float(np.percentile(density_series[0], 95))

    for t in range(T):
        widths[t] = compute_mixing_layer_width(
            density_series[t], mixing_axis, rho_hot, rho_cold
        ) * dx

    # Linear fit for growth rate
    if T > 2:
        coeffs = np.polyfit(times, widths, 1)
        growth_rate = float(coeffs[0])
    else:
        growth_rate = 0.0

    return MixingLayerAnalysis(
        time=times,
        width=widths,
        growth_rate=growth_rate,
        entrainment_velocity=abs(growth_rate),
        t_cool=t_cool,
        initial_width=float(widths[0]),
        final_width=float(widths[-1]),
        width_ratio=float(widths[-1]) / max(float(widths[0]), 1e-10),
    )


def find_critical_cooling_time(
    t_cool_values: NDArray[np.float64],
    mean_lifetimes: NDArray[np.float64],
) -> tuple[float, float]:
    """Find the critical cooling time that maximizes structure lifetime.

    Fits a function with a peak (e.g., skewed Gaussian or log-normal)
    to the (t_cool, lifetime) data to find the optimal cooling time.

    Args:
        t_cool_values: Cooling time parameter values.
        mean_lifetimes: Mean vortex lifetime for each cooling time.

    Returns:
        t_cool_critical: Optimal cooling time.
        uncertainty: Fit uncertainty on the critical value.
    """
    if len(t_cool_values) < 3:
        idx = np.argmax(mean_lifetimes)
        return float(t_cool_values[idx]), float("inf")

    # Use log-space for cooling time (often log-spaced in datasets)
    log_tc = np.log10(t_cool_values)

    # Fit a quadratic in log-space to find the peak
    try:
        coeffs = np.polyfit(log_tc, mean_lifetimes, 2)
        a, b, c = coeffs

        if a >= 0:
            # No maximum (monotonic) — return endpoint with max lifetime
            idx = np.argmax(mean_lifetimes)
            return float(t_cool_values[idx]), float("inf")

        # Peak at log_tc = -b/(2a)
        log_tc_peak = -b / (2 * a)
        t_cool_critical = 10**log_tc_peak

        # Uncertainty from curvature: σ ≈ 1/sqrt(|2a|)
        uncertainty = 10 ** (log_tc_peak + 1.0 / np.sqrt(abs(2 * a))) - t_cool_critical

        # Clamp to data range
        t_cool_critical = np.clip(
            t_cool_critical, t_cool_values.min(), t_cool_values.max()
        )

        return float(t_cool_critical), float(uncertainty)

    except (np.linalg.LinAlgError, ValueError):
        idx = np.argmax(mean_lifetimes)
        return float(t_cool_values[idx]), float("inf")


def build_cooling_stability_phase_diagram(
    t_cool_values: NDArray[np.float64],
    lifetime_data: dict[float, NDArray[np.float64]],
) -> CoolingStabilityResult:
    """Build phase diagram of cooling time vs vortex stability.

    Args:
        t_cool_values: Array of cooling time values.
        lifetime_data: Dict mapping t_cool → array of vortex lifetimes.

    Returns:
        CoolingStabilityResult with phase diagram data and critical t_cool.
    """
    n = len(t_cool_values)
    mean_lt = np.zeros(n)
    std_lt = np.zeros(n)
    max_lt = np.zeros(n)
    n_vortices = np.zeros(n, dtype=np.int64)

    for i, tc in enumerate(t_cool_values):
        lifetimes = lifetime_data.get(tc, np.array([]))
        if len(lifetimes) > 0:
            mean_lt[i] = np.mean(lifetimes)
            std_lt[i] = np.std(lifetimes)
            max_lt[i] = np.max(lifetimes)
            n_vortices[i] = len(lifetimes)

    tc_crit, tc_unc = find_critical_cooling_time(t_cool_values, mean_lt)

    return CoolingStabilityResult(
        t_cool_values=t_cool_values,
        mean_lifetimes=mean_lt,
        std_lifetimes=std_lt,
        max_lifetimes=max_lt,
        n_vortices=n_vortices,
        t_cool_critical=tc_crit,
        critical_uncertainty=tc_unc,
    )


def map_to_atmospheric_conditions(
    t_cool_critical: float,
    dataset_time_unit: float = 1.0,
) -> dict[str, float]:
    """Map cooling analysis results to atmospheric ball lightning conditions.

    Atmospheric conditions:
    - T_surface ~ 4200 K (Cen et al. 2014)
    - P ~ 1 atm
    - Radiative cooling dominated by N₂, O₂ molecular emission
    - Estimated t_cool ~ 1-10 s for partially ionized air at 4200 K

    Args:
        t_cool_critical: Critical cooling time from dataset analysis.
        dataset_time_unit: Physical time per dataset time unit.

    Returns:
        Dictionary with atmospheric mapping results.
    """
    # Atmospheric radiative cooling estimates
    # At T ~ 4200 K, partially ionized air:
    # Cooling rate ~ n² Λ(T) where Λ is the cooling function
    # For atomic line emission: Λ ~ 10⁻²³ - 10⁻²² erg cm³/s at ~4000 K
    # n ~ 10²⁵ m⁻³ at 1 atm
    # t_cool_atm ~ nkT / (n²Λ) ~ kT/(nΛ) ~ 1-10 s

    t_cool_atm_low = 0.5  # seconds (strong cooling, metallic vapor)
    t_cool_atm_high = 10.0  # seconds (weak cooling, pure air)
    t_cool_atm_typical = 3.0  # seconds

    t_cool_crit_physical = t_cool_critical * dataset_time_unit

    return {
        "t_cool_critical_dataset": t_cool_critical,
        "t_cool_critical_physical_s": t_cool_crit_physical,
        "t_cool_atm_range_s": (t_cool_atm_low, t_cool_atm_high),
        "t_cool_atm_typical_s": t_cool_atm_typical,
        "atm_in_optimal_range": t_cool_atm_low <= t_cool_crit_physical <= t_cool_atm_high,
        "ratio_atm_to_critical": t_cool_atm_typical / max(t_cool_crit_physical, 1e-10),
    }
