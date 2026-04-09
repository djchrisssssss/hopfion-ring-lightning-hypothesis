# Contribution Plan 02 — Hopfion Stability in Turbulent Environments via The Well Turbulence Datasets

**Version**: v1.0
**Date**: 2026-04-05
**Author**: Claude Opus 4.6 (Anthropic) via Claude Code
**Upstream**: [PolymathicAI/the_well](https://github.com/PolymathicAI/the_well)
**Hypothesis**: Hopfion (Ring) Lightning Hypothesis v0.7

---

## 1. Executive Summary

Ball lightning forms in thunderstorm environments — inherently turbulent. This plan uses The Well's turbulence datasets to answer a critical question:

> **Under what turbulence conditions can topologically protected magnetic structures survive?**

The three datasets — `turbulence_gravity_cooling`, `turbulent_radiative_layer_2D`, and `turbulent_radiative_layer_3D` — model astrophysical turbulence with cooling, gravity, and radiative processes. While not atmospheric MHD per se, they capture the **essential physics of compressible turbulence with energy dissipation** that governs ball lightning environments.

This plan:
1. **Characterizes vortex stability** across turbulence regimes
2. **Maps the parameter space** of coherent structure survival
3. **Trains ML models** that predict structure lifetime from local flow conditions
4. **Derives turbulence constraints** for the Hopfion hypothesis formation mechanism

This directly addresses **Problem 1 (Resistive Decay — Approach C: Turbulent Suppression)** and strengthens **Chapter 7 (Environmental Conditions)** of the hypothesis.

---

## 2. Dataset Specifications

### 2.1 turbulence_gravity_cooling

| Property | Value |
|----------|-------|
| **Fields** | density (scalar), pressure (scalar), temperature (scalar), velocity (3-vector) |
| **Resolution** | 64 x 64 x 64 |
| **Trajectories** | 2,700 (27 parameter sets x 100 runs) |
| **Timesteps** | 50 per trajectory |
| **Temperature** | T_0 in {10 K, 100 K, 1000 K} |
| **Density** | rho_0 in {44.5, 4.45, 0.445} /cc |
| **Metallicity** | Z in {Z_0, 0.1*Z_0, 0} |
| **Boundary** | Periodic |
| **Size** | ~829.4 GB |

**Relevance**: Models compressible turbulence with radiative cooling — the closest analog to atmospheric turbulence with energy dissipation. The temperature range covers the partially-ionized regime relevant to ball lightning formation. The 27-parameter grid enables systematic study of how cooling strength affects structure lifetime.

### 2.2 turbulent_radiative_layer_2D

| Property | Value |
|----------|-------|
| **Fields** | density (scalar), pressure (scalar), velocity (2-vector) |
| **Resolution** | 384 x 128 |
| **Trajectories** | 90 (9 cooling times x 10 seeds) |
| **Timesteps** | 101 per trajectory |
| **Cooling times** | t_cool in {0.03, 0.06, 0.1, 0.18, 0.32, 0.56, 1.00, 1.78, 3.16} |
| **Boundary** | Periodic (x), zero-gradient (y) |
| **Size** | ~6.9 GB |

**Relevance**: Kelvin-Helmholtz instability-driven mixing layer — directly models the shear flow environment at the boundary of a hot plasma structure (the Hopfion) embedded in cooler ambient air. The cooling time parameter directly maps to the energy dissipation rate.

### 2.3 turbulent_radiative_layer_3D

| Property | Value |
|----------|-------|
| **Fields** | density (scalar), pressure (scalar), velocity (3-vector) |
| **Resolution** | 256 x 128 x 128 |
| **Trajectories** | 90 (9 cooling times x 10 seeds) |
| **Timesteps** | 101 per trajectory |
| **Cooling times** | Same 9 values as 2D |
| **Boundary** | Periodic (x,y), zero-gradient (z) |
| **Size** | ~744.6 GB |
| **Simulation code** | Athena++ |

**Relevance**: 3D extension captures volumetric mixing and fractal structure of turbulent interfaces. Essential for understanding how a 3D toroidal Hopfion structure would interact with a turbulent boundary layer.

---

## 3. Scientific Questions

This contribution addresses four specific questions, each linking a dataset to a hypothesis problem:

| Question | Dataset | Hypothesis Link |
|----------|---------|----------------|
| Q1: How long do coherent vortex structures survive in compressible turbulence? | turbulence_gravity_cooling | Problem 1 (Approach C: turbulent suppression) |
| Q2: Does radiative cooling stabilize or destabilize coherent structures? | turbulent_radiative_layer_2D/3D | Problem 1 (Approach D: two-zone model) |
| Q3: What is the critical cooling time below which structures are destroyed? | turbulent_radiative_layer_2D/3D | Chapter 7 (Environmental Conditions) |
| Q4: Can ML models predict structure lifetime from local flow properties? | All three datasets | Problem 9 (Numerical Simulation — fast surrogate) |

---

## 4. Technical Architecture

### 4.1 Repository Structure

```
hopfion-ring-lightning-hypothesis/
  contrib/
    the_well_turbulence/
      README.md
      pyproject.toml
      src/
        hopfion_turb/
          __init__.py
          vortex_detection.py    # Q-criterion, lambda2, enstrophy-based detection
          structure_tracking.py   # Lagrangian tracking of coherent structures
          cooling_analysis.py     # Cooling time vs structure lifetime mapping
          boundary_layer.py       # Shear layer analysis for Hopfion boundary model
      configs/
        vortex_scan.yaml         # Structure detection parameter scan
      notebooks/
        01_vortex_census.py      # Jupytext notebook
      scripts/
        run_vortex_detection.py
      tests/
        test_vortex_detection.py
        test_structure_tracking.py
        test_cooling_analysis.py
        test_boundary_layer.py
```

### 4.2 Dependencies

```toml
[project]
name = "hopfion-turb"
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
    "scikit-image",
    "trackpy",             # Particle/structure tracking
]
```

---

## 5. Implementation Stages

### Stage 1: Coherent Structure Census (turbulence_gravity_cooling)

**Goal**: Systematically detect and catalog all coherent vortex structures across 2,700 trajectories, measuring their lifetime as a function of (T_0, rho_0, Z).

**Method**:

1. **Vortex identification** using multiple criteria:

   a. **Q-criterion**: Q = 0.5 * (|Omega|^2 - |S|^2)
      - Omega = antisymmetric part of velocity gradient (rotation)
      - S = symmetric part of velocity gradient (strain)
      - Vortex core where Q > 0 (rotation dominates strain)

   b. **Enstrophy density**: xi = |omega|^2 = |curl(v)|^2
      - High enstrophy = strong rotation
      - Used as supplementary metric alongside Q-criterion

   c. **Pressure minima**: Vortex cores are local pressure minima
      - Cross-validate with Q-criterion for robust detection

   Detection threshold: Q > mu + sigma_threshold * sigma (default sigma_threshold = 2.0)

2. **Connected-component labeling** on thresholded Q > Q_threshold field

3. **Structure tracking** across timesteps:
   - Centroid distance-based tracking with volume similarity: structure at t+1 matches if centroid distance < max_distance AND volume ratio > 0.3
   - Assign unique ID to each tracked structure
   - Record: birth time, death time, lifetime, peak Q, volume, centroid trajectory

4. **Statistical analysis** across the 27-parameter grid:

   | Parameter | Expected Effect | Test |
   |-----------|----------------|------|
   | T_0 (temperature) | Higher T → more energetic turbulence → shorter structure lifetime? Or higher T → more ionization → better MHD? | Lifetime vs T_0 regression |
   | rho_0 (density) | Higher density → more inertia → longer structure persistence | Lifetime vs rho_0 regression |
   | Z (metallicity/cooling) | Stronger cooling → faster energy loss → shorter lifetime? Or cooling creates density contrast → stabilizes? | Lifetime vs Z regression |

5. **Key metric**: **Structure survival function** S(t) = P(lifetime > t) for each parameter combination

**Deliverable**: Comprehensive catalog of ~10,000+ detected structures, survival curves across parameter space.

**Success Criteria**:
- Structure detection validated on known vortex ring test case
- Statistically significant dependence of lifetime on at least one parameter
- Clear identification of parameter regime with longest-lived structures

---

### Stage 2: Cooling-Stability Relationship (turbulent_radiative_layer_2D/3D)

**Goal**: Determine how radiative cooling time affects coherent structure stability at mixing layer interfaces.

**Method**:

1. **Load 2D dataset first** (6.9 GB — fast iteration):

```python
from the_well.data import WellDataset

ds_2d = WellDataset(
    well_base_path="hf://datasets/polymathic-ai/",
    well_dataset_name="turbulent_radiative_layer_2D",
    well_split_name="train",
    n_steps_input=1,
    n_steps_output=1,
)
```

2. **Mixing layer width evolution**:
   - Define mixing layer as region where 0.2 < density_normalized < 0.8
   - Track mixing layer width h(t) for each cooling time t_cool
   - Faster cooling → sharper interface → potential stabilization mechanism

3. **Kelvin-Helmholtz vortex tracking**:
   - KH instability generates vortex rolls at the shear interface
   - These vortices are the closest fluid-dynamic analog to a Hopfion embedded in ambient air
   - Track individual KH vortices: lifetime, merger events, dissipation

4. **Critical cooling time** determination:
   - Plot: vortex_lifetime vs t_cool for the 9 cooling time values
   - Identify t_cool_critical: the transition between:
     - Rapid cooling (t_cool < t_critical): structures destroyed by cooling-driven contraction
     - Slow cooling (t_cool > t_critical): structures destroyed by turbulent mixing
   - The **optimal regime** for structure survival is near t_critical

5. **3D validation** using turbulent_radiative_layer_3D:
   - Repeat analysis on 3D data
   - Compare 2D vs 3D: does dimensionality change the stability boundary?
   - 3D enables measurement of fractal dimension of mixing interface

6. **Map to atmospheric conditions**:
   - Ball lightning forms at T ~ 4200 K surface, atmospheric pressure
   - Radiative cooling time for air at these conditions: t_cool ~ several seconds
   - Compare with dataset's t_cool range to determine where ball lightning sits

**Deliverable**: Cooling time vs stability phase diagram, critical t_cool identification, atmospheric mapping.

**Success Criteria**:
- Clear non-monotonic or threshold relationship between t_cool and structure lifetime
- t_cool_critical identified with uncertainty bounds
- Atmospheric ball lightning conditions placed on the phase diagram
- 2D/3D comparison shows consistent stability boundary

---

### Stage 3: Boundary Layer Model for Hopfion-Atmosphere Interface

**Goal**: Use radiative mixing layer data to model the boundary between a hot Hopfion core and cool ambient atmosphere.

**Method**:

This stage directly addresses the Hopfion hypothesis's **two-zone model** (Problem 1, Approach D):

```
[Cool ambient air, T ~ 300 K, weakly ionized]
   |
   | ← Mixing layer / boundary layer
   |
[Hot Hopfion core, T ~ 10^4-10^5 K, fully ionized]
   |
   | ← Mixing layer / boundary layer
   |
[Cool ambient air]
```

1. **Density contrast analysis**:
   - In turbulent_radiative_layer datasets, hot/cold phases have density ratio chi = rho_cold/rho_hot
   - Measure effective diffusion coefficient across the mixing layer as function of chi and t_cool
   - Map chi to the Hopfion context: air at 300 K vs plasma at 10^4 K → chi ~ 30

2. **Entrainment rate measurement**:
   - Rate at which cold gas is entrained into the hot phase (and vice versa)
   - This determines how fast the Hopfion loses energy to the environment
   - Entrainment velocity v_e = dh/dt where h is mixing layer width

3. **Effective insulation factor**:
   - Define: kappa_eff = (heat flux through mixing layer) / (heat flux without layer)
   - If the mixing layer acts as a thermal insulator (kappa_eff << 1), it supports the two-zone model
   - Cooling can enhance insulation by creating a sharp density discontinuity

4. **Pressure equilibrium check**:
   - Verify that hot interior and cool exterior can coexist in pressure equilibrium
   - P_hot = n_hot * k * T_hot = P_cold = n_cold * k * T_cold
   - This constrains: n_hot/n_cold = T_cold/T_hot ~ 1/30

**Deliverable**: Effective diffusion/insulation coefficients, entrainment rates, boundary layer model parameters.

**Success Criteria**:
- Measured kappa_eff < 0.3 for at least one cooling regime (significant insulation)
- Entrainment rate v_e < L_hopfion / tau_observed (boundary survives for observed lifetime)
- Self-consistent two-zone model parameters identified

---

### Stage 4: ML Surrogate for Structure Lifetime Prediction

**Goal**: Train ML models that predict coherent structure lifetime from initial local flow conditions.

**Method**:

1. **Training data construction** (from Stage 1 catalog):

   For each detected structure at birth time:
   - **Input features**: local velocity field, density, pressure, temperature, Q-criterion, enstrophy (spatial patch around structure centroid)
   - **Target**: structure lifetime (in timesteps)

2. **Two model approaches**:

   a. **Regression on The Well's benchmark models**:
      - Train FNO/UNet on turbulence_gravity_cooling using standard The Well pipeline
      - Use trained model for autoregressive rollout
      - Measure how long detected structures persist in ML-predicted evolution
      - Compare with ground truth lifetime

   b. **Direct lifetime predictor** (lightweight):
      - Input: 16^3 spatial patch of (rho, P, T, v) centered on structure
      - Output: predicted lifetime (scalar regression)
      - Architecture: 3D CNN → Global Average Pooling → MLP → lifetime
      - This enables instant lifetime estimation without rollout

3. **Feature importance analysis**:
   - SHAP values or gradient-based attribution on the direct predictor
   - Which local flow properties most determine structure survival?
   - **Expected findings**: structures near high-strain regions die faster; structures with strong rotation (high Q) survive longer; cooling rate is a key moderator

4. **Extrapolation to atmospheric Hopfion conditions**:
   - The direct predictor maps (local flow properties) → (lifetime)
   - Input estimated atmospheric conditions for ball lightning formation zone
   - Predict expected Hopfion lifetime under atmospheric turbulence
   - This gives a **data-driven lifetime estimate** independent of analytic calculation

**Deliverable**: Trained lifetime predictor, feature importance analysis, atmospheric lifetime prediction.

**Success Criteria**:
- Lifetime predictor R^2 > 0.6 on held-out test set
- Top-3 most important features physically interpretable
- Atmospheric extrapolation yields lifetime in range 0.1–100 s (covering observed 5–10 s)

---

### Stage 5: Synthesis — Turbulence Constraints for the Hypothesis

**Goal**: Compile all results into a coherent set of constraints and predictions for the Hopfion hypothesis.

**Method**:

1. **Updated Environmental Conditions table** (strengthening Ch. 7):

   | Factor | Importance (original) | Updated Importance | Evidence |
   |--------|----------------------|-------------------|----------|
   | Atmospheric electric field | 5 stars | 5 stars | Unchanged |
   | Thunderstorm activity | 4 stars | 5 stars | Turbulence regime determines structure lifetime |
   | Turbulence intensity | Not listed | 4 stars | **NEW**: Strong turbulence destroys structures (Stage 1 data) |
   | Cooling rate | Not listed | 4 stars | **NEW**: Optimal t_cool window identified (Stage 2 data) |
   | Density contrast | Not listed | 3 stars | **NEW**: Boundary insulation depends on hot/cold ratio (Stage 3 data) |
   | Humidity | 2 stars | 2 stars | Unchanged |

2. **New falsifiable predictions** for Ch. 10:

   - P_new_1: Ball lightning occurrence correlates with **moderate** (not extreme) local turbulence intensity — too little turbulence cannot sustain the structure; too much destroys it
   - P_new_2: Ball lightning lifetime should anti-correlate with local wind shear
   - P_new_3: Ball lightning is more stable when ambient cooling rate falls in the optimal window identified from the radiative layer analysis
   - P_new_4: The ML lifetime predictor's top features predict which thunderstorm conditions produce ball lightning

3. **Constraint on Problem 1 (Approach C)**:
   - Quantitative answer: does turbulent suppression contribute a factor of X to lifetime extension?
   - Combined with Approach A (fully ionized core) and Approach D (two-zone model from Stage 3), what is the total lifetime?
   - If tau_combined = tau_eta * f_ionization * f_topology * f_turbulence ~ 1–10 s → Problem 1 resolved

4. **Paper draft section**:
   - Write "Turbulence Stability Analysis" section suitable for inclusion in the hypothesis paper
   - Include key figures: survival curves, phase diagrams, feature importance plots
   - All figures publication-ready with proper axis labels, legends, and captions

**Deliverable**: Updated hypothesis sections, new predictions, combined lifetime estimate, paper-ready figures.

**Success Criteria**:
- At least 2 new falsifiable predictions added to Ch. 10
- Combined lifetime estimate tau_combined > 1 s
- Clear narrative connecting turbulence data to ball lightning stability

---

## 6. Contributions to Upstream Repositories

### 6.1 To PolymathicAI/the_well

| Contribution | Type | Description |
|-------------|------|-------------|
| **Coherent structure metrics** | New feature | `the_well/benchmark/metrics/coherent_structures.py` — Q-criterion, enstrophy, structure count, mean lifetime |
| **Structure tracking utility** | New feature | Lagrangian structure tracker compatible with WellDataset temporal format |
| **Cooling-stability benchmark** | Documentation | Systematic analysis of model accuracy in preserving coherent structures vs cooling time |
| **Cross-dataset analysis example** | Documentation | Notebook showing how to combine insights from MHD + turbulence datasets |

### 6.2 To Hopfion Ring Lightning Hypothesis

| Contribution | Addresses | Description |
|-------------|-----------|-------------|
| **Turbulence survival constraints** | Problem 1 (Approach C) | Quantitative turbulent suppression factor for lifetime calculation |
| **Two-zone model validation** | Problem 1 (Approach D) | Data-driven boundary layer insulation coefficients |
| **Updated environmental conditions** | Chapter 7 | Turbulence intensity and cooling rate as critical factors |
| **New falsifiable predictions** | Chapter 10 | 4 data-derived predictions for ball lightning occurrence |
| **ML lifetime predictor** | Problem 9 | Fast surrogate for atmospheric Hopfion lifetime estimation |

---

## 7. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Turbulence datasets lack magnetic field (no direct helicity computation) | High | Focus on **hydrodynamic** vortex stability as proxy. MHD analysis done in Contribution 01. Cross-reference results. |
| Astrophysical parameters don't map to atmospheric conditions | Medium | Use dimensionless numbers (Re, Ma, cooling ratio) for mapping. Clearly state scaling assumptions. |
| Structure detection overwhelmed by turbulence (too many structures) | Medium | Use stricter thresholds; focus on top-10% longest-lived structures only |
| turbulence_gravity_cooling too large (829 GB) for full analysis | Medium | Use HuggingFace streaming; process in batches; start with 3-4 representative parameter combinations |
| No clear cooling-stability relationship | Medium | This is still a valid result — implies cooling doesn't help, narrowing hypothesis solution space |

---

## 8. Cross-Reference with Contribution 01

These two contribution plans are designed to be **complementary**:

| Aspect | Contribution 01 (MHD) | Contribution 02 (Turbulence) |
|--------|----------------------|------------------------------|
| **Primary focus** | Magnetic topology (H_m, Q_H) | Hydrodynamic structure stability |
| **Key field** | B (magnetic) | v (velocity) + thermodynamics |
| **Hypothesis problem** | Problem 9 (numerical simulation) | Problem 1 (lifetime, Approaches C & D) |
| **Dataset** | MHD_64, MHD_256 | turbulence_gravity_cooling, turbulent_radiative_layer |
| **ML model use** | Predict B-field evolution | Predict structure lifetime |
| **Key output** | Hopfion detection catalog, tau_H measurement | Turbulence survival constraints, boundary model |

**Integration points**:
- Contribution 01 Stage 4 (topology-lifetime validation) uses turbulence constraints from Contribution 02 Stage 1
- Contribution 02 Stage 3 (boundary layer model) informs the two-zone model parameters tested in Contribution 01 Stage 4
- Both contribute to the combined lifetime estimate in Contribution 02 Stage 5

---

## 9. Execution Timeline

| Stage | Description | Depends On | Estimated Compute |
|-------|-------------|------------|-------------------|
| **1** | Vortex census (turbulence_gravity_cooling) | Data download | ~12 hours (batch processing 2,700 trajectories) |
| **2** | Cooling-stability analysis (2D first, then 3D) | Data download | ~2 hours (2D) + ~24 hours (3D) |
| **3** | Boundary layer model | Stage 2 | ~4 hours post-Stage 2 |
| **4** | ML lifetime predictor | Stages 1 + 2 | ~8 hours GPU training |
| **5** | Synthesis and paper sections | Stages 1–4 + Contribution 01 | ~4 hours writing/analysis |

Stage 1 and Stage 2 can run in parallel. Stage 4 requires both.

---

## 10. Success Metrics Summary

| Metric | Target | Impact on Hypothesis |
|--------|--------|---------------------|
| Structure survival function characterized | S(t) for all 27 parameter combos | Maps turbulence parameter space for Hopfion viability |
| Critical cooling time identified | t_cool_critical with bounds | New constraint for ball lightning environment |
| Boundary insulation factor | kappa_eff < 0.3 | Validates two-zone model (Problem 1, Approach D) |
| Turbulent suppression factor | f_turbulence quantified | Addresses Problem 1, Approach C |
| ML lifetime predictor accuracy | R^2 > 0.6 | Enables fast atmospheric extrapolation |
| Combined lifetime estimate | tau_combined in [1, 100] s | Progress toward resolving Problem 1 |
| New falsifiable predictions | >= 2 added to Ch. 10 | Strengthens hypothesis scientific rigor |

---

*This contribution plan uses The Well's turbulence datasets to provide the first data-driven constraints on coherent structure survival in conditions relevant to ball lightning formation, directly strengthening the Hopfion Ring Lightning Hypothesis.*
