# Contribution Plan 01 — Hopfion Topology Detection via The Well MHD Datasets

**Version**: v1.0
**Date**: 2026-04-05
**Author**: Claude Opus 4.6 (Anthropic) via Claude Code
**Upstream**: [PolymathicAI/the_well](https://github.com/PolymathicAI/the_well)
**Hypothesis**: Hopfion (Ring) Lightning Hypothesis v0.7

---

## 1. Executive Summary

This plan uses The Well's MHD_64 and MHD_256 datasets — isothermal compressible MHD turbulence simulations — to:

1. **Train ML surrogate models** for MHD field evolution
2. **Compute magnetic helicity** (H_m) and topological invariants across all trajectories
3. **Search for emergent Hopfion-like structures** (Q_H != 0 stable regions)
4. **Validate the lifetime–topology relationship** central to the Hopfion Ring Lightning hypothesis
5. **Contribute findings back** to both the_well (new topological metrics) and the hypothesis (numerical evidence)

This directly addresses **Problem 9 (Numerical Simulation)** and provides data-driven constraints for **Problem 1 (Resistive Decay Timescale)** in the existing research plan.

---

## 2. Dataset Specifications

### 2.1 MHD_64

| Property | Value |
|----------|-------|
| **Fields** | density (scalar), velocity (3-vector), magnetic_field (3-vector) |
| **Resolution** | 64 x 64 x 64 |
| **Trajectories** | 100 (10 ICs x 10 parameter sets) |
| **Timesteps** | 100 per trajectory (dt = 0.01) |
| **Sonic Mach** | Ms in {0.5, 0.7, 1.5, 2.0, 7.0} |
| **Alfvenic Mach** | Ma in {0.7, 2.0} |
| **Boundary** | Periodic (all axes) |
| **Size** | ~71.6 GB |

### 2.2 MHD_256

| Property | Value |
|----------|-------|
| **Fields** | density (scalar), velocity (3-vector), magnetic_field (3-vector) |
| **Resolution** | 256 x 256 x 256 (downsampled to 64^3 available) |
| **Trajectories** | 100 (10 ICs x 10 parameter sets) |
| **Timesteps** | 100 per trajectory (dt = 0.01) |
| **Parameters** | Same Ms, Ma grid as MHD_64 |
| **Boundary** | Periodic (all axes) |
| **Size** | ~4.58 TB |

### 2.3 Why These Datasets

The MHD datasets contain exactly the fields needed for Hopfion analysis:

- **B** (magnetic field) — required for helicity integral H_m = integral(A . B) d^3r
- **v** (velocity) — required for MHD induction equation and cross-helicity
- **rho** (density) — required for compressible MHD energy budget
- **Periodic boundaries** — helicity is gauge-invariant under periodic BC (critical for correct H_m computation)
- **Multi-Mach parameter scan** — enables systematic study of topological structure dependence on Ms and Ma

---

## 3. Technical Architecture

### 3.1 Repository Structure

```
hopfion-ring-lightning-hypothesis/
  contrib/
    the_well_mhd/
      README.md
      pyproject.toml
      src/
        hopfion_well/
          __init__.py
          helicity.py          # Magnetic helicity computation (H_m, Q_H)
          topology.py           # Hopf charge detection & classification
          spectral.py           # Spectral analysis of B-field topology
          energy_budget.py      # E_magnetic, E_kinetic decomposition
      configs/
        mhd64_fno.yaml         # Hydra config for FNO on MHD_64
        helicity_scan.yaml     # Parameter scan config
      notebooks/
        01_helicity_survey.py   # Jupytext notebook
      scripts/
        download_data.sh
        run_helicity_scan.py
      tests/
        test_helicity.py
        test_topology.py
        test_spectral.py
        test_energy_budget.py
```

### 3.2 Dependencies

```toml
[project]
name = "hopfion-well"
requires-python = ">=3.10"
dependencies = [
    "the_well",
    "the_well[benchmark]",
    "torch>=2.1",
    "numpy>=1.20",
    "h5py>=3.9",
    "scipy",
    "matplotlib",
    "plotly",
    "pyvista",           # 3D field line visualization
    "scikit-image",      # Topological feature detection
]
```

---

## 4. Implementation Stages

### Stage 1: Data Ingestion & Helicity Computation

**Goal**: Compute magnetic helicity H_m and Hopf charge Q_H for all 200 trajectories (MHD_64 + MHD_256) across all timesteps.

**Method**:

1. **Load data via WellDataset**:
```python
from the_well.data import WellDataset

ds = WellDataset(
    well_base_path="hf://datasets/polymathic-ai/",
    well_dataset_name="MHD_64",
    well_split_name="train",
    n_steps_input=1,
    n_steps_output=1,
)
```

2. **Compute vector potential A from B** (periodic BC):
   - Use spectral method: B_hat = FFT(B), then A_hat = i*k x B_hat / |k|^2 (Coulomb gauge)
   - Periodic boundaries ensure gauge invariance of H_m

3. **Compute magnetic helicity density**: h(x) = A(x) . B(x)

4. **Integrate for global helicity**: H_m = integral h(x) d^3x

5. **Normalize for Hopf charge**: Q_H = H_m / (4*pi)^2

6. **Compute per-timestep** for all 100 trajectories in each dataset

**Deliverable**: HDF5 file with H_m(t), Q_H(t) for every trajectory, indexed by (Ms, Ma, IC).

**Success Criteria**:
- H_m computation validated against known analytic cases (uniform helical field)
- Conservation check: dH_m/dt should be bounded by resistive dissipation rate
- Statistical summary: distribution of H_m across parameter space

---

### Stage 2: Topological Structure Detection

**Goal**: Identify localized regions with non-trivial Hopf topology in the MHD simulation data.

**Method**:

1. **Helicity density field**: h(x) = A(x) . B(x) — already computed in Stage 1

2. **Identify coherent helicity structures**:
   - Threshold: |h(x)| > mu + 3*sigma (where mu, sigma from spatial average)
   - Connected-component labeling (scikit-image)
   - Track components across timesteps (particle tracking algorithm)

3. **For each detected structure, compute**:
   - Volume V, centroid position, peak |h|
   - Local Hopf charge: Q_local = integral_V h(x) d^3x / (4*pi)^2
   - Aspect ratio (distinguish ring/tube vs. blob)
   - Lifetime: number of consecutive timesteps where structure persists

4. **Ring-vs-blob classification** (eigenvalues sorted ascending: λ₁ ≤ λ₂ ≤ λ₃):
   - Compute eigenvalues of inertia tensor for each structure
   - Tube topology: lambda_1 << lambda_2 ~ lambda_3 (prolate — one small, two large)
   - Ring topology: lambda_1 ~ lambda_2 << lambda_3 (oblate — two small, one large)
   - Blob topology: lambda_1 ~ lambda_2 ~ lambda_3 (spherical)

5. **Correlation analysis**:
   - Lifetime vs. |Q_local| — the hypothesis predicts longer lifetime for higher topological charge
   - Lifetime vs. (Ms, Ma) — what turbulence regime favors topological stability?
   - Structure type vs. (Ms, Ma) — when do rings emerge?

**Deliverable**: Catalog of detected topological structures with properties, correlation plots.

**Success Criteria**:
- At least some structures with |Q_local| > 0.5 detected
- Statistically significant positive correlation between |Q_local| and lifetime
- Ring-like structures identified (if any) — these would be direct Hopfion candidates

---

### Stage 3: ML Surrogate Model Training

**Goal**: Train neural operator models to predict MHD evolution, then use them for fast topology parameter sweeps.

**Method**:

1. **Use The Well's benchmark framework** with Hydra configs:

```bash
cd the_well/benchmark
python train.py experiment=fno data=MHD_64 server=local
```

2. **Train 3 architectures** (leveraging existing benchmark infrastructure):

| Model | Why | Expected Strength |
|-------|-----|-------------------|
| **FNO** | Native spectral representation matches periodic MHD | Best for global topology (spectral structure) |
| **UNetConvNext** | Strong local feature extraction | Best for localized helicity structures |
| **TFNO** | Efficient at 256^3 via Tucker factorization | Only viable option for full MHD_256 resolution |

3. **Custom training targets**: In addition to standard field prediction, add:
   - **Helicity density prediction**: h(x, t+dt) from fields at t
   - **Helicity conservation loss**: |H_m(predicted) - H_m(true)| as auxiliary loss term

4. **Evaluation with The Well's metrics** plus custom topological metrics:
   - Standard: VRMSE, spectral MSE
   - New: **Helicity conservation error** = |H_m_pred - H_m_true| / |H_m_true|
   - New: **Topological structure F1** = overlap of detected structures between pred and true

**Deliverable**: Trained models on HuggingFace, training curves, metric comparison table.

**Success Criteria**:
- VRMSE competitive with The Well's existing benchmarks (FNO baseline for MHD_64)
- Helicity conservation error < 10% over 10-step rollout
- Topological structure F1 > 0.7 for structures lasting > 5 timesteps

---

### Stage 4: Topology-Lifetime Validation

**Goal**: Use trained surrogate models for long-horizon rollouts to study topological decay dynamics.

**Method**:

1. **Initialize with synthetic Hopfion fields**:
   - Construct analytic Hopf-Ranada field: B = (1/(1+r^2)^3) * Hopf_map(x)
   - Scale to match MHD dataset parameter ranges (Ms, Ma)
   - Embed in periodic box with matching grid resolution

2. **Autoregressive rollout** using trained surrogate:
   - Step the synthetic Hopfion field forward using the ML model
   - Track H_m(t), Q_H(t), and structure properties over extended time
   - Compare decay rate with: tau_eta = L^2 / eta (standard resistive prediction)

3. **Parameter sweep** (enabled by fast ML inference):
   - Vary initial Q_H: {0.5, 1.0, 2.0, 5.0, 10.0}
   - Vary (Ms, Ma) across all 10 parameter combinations
   - Vary initial structure size: {8, 16, 32} grid cells

4. **Key measurements**:
   - **Helicity half-life** tau_H: time for |H_m| to decay to 50%
   - **Topology preservation time** tau_T: time until Q_H crosses integer boundary
   - **Energy decay rate**: dE/dt decomposed into magnetic, kinetic, thermal channels
   - **Relationship**: tau_H vs tau_E — the hypothesis predicts tau_H >> tau_E (helicity outlives energy)

5. **Direct test of Problem 1**: Compare measured tau_H from ML rollout with:
   - Classical prediction: tau_eta ~ L^2 / eta
   - Hypothesis prediction: tau_H ~ (alpha * L)^2 / eta >> tau_eta

**Deliverable**: Decay curves, parameter sweep results, validation/falsification of the lifetime prediction.

**Success Criteria**:
- Clear measurement of helicity decay rate across parameter space
- Identification of (Ms, Ma) regimes where topological structures are most stable
- Quantitative constraint on effective magnetic diffusivity eta_eff
- If tau_H >> tau_eta observed: **strong support** for the hypothesis
- If tau_H ~ tau_eta: identifies which additional physics (two-zone model, etc.) is needed

---

### Stage 5: Spectral Topology Analysis

**Goal**: Characterize the frequency-domain signature of Hopfion-like structures using The Well's spectral metrics.

**Method**:

1. **Power spectrum of helicity density**: P_h(k) = |FFT(h(x))|^2
   - Hopfion structures have characteristic spectral peak at k ~ 2*pi/L_structure
   - Compare P_h(k) between high-Q_H and low-Q_H trajectories

2. **Cross-helicity spectrum**: H_c(k) = Re(v_hat . B_hat*)
   - Measures alignment between velocity and magnetic field at each scale
   - Hopfion structures should show strong alignment at the structure scale

3. **Magnetic energy spectrum decomposition**:
   - E_B(k) = 0.5 * |B_hat(k)|^2 (code units, mu_0 = 1)
   - Separate into: **helical part** (linked to H_m) and **non-helical part**
   - Method: E_B(k) = E_B^+(k) + E_B^-(k) using helical decomposition (Moffatt 1978)
   - Realizability condition: |H_m(k)| <= 2*k*E_B(k) — saturated when field is maximally helical

4. **Use The Well's `binned_spectral_mse`** to evaluate how well surrogate models preserve spectral topology:
   - Compute per-wavenumber error for both E_B(k) and H_m(k)
   - Identify if errors are concentrated at the topology-carrying scales

5. **Time-frequency analysis**:
   - Track P_h(k, t) evolution — does helicity migrate to larger scales (inverse cascade)?
   - This is the spectral signature of topological protection

**Deliverable**: Spectral analysis notebook, helical decomposition results, cascade direction identification.

**Success Criteria**:
- Clear spectral signature differentiating high-Q_H vs low-Q_H states
- Evidence of inverse helicity cascade (energy at topology scale grows or is maintained)
- Surrogate model preserves spectral topology to within 15% per-bin error

---

## 5. Contributions to Upstream Repositories

### 5.1 To PolymathicAI/the_well

| Contribution | Type | Description |
|-------------|------|-------------|
| **Topological metrics module** | New feature | `the_well/benchmark/metrics/topological.py` — magnetic helicity, Hopf charge, cross-helicity metrics |
| **Helical spectral decomposition** | Enhancement | Extend `binned_spectral_mse` with helical mode separation for vector field datasets |
| **MHD-specific augmentations** | Enhancement | Add magnetic-field-aware augmentations that preserve div(B) = 0 |
| **Benchmark results** | Documentation | Add helicity-aware model comparison to MHD benchmark tables |

### 5.2 To Hopfion Ring Lightning Hypothesis

| Contribution | Addresses | Description |
|-------------|-----------|-------------|
| **Helicity survey results** | Problem 9 | First systematic topological census of MHD turbulence data |
| **Lifetime-topology correlation** | Problem 1 | Data-driven constraint on tau_H vs tau_eta |
| **Energy decomposition** | Problem 2 | E_magnetic vs E_kinetic vs E_thermal partitioning from simulations |
| **Spectral signatures** | Ch. 10 (Predictions) | New falsifiable prediction: spectral fingerprint of Hopfion state |

---

## 6. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| No Hopfion-like structures found in MHD data | High | This is still a valid result — constrains parameter space. Also try synthetic initialization (Stage 4) |
| MHD_256 too large to process locally | Medium | Start with MHD_64; use HuggingFace streaming; downsample 256^3 to 128^3 |
| Surrogate model doesn't preserve topology | Medium | Add helicity conservation loss; use FNO (spectral methods naturally preserve global structure) |
| Gauge ambiguity in A computation | Low | Periodic BC + Coulomb gauge eliminates ambiguity. Validate with analytic test cases |
| ML rollout diverges before topology decays | Medium | Use DeltaWellDataset for stability; limit rollout to 50 steps; use teacher forcing at 10% |

---

## 7. Execution Timeline

| Stage | Description | Depends On | Estimated Compute |
|-------|-------------|------------|-------------------|
| **1** | Helicity computation (all trajectories) | Data download | ~4 hours (MHD_64), ~48 hours (MHD_256) |
| **2** | Topological structure detection | Stage 1 | ~2 hours post-Stage 1 |
| **3** | Surrogate model training | Data download | ~12 hours GPU (MHD_64), ~72 hours GPU (MHD_256) |
| **4** | Topology-lifetime validation | Stages 2 + 3 | ~8 hours GPU (parameter sweep) |
| **5** | Spectral topology analysis | Stage 1 | ~4 hours post-Stage 1 |

Stages 1+5 and Stage 3 can run in parallel.

---

## 8. Success Metrics Summary

| Metric | Target | Impact on Hypothesis |
|--------|--------|---------------------|
| Hopfion-like structures detected | >= 1 per 10 trajectories | Validates topological stability in MHD turbulence |
| Lifetime-Q_H correlation | Pearson r > 0.5, p < 0.01 | Supports topological protection mechanism |
| tau_H / tau_eta ratio | > 10 (for high Q_H structures) | Directly addresses Problem 1 |
| E_thermal / E_total fraction | Measured | Resolves Problem 2 (container vs reservoir question) |
| Inverse helicity cascade observed | Yes/No | Validates Taylor relaxation pathway |
| Spectral Hopfion signature | Identifiable peak in P_h(k) | New falsifiable prediction for Ch. 10 |

---

*This contribution plan bridges the Hopfion Ring Lightning Hypothesis with PolymathicAI's The Well MHD datasets to provide the first ML-driven topological analysis of MHD turbulence in the context of ball lightning physics.*
