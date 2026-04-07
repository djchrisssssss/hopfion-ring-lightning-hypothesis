"""Tests for hopfion_turb.cooling_analysis module."""

import numpy as np
import pytest

from hopfion_turb.cooling_analysis import (
    compute_mixing_layer_width,
    analyze_mixing_layer_evolution,
    find_critical_cooling_time,
    build_cooling_stability_phase_diagram,
    map_to_atmospheric_conditions,
)


class TestMixingLayerWidth:
    def test_uniform_density(self):
        """Uniform density (no mixing) should give zero width."""
        density = np.ones((32, 32))
        width = compute_mixing_layer_width(density)
        assert width == 0.0

    def test_step_function(self):
        """Sharp step should give zero mixing width."""
        density = np.zeros((32, 64))
        density[:, :32] = 1.0  # hot
        density[:, 32:] = 10.0  # cold

        width = compute_mixing_layer_width(density, axis=-1, rho_hot=1.0, rho_cold=10.0)
        # Sharp interface → no cells in (0.2, 0.8) range of normalized density
        assert width == 0.0

    def test_smooth_gradient(self):
        """Smooth gradient should have nonzero mixing width."""
        Nz = 64
        z = np.linspace(0, 1, Nz)
        # Tanh profile: smooth transition from 0 to 1
        profile = 0.5 * (1 + np.tanh(10 * (z - 0.5)))
        density = np.broadcast_to(profile, (16, Nz)).copy()

        width = compute_mixing_layer_width(
            density, axis=-1, rho_hot=0.0, rho_cold=1.0
        )
        assert width > 0
        assert width < Nz  # not the entire domain

    def test_custom_thresholds(self):
        """Wider threshold range should give wider mixing layer."""
        Nz = 64
        z = np.linspace(0, 1, Nz)
        profile = 0.5 * (1 + np.tanh(5 * (z - 0.5)))
        density = np.broadcast_to(profile, (16, Nz)).copy()

        w_narrow = compute_mixing_layer_width(
            density, axis=-1, rho_hot=0.0, rho_cold=1.0,
            threshold_lo=0.3, threshold_hi=0.7,
        )
        w_wide = compute_mixing_layer_width(
            density, axis=-1, rho_hot=0.0, rho_cold=1.0,
            threshold_lo=0.1, threshold_hi=0.9,
        )
        assert w_wide >= w_narrow


class TestMixingLayerEvolution:
    def test_growing_layer(self):
        """Broadening mixing layer should give positive growth rate."""
        T = 10
        Nz = 64
        z = np.linspace(0, 1, Nz)
        times = np.linspace(0, 1, T)

        density_series = np.zeros((T, Nz))
        for t in range(T):
            # Mixing layer broadens over time
            width = 5 + t * 2  # steepness decreases
            density_series[t] = 0.5 * (1 + np.tanh(width * (z - 0.5)))

        # Set rho range from first frame
        result = analyze_mixing_layer_evolution(
            density_series, times, mixing_axis=-1, t_cool=0.5,
        )
        assert result.t_cool == 0.5
        assert len(result.width) == T

    def test_static_layer(self):
        """Unchanging density should give near-zero growth rate."""
        T = 10
        Nz = 64
        z = np.linspace(0, 1, Nz)
        times = np.linspace(0, 1, T)

        profile = 0.5 * (1 + np.tanh(10 * (z - 0.5)))
        density_series = np.tile(profile, (T, 1))

        result = analyze_mixing_layer_evolution(density_series, times)
        assert abs(result.growth_rate) < 1e-10


class TestCriticalCoolingTime:
    def test_peak_detection(self):
        """Should find the t_cool that maximizes lifetime."""
        t_cool = np.array([0.1, 0.3, 1.0, 3.0, 10.0])
        lifetimes = np.array([2.0, 5.0, 10.0, 6.0, 3.0])

        tc_crit, unc = find_critical_cooling_time(t_cool, lifetimes)
        # Should be near the peak at t_cool=1.0
        assert 0.3 < tc_crit < 3.0

    def test_monotonic(self):
        """Monotonic lifetime should return endpoint."""
        t_cool = np.array([0.1, 1.0, 10.0])
        lifetimes = np.array([1.0, 2.0, 3.0])

        tc_crit, unc = find_critical_cooling_time(t_cool, lifetimes)
        # Monotonic increasing → endpoint at 10.0
        assert tc_crit == pytest.approx(10.0)

    def test_two_points(self):
        """With only 2 points, should return the one with higher lifetime."""
        t_cool = np.array([0.1, 1.0])
        lifetimes = np.array([3.0, 7.0])

        tc_crit, unc = find_critical_cooling_time(t_cool, lifetimes)
        assert tc_crit == pytest.approx(1.0)
        assert unc == float("inf")


class TestCoolingStabilityPhaseDiagram:
    def test_basic(self):
        """Should compute summary statistics for each t_cool."""
        t_cool = np.array([0.1, 1.0, 10.0])
        lifetime_data = {
            0.1: np.array([2, 3, 4]),
            1.0: np.array([5, 8, 10, 7]),
            10.0: np.array([1, 2]),
        }

        result = build_cooling_stability_phase_diagram(t_cool, lifetime_data)
        assert len(result.mean_lifetimes) == 3
        assert result.n_vortices[0] == 3
        assert result.n_vortices[1] == 4
        assert result.n_vortices[2] == 2
        assert result.t_cool_critical > 0

    def test_empty_bins(self):
        """Missing t_cool values should get zero entries."""
        t_cool = np.array([0.1, 1.0, 10.0])
        lifetime_data = {
            1.0: np.array([5, 8]),
        }

        result = build_cooling_stability_phase_diagram(t_cool, lifetime_data)
        assert result.mean_lifetimes[0] == 0.0
        assert result.n_vortices[0] == 0


class TestAtmosphericMapping:
    def test_returns_all_keys(self):
        """Should return expected mapping fields."""
        result = map_to_atmospheric_conditions(1.0)
        expected_keys = {
            "t_cool_critical_dataset",
            "t_cool_critical_physical_s",
            "t_cool_atm_range_s",
            "t_cool_atm_typical_s",
            "atm_in_optimal_range",
            "ratio_atm_to_critical",
        }
        assert set(result.keys()) == expected_keys

    def test_in_range(self):
        """t_cool=3s should be in atmospheric range (0.5-10s)."""
        result = map_to_atmospheric_conditions(3.0, dataset_time_unit=1.0)
        assert result["atm_in_optimal_range"] is True

    def test_unit_scaling(self):
        """Physical time should scale with dataset_time_unit."""
        r1 = map_to_atmospheric_conditions(1.0, dataset_time_unit=1.0)
        r2 = map_to_atmospheric_conditions(1.0, dataset_time_unit=2.0)
        assert r2["t_cool_critical_physical_s"] == pytest.approx(
            2.0 * r1["t_cool_critical_physical_s"]
        )
