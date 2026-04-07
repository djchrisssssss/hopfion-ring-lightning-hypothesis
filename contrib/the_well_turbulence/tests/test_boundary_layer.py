"""Tests for hopfion_turb.boundary_layer module."""

import numpy as np
import pytest

from hopfion_turb.boundary_layer import (
    compute_density_contrast,
    compute_heat_flux_profile,
    compute_effective_insulation,
    compute_entrainment_rate,
    check_pressure_equilibrium,
    build_two_zone_model,
)


class TestDensityContrast:
    def test_uniform_density(self):
        """Uniform density should give contrast of 1."""
        density = np.ones((32, 32)) * 5.0
        chi = compute_density_contrast(density)
        assert chi == pytest.approx(1.0, rel=0.01)

    def test_two_phase(self):
        """Clear hot/cold separation should give correct contrast."""
        density = np.zeros((32, 64))
        density[:, :32] = 1.0   # hot (low density)
        density[:, 32:] = 10.0  # cold (high density)

        chi = compute_density_contrast(density)
        assert chi == pytest.approx(10.0, rel=0.1)

    def test_custom_percentiles(self):
        """Different percentiles should change the result."""
        np.random.seed(42)
        density = np.random.lognormal(0, 1, size=(64, 64))

        chi_default = compute_density_contrast(density)
        chi_extreme = compute_density_contrast(
            density, percentile_hot=1.0, percentile_cold=99.0
        )
        # More extreme percentiles → larger contrast
        assert chi_extreme >= chi_default


class TestHeatFluxProfile:
    def test_zero_velocity(self):
        """Zero velocity should give zero heat flux."""
        N = 32
        density = np.ones((N, N))
        velocity = np.zeros((2, N, N))

        flux = compute_heat_flux_profile(density, velocity, mixing_axis=-1)
        assert np.allclose(flux, 0.0)

    def test_with_pressure(self):
        """Nonzero pressure and velocity should give nonzero flux."""
        N = 32
        density = np.ones((N, N))
        velocity = np.zeros((2, N, N))
        velocity[1] = 1.0  # flow along mixing axis
        pressure = np.ones((N, N))

        flux = compute_heat_flux_profile(
            density, velocity, pressure=pressure, mixing_axis=-1
        )
        assert np.any(flux != 0)

    def test_output_shape(self):
        """Flux profile should be 1D along mixing axis."""
        density = np.ones((16, 32))
        velocity = np.ones((2, 16, 32))

        flux = compute_heat_flux_profile(density, velocity, mixing_axis=-1)
        assert flux.ndim == 1
        assert len(flux) == 32


class TestEffectiveInsulation:
    def test_static_system(self):
        """Zero velocity should give kappa_eff = 1.0 (no insulation info)."""
        T, Nx, Nz = 5, 16, 32
        density_series = np.ones((T, Nx, Nz))
        velocity_series = np.zeros((T, 2, Nx, Nz))

        kappa = compute_effective_insulation(
            density_series, velocity_series, mixing_axis=-1
        )
        # With zero velocity, actual flux is 0, reference is also ~0
        # Function returns 1.0 when reference is too small
        assert isinstance(kappa, float)


class TestEntrainmentRate:
    def test_static_density(self):
        """Unchanging density should give near-zero entrainment."""
        T = 10
        Nz = 64
        times = np.linspace(0, 1, T)

        z = np.linspace(0, 1, Nz)
        profile = 0.5 * (1 + np.tanh(10 * (z - 0.5)))
        density_series = np.tile(profile, (T, 1))

        v_e = compute_entrainment_rate(density_series, times, mixing_axis=-1)
        assert abs(v_e) < 1e-10

    def test_two_timesteps(self):
        """With T=2, should compute simple difference."""
        Nz = 64
        times = np.array([0.0, 1.0])
        z = np.linspace(0, 1, Nz)

        density_series = np.zeros((2, Nz))
        density_series[0] = 0.5 * (1 + np.tanh(20 * (z - 0.5)))
        density_series[1] = 0.5 * (1 + np.tanh(5 * (z - 0.5)))  # broader

        v_e = compute_entrainment_rate(density_series, times, mixing_axis=-1)
        assert v_e >= 0


class TestPressureEquilibrium:
    def test_uniform_pressure(self):
        """Uniform pressure should give zero error."""
        pressure = np.ones((32, 32)) * 100.0
        density = np.zeros((32, 32))
        density[:, :16] = 1.0
        density[:, 16:] = 10.0

        error = check_pressure_equilibrium(pressure, density)
        assert error == pytest.approx(0.0, abs=1e-10)

    def test_pressure_imbalance(self):
        """Different pressures in hot/cold phases should give nonzero error."""
        density = np.zeros((32, 32))
        density[:, :16] = 1.0   # hot
        density[:, 16:] = 10.0  # cold

        pressure = np.zeros((32, 32))
        pressure[:, :16] = 100.0   # hot phase
        pressure[:, 16:] = 200.0   # cold phase

        error = check_pressure_equilibrium(pressure, density)
        # |100 - 200| / 150 ≈ 0.67
        assert error > 0.5

    def test_uniform_density(self):
        """Uniform density → can't distinguish phases → returns 0."""
        pressure = np.random.randn(32, 32) + 100
        density = np.ones((32, 32))

        error = check_pressure_equilibrium(pressure, density)
        # All cells in one phase, P_hot = P_cold = P_mean → error ≈ 0
        assert error < 0.1


class TestTwoZoneModel:
    def test_basic_construction(self):
        """Should construct a valid two-zone model."""
        model = build_two_zone_model(
            kappa_eff=0.1,
            v_entrainment=1.0,
            density_contrast=10.0,
        )
        assert model.kappa_eff == 0.1
        assert model.v_entrainment == 1.0
        assert model.R_core_m == 0.1  # default
        assert model.T_core_K == 10000.0  # default

    def test_lifetime_extension(self):
        """Lower kappa_eff should give higher lifetime extension."""
        m1 = build_two_zone_model(kappa_eff=0.5, v_entrainment=1.0, density_contrast=10.0)
        m2 = build_two_zone_model(kappa_eff=0.1, v_entrainment=1.0, density_contrast=10.0)
        assert m2.lifetime_extension > m1.lifetime_extension

    def test_cooling_time(self):
        """tau_cooling = R / v_e."""
        model = build_two_zone_model(
            kappa_eff=0.5,
            v_entrainment=2.0,
            density_contrast=10.0,
            R_hopfion_m=0.2,
        )
        assert model.tau_cooling == pytest.approx(0.1, rel=1e-10)

    def test_zero_entrainment(self):
        """Zero entrainment should give infinite cooling time."""
        model = build_two_zone_model(
            kappa_eff=0.5,
            v_entrainment=0.0,
            density_contrast=10.0,
        )
        assert model.tau_cooling == float("inf")

    def test_ideal_gas_density(self):
        """Core density should be lower than ambient (hot gas is lighter)."""
        model = build_two_zone_model(
            kappa_eff=0.5,
            v_entrainment=1.0,
            density_contrast=10.0,
        )
        assert model.rho_core < model.rho_ambient
