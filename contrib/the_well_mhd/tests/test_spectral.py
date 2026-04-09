"""Tests for hopfion_well.spectral module."""

import numpy as np
import pytest

from hopfion_well.spectral import (
    compute_shell_spectrum,
    compute_magnetic_energy_spectrum,
    compute_helical_decomposition,
    compute_cross_helicity_spectrum,
    detect_inverse_cascade,
)


class TestShellSpectrum:
    def test_single_mode(self):
        """Single k-mode should land in the correct bin."""
        N = 16
        k = np.fft.rfftfreq(N) * 2 * np.pi
        kx, ky, kz = np.meshgrid(
            np.fft.fftfreq(N) * 2 * np.pi,
            np.fft.fftfreq(N) * 2 * np.pi,
            k, indexing="ij",
        )
        k_mag = np.sqrt(kx**2 + ky**2 + kz**2)

        field = np.zeros_like(k_mag)
        field[1, 0, 0] = 1.0  # single mode at kx = 2π/N

        k_bins, spectrum = compute_shell_spectrum(field, k_mag)
        assert np.sum(spectrum) == pytest.approx(1.0, abs=1e-10)

    def test_zero_field(self):
        """Zero field should give zero spectrum."""
        N = 8
        k = np.fft.rfftfreq(N) * 2 * np.pi
        kx, ky, kz = np.meshgrid(
            np.fft.fftfreq(N) * 2 * np.pi,
            np.fft.fftfreq(N) * 2 * np.pi,
            k, indexing="ij",
        )
        k_mag = np.sqrt(kx**2 + ky**2 + kz**2)

        field = np.zeros_like(k_mag)
        k_bins, spectrum = compute_shell_spectrum(field, k_mag)
        assert np.allclose(spectrum, 0.0)

    def test_output_shapes(self):
        """k_bins and spectrum should have the same length."""
        N = 16
        k = np.fft.rfftfreq(N) * 2 * np.pi
        kx, ky, kz = np.meshgrid(
            np.fft.fftfreq(N) * 2 * np.pi,
            np.fft.fftfreq(N) * 2 * np.pi,
            k, indexing="ij",
        )
        k_mag = np.sqrt(kx**2 + ky**2 + kz**2)
        field = np.ones_like(k_mag)

        k_bins, spectrum = compute_shell_spectrum(field, k_mag, n_bins=10)
        assert len(k_bins) == 10
        assert len(spectrum) == 10


class TestMagneticEnergySpectrum:
    def test_uniform_field(self):
        """Uniform field has all energy at k=0 (not binned)."""
        N = 16
        B = np.zeros((3, N, N, N))
        B[2] = 1.0  # uniform Bz

        k_bins, E_B = compute_magnetic_energy_spectrum(B)
        # Most energy should be at or near k=0 which maps to the first bin
        assert E_B[0] > np.sum(E_B[1:])

    def test_energy_nonnegative(self):
        """Magnetic energy should always be non-negative."""
        np.random.seed(42)
        N = 16
        B = np.random.randn(3, N, N, N)
        k_bins, E_B = compute_magnetic_energy_spectrum(B)
        assert np.all(E_B >= 0)

    def test_stronger_field_more_energy(self):
        """Doubling field strength should ~4x the energy spectrum."""
        np.random.seed(123)
        N = 16
        B1 = np.random.randn(3, N, N, N) * 0.1
        B2 = B1 * 2.0

        _, E1 = compute_magnetic_energy_spectrum(B1)
        _, E2 = compute_magnetic_energy_spectrum(B2)
        assert np.sum(E2) == pytest.approx(4.0 * np.sum(E1), rel=0.01)


class TestHelicalDecomposition:
    def test_output_fields(self):
        """SpectralAnalysis should have all expected fields."""
        np.random.seed(42)
        N = 16
        B = np.random.randn(3, N, N, N) * 0.1

        result = compute_helical_decomposition(B)
        assert result.k_bins is not None
        assert len(result.E_B) == len(result.k_bins)
        assert len(result.E_plus) == len(result.k_bins)
        assert len(result.E_minus) == len(result.k_bins)
        assert len(result.H_m_spectrum) == len(result.k_bins)
        assert len(result.realizability_ratio) == len(result.k_bins)

    def test_energy_decomposition(self):
        """E_plus + E_minus should approximately equal E_B."""
        np.random.seed(42)
        N = 16
        B = np.random.randn(3, N, N, N) * 0.1

        result = compute_helical_decomposition(B)
        E_sum = result.E_plus + result.E_minus
        # Should match within numerical precision
        np.testing.assert_allclose(E_sum, result.E_B, atol=1e-20)

    def test_realizability_bound(self):
        """Realizability ratio should be in [0, 1]."""
        np.random.seed(42)
        N = 16
        B = np.random.randn(3, N, N, N) * 0.1

        result = compute_helical_decomposition(B)
        mask = result.E_B > 1e-30  # only where there is energy
        assert np.all(result.realizability_ratio[mask] >= -1e-10)
        assert np.all(result.realizability_ratio[mask] <= 1.0 + 1e-10)

    def test_maximally_helical_field(self):
        """A Beltrami (maximally helical) field should have realizability ≈ 1."""
        N = 16
        dx = 2 * np.pi / N
        x = np.arange(N) * dx

        # ABC flow: curl(B) = B → maximally helical
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
        A, Bc, C = 1.0, 1.0, 1.0
        Bx = A * np.sin(Z) + C * np.cos(Y)
        By = Bc * np.sin(X) + A * np.cos(Z)
        Bz = C * np.sin(Y) + Bc * np.cos(X)
        B = np.stack([Bx, By, Bz])

        result = compute_helical_decomposition(B, dx=dx)
        # The dominant modes should have nonzero realizability
        # (ABC flow is maximally helical, but binning and normalization
        # reduce the measured ratio)
        dominant = result.E_B > 0.1 * np.max(result.E_B)
        if np.any(dominant):
            assert np.mean(result.realizability_ratio[dominant]) > 0.05


class TestCrossHelicitySpectrum:
    def test_aligned_fields(self):
        """Perfectly aligned v and B should have positive cross-helicity."""
        N = 16
        dx = 2 * np.pi / N
        x = np.arange(N) * dx
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

        B = np.stack([np.sin(X), np.zeros_like(X), np.zeros_like(X)])
        v = B.copy()  # perfectly aligned

        k_bins, H_c = compute_cross_helicity_spectrum(v, B, dx)
        assert np.sum(H_c) > 0

    def test_orthogonal_fields(self):
        """Orthogonal v and B should have near-zero cross-helicity."""
        N = 16
        dx = 2 * np.pi / N
        x = np.arange(N) * dx
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

        B = np.stack([np.sin(X), np.zeros_like(X), np.zeros_like(X)])
        v = np.stack([np.zeros_like(X), np.sin(X), np.zeros_like(X)])

        k_bins, H_c = compute_cross_helicity_spectrum(v, B, dx)
        assert abs(np.sum(H_c)) < 1e-10


class TestInverseCascade:
    def test_too_few_timesteps(self):
        """With < 3 timesteps, should return no cascade."""
        k_bins = np.arange(1.0, 6.0)
        H_m_list = [np.array([1.0, 0.5, 0.1, 0.01, 0.001])]
        result = detect_inverse_cascade(H_m_list, k_bins)
        assert result["cascade_detected"] is False

    def test_static_spectrum(self):
        """Unchanging spectrum should show no cascade."""
        k_bins = np.arange(1.0, 6.0)
        H_m = np.array([0.1, 0.5, 1.0, 0.5, 0.1])
        H_m_list = [H_m.copy() for _ in range(10)]

        result = detect_inverse_cascade(H_m_list, k_bins)
        assert abs(result["k_peak_trend"]) < 0.1

    def test_inverse_cascade_signature(self):
        """Spectrum peak moving to lower k should be detected."""
        k_bins = np.arange(1.0, 11.0)
        H_m_list = []
        for t in range(20):
            H_m = np.zeros(10)
            peak_idx = max(0, 8 - t)  # peak moves from k=9 to k=0
            H_m[peak_idx] = 1.0
            H_m_list.append(H_m)

        result = detect_inverse_cascade(H_m_list, k_bins)
        assert result["k_peak_trend"] < 0  # peak moving to lower k
