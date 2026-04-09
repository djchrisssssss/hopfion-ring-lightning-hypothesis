# Hopfion Topology Detection via The Well MHD Datasets

Magnetic helicity computation, topological structure detection, and spectral
analysis for [The Well](https://github.com/PolymathicAI/the_well) MHD datasets
in the context of the [Hopfion Ring Lightning Hypothesis](../../README.md).

## Quick Start

```bash
# Install dependencies
pip install the_well numpy scipy scikit-image matplotlib h5py

# Run tests
PYTHONPATH=src python -m pytest tests/ -v

# Run helicity scan on MHD_64 (streaming from HuggingFace)
python scripts/run_helicity_scan.py --dataset MHD_64 --split train --max-trajectories 10
```

## Modules

| Module | Description |
|--------|-------------|
| `helicity.py` | Vector potential A, helicity density h = A . B, global H_m, Hopf charge Q_H |
| `topology.py` | Structure detection, ring/blob/tube classification, cross-timestep tracking |
| `spectral.py` | Helical decomposition E+(k)/E-(k), helicity spectrum, inverse cascade detection |
| `energy_budget.py` | E_magnetic, E_kinetic decomposition, Alfven/sonic Mach numbers |

## Datasets Used

- **MHD_64**: 100 trajectories of 64^3 isothermal MHD turbulence (~71.6 GB)
- **MHD_256**: 100 trajectories of 256^3 MHD turbulence (~4.58 TB)

## Hypothesis Connection

This work addresses **Problem 9** (Numerical Simulation) of the Hopfion hypothesis
by providing the first ML-driven topological analysis of MHD turbulence data.
See [CONTRIBUTION-01-MHD-en.md](../../plan/CONTRIBUTION-01-MHD-en.md) for the full plan.

## License

BSD-3-Clause (same as The Well)
