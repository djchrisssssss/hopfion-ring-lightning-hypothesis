"""Lagrangian tracking of coherent structures across timesteps.

Tracks vortex cores detected in sequential snapshots using
overlap-based matching with centroid distance fallback.

Computes survival functions S(t) = P(lifetime > t) for
statistical analysis of structure persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .vortex_detection import VortexCore


@dataclass
class TrackedVortex:
    """A vortex tracked across multiple timesteps."""

    track_id: int
    birth_time: int
    death_time: int
    lifetime: int
    cores: list[VortexCore] = field(default_factory=list)
    centroid_trajectory: list[tuple[float, ...]] = field(default_factory=list)
    peak_Q_history: list[float] = field(default_factory=list)
    peak_enstrophy_history: list[float] = field(default_factory=list)
    circulation_history: list[float] = field(default_factory=list)


def track_vortices(
    cores_by_time: list[list[VortexCore]],
    max_distance: float = 8.0,
    volume_overlap_threshold: float = 0.3,
) -> list[TrackedVortex]:
    """Track vortex cores across timesteps using centroid proximity.

    Algorithm:
    1. For each structure at time t, find nearest structure at t-1
    2. Match if distance < max_distance AND volume ratio > threshold
    3. Unmatched structures start new tracks
    4. Tracks without matches are closed

    Args:
        cores_by_time: List of VortexCore lists, one per timestep.
        max_distance: Maximum centroid displacement between frames.
        volume_overlap_threshold: Minimum volume similarity ratio.

    Returns:
        List of TrackedVortex objects, sorted by lifetime (descending).
    """
    if not cores_by_time:
        return []

    tracks: list[TrackedVortex] = []
    active: dict[int, TrackedVortex] = {}
    next_id = 0

    for t, cores in enumerate(cores_by_time):
        matched_track_ids = set()
        unmatched = []

        # Build cost matrix and match greedily
        assignments = _greedy_match(
            cores, active, max_distance, volume_overlap_threshold
        )

        for core_idx, track_id in assignments.items():
            core = cores[core_idx]
            track = active[track_id]
            track.cores.append(core)
            track.death_time = t
            track.lifetime = t - track.birth_time + 1
            track.centroid_trajectory.append(core.centroid)
            track.peak_Q_history.append(core.peak_Q)
            track.peak_enstrophy_history.append(core.peak_enstrophy)
            track.circulation_history.append(core.circulation)
            matched_track_ids.add(track_id)

        # Identify unmatched cores
        for i, core in enumerate(cores):
            if i not in assignments:
                unmatched.append(core)

        # Close unmatched active tracks
        to_close = [tid for tid in active if tid not in matched_track_ids]
        for tid in to_close:
            tracks.append(active.pop(tid))

        # Start new tracks
        for core in unmatched:
            track = TrackedVortex(
                track_id=next_id,
                birth_time=t,
                death_time=t,
                lifetime=1,
                cores=[core],
                centroid_trajectory=[core.centroid],
                peak_Q_history=[core.peak_Q],
                peak_enstrophy_history=[core.peak_enstrophy],
                circulation_history=[core.circulation],
            )
            active[next_id] = track
            next_id += 1

    # Close remaining tracks
    tracks.extend(active.values())
    tracks.sort(key=lambda t: t.lifetime, reverse=True)
    return tracks


def _greedy_match(
    cores: list[VortexCore],
    active: dict[int, TrackedVortex],
    max_dist: float,
    vol_thresh: float,
) -> dict[int, int]:
    """Greedy nearest-neighbor matching between cores and active tracks.

    Returns:
        Dictionary mapping core index → track_id.
    """
    if not cores or not active:
        return {}

    assignments: dict[int, int] = {}
    used_tracks = set()

    # Build all (core_idx, track_id, distance) candidates
    candidates = []
    for i, core in enumerate(cores):
        for tid, track in active.items():
            last_centroid = track.centroid_trajectory[-1]
            dist = np.sqrt(sum(
                (a - b) ** 2 for a, b in zip(core.centroid, last_centroid)
            ))
            if dist < max_dist:
                last_vol = track.cores[-1].volume
                vol_ratio = min(core.volume, last_vol) / max(core.volume, last_vol, 1)
                if vol_ratio > vol_thresh:
                    candidates.append((dist, i, tid))

    # Sort by distance and assign greedily
    candidates.sort()
    for _, core_idx, track_id in candidates:
        if core_idx not in assignments and track_id not in used_tracks:
            assignments[core_idx] = track_id
            used_tracks.add(track_id)

    return assignments


def compute_survival_function(
    tracks: list[TrackedVortex],
    max_time: int | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute Kaplan-Meier-style survival function S(t) = P(lifetime > t).

    Args:
        tracks: List of TrackedVortex objects.
        max_time: Maximum time for survival function. Defaults to max lifetime.

    Returns:
        t: Time array.
        S: Survival probability array.
    """
    if not tracks:
        return np.array([0.0]), np.array([1.0])

    lifetimes = np.array([t.lifetime for t in tracks])

    if max_time is None:
        max_time = int(np.max(lifetimes))

    t = np.arange(0, max_time + 1, dtype=float)
    S = np.array([np.mean(lifetimes > ti) for ti in t])

    return t, S


def compute_lifetime_statistics(
    tracks: list[TrackedVortex],
) -> dict[str, float | int]:
    """Compute summary statistics for tracked vortex lifetimes.

    Args:
        tracks: List of TrackedVortex objects.

    Returns:
        Dictionary with statistics.
    """
    if not tracks:
        return {
            "n_tracks": 0,
            "mean_lifetime": 0.0,
            "median_lifetime": 0.0,
            "max_lifetime": 0,
            "std_lifetime": 0.0,
            "mean_peak_Q": 0.0,
            "lifetime_Q_correlation": 0.0,
        }

    lifetimes = np.array([t.lifetime for t in tracks])
    peak_Qs = np.array([max(t.peak_Q_history) if t.peak_Q_history else 0 for t in tracks])

    # Correlation between lifetime and peak Q
    if len(lifetimes) > 2 and np.std(lifetimes) > 0 and np.std(peak_Qs) > 0:
        corr = float(np.corrcoef(lifetimes, peak_Qs)[0, 1])
    else:
        corr = 0.0

    return {
        "n_tracks": len(tracks),
        "mean_lifetime": float(np.mean(lifetimes)),
        "median_lifetime": float(np.median(lifetimes)),
        "max_lifetime": int(np.max(lifetimes)),
        "std_lifetime": float(np.std(lifetimes)),
        "mean_peak_Q": float(np.mean(peak_Qs)),
        "lifetime_Q_correlation": corr,
    }


def bin_tracks_by_parameter(
    tracks: list[TrackedVortex],
    parameter_values: NDArray[np.float64],
    n_bins: int = 5,
) -> list[dict]:
    """Bin tracked vortex lifetimes by an external parameter.

    Useful for studying how lifetime depends on (T_0, rho_0, Z, t_cool).

    Args:
        tracks: List of TrackedVortex objects.
        parameter_values: Parameter value for each track, shape (n_tracks,).
        n_bins: Number of bins.

    Returns:
        List of dicts with bin center, mean lifetime, std, count.
    """
    if not tracks or len(parameter_values) != len(tracks):
        return []

    lifetimes = np.array([t.lifetime for t in tracks])
    bin_edges = np.linspace(
        np.min(parameter_values), np.max(parameter_values), n_bins + 1
    )

    results = []
    for i in range(n_bins):
        mask = (parameter_values >= bin_edges[i]) & (parameter_values < bin_edges[i + 1])
        if i == n_bins - 1:
            mask |= parameter_values == bin_edges[i + 1]

        if np.sum(mask) > 0:
            results.append({
                "bin_center": float((bin_edges[i] + bin_edges[i + 1]) / 2),
                "bin_lo": float(bin_edges[i]),
                "bin_hi": float(bin_edges[i + 1]),
                "count": int(np.sum(mask)),
                "mean_lifetime": float(np.mean(lifetimes[mask])),
                "std_lifetime": float(np.std(lifetimes[mask])),
                "median_lifetime": float(np.median(lifetimes[mask])),
            })

    return results
