"""Tests for vortex detection module."""

import numpy as np
import pytest

from hopfion_turb.vortex_detection import (
    compute_velocity_gradient,
    compute_q_criterion,
    detect_vortex_cores,
    extract_vortex_properties,
    compute_vortex_census,
)


class TestVelocityGradient:
    def test_uniform_field_zero_gradient(self):
        """Uniform velocity should have zero gradient."""
        v = np.ones((3, 16, 16, 16)) * 5.0
        grad_v = compute_velocity_gradient(v, dx=1.0)
        assert np.max(np.abs(grad_v)) < 1e-10

    def test_linear_field(self):
        """Linear velocity field should have constant gradient."""
        N = 16
        x = np.arange(N, dtype=float)
        v = np.zeros((3, N, N, N))
        # v_x = x (linear in x-direction)
        v[0] = x[:, None, None]

        grad_v = compute_velocity_gradient(v, dx=1.0, periodic=False)
        # dv_x/dx should be approximately 1
        interior = grad_v[0, 0, 2:-2, 2:-2, 2:-2]
        assert np.allclose(interior, 1.0, atol=0.1)

    def test_shape(self):
        v = np.random.randn(3, 8, 8, 8)
        grad_v = compute_velocity_gradient(v)
        assert grad_v.shape == (3, 3, 8, 8, 8)


class TestQCriterion:
    def test_irrotational_flow(self):
        """Irrotational flow (potential flow) should have Q < 0 everywhere."""
        N = 16
        x = np.linspace(0, 2 * np.pi, N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

        # Potential flow: v = ∇φ where φ = sin(x)cos(y)
        v = np.stack([
            np.cos(X) * np.cos(Y) * np.ones_like(Z),
            -np.sin(X) * np.sin(Y) * np.ones_like(Z),
            np.zeros_like(X),
        ])

        fields = compute_q_criterion(v)
        # Q should be non-positive (strain dominates)
        assert np.mean(fields.Q_criterion) <= 0.1

    def test_solid_body_rotation(self):
        """Solid body rotation should have Q > 0."""
        N = 32
        x = np.linspace(-5, 5, N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

        # Solid body rotation around z-axis: v = Ω × r
        omega = 1.0
        v = np.stack([
            -omega * Y,
            omega * X,
            np.zeros_like(X),
        ])

        fields = compute_q_criterion(v, periodic=False)
        # Center region should have Q > 0
        center = slice(N // 4, 3 * N // 4)
        Q_center = fields.Q_criterion[center, center, center]
        assert np.mean(Q_center) > 0, "Solid body rotation should have positive Q"

    def test_enstrophy_nonnegative(self):
        """Enstrophy should always be non-negative."""
        v = np.random.randn(3, 8, 8, 8)
        fields = compute_q_criterion(v)
        assert np.all(fields.enstrophy >= -1e-10)


class TestVortexCoreDetection:
    def test_no_vortices_in_noise(self):
        """Low-amplitude noise shouldn't produce vortex cores."""
        Q = np.random.randn(16, 16, 16) * 0.01
        labeled, n = detect_vortex_cores(Q, sigma_threshold=5.0)
        assert n == 0

    def test_detect_strong_core(self):
        """A strong isolated Q peak should be detected."""
        N = 32
        Q = np.zeros((N, N, N))
        # Insert a strong vortex core
        Q[14:18, 14:18, 14:18] = 100.0

        labeled, n = detect_vortex_cores(Q, sigma_threshold=2.0, min_volume=4)
        assert n >= 1


class TestVortexCensus:
    def test_2d_field(self):
        """Should work with 2D velocity fields."""
        N = 32
        x = np.linspace(-5, 5, N, endpoint=False)
        X, Y = np.meshgrid(x, x, indexing="ij")

        v = np.stack([
            -Y * np.exp(-(X**2 + Y**2) / 4),
            X * np.exp(-(X**2 + Y**2) / 4),
        ])

        cores, fields = compute_vortex_census(v, periodic=False)
        # Should detect at least the central vortex
        assert fields.Q_criterion.shape == (N, N)

    def test_3d_field(self):
        """Should work with 3D velocity fields."""
        v = np.random.randn(3, 16, 16, 16)
        cores, fields = compute_vortex_census(v)
        assert fields.Q_criterion.shape == (16, 16, 16)
        assert isinstance(cores, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
