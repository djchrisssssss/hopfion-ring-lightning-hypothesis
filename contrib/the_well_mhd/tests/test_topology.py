"""Tests for topological structure detection module."""

import numpy as np
import pytest

from hopfion_well.topology import (
    detect_helicity_structures,
    track_structures,
    compute_structure_statistics,
    _compute_inertia_eigenvalues,
    _classify_morphology,
)


class TestDetectStructures:
    def test_uniform_field_no_structures(self):
        """Uniform helicity density should yield no structures."""
        h = np.ones((16, 16, 16)) * 5.0
        structures = detect_helicity_structures(h, sigma_threshold=3.0)
        assert len(structures) == 0

    def test_gaussian_blob(self):
        """A Gaussian blob of helicity should be detected."""
        N = 32
        h = np.zeros((N, N, N))
        cx, cy, cz = N // 2, N // 2, N // 2
        x, y, z = np.mgrid[:N, :N, :N]
        r2 = (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2
        h = 10.0 * np.exp(-r2 / 8.0)  # Gaussian blob

        structures = detect_helicity_structures(h, sigma_threshold=2.0)
        assert len(structures) >= 1, "Should detect at least one structure"
        assert structures[0].morphology == "blob"

    def test_min_volume_filter(self):
        """Structures below min_volume should be filtered out."""
        N = 16
        h = np.zeros((N, N, N))
        h[5, 5, 5] = 100.0  # Single voxel — below min_volume=8

        structures = detect_helicity_structures(h, sigma_threshold=1.0, min_volume=8)
        assert len(structures) == 0


class TestMorphologyClassification:
    def test_blob(self):
        """Equal eigenvalues → blob."""
        eigenvalues = np.array([1.0, 1.0, 1.0])
        assert _classify_morphology(eigenvalues) == "blob"

    def test_ring(self):
        """One small eigenvalue, two large → ring."""
        eigenvalues = np.array([0.05, 0.475, 0.475]) * 3
        morphology = _classify_morphology(eigenvalues, ring_threshold=0.3)
        assert morphology == "ring"

    def test_tube(self):
        """One large eigenvalue, two small → tube."""
        eigenvalues = np.array([0.1, 0.1, 10.0])
        morphology = _classify_morphology(eigenvalues, tube_threshold=3.0)
        assert morphology == "tube"


class TestInertiaEigenvalues:
    def test_sphere(self):
        """Spherical distribution should have roughly equal eigenvalues."""
        np.random.seed(42)
        N = 500
        coords = np.random.randn(N, 3) * 5
        coords = coords + 50  # offset
        coords = coords.astype(np.int64)

        eigenvalues = _compute_inertia_eigenvalues(coords)
        ratios = eigenvalues / eigenvalues.max()
        assert all(r > 0.5 for r in ratios), "Sphere should have similar eigenvalues"

    def test_rod(self):
        """Rod-like distribution should have one dominant eigenvalue."""
        N = 100
        coords = np.zeros((N, 3), dtype=np.int64)
        coords[:, 0] = np.arange(N)
        coords[:, 1] = 50
        coords[:, 2] = 50

        eigenvalues = _compute_inertia_eigenvalues(coords)
        assert eigenvalues[2] > 10 * eigenvalues[0], "Rod should have one large eigenvalue"


class TestTracking:
    def test_stationary_structure(self):
        """A structure that stays in the same place should be tracked."""
        from hopfion_well.topology import TopologicalStructure

        structures_by_time = []
        for t in range(5):
            s = TopologicalStructure(
                label_id=1,
                volume=100.0,
                centroid=(10.0, 10.0, 10.0),
                peak_helicity_density=5.0,
                mean_helicity_density=3.0,
                local_hopf_charge=0.8,
                eigenvalues=(1.0, 1.0, 1.0),
                morphology="blob",
                bbox=(5, 5, 5, 15, 15, 15),
            )
            structures_by_time.append([s])

        tracks = track_structures(structures_by_time)
        assert len(tracks) >= 1
        assert tracks[0].lifetime == 5

    def test_moving_structure(self):
        """A slowly moving structure should be tracked."""
        from hopfion_well.topology import TopologicalStructure

        structures_by_time = []
        for t in range(5):
            s = TopologicalStructure(
                label_id=1,
                volume=100.0,
                centroid=(10.0 + t, 10.0, 10.0),  # Move 1 unit per step
                peak_helicity_density=5.0,
                mean_helicity_density=3.0,
                local_hopf_charge=0.8,
                eigenvalues=(1.0, 1.0, 1.0),
                morphology="blob",
                bbox=(5, 5, 5, 15, 15, 15),
            )
            structures_by_time.append([s])

        tracks = track_structures(structures_by_time, max_distance=5.0)
        assert len(tracks) >= 1
        assert tracks[0].lifetime == 5

    def test_empty_frames(self):
        """Empty frames should not crash."""
        tracks = track_structures([[], [], []])
        assert len(tracks) == 0


class TestStatistics:
    def test_empty(self):
        stats = compute_structure_statistics([])
        assert stats["n_structures"] == 0

    def test_basic_stats(self):
        from hopfion_well.topology import TrackedStructure, TopologicalStructure

        s = TopologicalStructure(
            label_id=1, volume=50, centroid=(5, 5, 5),
            peak_helicity_density=3.0, mean_helicity_density=2.0,
            local_hopf_charge=0.5, eigenvalues=(1, 1, 1),
            morphology="blob", bbox=(0, 0, 0, 10, 10, 10),
        )
        track = TrackedStructure(
            track_id=0, birth_time=0, death_time=4, lifetime=5,
            structures=[s] * 5, peak_hopf_charge=0.5, mean_hopf_charge=0.5,
            morphology_history=["blob"] * 5,
        )

        stats = compute_structure_statistics([track])
        assert stats["n_structures"] == 1
        assert stats["mean_lifetime"] == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
