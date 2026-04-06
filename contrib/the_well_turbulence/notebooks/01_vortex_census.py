"""
# 01 — Vortex Census of The Well Turbulence Datasets

Detects coherent vortex structures in turbulent_radiative_layer_2D
and analyzes their lifetime dependence on cooling time t_cool.

Run as notebook: `jupytext --to notebook 01_vortex_census.py`
"""
# %% Imports
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path("../src")))

from hopfion_turb.vortex_detection import compute_vortex_census
from hopfion_turb.structure_tracking import (
    track_vortices,
    compute_survival_function,
    compute_lifetime_statistics,
)
from hopfion_turb.cooling_analysis import (
    find_critical_cooling_time,
    map_to_atmospheric_conditions,
)

# %% Configuration
DATASET = "turbulent_radiative_layer_2D"
BASE_PATH = "hf://datasets/polymathic-ai/"
SPLIT = "train"
MAX_TRAJECTORIES = 10  # Set to None for full scan

T_COOL_VALUES = np.array([0.03, 0.06, 0.1, 0.18, 0.32, 0.56, 1.00, 1.78, 3.16])

# %% Validate with synthetic vortex ring
print("=== Validating vortex detection on synthetic Lamb-Oseen vortex ===")
N = 64
x = np.linspace(-5, 5, N, endpoint=False)
X, Y = np.meshgrid(x, x, indexing="ij")
r = np.sqrt(X**2 + Y**2)

# Lamb-Oseen vortex
Gamma = 10.0
r_c = 1.0
v_theta = Gamma / (2 * np.pi * np.maximum(r, 0.01)) * (1 - np.exp(-r**2 / r_c**2))
v = np.stack([
    -v_theta * Y / np.maximum(r, 0.01),
    v_theta * X / np.maximum(r, 0.01),
])

cores, fields = compute_vortex_census(v, dx=10.0/N, periodic=False, sigma_threshold=1.5)
print(f"Synthetic Lamb-Oseen vortex (N={N}):")
print(f"  Q field shape: {fields.Q_criterion.shape}")
print(f"  Detected cores: {len(cores)}")
for c in cores[:3]:
    print(f"    peak_Q={c.peak_Q:.4f}, vol={c.volume}, centroid={c.centroid}")

# %% Load The Well turbulence dataset
print(f"\n=== Loading {DATASET}/{SPLIT} ===")
from the_well.data import WellDataset
import torch

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

# %% Run vortex census
all_cores = []
all_mean_Q = []
all_mean_enstrophy = []

for i in range(n_traj):
    sample = dataset[i]

    # Extract velocity
    fields_dict = sample.get("input_fields", sample)
    if isinstance(fields_dict, dict):
        v_data = None
        for key in ["velocity", "Velocity"]:
            if key in fields_dict:
                v_data = fields_dict[key]
                break
        if v_data is None:
            print(f"  [{i+1}] Skipping - no velocity field. Keys: {list(fields_dict.keys())}")
            continue
    else:
        v_data = fields_dict

    if isinstance(v_data, torch.Tensor):
        v_data = v_data.numpy()

    # Squeeze extra dims
    while v_data.ndim > 3:
        v_data = v_data[0]

    # Channels-last to channels-first
    if v_data.shape[-1] in (2, 3):
        v_data = np.moveaxis(v_data, -1, 0)

    v_data = v_data.astype(np.float64)

    cores, vf = compute_vortex_census(v_data, sigma_threshold=2.0)
    all_cores.append(cores)
    all_mean_Q.append(np.mean(vf.Q_criterion))
    all_mean_enstrophy.append(np.mean(vf.enstrophy))

    print(f"  [{i+1}/{n_traj}] cores={len(cores)}, <Q>={np.mean(vf.Q_criterion):.4e}")

# %% Plot results
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

n_cores_list = [len(c) for c in all_cores]
axes[0].bar(range(len(n_cores_list)), n_cores_list, alpha=0.7)
axes[0].set_xlabel("Trajectory Index")
axes[0].set_ylabel("Number of Vortex Cores")
axes[0].set_title("Vortex Cores per Trajectory")

axes[1].plot(all_mean_Q, "o-", alpha=0.7)
axes[1].set_xlabel("Trajectory Index")
axes[1].set_ylabel("Mean Q-criterion")
axes[1].set_title("Mean Q per Trajectory")

axes[2].plot(all_mean_enstrophy, "s-", alpha=0.7, color="red")
axes[2].set_xlabel("Trajectory Index")
axes[2].set_ylabel("Mean Enstrophy")
axes[2].set_title("Mean Enstrophy per Trajectory")

plt.tight_layout()
plt.savefig("../results/figures/vortex_census.png", dpi=150, bbox_inches="tight")
plt.show()

# %% Summary
print("\n=== Summary ===")
print(f"Trajectories processed: {len(all_cores)}")
print(f"Total vortex cores: {sum(n_cores_list)}")
print(f"Cores per trajectory: mean={np.mean(n_cores_list):.1f}, max={max(n_cores_list) if n_cores_list else 0}")
print(f"Mean Q: {np.mean(all_mean_Q):.4e}")
print(f"Mean enstrophy: {np.mean(all_mean_enstrophy):.4e}")
