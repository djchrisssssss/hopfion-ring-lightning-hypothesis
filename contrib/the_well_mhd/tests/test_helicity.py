"""Tests for magnetic helicity computation module."""

import numpy as np
import pytest

from hopfion_well.helicity import (
    build_k_grid,
    compute_helicity_density,
    compute_magnetic_helicity,
    compute_vector_potential,
    generate_hopf_ranada_field,
    verify_divergence_free,
    compute_cross_helicity,
    compute_relative_helicity,
)


class TestBuildKGrid:
    def test_shape(self):
        kx, ky, kz, k2 = build_k_grid((16, 16, 16))
        assert kx.shape == (16, 16, 9)  # rfft: N//2 + 1
        assert k2.shape == (16, 16, 9)

    def test_k0_safe(self):
        _, _, _, k2 = build_k_grid((8, 8, 8))
        assert k2[0, 0, 0] == 1.0  # Avoid div-by-zero


class TestVectorPotential:
    def test_uniform_field_zero_helicity(self):
        """Uniform B should give A with zero helicity."""
        N = 16
        B = np.zeros((3, N, N, N))
        B[2] = 1.0  # Uniform Bz

        A = compute_vector_potential(B)
        h = compute_helicity_density(A, B)
        H_m = np.sum(h)

        assert abs(H_m) < 1e-10, f"Uniform field should have zero helicity, got {H_m}"

    def test_coulomb_gauge(self):
        """Vector potential should satisfy Coulomb gauge: ∇·A = 0."""
        N = 16
        B = generate_hopf_ranada_field(N)
        A = compute_vector_potential(B)

        # Check ∇·A via spectral method
        kx, ky, kz, _ = build_k_grid((N, N, N))
        Ax_hat = np.fft.rfftn(A[0])
        Ay_hat = np.fft.rfftn(A[1])
        Az_hat = np.fft.rfftn(A[2])

        div_A_hat = 1j * (kx * Ax_hat + ky * Ay_hat + kz * Az_hat)
        div_A = np.fft.irfftn(div_A_hat, s=(N, N, N))

        assert np.max(np.abs(div_A)) < 1e-10, "Coulomb gauge violated"

    def test_curl_A_equals_B(self):
        """∇ × A should equal B for a divergence-free field."""
        N = 16
        dx = 2 * np.pi / N
        # Use a simple ABC flow (exactly div-free on periodic grid)
        x = np.linspace(0, 2 * np.pi, N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
        B = np.stack([
            np.sin(Z) + np.cos(Y),
            np.sin(X) + np.cos(Z),
            np.sin(Y) + np.cos(X),
        ])

        A = compute_vector_potential(B, dx=dx)

        # Compute ∇ × A spectrally
        kx, ky, kz, _ = build_k_grid((N, N, N), dx=dx)
        Ax_hat = np.fft.rfftn(A[0])
        Ay_hat = np.fft.rfftn(A[1])
        Az_hat = np.fft.rfftn(A[2])

        curl_x = np.fft.irfftn(1j * (ky * Az_hat - kz * Ay_hat), s=(N, N, N))
        curl_y = np.fft.irfftn(1j * (kz * Ax_hat - kx * Az_hat), s=(N, N, N))
        curl_z = np.fft.irfftn(1j * (kx * Ay_hat - ky * Ax_hat), s=(N, N, N))

        curl_A = np.stack([curl_x, curl_y, curl_z])

        err = np.max(np.abs(curl_A - B)) / np.max(np.abs(B))
        assert err < 1e-6, f"∇×A ≠ B, relative error: {err}"


class TestMagneticHelicity:
    def test_hopf_ranada_nonzero_helicity(self):
        """Hopf-Ranada field should have non-zero helicity."""
        N = 32
        B = generate_hopf_ranada_field(N)
        result = compute_magnetic_helicity(B)

        assert abs(result.global_helicity) > 1e-10, \
            f"Hopf-Ranada field should have non-zero H_m, got {result.global_helicity}"

    def test_zero_field_zero_helicity(self):
        """Zero field should give zero helicity."""
        N = 8
        B = np.zeros((3, N, N, N))
        result = compute_magnetic_helicity(B)

        assert result.global_helicity == 0.0
        assert result.hopf_charge == 0.0

    def test_helicity_density_shape(self):
        N = 16
        B = generate_hopf_ranada_field(N)
        result = compute_magnetic_helicity(B)

        assert result.helicity_density.shape == (N, N, N)
        assert result.vector_potential.shape == (3, N, N, N)


class TestDivergenceFree:
    def test_hopf_ranada_approximately_divfree(self):
        """Hopf-Ranada field should be approximately divergence-free."""
        N = 32
        B = generate_hopf_ranada_field(N)
        div_err = verify_divergence_free(B)

        # Not exactly zero due to discrete construction, but should be small
        assert div_err < 0.1, f"div(B) error too large: {div_err}"


class TestCrossHelicity:
    def test_aligned_fields(self):
        """Perfectly aligned v and B should have maximum cross-helicity."""
        N = 8
        B = np.random.randn(3, N, N, N)
        v = B.copy()  # v ∥ B

        H_c = compute_cross_helicity(v, B)
        assert H_c > 0, "Aligned fields should have positive cross-helicity"

    def test_orthogonal_fields(self):
        """Orthogonal v and B should have zero cross-helicity."""
        N = 8
        B = np.zeros((3, N, N, N))
        B[0] = 1.0
        v = np.zeros((3, N, N, N))
        v[1] = 1.0

        H_c = compute_cross_helicity(v, B)
        assert abs(H_c) < 1e-10


class TestRelativeHelicity:
    def test_range(self):
        """Relative helicity should be in [-1, 1]."""
        N = 16
        B = generate_hopf_ranada_field(N)
        H_rel = compute_relative_helicity(B)

        assert -1.0 <= H_rel <= 1.0, f"Relative helicity out of range: {H_rel}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
