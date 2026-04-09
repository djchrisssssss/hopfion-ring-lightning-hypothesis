"""Boundary layer model for Hopfion-atmosphere interface.

Models the two-zone structure:
  [Cool ambient air] ↔ [Mixing layer] ↔ [Hot Hopfion core]

Computes effective insulation, entrainment rates, and pressure
equilibrium for the Hopfion hypothesis two-zone model.

Addresses Problem 1, Approach D: Two-zone lifetime extension.

References:
    Fielding et al. (2020) ApJ Letters 894, L24
    Tan et al. (2021) MNRAS 502, 3179-3199
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class BoundaryLayerModel:
    """Results of boundary layer analysis for one snapshot."""

    density_contrast: float  # χ = ρ_cold / ρ_hot
    temperature_contrast: float  # T_hot / T_cold
    mixing_layer_width: float  # in physical units
    heat_flux_with_layer: float  # q (W/m² equivalent)
    heat_flux_without_layer: float  # q₀ (conductive estimate)
    effective_insulation: float  # κ_eff = q / q₀ (< 1 means insulation)
    entrainment_velocity: float  # v_e = dh/dt
    pressure_equilibrium_error: float  # |P_hot - P_cold| / P_mean


@dataclass
class TwoZoneModel:
    """Two-zone model parameters derived from mixing layer data."""

    R_core_m: float  # Core radius (hot zone)
    T_core_K: float  # Core temperature
    T_ambient_K: float  # Ambient temperature
    rho_core: float  # Core density
    rho_ambient: float  # Ambient density
    kappa_eff: float  # Effective insulation factor
    v_entrainment: float  # Entrainment velocity
    tau_cooling: float  # Estimated cooling time = R / v_e
    lifetime_extension: float  # Factor by which boundary extends lifetime


def compute_density_contrast(
    density: NDArray[np.float64],
    mixing_axis: int = -1,
    percentile_hot: float = 5.0,
    percentile_cold: float = 95.0,
) -> float:
    """Compute density contrast χ = ρ_cold / ρ_hot.

    Args:
        density: Density field.
        mixing_axis: Axis along which mixing occurs.
        percentile_hot: Percentile for hot phase density.
        percentile_cold: Percentile for cold phase density.

    Returns:
        chi: Density contrast ratio.
    """
    rho_hot = float(np.percentile(density, percentile_hot))
    rho_cold = float(np.percentile(density, percentile_cold))

    if rho_hot < 1e-30:
        return float("inf")
    return rho_cold / rho_hot


def compute_heat_flux_profile(
    density: NDArray[np.float64],
    velocity: NDArray[np.float64],
    temperature: NDArray[np.float64] | None = None,
    pressure: NDArray[np.float64] | None = None,
    mixing_axis: int = -1,
    gamma: float = 5.0 / 3.0,
) -> NDArray[np.float64]:
    """Compute advective heat flux across the mixing layer.

    Heat flux q = ρ v_z (e + P/ρ) where e is specific internal energy.
    For ideal gas: e = P / (ρ(γ-1))

    If temperature/pressure not available, uses density*velocity as proxy.

    Args:
        density: Density field.
        velocity: Velocity field, shape (ndim, ...).
        temperature: Temperature field. Optional.
        pressure: Pressure field. Optional.
        mixing_axis: Axis along which mixing occurs.
        gamma: Adiabatic index.

    Returns:
        Heat flux profile along mixing axis.
    """
    if mixing_axis < 0:
        mixing_axis = density.ndim + mixing_axis

    # Velocity component along mixing axis
    v_mix = velocity[min(mixing_axis, velocity.shape[0] - 1)]

    if pressure is not None:
        # Enthalpy flux: q = ρ v_z (e + P/ρ) = v_z (P γ/(γ-1))
        enthalpy_flux = v_mix * pressure * gamma / (gamma - 1)
    else:
        # Proxy: mass flux * velocity² (kinetic energy flux)
        enthalpy_flux = density * v_mix * np.sum(velocity**2, axis=0)

    # Average over non-mixing axes
    axes = list(range(density.ndim))
    axes.remove(mixing_axis)
    if axes:
        return np.mean(enthalpy_flux, axis=tuple(axes))
    return enthalpy_flux


def compute_effective_insulation(
    density_series: NDArray[np.float64],
    velocity_series: NDArray[np.float64],
    mixing_axis: int = -1,
    dx: float = 1.0,
    pressure_series: NDArray[np.float64] | None = None,
) -> float:
    """Compute effective thermal insulation factor κ_eff.

    κ_eff = (actual heat flux through mixing layer) /
            (heat flux by pure conduction across same ΔT)

    κ_eff < 1 means the mixing layer provides thermal insulation.
    κ_eff << 1 means significant insulation (supports two-zone model).

    Args:
        density_series: Density time series, shape (T, ...).
        velocity_series: Velocity time series, shape (T, ndim, ...).
        mixing_axis: Mixing axis.
        dx: Grid spacing.
        pressure_series: Pressure time series. Optional.

    Returns:
        kappa_eff: Effective insulation factor.
    """
    T = density_series.shape[0]
    flux_values = []

    for t in range(T):
        P = pressure_series[t] if pressure_series is not None else None
        flux_profile = compute_heat_flux_profile(
            density_series[t], velocity_series[t],
            pressure=P, mixing_axis=mixing_axis,
        )
        # Peak flux across mixing layer
        flux_values.append(float(np.max(np.abs(flux_profile))))

    actual_flux = np.mean(flux_values)

    # Reference: conductive flux across same domain without mixing
    # q_cond = κ ΔT / L where κ is thermal conductivity
    # In dimensionless units, approximate as max density gradient * velocity scale
    rho_range = np.max(density_series) - np.min(density_series)
    spatial_shape = density_series.shape[1:]  # exclude time dimension
    domain_size = spatial_shape[mixing_axis] * dx
    v_rms = float(np.sqrt(np.mean(velocity_series**2)))

    reference_flux = rho_range * v_rms / max(domain_size, 1e-10)

    if reference_flux < 1e-30:
        return 1.0

    return float(actual_flux / reference_flux)


def compute_entrainment_rate(
    density_series: NDArray[np.float64],
    times: NDArray[np.float64],
    mixing_axis: int = -1,
    dx: float = 1.0,
) -> float:
    """Compute entrainment velocity v_e = dh/dt.

    The entrainment velocity measures how fast cold gas is mixed
    into the hot phase (or vice versa). For Hopfion stability,
    we need v_e < L_hopfion / τ_observed.

    Args:
        density_series: Density time series, shape (T, ...).
        times: Time values, shape (T,).
        mixing_axis: Mixing axis.
        dx: Grid spacing.

    Returns:
        v_e: Entrainment velocity (grid units per time unit).
    """
    from .cooling_analysis import compute_mixing_layer_width

    T = len(times)
    widths = np.zeros(T)

    rho_hot = float(np.percentile(density_series[0], 5))
    rho_cold = float(np.percentile(density_series[0], 95))

    for t in range(T):
        widths[t] = compute_mixing_layer_width(
            density_series[t], mixing_axis, rho_hot, rho_cold
        ) * dx

    if T > 2:
        coeffs = np.polyfit(times, widths, 1)
        return abs(float(coeffs[0]))
    elif T == 2:
        dt = times[1] - times[0]
        return abs(float(widths[1] - widths[0])) / max(dt, 1e-10)
    return 0.0


def check_pressure_equilibrium(
    pressure: NDArray[np.float64],
    density: NDArray[np.float64],
    mixing_axis: int = -1,
) -> float:
    """Check if hot and cold phases are in pressure equilibrium.

    For Hopfion stability, the hot interior and cool exterior must
    satisfy P_hot ≈ P_cold (isobaric mixing).

    Args:
        pressure: Pressure field.
        density: Density field (to identify phases).
        mixing_axis: Mixing axis.

    Returns:
        Pressure equilibrium error: |P_hot - P_cold| / P_mean.
    """
    rho_median = np.median(density)

    hot_mask = density < rho_median
    cold_mask = density >= rho_median

    if not np.any(hot_mask) or not np.any(cold_mask):
        return 0.0

    P_hot = float(np.mean(pressure[hot_mask]))
    P_cold = float(np.mean(pressure[cold_mask]))
    P_mean = 0.5 * (P_hot + P_cold)

    if P_mean < 1e-30:
        return 0.0

    return abs(P_hot - P_cold) / P_mean


def build_two_zone_model(
    kappa_eff: float,
    v_entrainment: float,
    density_contrast: float,
    R_hopfion_m: float = 0.1,
    T_core_K: float = 10000.0,
    T_ambient_K: float = 300.0,
) -> TwoZoneModel:
    """Construct two-zone model for Hopfion lifetime estimation.

    The two-zone model:
    - Hot, fully ionized core (low η → slow magnetic diffusion)
    - Cool, weakly ionized sheath (acts as thermal insulator)
    - Mixing layer between them limits energy loss

    Lifetime extension: τ_extended = τ_base / κ_eff

    Args:
        kappa_eff: Effective insulation factor from mixing layer data.
        v_entrainment: Entrainment velocity.
        density_contrast: χ = ρ_cold / ρ_hot.
        R_hopfion_m: Hopfion core radius in meters.
        T_core_K: Core temperature.
        T_ambient_K: Ambient temperature.

    Returns:
        TwoZoneModel with all parameters.
    """
    k_B = 1.381e-23  # Boltzmann
    m_air = 4.81e-26  # Mean air molecule mass

    # Density from ideal gas at atmospheric pressure
    P_atm = 101325  # Pa
    n_core = P_atm / (k_B * T_core_K)
    n_ambient = P_atm / (k_B * T_ambient_K)
    rho_core = n_core * m_air
    rho_ambient = n_ambient * m_air

    # Cooling time: time for core to lose energy through boundary
    # τ_cooling ~ R / v_e (if v_e in m/s)
    if v_entrainment > 1e-30:
        tau_cooling = R_hopfion_m / v_entrainment
    else:
        tau_cooling = float("inf")

    # Lifetime extension factor
    # The boundary layer reduces heat loss by factor κ_eff
    # Additionally, the core's low resistivity (Spitzer: η ∝ T^{-3/2})
    # extends the magnetic diffusion time
    lifetime_extension = 1.0 / max(kappa_eff, 1e-10)

    return TwoZoneModel(
        R_core_m=R_hopfion_m,
        T_core_K=T_core_K,
        T_ambient_K=T_ambient_K,
        rho_core=rho_core,
        rho_ambient=rho_ambient,
        kappa_eff=kappa_eff,
        v_entrainment=v_entrainment,
        tau_cooling=tau_cooling,
        lifetime_extension=lifetime_extension,
    )
