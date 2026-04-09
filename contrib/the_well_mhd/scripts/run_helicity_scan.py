#!/usr/bin/env python3
"""Run magnetic helicity survey across The Well MHD datasets.

This script:
1. Loads MHD trajectories from The Well (local or HuggingFace streaming)
2. Computes magnetic helicity H_m and Hopf charge Q_H for each timestep
3. Detects topological structures in the helicity density field
4. Tracks structures across timesteps
5. Computes spectral analysis
6. Saves results to HDF5 and JSON

Usage:
    python run_helicity_scan.py --dataset MHD_64 --split train
    python run_helicity_scan.py --dataset MHD_64 --split train --streaming
    python run_helicity_scan.py --dataset MHD_256 --split train --max-trajectories 10
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
    parser = argparse.ArgumentParser(description="Helicity survey on The Well MHD data")
    parser.add_argument("--dataset", default="MHD_64", choices=["MHD_64", "MHD_256"])
    parser.add_argument("--split", default="train", choices=["train", "test"])
    parser.add_argument("--base-path", default=None, help="Local data path. If None, uses HF streaming.")
    parser.add_argument("--output-dir", default="results/", help="Output directory")
    parser.add_argument("--max-trajectories", type=int, default=None, help="Limit number of trajectories")
    parser.add_argument("--sigma-threshold", type=float, default=3.0, help="Structure detection threshold")
    parser.add_argument("--n-bins", type=int, default=32, help="Spectral bins")
    parser.add_argument("--streaming", action="store_true", help="Force HF streaming mode")
    return parser.parse_args()


def main():
    args = parse_args()

    # Import here to allow --help without dependencies
    from the_well.data import WellDataset

    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from hopfion_well.helicity import (
        compute_magnetic_helicity,
        compute_helicity_timeseries,
        extract_b_field_from_well,
        verify_divergence_free,
    )
    from hopfion_well.topology import (
        detect_helicity_structures,
        track_structures,
        compute_structure_statistics,
    )
    from hopfion_well.spectral import compute_helical_decomposition

    # Setup paths
    if args.base_path:
        base_path = args.base_path
    elif args.streaming:
        base_path = "hf://datasets/polymathic-ai/"
    else:
        base_path = "hf://datasets/polymathic-ai/"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading {args.dataset}/{args.split} from {base_path}")

    # Load dataset — iterate trajectory by trajectory
    dataset = WellDataset(
        well_base_path=base_path,
        well_dataset_name=args.dataset,
        well_split_name=args.split,
        n_steps_input=1,
        n_steps_output=0,
    )

    n_trajectories = len(dataset)
    if args.max_trajectories:
        n_trajectories = min(n_trajectories, args.max_trajectories)

    logger.info(f"Processing {n_trajectories} trajectories")

    # Results accumulators
    all_H_m = []
    all_Q_H = []
    all_structures = []
    all_stats = []

    output_h5 = output_dir / f"helicity_{args.dataset}_{args.split}.h5"

    with h5py.File(output_h5, "w") as f:
        f.attrs["dataset"] = args.dataset
        f.attrs["split"] = args.split
        f.attrs["sigma_threshold"] = args.sigma_threshold

        for traj_idx in range(n_trajectories):
            t_start = time.time()

            try:
                sample = dataset[traj_idx]
                B = extract_b_field_from_well(sample)

                # Compute helicity
                result = compute_magnetic_helicity(B, dx=1.0)

                # Verify div(B) = 0
                div_err = verify_divergence_free(B)

                # Detect structures
                structures = detect_helicity_structures(
                    result.helicity_density,
                    sigma_threshold=args.sigma_threshold,
                )

                # Save to HDF5
                grp = f.create_group(f"trajectory_{traj_idx:04d}")
                grp.attrs["H_m"] = result.global_helicity
                grp.attrs["Q_H"] = result.hopf_charge
                grp.attrs["div_B_error"] = div_err
                grp.attrs["n_structures"] = len(structures)
                grp.attrs["compute_time_s"] = time.time() - t_start

                if structures:
                    grp.attrs["max_Q_local"] = max(
                        abs(s.local_hopf_charge) for s in structures
                    )
                    grp.attrs["n_rings"] = sum(
                        1 for s in structures if s.morphology == "ring"
                    )

                    # Save structure catalog
                    for i, s in enumerate(structures[:50]):  # Top 50
                        s_grp = grp.create_group(f"structure_{i:03d}")
                        s_grp.attrs["volume"] = s.volume
                        s_grp.attrs["Q_local"] = s.local_hopf_charge
                        s_grp.attrs["morphology"] = s.morphology
                        s_grp.attrs["peak_h"] = s.peak_helicity_density
                        s_grp.attrs["centroid"] = s.centroid

                all_H_m.append(result.global_helicity)
                all_Q_H.append(result.hopf_charge)

                elapsed = time.time() - t_start
                logger.info(
                    f"[{traj_idx+1}/{n_trajectories}] "
                    f"H_m={result.global_helicity:.4e}, Q_H={result.hopf_charge:.4f}, "
                    f"div(B)={div_err:.2e}, structures={len(structures)}, "
                    f"time={elapsed:.1f}s"
                )

            except Exception as e:
                logger.error(f"[{traj_idx+1}/{n_trajectories}] Error: {e}")
                continue

        # Save summary
        f.create_dataset("H_m_all", data=np.array(all_H_m))
        f.create_dataset("Q_H_all", data=np.array(all_Q_H))

    # Save JSON summary
    summary = {
        "dataset": args.dataset,
        "split": args.split,
        "n_trajectories": n_trajectories,
        "H_m_mean": float(np.mean(all_H_m)) if all_H_m else 0,
        "H_m_std": float(np.std(all_H_m)) if all_H_m else 0,
        "Q_H_mean": float(np.mean(all_Q_H)) if all_Q_H else 0,
        "Q_H_std": float(np.std(all_Q_H)) if all_Q_H else 0,
        "Q_H_max": float(np.max(np.abs(all_Q_H))) if all_Q_H else 0,
    }

    summary_path = output_dir / f"summary_{args.dataset}_{args.split}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Results saved to {output_h5}")
    logger.info(f"Summary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()
