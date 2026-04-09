"""Topological structure detection and classification in MHD fields.

Identifies localized regions with non-trivial Hopf topology by:
1. Thresholding the helicity density field h(x) = A · B
2. Connected-component labeling
3. Tracking structures across timesteps
4. Classifying geometry (ring vs blob) via inertia tensor eigenvalues

References:
    Smiet et al. (2015) PRL 115, 095001
    Arrayás & Trueba (2017) J. Phys. A 50, 025203
"""

from __future__ import annotations

from dataclasses import dataclass, field

from collections import Counter

import numpy as np
from numpy.typing import NDArray
from skimage.measure import label, regionprops


@dataclass
class TopologicalStructure:
    """A detected localized helicity structure."""

    label_id: int
    volume: float  # in grid cells
    centroid: tuple[float, float, float]
    peak_helicity_density: float
    mean_helicity_density: float
    local_hopf_charge: float  # Q_local = ∫_V h(x) d³x / (4π)²
    eigenvalues: tuple[float, float, float]  # inertia tensor eigenvalues (sorted)
    morphology: str  # "ring", "blob", "tube"
    bbox: tuple[int, ...]  # bounding box


@dataclass
class TrackedStructure:
    """A structure tracked across multiple timesteps."""

    track_id: int
    birth_time: int
    death_time: int
    lifetime: int  # in timesteps
    structures: list[TopologicalStructure] = field(default_factory=list)
    peak_hopf_charge: float = 0.0
    mean_hopf_charge: float = 0.0
    morphology_history: list[str] = field(default_factory=list)


def detect_helicity_structures(
    helicity_density: NDArray[np.float64],
    dx: float = 1.0,
    sigma_threshold: float = 3.0,
    min_volume: int = 8,
) -> list[TopologicalStructure]:
    """Detect localized helicity structures via thresholding and labeling.

    Args:
        helicity_density: h(x) = A · B, shape (Nx, Ny, Nz).
        dx: Grid spacing.
        sigma_threshold: Detection threshold in units of standard deviation.
        min_volume: Minimum structure volume in grid cells.

    Returns:
        List of detected TopologicalStructure objects.
    """
    mu = np.mean(helicity_density)
    sigma = np.std(helicity_density)

    if sigma < 1e-30:
        return []

    # Threshold on |h| (detect both positive and negative helicity)
    threshold = mu + sigma_threshold * sigma
    mask_pos = helicity_density > threshold
    mask_neg = helicity_density < (mu - sigma_threshold * sigma)
    mask = mask_pos | mask_neg

    labeled_array = label(mask, connectivity=1)
    regions = regionprops(labeled_array)

    structures = []
    dV = dx**3

    for region in regions:
        if region.area < min_volume:
            continue

        # Extract helicity values in this region
        coords = region.coords  # (N, 3) array of voxel coordinates
        h_values = helicity_density[coords[:, 0], coords[:, 1], coords[:, 2]]

        # Local Hopf charge
        local_H_m = float(np.sum(h_values) * dV)
        local_Q_H = local_H_m / (4 * np.pi) ** 2

        # Inertia tensor for morphology classification
        eigenvalues = _compute_inertia_eigenvalues(coords)

        # Classify morphology
        morphology = _classify_morphology(eigenvalues)

        centroid = tuple(float(c) for c in region.centroid)

        structures.append(
            TopologicalStructure(
                label_id=region.label,
                volume=float(region.area),
                centroid=centroid,
                peak_helicity_density=float(np.max(np.abs(h_values))),
                mean_helicity_density=float(np.mean(h_values)),
                local_hopf_charge=local_Q_H,
                eigenvalues=tuple(float(e) for e in eigenvalues),
                morphology=morphology,
                bbox=region.bbox,
            )
        )

    # Sort by |Q_H| descending
    structures.sort(key=lambda s: abs(s.local_hopf_charge), reverse=True)
    return structures


def _compute_inertia_eigenvalues(
    coords: NDArray[np.int64],
) -> NDArray[np.float64]:
    """Compute eigenvalues of the inertia tensor for a set of voxel coordinates.

    Args:
        coords: Voxel coordinates, shape (N, 3).

    Returns:
        eigenvalues: Sorted eigenvalues (ascending), shape (3,).
    """
    if len(coords) < 4:
        return np.array([1.0, 1.0, 1.0])

    centroid = np.mean(coords, axis=0)
    r = coords - centroid

    # Inertia tensor I_ij = Σ(|r|² δ_ij - r_i r_j)
    r2 = np.sum(r**2, axis=1)
    I = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if i == j:
                I[i, j] = np.sum(r2 - r[:, i] * r[:, j])
            else:
                I[i, j] = -np.sum(r[:, i] * r[:, j])

    eigenvalues = np.linalg.eigvalsh(I)
    return np.sort(eigenvalues)


def _classify_morphology(
    eigenvalues: NDArray[np.float64],
    ring_threshold: float = 0.3,
    tube_threshold: float = 3.0,
) -> str:
    """Classify structure morphology from inertia tensor eigenvalues.

    Eigenvalues are sorted ascending: λ₁ ≤ λ₂ ≤ λ₃.

    For an inertia tensor, the eigenvalue corresponding to a symmetry
    axis is small when mass is concentrated near that axis (rod/tube)
    and large when mass is spread away from it (ring/disk).

    Classification:
        - Tube/prolate: λ₁ << λ₂ ≈ λ₃ (one small, two large — rod along λ₁ axis)
        - Ring/oblate: λ₁ ≈ λ₂ << λ₃ (two small, one large — disk in λ₁-λ₂ plane)
        - Blob/spherical: λ₁ ≈ λ₂ ≈ λ₃ (all similar)

    Args:
        eigenvalues: Sorted eigenvalues (ascending), shape (3,).
        ring_threshold: Normalized smallest eigenvalue threshold. If λ₁/total < this,
            structure may be prolate (tube). Named historically; controls tube branch.
        tube_threshold: Ratio threshold λ₃/λ₂. If this ratio exceeds the value,
            structure is oblate (ring). Named historically; controls ring branch.

    Returns:
        Morphology string: "ring", "tube", or "blob".
    """
    e1, e2, e3 = eigenvalues
    total = e1 + e2 + e3

    if total < 1e-30:
        return "blob"

    # Normalized eigenvalues
    n1, n2, n3 = e1 / total, e2 / total, e3 / total

    # Tube/prolate: smallest eigenvalue << other two (which are similar)
    # A rod along axis 1 has small I_11 and large, equal I_22 ≈ I_33
    if n1 < ring_threshold and abs(n2 - n3) / max(n3, 1e-10) < 0.5:
        return "tube"

    # Ring/oblate: largest eigenvalue >> other two (which are similar)
    # A disk/ring in the 1-2 plane has large I_33 and smaller I_11 ≈ I_22
    if n3 / max(n2, 1e-10) > tube_threshold:
        return "ring"

    return "blob"


def track_structures(
    structures_by_time: list[list[TopologicalStructure]],
    overlap_threshold: float = 0.3,
    max_distance: float = 10.0,
) -> list[TrackedStructure]:
    """Track topological structures across timesteps.

    Uses centroid distance and volume ratio for matching.

    Args:
        structures_by_time: List of structure lists, one per timestep.
        overlap_threshold: Minimum volume ratio for matching.
        max_distance: Maximum centroid displacement between frames.

    Returns:
        List of TrackedStructure objects.
    """
    if not structures_by_time:
        return []

    tracks: list[TrackedStructure] = []
    active_tracks: dict[int, TrackedStructure] = {}
    next_track_id = 0

    for t, structures in enumerate(structures_by_time):
        # Try to match each structure to an active track
        matched_track_ids = set()
        unmatched_structures = []

        for struct in structures:
            best_track_id = None
            best_distance = float("inf")

            for track_id, track in active_tracks.items():
                if track_id in matched_track_ids:
                    continue

                last_struct = track.structures[-1]
                dist = np.sqrt(sum(
                    (a - b) ** 2
                    for a, b in zip(struct.centroid, last_struct.centroid)
                ))

                if dist < max_distance and dist < best_distance:
                    # Check volume similarity
                    vol_ratio = min(struct.volume, last_struct.volume) / max(
                        struct.volume, last_struct.volume, 1e-10
                    )
                    if vol_ratio > overlap_threshold:
                        best_track_id = track_id
                        best_distance = dist

            if best_track_id is not None:
                track = active_tracks[best_track_id]
                track.structures.append(struct)
                track.death_time = t
                track.lifetime = t - track.birth_time + 1
                track.morphology_history.append(struct.morphology)
                matched_track_ids.add(best_track_id)
            else:
                unmatched_structures.append(struct)

        # Close unmatched active tracks
        closed_ids = []
        for track_id in active_tracks:
            if track_id not in matched_track_ids:
                track = active_tracks[track_id]
                track.peak_hopf_charge = max(
                    abs(s.local_hopf_charge) for s in track.structures
                )
                track.mean_hopf_charge = np.mean(
                    [s.local_hopf_charge for s in track.structures]
                )
                tracks.append(track)
                closed_ids.append(track_id)

        for tid in closed_ids:
            del active_tracks[tid]

        # Start new tracks for unmatched structures
        for struct in unmatched_structures:
            track = TrackedStructure(
                track_id=next_track_id,
                birth_time=t,
                death_time=t,
                lifetime=1,
                structures=[struct],
                morphology_history=[struct.morphology],
            )
            active_tracks[next_track_id] = track
            next_track_id += 1

    # Close remaining active tracks
    for track in active_tracks.values():
        if track.structures:
            track.peak_hopf_charge = max(
                abs(s.local_hopf_charge) for s in track.structures
            )
            track.mean_hopf_charge = np.mean(
                [s.local_hopf_charge for s in track.structures]
            )
        tracks.append(track)

    # Sort by lifetime descending
    tracks.sort(key=lambda tr: tr.lifetime, reverse=True)
    return tracks


def compute_structure_statistics(
    tracks: list[TrackedStructure],
) -> dict[str, float | NDArray]:
    """Compute summary statistics for tracked structures.

    Args:
        tracks: List of TrackedStructure objects.

    Returns:
        Dictionary with statistics:
            n_structures: Total number of detected tracks
            n_rings: Number of ring-classified structures
            mean_lifetime: Mean lifetime in timesteps
            max_lifetime: Maximum lifetime
            lifetime_Q_correlation: Pearson correlation between lifetime and |Q_H|
            ring_fraction: Fraction of structures classified as ring
    """
    if not tracks:
        return {
            "n_structures": 0,
            "n_rings": 0,
            "mean_lifetime": 0.0,
            "max_lifetime": 0,
            "lifetime_Q_correlation": 0.0,
            "ring_fraction": 0.0,
        }

    lifetimes = np.array([t.lifetime for t in tracks])
    q_values = np.array([t.peak_hopf_charge for t in tracks])

    # Dominant morphology for each track
    morphologies = []
    for t in tracks:
        if t.morphology_history:
            counts = Counter(t.morphology_history)
            morphologies.append(counts.most_common(1)[0][0])
        else:
            morphologies.append("blob")

    n_rings = sum(1 for m in morphologies if m == "ring")

    # Pearson correlation between lifetime and |Q_H|
    if len(lifetimes) > 2 and np.std(lifetimes) > 0 and np.std(q_values) > 0:
        correlation = float(np.corrcoef(lifetimes, q_values)[0, 1])
    else:
        correlation = 0.0

    return {
        "n_structures": len(tracks),
        "n_rings": n_rings,
        "mean_lifetime": float(np.mean(lifetimes)),
        "max_lifetime": int(np.max(lifetimes)),
        "lifetime_Q_correlation": correlation,
        "ring_fraction": n_rings / len(tracks),
    }
