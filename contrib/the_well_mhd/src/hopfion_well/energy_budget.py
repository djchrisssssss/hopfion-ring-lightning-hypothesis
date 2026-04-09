"""Energy budget decomposition for MHD fields.

Computes:
- E_magnetic = ∫ B²/(2μ₀) d³V
- E_kinetic = (1/2) ∫ ρv² d³V
- Energy spectra and transfer functions
- Equipartition ratio E_kinetic/E_magnetic

References:
    Biskamp (1993) Nonlinear Magnetohydrodynamics
    Brandenburg & Subramanian (2005) Phys. Rep. 417, 1-209
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


# CGS Gaussian units: μ₀ = 4π (in Gaussian) or 1 (code units)
# The Well MHD datasets use dimensionless code units where μ₀ = 1
MU_0_CODE = 1.0

# SI: μ₀ = 4π × 10⁻⁷ H/m (for physical unit conversion)
MU_0_SI = 4.0 * np.pi * 1e-7


@dataclass
class EnergyBudget:
    """Complete energy budget for an MHD snapshot."""

    E_magnetic: float  # ∫ B²/(2μ₀) d³V
    E_kinetic: float  # (1/2) ∫ ρv² d³V
    E_total: float  # E_magnetic + E_kinetic
    equipartition_ratio: float  # E_kinetic / E_magnetic
    E_magnetic_density: NDArray[np.float64]  # B²/(2μ₀), shape (Nx, Ny, Nz)
    E_kinetic_density: NDArray[np.float64]  # (1/2)ρv², shape (Nx, Ny, Nz)
    beta_plasma: float  # 2μ₀ <P> / <B²> (plasma beta, if pressure available)


def compute_magnetic_energy_density(
    B: NDArray[np.float64],
    mu_0: float = MU_0_CODE,
) -> NDArray[np.float64]:
    """Compute magnetic energy density e_B = B²/(2μ₀).

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        mu_0: Permeability of free space.

    Returns:
        e_B: Magnetic energy density, shape (Nx, Ny, Nz).
    """
    B2 = np.sum(B**2, axis=0)
    return B2 / (2.0 * mu_0)


def compute_kinetic_energy_density(
    rho: NDArray[np.float64],
    v: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute kinetic energy density e_K = (1/2)ρv².

    Args:
        rho: Mass density, shape (Nx, Ny, Nz).
        v: Velocity field, shape (3, Nx, Ny, Nz).

    Returns:
        e_K: Kinetic energy density, shape (Nx, Ny, Nz).
    """
    v2 = np.sum(v**2, axis=0)
    return 0.5 * rho * v2


def compute_energy_budget(
    B: NDArray[np.float64],
    v: NDArray[np.float64],
    rho: NDArray[np.float64],
    dx: float = 1.0,
    mu_0: float = MU_0_CODE,
    pressure: NDArray[np.float64] | None = None,
) -> EnergyBudget:
    """Compute complete energy budget for an MHD snapshot.

    Args:
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        v: Velocity field, shape (3, Nx, Ny, Nz).
        rho: Mass density, shape (Nx, Ny, Nz).
        dx: Grid spacing.
        mu_0: Permeability of free space.
        pressure: Thermal pressure, shape (Nx, Ny, Nz). Optional.

    Returns:
        EnergyBudget with all computed quantities.
    """
    dV = dx**3

    e_B = compute_magnetic_energy_density(B, mu_0)
    e_K = compute_kinetic_energy_density(rho, v)

    E_magnetic = float(np.sum(e_B) * dV)
    E_kinetic = float(np.sum(e_K) * dV)
    E_total = E_magnetic + E_kinetic

    equipartition = E_kinetic / max(E_magnetic, 1e-30)

    # Plasma beta
    if pressure is not None:
        B2_mean = np.mean(np.sum(B**2, axis=0))
        P_mean = np.mean(pressure)
        beta = float(2.0 * mu_0 * P_mean / max(B2_mean, 1e-30))
    else:
        beta = float("nan")

    return EnergyBudget(
        E_magnetic=E_magnetic,
        E_kinetic=E_kinetic,
        E_total=E_total,
        equipartition_ratio=equipartition,
        E_magnetic_density=e_B,
        E_kinetic_density=e_K,
        beta_plasma=beta,
    )


def compute_energy_timeseries(
    B_series: NDArray[np.float64],
    v_series: NDArray[np.float64],
    rho_series: NDArray[np.float64],
    dx: float = 1.0,
    mu_0: float = MU_0_CODE,
) -> dict[str, NDArray[np.float64]]:
    """Compute energy budget over a time series.

    Args:
        B_series: Magnetic field, shape (T, 3, Nx, Ny, Nz).
        v_series: Velocity field, shape (T, 3, Nx, Ny, Nz).
        rho_series: Density, shape (T, Nx, Ny, Nz).
        dx: Grid spacing.
        mu_0: Permeability of free space.

    Returns:
        Dictionary with arrays of shape (T,):
            E_magnetic, E_kinetic, E_total, equipartition_ratio
    """
    T = B_series.shape[0]
    E_mag = np.zeros(T)
    E_kin = np.zeros(T)
    E_tot = np.zeros(T)
    equip = np.zeros(T)

    for t in range(T):
        budget = compute_energy_budget(
            B_series[t], v_series[t], rho_series[t], dx, mu_0
        )
        E_mag[t] = budget.E_magnetic
        E_kin[t] = budget.E_kinetic
        E_tot[t] = budget.E_total
        equip[t] = budget.equipartition_ratio

    return {
        "E_magnetic": E_mag,
        "E_kinetic": E_kin,
        "E_total": E_tot,
        "equipartition_ratio": equip,
    }


def compute_alfven_mach(
    v: NDArray[np.float64],
    B: NDArray[np.float64],
    rho: NDArray[np.float64],
    mu_0: float = MU_0_CODE,
) -> float:
    """Compute volume-averaged Alfvénic Mach number.

    M_A = <v_rms> / <v_A> where v_A = B / sqrt(μ₀ ρ)

    Args:
        v: Velocity field, shape (3, Nx, Ny, Nz).
        B: Magnetic field, shape (3, Nx, Ny, Nz).
        rho: Density, shape (Nx, Ny, Nz).
        mu_0: Permeability.

    Returns:
        M_A: Alfvénic Mach number.
    """
    v_rms = float(np.sqrt(np.mean(np.sum(v**2, axis=0))))
    B_rms = float(np.sqrt(np.mean(np.sum(B**2, axis=0))))
    rho_mean = float(np.mean(rho))

    v_A = B_rms / np.sqrt(mu_0 * max(rho_mean, 1e-30))
    return v_rms / max(v_A, 1e-30)


def compute_sonic_mach(
    v: NDArray[np.float64],
    rho: NDArray[np.float64],
    pressure: NDArray[np.float64] | None = None,
    gamma: float = 1.0,
    c_s: float | None = None,
) -> float:
    """Compute volume-averaged sonic Mach number.

    For isothermal MHD (gamma=1), c_s is a constant parameter.
    For adiabatic MHD, c_s = sqrt(gamma * P / rho).

    Args:
        v: Velocity field, shape (3, Nx, Ny, Nz).
        rho: Density, shape (Nx, Ny, Nz).
        pressure: Thermal pressure (for adiabatic). Optional.
        gamma: Adiabatic index (1.0 for isothermal).
        c_s: Sound speed (for isothermal). If None, computed from pressure.

    Returns:
        M_s: Sonic Mach number.
    """
    v_rms = float(np.sqrt(np.mean(np.sum(v**2, axis=0))))

    if c_s is not None:
        return v_rms / max(c_s, 1e-30)

    if pressure is not None:
        cs_local = np.sqrt(gamma * pressure / np.maximum(rho, 1e-30))
        c_s_mean = float(np.mean(cs_local))
        return v_rms / max(c_s_mean, 1e-30)

    # Isothermal: assume c_s = 1 (code units)
    return v_rms


def hopfion_energy_budget_physical(
    B_peak_mT: float = 50.0,
    R_major_m: float = 0.1,
    R_minor_m: float = 0.05,
    T_core_K: float = 4200.0,
    v_rotation_ms: float = 1000.0,
    gamma: float = 5.0 / 3.0,
) -> dict[str, float]:
    """Compute idealized Hopfion energy budget in physical SI units.

    Estimates E_magnetic, E_kinetic, E_thermal for a torus with
    given parameters, to compare with observed ball lightning energy
    of 8-80 kJ.

    Args:
        B_peak_mT: Peak magnetic field in millitesla.
        R_major_m: Torus major radius in meters.
        R_minor_m: Torus minor radius in meters.
        T_core_K: Core temperature in Kelvin.
        v_rotation_ms: Plasma rotation speed in m/s.
        gamma: Adiabatic index.

    Returns:
        Dictionary with E_magnetic, E_kinetic, E_thermal, E_total in Joules.
    """
    B_peak = B_peak_mT * 1e-3  # Convert to Tesla
    V_torus = 2 * np.pi**2 * R_major_m * R_minor_m**2  # Torus volume

    # Magnetic energy: E_B = <B²>/(2μ₀) * V
    # For force-free field, <B²> ~ B_peak² / 2 (rough average over torus)
    B2_avg = B_peak**2 / 2
    E_magnetic = B2_avg / (2 * MU_0_SI) * V_torus

    # Kinetic energy: E_K = (1/2) ρ v² V
    # Atmospheric pressure ~ 101325 Pa, at T_core_K:
    k_B = 1.381e-23  # Boltzmann constant
    m_air = 4.81e-26  # Average mass of air molecule (N₂/O₂ mix)
    n_density = 101325 / (k_B * T_core_K)  # Ideal gas at atmospheric pressure
    rho = n_density * m_air
    E_kinetic = 0.5 * rho * v_rotation_ms**2 * V_torus

    # Thermal energy: E_th = n k T / (γ-1) * V
    E_thermal = n_density * k_B * T_core_K / (gamma - 1) * V_torus

    E_total = E_magnetic + E_kinetic + E_thermal

    return {
        "E_magnetic_J": E_magnetic,
        "E_kinetic_J": E_kinetic,
        "E_thermal_J": E_thermal,
        "E_total_J": E_total,
        "E_total_kJ": E_total / 1000,
        "V_torus_m3": V_torus,
        "rho_kg_m3": rho,
        "n_density_m3": n_density,
        "dominant_component": max(
            [("magnetic", E_magnetic), ("kinetic", E_kinetic), ("thermal", E_thermal)],
            key=lambda x: x[1],
        )[0],
    }
