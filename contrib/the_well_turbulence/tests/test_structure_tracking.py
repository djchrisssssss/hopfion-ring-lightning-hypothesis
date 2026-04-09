"""Tests for structure tracking module."""

import numpy as np
import pytest

from hopfion_turb.vortex_detection import VortexCore
from hopfion_turb.structure_tracking import (
    track_vortices,
    compute_survival_function,
    compute_lifetime_statistics,
    bin_tracks_by_parameter,
)


def make_core(core_id=1, centroid=(10.0, 10.0, 10.0), volume=50, peak_Q=5.0):
    return VortexCore(
        core_id=core_id,
        volume=volume,
        centroid=centroid,
        peak_Q=peak_Q,
        mean_Q=peak_Q * 0.6,
        peak_enstrophy=peak_Q * 2,
        mean_enstrophy=peak_Q,
        circulation=peak_Q * 10,
        bbox=(0, 0, 0, 20, 20, 20),
    )


class TestTracking:
    def test_stationary(self):
        cores_by_time = [[make_core()] for _ in range(10)]
        tracks = track_vortices(cores_by_time)
        assert len(tracks) >= 1
        assert tracks[0].lifetime == 10

    def test_moving(self):
        cores_by_time = [
            [make_core(centroid=(10.0 + t * 0.5, 10.0, 10.0))]
            for t in range(10)
        ]
        tracks = track_vortices(cores_by_time, max_distance=5.0)
        assert tracks[0].lifetime == 10

    def test_two_separate(self):
        cores_by_time = [
            [
                make_core(core_id=1, centroid=(5.0, 5.0, 5.0)),
                make_core(core_id=2, centroid=(50.0, 50.0, 50.0)),
            ]
            for _ in range(5)
        ]
        tracks = track_vortices(cores_by_time)
        assert len(tracks) >= 2
        for t in tracks:
            assert t.lifetime == 5

    def test_birth_and_death(self):
        cores_by_time = [
            [make_core(centroid=(10, 10, 10))],
            [make_core(centroid=(10, 10, 10))],
            [],  # structure dies
            [make_core(centroid=(30, 30, 30))],  # new structure
            [make_core(centroid=(30, 30, 30))],
        ]
        tracks = track_vortices(cores_by_time)
        assert len(tracks) >= 2

    def test_empty(self):
        tracks = track_vortices([])
        assert len(tracks) == 0


class TestSurvivalFunction:
    def test_basic(self):
        from hopfion_turb.structure_tracking import TrackedVortex

        tracks = [
            TrackedVortex(0, 0, 9, 10, [], [], [], [], []),
            TrackedVortex(1, 0, 4, 5, [], [], [], [], []),
            TrackedVortex(2, 0, 2, 3, [], [], [], [], []),
        ]
        t, S = compute_survival_function(tracks)
        assert S[0] == 1.0  # All survive at t=0
        assert S[-1] <= 1.0

    def test_empty(self):
        t, S = compute_survival_function([])
        assert len(t) == 1
        assert S[0] == 1.0


class TestLifetimeStatistics:
    def test_basic(self):
        from hopfion_turb.structure_tracking import TrackedVortex

        tracks = [
            TrackedVortex(0, 0, 9, 10, [], [], [5.0], [], []),
            TrackedVortex(1, 0, 4, 5, [], [], [3.0], [], []),
        ]
        stats = compute_lifetime_statistics(tracks)
        assert stats["n_tracks"] == 2
        assert stats["mean_lifetime"] == 7.5
        assert stats["max_lifetime"] == 10

    def test_empty(self):
        stats = compute_lifetime_statistics([])
        assert stats["n_tracks"] == 0


class TestBinning:
    def test_basic_binning(self):
        from hopfion_turb.structure_tracking import TrackedVortex

        tracks = [
            TrackedVortex(i, 0, i, i + 1, [], [], [], [], [])
            for i in range(20)
        ]
        params = np.linspace(0, 1, 20)
        bins = bin_tracks_by_parameter(tracks, params, n_bins=4)
        assert len(bins) == 4
        assert all("mean_lifetime" in b for b in bins)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
