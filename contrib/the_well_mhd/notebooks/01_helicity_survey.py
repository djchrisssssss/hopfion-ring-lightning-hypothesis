"""
# 01 — Magnetic Helicity Survey of The Well MHD Datasets

Computes H_m and Q_H across all MHD_64 trajectories to build
the first systematic topological census of MHD turbulence data.

Run as notebook: `jupytext --to notebook 01_helicity_survey.py`
"""
# %% Imports
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path("../src")))

from hopfion_well.helicity import (
    compute_magnetic_helicity,
    extract_b_field_from_well,
    generate_hopf_ranada_field,
    verify_divergence_free,
)
from hopfion_well.topology import detect_helicity_structures

# %% Configuration
DATASET = "MHD_64"
BASE_PATH = "hf://datasets/polymathic-ai/"
SPLIT = "train"
MAX_TRAJECTORIES = 10  # Set to None for full scan

# %% Validate with synthetic Hopf-Ranada field first
print("=== Validating with synthetic Hopf-Ranada field ===")
N = 64
B_synth = generate_hopf_ranada_field(N, L=2 * np.pi, a=1.0)
result_synth = compute_magnetic_helicity(B_synth, dx=2 * np.pi / N)
div_err = verify_divergence_free(B_synth, dx=2 * np.pi / N)

print(f"Synthetic Hopf-Ranada field (N={N}):")
print(f"  H_m = {result_synth.global_helicity:.6e}")
print(f"  Q_H = {result_synth.hopf_charge:.6f}")
print(f"  div(B) error = {div_err:.2e}")
print(f"  h_rms = {np.sqrt(np.mean(result_synth.helicity_density**2)):.6e}")

structures = detect_helicity_structures(result_synth.helicity_density, dx=2 * np.pi / N)
print(f"  Detected structures: {len(structures)}")
for s in structures[:5]:
    print(f"    Q_local={s.local_hopf_charge:.4f}, vol={s.volume:.0f}, morph={s.morphology}")

# %% Load The Well MHD dataset
print(f"\n=== Loading {DATASET}/{SPLIT} ===")
from the_well.data import WellDataset

dataset = WellDataset(
    well_base_path=BASE_PATH,
    well_dataset_name=DATASET,
    well_split_name=SPLIT,
    n_steps_input=1,
    n_steps_output=0,
)
n_traj = len(dataset)
if MAX_TRAJECTORIES:
    n_traj = min(n_traj, MAX_TRAJECTORIES)
print(f"Dataset size: {len(dataset)} trajectories, processing {n_traj}")

# %% Run helicity survey
H_m_values = []
Q_H_values = []
div_errors = []
n_structures_list = []

for i in range(n_traj):
    sample = dataset[i]
    B = extract_b_field_from_well(sample)
    result = compute_magnetic_helicity(B)
    div_err = verify_divergence_free(B)
    structs = detect_helicity_structures(result.helicity_density)

    H_m_values.append(result.global_helicity)
    Q_H_values.append(result.hopf_charge)
    div_errors.append(div_err)
    n_structures_list.append(len(structs))

    print(f"  [{i+1}/{n_traj}] H_m={result.global_helicity:.4e}, "
          f"Q_H={result.hopf_charge:.4f}, structs={len(structs)}")

H_m_values = np.array(H_m_values)
Q_H_values = np.array(Q_H_values)

# %% Plot results
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].hist(H_m_values, bins=20, edgecolor="black", alpha=0.7)
axes[0, 0].set_xlabel("Magnetic Helicity H_m")
axes[0, 0].set_ylabel("Count")
axes[0, 0].set_title("H_m Distribution")
axes[0, 0].axvline(0, color="red", linestyle="--", alpha=0.5)

axes[0, 1].hist(Q_H_values, bins=20, edgecolor="black", alpha=0.7, color="orange")
axes[0, 1].set_xlabel("Hopf Charge Q_H")
axes[0, 1].set_ylabel("Count")
axes[0, 1].set_title("Q_H Distribution")

axes[1, 0].bar(range(n_traj), n_structures_list, alpha=0.7, color="green")
axes[1, 0].set_xlabel("Trajectory Index")
axes[1, 0].set_ylabel("Number of Structures")
axes[1, 0].set_title("Topological Structures per Trajectory")

axes[1, 1].scatter(np.abs(Q_H_values), n_structures_list, alpha=0.7)
axes[1, 1].set_xlabel("|Q_H|")
axes[1, 1].set_ylabel("Number of Structures")
axes[1, 1].set_title("|Q_H| vs Structure Count")

plt.tight_layout()
plt.savefig("../results/figures/helicity_survey.png", dpi=150, bbox_inches="tight")
plt.show()

# %% Summary
print("\n=== Summary ===")
print(f"Trajectories processed: {n_traj}")
print(f"H_m: mean={np.mean(H_m_values):.4e}, std={np.std(H_m_values):.4e}")
print(f"Q_H: mean={np.mean(Q_H_values):.4f}, std={np.std(Q_H_values):.4f}")
print(f"|Q_H| max: {np.max(np.abs(Q_H_values)):.4f}")
print(f"Structures per trajectory: mean={np.mean(n_structures_list):.1f}, "
      f"max={np.max(n_structures_list)}")
