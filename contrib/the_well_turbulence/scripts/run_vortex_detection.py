#!/usr/bin/env python3
"""Run vortex detection and tracking across The Well turbulence datasets.

Usage:
    python run_vortex_detection.py --dataset turbulent_radiative_layer_2D --split train
    python run_vortex_detection.py --dataset turbulence_gravity_cooling --split train --max-trajectories 100
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

import h5py
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vortex census on The Well turbulence data")
    parser.add_argument(
        "--dataset", default="turbulent_radiative_layer_2D",
        choices=["turbulence_gravity_cooling", "turbulent_radiative_layer_2D", "turbulent_radiative_layer_3D"],
    )
    parser.add_argument("--split", default="train")
    parser.add_argument("--base-path", default=None)
    parser.add_argument("--output-dir", default="results/")
    parser.add_argument("--max-trajectories", type=int, default=None)
    parser.add_argument("--sigma-threshold", type=float, default=2.0)
    return parser.parse_args()


def extract_velocity(sample: dict) -> np.ndarray:
    """Extract velocity field from WellDataset sample as (ndim, N1, N2, ...)."""
    import torch

    if "input_fields" in sample:
        fields = sample["input_fields"]
        if isinstance(fields, dict):
            for key in ["velocity", "Velocity"]:
                if key in fields:
                    data = fields[key]
                    break
            else:
                raise KeyError(f"No velocity field found in {list(fields.keys())}")
        else:
            data = fields
    else:
        data = sample.get("velocity", sample)

    if isinstance(data, torch.Tensor):
        data = data.numpy()

    # Remove batch/time dims
    # Determine target ndim from trailing channel dimension
    # 2D velocity: (Nx, Ny, 2) → ndim 3; 3D velocity: (Nx, Ny, Nz, 3) → ndim 4
    if data.shape[-1] in (2, 3):
        target_ndim = data.shape[-1] + 1
    else:
        target_ndim = 4  # assume 3D channels-first
    while data.ndim > target_ndim:
        data = data[0]

    # Channels-last to channels-first
    if data.ndim >= 2 and data.shape[-1] in (2, 3) and data.shape[-1] < data.shape[0]:
        data = np.moveaxis(data, -1, 0)

    return data.astype(np.float64)


def extract_density(sample: dict) -> np.ndarray:
    """Extract density field from WellDataset sample."""
    import torch

    if "input_fields" in sample:
        fields = sample["input_fields"]
        if isinstance(fields, dict):
            for key in ["density", "Density"]:
                if key in fields:
                    data = fields[key]
                    break
            else:
                raise KeyError(f"No density field found in {list(fields.keys())}")
        else:
            data = fields
    else:
        data = sample.get("density", sample)

    if isinstance(data, torch.Tensor):
        data = data.numpy()

    # Remove batch/time/channel dims
    while data.ndim > 3:
        if data.shape[-1] == 1:
            data = data[..., 0]
        else:
            data = data[0]

    return data.astype(np.float64)


def main():
    args = parse_args()

    from the_well.data import WellDataset

    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from hopfion_turb.vortex_detection import compute_vortex_census
    from hopfion_turb.structure_tracking import (
        track_vortices,
        compute_survival_function,
        compute_lifetime_statistics,
    )

    base_path = args.base_path or "hf://datasets/polymathic-ai/"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    is_3d = "3D" in args.dataset or "gravity" in args.dataset
    periodic = "gravity" in args.dataset  # TGC is fully periodic

    logger.info(f"Loading {args.dataset}/{args.split}")

    dataset = WellDataset(
        well_base_path=base_path,
        well_dataset_name=args.dataset,
        well_split_name=args.split,
        n_steps_input=1,
        n_steps_output=0,
    )

    n_traj = len(dataset)
    if args.max_trajectories:
        n_traj = min(n_traj, args.max_trajectories)

    logger.info(f"Processing {n_traj} trajectories")

    output_h5 = output_dir / f"vortex_{args.dataset}_{args.split}.h5"
    all_stats = []

    with h5py.File(output_h5, "w") as f:
        f.attrs["dataset"] = args.dataset
        f.attrs["split"] = args.split

        for traj_idx in range(n_traj):
            t_start = time.time()

            try:
                sample = dataset[traj_idx]
                v = extract_velocity(sample)

                cores, fields = compute_vortex_census(
                    v, dx=1.0, periodic=periodic,
                    sigma_threshold=args.sigma_threshold,
                )

                grp = f.create_group(f"trajectory_{traj_idx:04d}")
                grp.attrs["n_vortices"] = len(cores)
                grp.attrs["mean_Q"] = float(np.mean(fields.Q_criterion))
                grp.attrs["mean_enstrophy"] = float(np.mean(fields.enstrophy))
                grp.attrs["strain_rate"] = fields.strain_rate
                grp.attrs["rotation_rate"] = fields.rotation_rate

                if cores:
                    grp.attrs["max_Q"] = cores[0].peak_Q
                    grp.attrs["max_circulation"] = max(c.circulation for c in cores)

                    for i, c in enumerate(cores[:20]):
                        c_grp = grp.create_group(f"core_{i:03d}")
                        c_grp.attrs["volume"] = c.volume
                        c_grp.attrs["peak_Q"] = c.peak_Q
                        c_grp.attrs["circulation"] = c.circulation
                        c_grp.attrs["centroid"] = c.centroid

                elapsed = time.time() - t_start
                logger.info(
                    f"[{traj_idx+1}/{n_traj}] "
                    f"vortices={len(cores)}, "
                    f"<Q>={np.mean(fields.Q_criterion):.4e}, "
                    f"time={elapsed:.1f}s"
                )

                all_stats.append({
                    "traj_idx": traj_idx,
                    "n_vortices": len(cores),
                    "mean_Q": float(np.mean(fields.Q_criterion)),
                })

            except Exception as e:
                logger.error(f"[{traj_idx+1}/{n_traj}] Error: {e}")
                continue

    # Save summary
    summary = {
        "dataset": args.dataset,
        "split": args.split,
        "n_trajectories": n_traj,
        "n_processed": len(all_stats),
        "total_vortices": sum(s["n_vortices"] for s in all_stats),
        "mean_vortices_per_traj": np.mean([s["n_vortices"] for s in all_stats]) if all_stats else 0,
    }

    summary_path = output_dir / f"summary_{args.dataset}_{args.split}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Results saved to {output_h5}")
    logger.info(f"Summary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()
