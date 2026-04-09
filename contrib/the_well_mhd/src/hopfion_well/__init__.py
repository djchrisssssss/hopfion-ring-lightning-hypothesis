"""Hopfion topology detection and analysis using The Well MHD datasets."""

__version__ = "0.1.0"

from .helicity import (
    compute_magnetic_helicity,
    compute_vector_potential,
    compute_helicity_density,
    compute_helicity_timeseries,
    compute_cross_helicity,
    compute_relative_helicity,
    verify_divergence_free,
    generate_hopf_ranada_field,
    extract_b_field_from_well,
    HelicityResult,
)
from .topology import (
    detect_helicity_structures,
    track_structures,
    compute_structure_statistics,
    TopologicalStructure,
    TrackedStructure,
)
from .spectral import (
    compute_helical_decomposition,
    compute_magnetic_energy_spectrum,
    compute_cross_helicity_spectrum,
    detect_inverse_cascade,
    SpectralAnalysis,
)
from .energy_budget import (
    compute_energy_budget,
    compute_energy_timeseries,
    compute_alfven_mach,
    compute_sonic_mach,
    hopfion_energy_budget_physical,
    EnergyBudget,
)
