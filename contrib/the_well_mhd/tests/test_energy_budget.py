"""Tests for hopfion_well.energy_budget module."""

import numpy as np
import pytest

from hopfion_well.energy_budget import (
    compute_magnetic_energy_density,
    compute_kinetic_energy_density,
    compute_energy_budget,
    compute_energy_timeseries,
    compute_alfven_mach,
    compute_sonic_mach,
    hopfion_energy_budget_physical,
    MU_0_CODE,
)


class TestMagneticEnergyDensity:
    def test_uniform_field(self):
        """Uniform B should give uniform energy density B²/(2μ₀)."""
        N = 8
        B = np.zeros((3, N, N, N))
        B[2] = 2.0  # Bz = 2

        e_B = compute_magnetic_energy_density(B)
        expected = 2.0**2 / (2.0 * MU_0_CODE)
        assert np.allclose(e_B, expected)

    def test_zero_field(self):
        """Zero field should give zero energy."""
        N = 8
        B = np.zeros((3, N, N, N))
        e_B = compute_magnetic_energy_density(B)
        assert np.allclose(e_B, 0.0)

    def test_shape(self):
        """Output shape should match spatial dimensions."""
        N = 8
        B = np.random.randn(3, N, N, N)
        e_B = compute_magnetic_energy_density(B)
        assert e_B.shape == (N, N, N)


class TestKineticEnergyDensity:
    def test_uniform(self):
        """Uniform density and velocity should give (1/2)ρv²."""
        N = 8
        rho = np.ones((N, N, N)) * 2.0
        v = np.zeros((3, N, N, N))
        v[0] = 3.0  # vx = 3

        e_K = compute_kinetic_energy_density(rho, v)
        expected = 0.5 * 2.0 * 3.0**2
        assert np.allclose(e_K, expected)

    def test_zero_velocity(self):
        """Zero velocity should give zero kinetic energy."""
        N = 8
        rho = np.ones((N, N, N))
        v = np.zeros((3, N, N, N))
        e_K = compute_kinetic_energy_density(rho, v)
        assert np.allclose(e_K, 0.0)


class TestEnergyBudget:
    def test_equipartition(self):
        """When E_mag = E_kin, equipartition ratio should be ~1."""
        N = 8
        B = np.zeros((3, N, N, N))
        B[0] = 1.0
        v = np.zeros((3, N, N, N))
        rho = np.ones((N, N, N))

        # E_B = B²/(2μ₀) * V = 1/(2*1) * N³ = N³/2
        # E_K = (1/2)ρv² * V → set v so E_K = N³/2
        # v² = 1/μ₀ = 1 → v = 1
        v[0] = 1.0

        budget = compute_energy_budget(B, v, rho)
        assert budget.equipartition_ratio == pytest.approx(1.0, rel=0.01)

    def test_total_energy(self):
        """E_total should equal E_magnetic + E_kinetic."""
        np.random.seed(42)
        N = 8
        B = np.random.randn(3, N, N, N) * 0.5
        v = np.random.randn(3, N, N, N) * 0.5
        rho = np.ones((N, N, N))

        budget = compute_energy_budget(B, v, rho)
        assert budget.E_total == pytest.approx(
            budget.E_magnetic + budget.E_kinetic, rel=1e-10
        )

    def test_plasma_beta_with_pressure(self):
        """Plasma beta should be computed when pressure is provided."""
        N = 8
        B = np.zeros((3, N, N, N))
        B[0] = 1.0
        v = np.zeros((3, N, N, N))
        rho = np.ones((N, N, N))
        P = np.ones((N, N, N)) * 0.5

        budget = compute_energy_budget(B, v, rho, pressure=P)
        assert not np.isnan(budget.beta_plasma)
        # beta = 2μ₀ P / B² = 2*1*0.5/1 = 1.0
        assert budget.beta_plasma == pytest.approx(1.0, rel=0.01)

    def test_plasma_beta_without_pressure(self):
        """Without pressure, beta should be NaN."""
        N = 8
        B = np.ones((3, N, N, N))
        v = np.zeros((3, N, N, N))
        rho = np.ones((N, N, N))

        budget = compute_energy_budget(B, v, rho)
        assert np.isnan(budget.beta_plasma)


class TestEnergyTimeseries:
    def test_shape(self):
        """Time series output should have length T."""
        T, N = 5, 8
        B = np.random.randn(T, 3, N, N, N) * 0.1
        v = np.random.randn(T, 3, N, N, N) * 0.1
        rho = np.ones((T, N, N, N))

        result = compute_energy_timeseries(B, v, rho)
        assert len(result["E_magnetic"]) == T
        assert len(result["E_kinetic"]) == T
        assert len(result["E_total"]) == T


class TestAlfvenMach:
    def test_sub_alfvenic(self):
        """Slow flow in strong field should give M_A < 1."""
        N = 8
        v = np.zeros((3, N, N, N))
        v[0] = 0.1
        B = np.zeros((3, N, N, N))
        B[0] = 10.0
        rho = np.ones((N, N, N))

        M_A = compute_alfven_mach(v, B, rho)
        assert M_A < 1.0

    def test_super_alfvenic(self):
        """Fast flow in weak field should give M_A > 1."""
        N = 8
        v = np.zeros((3, N, N, N))
        v[0] = 10.0
        B = np.zeros((3, N, N, N))
        B[0] = 0.1
        rho = np.ones((N, N, N))

        M_A = compute_alfven_mach(v, B, rho)
        assert M_A > 1.0


class TestSonicMach:
    def test_with_explicit_cs(self):
        """Given c_s, M_s = v_rms / c_s."""
        N = 8
        v = np.zeros((3, N, N, N))
        v[0] = 2.0
        rho = np.ones((N, N, N))

        M_s = compute_sonic_mach(v, rho, c_s=1.0)
        assert M_s == pytest.approx(2.0, rel=0.01)

    def test_with_pressure(self):
        """With pressure, c_s = sqrt(gamma*P/rho)."""
        N = 8
        v = np.zeros((3, N, N, N))
        v[0] = 1.0
        rho = np.ones((N, N, N))
        P = np.ones((N, N, N))

        # c_s = sqrt(5/3 * 1 / 1) ≈ 1.29
        M_s = compute_sonic_mach(v, rho, pressure=P, gamma=5.0 / 3.0)
        expected = 1.0 / np.sqrt(5.0 / 3.0)
        assert M_s == pytest.approx(expected, rel=0.01)

    def test_isothermal_default(self):
        """Isothermal with no c_s should use c_s=1 (return v_rms)."""
        N = 8
        v = np.zeros((3, N, N, N))
        v[0] = 3.0
        rho = np.ones((N, N, N))

        M_s = compute_sonic_mach(v, rho, gamma=1.0)
        assert M_s == pytest.approx(3.0, rel=0.01)


class TestHopfionPhysical:
    def test_returns_all_keys(self):
        """Should return all expected energy components."""
        result = hopfion_energy_budget_physical()
        expected_keys = {
            "E_magnetic_J", "E_kinetic_J", "E_thermal_J",
            "E_total_J", "E_total_kJ", "V_torus_m3",
            "rho_kg_m3", "n_density_m3", "dominant_component",
        }
        assert set(result.keys()) == expected_keys

    def test_positive_energies(self):
        """All energy components should be positive."""
        result = hopfion_energy_budget_physical()
        assert result["E_magnetic_J"] > 0
        assert result["E_kinetic_J"] > 0
        assert result["E_thermal_J"] > 0
        assert result["E_total_J"] > 0

    def test_energy_sum(self):
        """E_total should equal sum of components."""
        result = hopfion_energy_budget_physical()
        expected = result["E_magnetic_J"] + result["E_kinetic_J"] + result["E_thermal_J"]
        assert result["E_total_J"] == pytest.approx(expected, rel=1e-10)

    def test_ball_lightning_range(self):
        """Default params should give energy in plausible ball lightning range (1-100 kJ)."""
        result = hopfion_energy_budget_physical()
        # Ball lightning observed energy: 8-80 kJ (wide range)
        assert 0.01 < result["E_total_kJ"] < 1000

    def test_torus_volume(self):
        """Torus volume V = 2π² R r²."""
        R, r = 0.1, 0.05
        result = hopfion_energy_budget_physical(R_major_m=R, R_minor_m=r)
        expected_V = 2 * np.pi**2 * R * r**2
        assert result["V_torus_m3"] == pytest.approx(expected_V, rel=1e-10)
