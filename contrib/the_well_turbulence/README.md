# Hopfion Stability in Turbulent Environments

Vortex detection, structure tracking, and cooling-stability analysis for
[The Well](https://github.com/PolymathicAI/the_well) turbulence datasets
in the context of the [Hopfion Ring Lightning Hypothesis](../../README.md).

## Quick Start

```bash
# Install dependencies
pip install the_well torch numpy scipy scikit-image matplotlib plotly h5py

# Run tests
PYTHONPATH=src python -m pytest tests/ -v

# Run vortex detection on 2D radiative layer (streaming from HuggingFace)
python scripts/run_vortex_detection.py --dataset turbulent_radiative_layer_2D --split train --max-trajectories 10
```

## Modules

| Module | Description |
|--------|-------------|
| `vortex_detection.py` | Q-criterion, enstrophy, lambda-2, vortex core detection |
| `structure_tracking.py` | Lagrangian tracking, survival functions, lifetime statistics |
| `cooling_analysis.py` | Mixing layer width, critical cooling time, phase diagrams |
| `boundary_layer.py` | Two-zone model, effective insulation, entrainment rates |

## Datasets Used

- **turbulence_gravity_cooling**: 2,700 trajectories, 27 parameter sets (~829 GB)
- **turbulent_radiative_layer_2D**: 90 trajectories, 9 cooling times (~6.9 GB)
- **turbulent_radiative_layer_3D**: 90 trajectories, 9 cooling times (~745 GB)

## Hypothesis Connection

This work addresses **Problem 1** (Resistive Decay Timescale, Approaches C and D)
by providing data-driven turbulence survival constraints and two-zone model parameters.
See [CONTRIBUTION-02-TURBULENCE-en.md](../../plan/CONTRIBUTION-02-TURBULENCE-en.md).

## License

BSD-3-Clause (same as The Well)
