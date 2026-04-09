"""Hopfion stability analysis in turbulent environments using The Well datasets."""

__version__ = "0.1.0"

from .vortex_detection import (
    compute_q_criterion,
    compute_lambda2,
    compute_vortex_census,
    detect_vortex_cores,
    extract_vortex_properties,
    VortexField,
    VortexCore,
)
from .structure_tracking import (
    track_vortices,
    compute_survival_function,
    compute_lifetime_statistics,
    bin_tracks_by_parameter,
    TrackedVortex,
)
from .cooling_analysis import (
    compute_mixing_layer_width,
    analyze_mixing_layer_evolution,
    find_critical_cooling_time,
    build_cooling_stability_phase_diagram,
    map_to_atmospheric_conditions,
)
from .boundary_layer import (
    compute_density_contrast,
    compute_heat_flux_profile,
    compute_effective_insulation,
    compute_entrainment_rate,
    check_pressure_equilibrium,
    build_two_zone_model,
    BoundaryLayerModel,
    TwoZoneModel,
)
