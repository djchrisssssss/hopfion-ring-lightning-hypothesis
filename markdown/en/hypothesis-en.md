# Hopfion (Ring) Lightning Hypothesis — Reinterpreting "Ball Lightning" as a Topological Ring-Shaped Plasma Soliton

---

## Metadata

- **Author**: Kris Lai (@djchrisssssss)
- **Date**: 2025-10-30
- **Status**: Theoretical Hypothesis (Pending Experimental Verification; central lifetime problem open — see Ch. 8A)
- **License**: CC BY 4.0
- **Version**: v0.8
- **Last Updated**: 2026-11-07
- **Collaborative Models**: Claude Sonnet 4.5 (Theoretical Draft), GPT-5 (Theoretical Review & Structural Integration), Claude Opus 5.5 (v0.8 Physics Re-audit, Corrections & Quantitative Checks)

---

## What Changed in v0.8

v0.8 is a correction release. A physics re-audit found errors in v0.7, several of which earlier verification passes had marked as correct. The main changes:

1. **Lifetime formula (Ch. 8).** v0.7's τ ∝ L / P_dissipation, with L the angular momentum, has units of s², not s. It is replaced by τ ≈ E / P_loss. The unsupported "L ≈ 10⁻³ kg·m²/s ⇒ τ ≈ 5–10 s" is withdrawn.
2. **Helicity vs. Hopf charge (Ch. 2.2).** v0.7 used H_m and Q_H "interchangeably" via Q_H = H_m / (4π)². That relation holds only for a dimensionless field built from a unit-vector map. For a physical magnetic field, H_m has units of Wb² and equals a flux-weighted sum of linking numbers.
3. **When topology protects (Ch. 4, 8A).** Helicity is conserved only when the magnetic Reynolds number Rm ≫ 1. For air plasma at a few thousand kelvin (v0.7 used ~4,200 K), Rm ≪ 1 and the resistive decay time of a 10 cm structure is ~10⁻⁷ s; even at 20,000 K it is ~10⁻⁴ s. A 5 s lifetime would need an electrical conductivity 7–170 times that of copper — and a solid copper ball of the same size loses its internal magnetic energy in 30–60 ms. This is now stated as the hypothesis's central open problem.
4. **Confinement (Ch. 2.3, 4).** By the magnetic virial theorem, a magnetized plasma cannot confine itself. The pressure of the surrounding atmosphere must do it. Statements that the structure needs "no container or external field" are corrected.
5. **Predictions made self-consistent (Ch. 10).** The v0.7 rotation speed (500–2,000 m/s) is incompatible with the predicted 10–100 mT field: it exceeds the Alfvén speed, is supersonic in the ambient air, and its centrifugal pressure exceeds the magnetic pressure by factors of 5 to 85 even at 100 mT. It is replaced by v ≲ v_A ≈ 30–300 m/s. Because rotation broadening is unmeasurable at 1 atm, the spectral signature is changed to Zeeman circular polarization.
6. **"The sphere is an optical artifact" (Ch. 1.1, Appendix A).** Now quantified: a torus with major radius R ≥ minor radius a looks clearly non-circular from most viewing directions. The claim survives only for a fat torus inside a surrounding glow comparable to its size — a near-spherical luminous body with toroidal internal structure.
7. **Energy budget (Ch. 8A).** At 10–100 mT, a 25 cm body stores only 0.3–33 J of magnetic energy. The field cannot be the main energy reservoir.
8. **New sections:** Ch. 6A (helicity injection), Ch. 8A (quantitative self-consistency checks), Appendix A (torus projection geometry); reproducible scripts in [`analysis/`](../../analysis/). Observation-table, reference and attribution corrections are listed in the Verification Report, §0.

---

## Chapter 0 — Preface: From Lightning to a Ring-Shaped Energy Body

Under extreme natural conditions, Ball Lightning has long been regarded as one of the most mysterious and hard-to-reproduce electromagnetic phenomena.

Conventional theories cannot fully explain its energy density, its multi-second lifetime, and its near-neutral buoyancy. (Confinement as such is not the puzzle: any hot gas bubble is held by atmospheric pressure.)

This hypothesis proposes that so-called Ball Lightning should be redefined as **Hopfion (Ring) Lightning** — a plasma ring vortex formed by plasma and electric current, whose magnetic field lines are linked with one another.

The hypothesis proposes that its structure is organized by a **topological quantity of the magnetic field** — the magnetic helicity, which counts how field lines link — and by **self-linked magnetic current structures**. Whether this can also explain its multi-second lifetime is the central open problem (Ch. 8A).

This configuration can be viewed as an energy bubble "blown" at the electromagnetic scale.

Just as a diver or a marine mammal produces a long-lived bubble ring that maintains its form, rises slowly, and rotates while drifting, the electromagnetic field can, under specific conditions, "blow" a closed ring composed of plasma and magnetic current.

This ring-shaped structure is neither a solid nor a fleeting plasma flare; it is proposed to be a **ring-like field body whose outer boundary is held by the surrounding atmosphere's pressure and whose internal structure is organized by field-line linkage**.

The hypothesis therefore holds that the so-called "ball" is a luminous body with a toroidal internal structure, and that its round appearance comes from ring thickness, plasma emission and the surrounding glow (quantitative constraints in Appendix A).

---

## Chapter 1 — Redefining Ball Lightning as Hopfion (Ring) Lightning

### 1.1 — The Misread Appearance

The observed "spherical" shape is proposed to be the projection of a thick torus, rounded off by the glow of the surrounding hot gas, misleading observers into seeing a solid ball. (v0.7 attributed the rounding to atmospheric scattering; at the metre-scale distances of most reports that is negligible — the Rayleigh optical depth of clean air is ~10⁻⁴ at 10 m. Blooming in a saturated eye or camera can also round off a bright image.)

Non-saturated high-speed imaging should reveal the ring structure. Thermal emission is unpolarized, so polarization cannot reveal rotation; spectropolarimetry can, however, detect the magnetic field (Ch. 10).

**Geometric constraint (added in v0.8; Appendix A).** For a sharp-edged luminous torus with major radius R and minor radius a, the projected axis ratio at inclination i is q = (R cos i + a) / (R + a). For R ≥ a, at most ~30% of random viewing directions give q ≥ 0.85, and near-face-on views show a dark central hole when R > a. Since most witnesses report a round object, the visible torus must be fat (R ≤ a so that it has no central hole, and R ≈ 0.5 a or less to look nearly round) and embedded in a glow comparable to its own size. The testable form of the claim is therefore that the toroidal structure appears in non-saturated high-speed imaging or magnetic-field measurements — not necessarily in the naked-eye outline.

### 1.2 — Natural Analogy: Bubble Rings

Bubble rings blown by divers, dolphins, or whales rise stably in water while maintaining closure. Their stability comes from a balance between internal–external pressure differences and self-spinning flow.

This self-organized closed ring in a fluid is the natural analogue of Hopfion (Ring) Lightning, with the medium replaced from water to electromagnetic field plus plasma.

The analogy is heuristic. A plain vortex ring carries no helicity (its vortex lines are unlinked circles), a bubble ring has a surface-tension interface that a gas-in-gas plasma lacks, and bubble rings slowly expand and break up as they rise.

The analogy also shows what the electromagnetic version needs. A vortex ring persists because circulation is conserved in a fluid of low viscosity (high Reynolds number). The magnetic counterpart of low viscosity is high electrical conductivity (high magnetic Reynolds number). Whether atmospheric plasma meets this condition is examined quantitatively in Ch. 8A; it is the weakest point of the hypothesis.

### 1.3 — Core Claim

Accordingly, Ball Lightning should be renamed and understood as:

**Hopfion (Ring) Lightning** — a topological energy ring formed by linked magnetic field lines.

It is proposed to be an energy bubble formed by atmospheric plasma under topological conditions, not an afterglow or residue of conventional lightning discharge.

---

## Chapter 2 — The Hopfion (Ring) Structure: Topological Self-Closure of an Energy Ring

### 2.1 — Theoretical Background

A Hopfion is a field configuration whose topology is classified by the Hopf invariant, which Heinz Hopf (1931) [16] introduced for continuous mappings from the 3-sphere to the 2-sphere (S³ → S²). As stable field-theory objects, hopfions were proposed by Faddeev in the 1970s and first computed as stable knotted solitons by Faddeev and Niemi (1997) [18].

In physics, a Hopfion can be understood as a configuration in which field lines form ring-like linking. When such a configuration occurs in a plasma, the linking is preserved for as long as the magnetic field stays frozen into a highly conducting medium. It is then a **topologically constrained ring-shaped energy body**.

**Terminology note (v0.8).** "Soliton" is used loosely in this document. In the Faddeev–Niemi model, stability and a preferred size come from a higher-derivative (Skyrme-like) term that evades Derrick's scaling theorem [18, 39]. MHD has no such term: helicity forbids unlinking but sets no size, and a magnetized plasma can always lower its energy by expanding (Arnold's inequality bounds the energy from below only for a fixed volume [36]). Here "soliton" therefore means "coherent, self-organized structure", not a topological soliton in the strict field-theory sense.

### 2.2 — Mathematical Definition and Topological Charge

The key topological quantity of a magnetized plasma is the **magnetic helicity**:

```
H_m = ∫ (A · B) d³r
```

where:
- **A** is the magnetic vector potential,
- **B** = ∇ × A is the magnetic field.

Woltjer (1958) [21] proved this quantity is conserved in ideal MHD, and Moffatt (1969) [22] showed it measures the degree of knottedness and linkage of field lines. For a field made of thin closed flux tubes with fluxes Φᵢ [22, 25]:

```
H_m = Σᵢ (Twᵢ + Wrᵢ) Φᵢ²  +  2 Σᵢ<ⱼ Lkᵢⱼ Φᵢ Φⱼ
```

where Lkᵢⱼ is the Gauss linking number of tubes i and j, and Twᵢ + Wrᵢ (twist plus writhe) is the self-linking of tube i. Magnetic helicity is therefore a flux-weighted linking count with units of Wb² (T²·m⁴). It is not an integer.

An integer **Hopf invariant** Q_H appears only for a dimensionless field built from a unit-vector field **n**: S³ → S², through Whitehead's integral [17]; Ranada's electromagnetic knots are of this type, and their helicity equals Q_H times a fixed normalization constant [8, 19]. v0.7's statement Q_H = H_m / (4π)², applied to a physical magnetic field, is dimensionally inconsistent and is withdrawn. This document uses H_m for the physical quantity and "Hopf charge" only for idealized Hopf-map fields.

Two further conditions apply:

- ∫ A · B is gauge-invariant only if no field lines cross the boundary of the region. In the open atmosphere, with the geomagnetic field threading the region, the meaningful quantity is the **relative helicity** [25].
- H_m is conserved exactly only in ideal MHD. With finite electrical resistivity η_e it decays as dH_m/dt = −2 η_e ∫ J · B d³r. Topological protection is therefore conditional on the magnetic Reynolds number being large (Ch. 4, 8A).

When H_m is nonzero and the field is frozen in, magnetic field lines encircle each other in a configuration that cannot be unlinked without reconnection, and the field forms a structured **field bubble** inside the plasma.

### 2.3 — Stability Ingredients (corrected in v0.8)

v0.7 listed three sources of stability. Each holds only in the restricted form below:

1. **Topological constraint**: while the field stays frozen into the plasma (Rm ≫ 1), linked field lines cannot unlink without reconnection. This constrains how the field can relax — Taylor relaxation conserves helicity while energy is dissipated [23, 24] — but it does not by itself prevent energy loss or expansion.
2. **Angular momentum**: a rotating structure keeps its angular momentum only until viscous and aerodynamic drag remove it. For the field to organize the flow, the rotation must stay below the Alfvén speed (Ch. 8A.3).
3. **Pressure balance**: by the magnetic virial theorem, a finite-energy plasma–field configuration cannot be in equilibrium under its own forces alone [40]; it needs an external agent. Here that agent is the surrounding atmosphere, through total pressure balance at the boundary, p_in + B²/2μ₀ = p_atm. At 50 mT the magnetic pressure is ~1% of atmospheric pressure (plasma β ≈ 100), so the atmosphere — not the field — sets the outer boundary. It plays the containing role that the conducting wall plays for a laboratory spheromak [38].

The bubble-ring analogy holds here too: the surrounding water's pressure contains a bubble ring, while its circulation maintains its shape. Hopfion (Ring) Lightning is proposed as the electromagnetic counterpart, a "bubble ring" in field space.

### 2.4 — Corresponding Physical Systems

Hopfion-type structures have been realized or simulated in several systems:

- Spin hopfions in magnetic multilayers [30] and hopfion rings in a cubic chiral magnet [32];
- Knot solitons in Bose–Einstein condensates [28, 29];
- Three-dimensional topological solitons in chiral liquid crystals [33, 34];
- Optical skyrmionic hopfions in structured light [31];
- Self-organizing knotted magnetic fields in resistive MHD simulations [27];
- Laboratory spheromaks — compact plasma tori with linked toroidal and poloidal magnetic flux, the closest existing plasma analog [38];
- Topological flux structures in superconductors (theoretical proposals only).

In the condensed-matter, optical and condensate cases, the topology is stabilized by the medium's own stiffness (exchange interaction, elasticity, phase coherence), which atmospheric plasma lacks. These systems show that hopfion topology is physically realizable, not that it is stable in air.

Hopfion (Ring) Lightning under atmospheric conditions would be a discharge-driven, open-air relative of these structures — closest in kind to the spheromak — in which the electromagnetic field is the fluid and topology is the skeleton.

---

## Chapter 3 — Abstract: The Core of the Hopfion (Ring) Lightning Hypothesis

This work proposes that Ball Lightning is a **compact toroidal plasma structure with linked magnetic field lines** — a hopfion-type configuration with nonzero magnetic helicity:

```
H_m = ∫ (A · B) d³r ≠ 0
```

and that its round appearance comes from a thick torus seen through its own glow.

In this picture the atmosphere's pressure contains the structure, while helicity organizes its internal field and constrains how it relaxes and splits.

The v0.8 audit shows that this topological constraint is effective only if the plasma's magnetic Reynolds number is large. For air plasma at any plausible ball-lightning temperature it is far below one, and the resistive decay time of a 10 cm structure lies between ~10⁻⁷ s (at 4,200 K) and ~10⁻⁴ s (at 20,000 K) (Ch. 8A). Explaining multi-second lifetimes therefore requires a mechanism beyond topology; this is the hypothesis's central open problem.

The model's distinctive, testable signatures are a toroidal internal structure, a measurable magnetic field and its decay history, and helicity-consistent splitting (Ch. 10).

---

## Chapter 4 — Core Statements and Governing Equations: MHD for Hopfion (Ring) Lightning

At atmospheric pressure the plasma is highly collisional, so a fluid (MHD) description is appropriate. The governing equations of compressible resistive MHD are:

```
∇ · B = 0,        J = (∇ × B) / μ₀
∂ρ/∂t + ∇ · (ρv) = 0
ρ ( ∂v/∂t + v · ∇v ) = −∇p + J × B + ρν ∇²v + ρg
∂B/∂t = ∇ × (v × B) + η_m ∇²B        (uniform η_m)
```

supplemented by an energy equation that includes Ohmic heating, thermal conduction and radiation.

where:
- **η_m** = 1/(μ₀σ) is the magnetic diffusivity (σ: electrical conductivity),
- **ν** is the kinematic viscosity (so the viscous force density is ρν∇²v; v0.7 omitted the factor ρ),
- **μ₀** is the permeability of free space.

v0.7 used the incompressible form, which does not fit this problem: a pressure-balanced 4,200 K body has only ~7% of the ambient air density. For weakly ionized air (ionization fraction ~10⁻⁵ at 4,200 K), Ohm's law also gains Hall and ambipolar terms. The ambipolar term adds dissipation and the Hall term does not remove it, so neither rescues the lifetime estimates of Ch. 8A.

Three dimensionless measures decide whether topology matters:

```
Rm  = v L / η_m          magnetic Reynolds number
S   = v_A L / η_m        Lundquist number   (v_A = B / √(μ₀ρ))
τ_η ≈ L² / η_m = μ₀ σ L²  resistive decay time
```

Field lines are frozen in, and helicity is conserved, only when Rm and S are much larger than one. The statement "if field lines form a closed ring and H_m ≠ 0, the structure is topologically protected" therefore holds only for Rm ≫ 1, and confinement comes from atmospheric pressure, not from field linkage alone (Ch. 2.3).

---

## Chapter 5 — Topological Features of Hopfion (Ring) Lightning

1. Magnetic field lines lie on nested toroidal surfaces and close on themselves (or cover each surface densely);
2. In the ideal Hopf-charge-1 configuration, any two closed field lines link exactly once (the Hopf fibration); a real plasma field need only carry nonzero net helicity;
3. The luminous body may look round while the core magnetic structure is toroidal (Appendix A);
4. Internal plasma flow includes both azimuthal and helical components.

In ideal MHD, a field with H_m ≠ 0 cannot be unwound by continuous deformation; changing its topology requires a **topological change** such as magnetic reconnection. Two qualifications apply. First, most of the magnetic energy can be dissipated without changing the helicity (Taylor relaxation [23, 24]). Second, in a resistive plasma the field also decays by diffusion on the time scale τ_η. Nonzero helicity guarantees a lower bound on the magnetic energy only for a given volume (Arnold's inequality [36]), and the atmosphere does not hold the volume fixed.

---

## Chapter 6 — Formation Mechanisms: From Discharge to Ring Fields

### (A) Lightning-Triggered Mechanism

1. A cloud-to-ground return stroke (peak current typically 10⁴–10⁵ A; median ~30 kA for negative first strokes [41]) creates intense magnetic fields and shear;
2. A rotating plasma vortex forms near the channel tip (assumed; not yet observed);
3. Magnetic reconnection detaches a closed, ring-shaped field structure;
4. If net helicity has been injected (Ch. 6A), the detached ring carries H_m ≠ 0;
5. The ring relaxes toward a minimum-energy (force-free) state at nearly constant helicity, as in spheromak formation [23, 38]; its residual angular momentum, buoyancy and any electric forces then govern its drift and rotation.

### (B) Spontaneous Topological Generation (Conjectural)

Strong electric-field gradients and the geomagnetic field might generate a topological ring without a lightning strike. The comparison with cosmic-string formation, superconducting vortices or liquid-crystal defects is only a loose analogy: those form through symmetry-breaking phase transitions, for which atmospheric plasma has no known counterpart.

No mechanism or rate estimate is offered for this route; it is conjectural and currently untestable.

---

## Chapter 6A — Helicity Injection (added in v0.8)

Taylor relaxation conserves helicity but does not create it, so the formation sequence must explain where H_m comes from.

- **Straight channel**: a straight lightning channel produces circular (azimuthal) field lines, which do not link one another: H_m = 0.
- **Requirement (order of magnitude)**: a structure of radius 12.5 cm with B = 50 mT carries a flux Φ ≈ Bπr² ≈ 2.5 × 10⁻³ Wb, so it needs H_m ~ Φ² ≈ 6 × 10⁻⁶ Wb².
- **Geomagnetic route**: the geomagnetic field (B_g ≈ 50 µT) threading the channel turns the channel's circular field lines into helices. The resulting mutual helicity, ~2 Φ_axial Φ_azimuthal with Φ_axial = B_g π r² ≈ 3.5 × 10⁻⁶ Wb (r = 15 cm) and Φ_azimuthal ≈ (μ₀ I / 2π) ℓ ln(r_out/r_in) ≈ 4 × 10⁻³ Wb (I = 30 kA, ℓ = 0.3 m, r_out/r_in = 10), is ≈ 3 × 10⁻⁸ Wb². That is about 200 times too small, even with the full geomagnetic field taken along the channel.
- **Candidates not yet quantified**: self-helicity of a non-planar (writhed or twisted) channel; mutual linking of successive return strokes or branches; selective capture of turbulent helicity.

**Status: open.** The helicity source is a necessary link in the causal chain. It must be quantified before the formation mechanism can be called physical. (Script: [`analysis/self_consistency.py`](../../analysis/self_consistency.py).)

---

## Chapter 7 — Environmental Conditions and Formation Weights for Ring Lightning

The weights below are the author's qualitative assessment. They are not derived from data; read them as research priorities, not measured importance. The humidity entry in particular is unsourced: water vapour generally shortens the life of non-equilibrium plasma through electron attachment.

| Factor | Importance | Certainty | Primary Role |
|--------|-----------|-----------|-------------|
| Atmospheric electric field strength | ★★★★★ | High | Ionization and energy source |
| Thunderstorm activity | ★★★★ | High | Transient magnetic field and shear |
| Humidity | ★★ | Medium | Conductivity and plasma lifetime |
| Geomagnetic anomalies | ★★ | Low | Possible topological alignment |
| Pressure / altitude | ★ | Medium | Breakdown threshold and diffusion rate |

**Hypothesized necessary conditions**: an ionized gas and a strong transient electric field (e.g., >10⁵ V/m near a lightning channel). Thunderstorm fields at ground level are typically only ~10⁴ V/m because corona space charge limits them [41], and some reports come from indoors or aircraft cabins; such cases directly test this condition.

**Hypothesized formation route**: a lightning-induced event with magnetic reconnection and net helicity injection (Ch. 6A). This is not a sufficient condition: lightning and reconnection are vastly more common than ball lightning, so some further, rarer condition must select the events that produce it.

**Hypothesized facilitators** (unsourced): moderate humidity and rotational airflow

---

## Chapter 8 — Lifetime: A Topologically Constrained Energy Bubble?

Non-equilibrium discharge plasma in air recombines within milliseconds. A hot gas ball in local thermal equilibrium, by contrast, stays luminous as long as it stays hot: conduction alone would take ~1–8 s to cool a 25 cm ball, and the faster loss is buoyant mixing (~0.1–1 s; Ch. 8A.2). Ball lightning is reported to last seconds. The lifetime of any structure is its stored energy divided by its total loss rate:

```
τ ≈ E_stored / P_loss
P_loss = P_Ohmic + P_radiation + P_conduction + P_convection,    P_Ohmic = ∫ J²/σ d³r
```

**Correction.** v0.7 wrote τ ∝ L / P_dissipation with L ≈ MR²ω the angular momentum. That ratio has units of s², not s, and the quoted "L ≈ 10⁻³ kg·m²/s ⇒ τ ≈ 5–10 s" gave no value for P_dissipation. Both are withdrawn. In addition, L ≈ 10⁻³ kg·m²/s for a 0.7 g body of radius 10 cm implies a rim speed of only ~15 m/s, which contradicts v0.7's own rotation prediction of 500–2,000 m/s.

For the magnetic structure itself, the relevant time is the resistive decay time τ_η ≈ μ₀σL². Chapter 8A evaluates it: for atmospheric plasma it is shorter than observed lifetimes by many orders of magnitude. Whether the topological structure suppresses radial diffusion enough to close that gap — the original intuition of this chapter — is the open problem of this hypothesis.

---

## Chapter 8A — Quantitative Self-Consistency Checks (added in v0.8)

Reference body: diameter 25 cm (V = 8.2 × 10⁻³ m³), temperature 4,200 K (v0.7's value; the spectral study of the best-documented event gives ~4,300–4,600 K from Si I and Fe I lines and ~8,750 K from O I lines [46]), pressure 1 atm. Pressure balance then gives a density of ~0.08 kg/m³ (6–7% of ambient air, depending on O₂ dissociation) and a mass of ~0.6–0.7 g. None of the conclusions below depends on the exact temperature: the table in 8A.1 spans 3,000–20,000 K. All numbers are reproduced by [`analysis/self_consistency.py`](../../analysis/self_consistency.py).

### 8A.1 — Resistive Lifetime and Magnetic Reynolds Number

| Plasma state | Conductivity σ (S/m) | η_m = 1/(μ₀σ) (m²/s) | τ_η for L = 0.1 m |
|---|---|---|---|
| 3,000 K equilibrium air (estimate) | ~0.4 | ~2 × 10⁶ | ~5 × 10⁻⁹ s |
| 4,200 K equilibrium air (estimate; ionization ~10⁻⁵) | ~7 | ~1 × 10⁵ | ~1 × 10⁻⁷ s |
| 6,000 K equilibrium air (estimate) | ~4 × 10² | ~2 × 10³ | ~5 × 10⁻⁶ s |
| 10,000 K equilibrium air [42] | ~3 × 10³ | ~3 × 10² | ~4 × 10⁻⁵ s |
| 20,000 K equilibrium air [42] | ~1 × 10⁴ | ~80 | ~1 × 10⁻⁴ s |
| **Required for τ_η = 5 s** | **~4 × 10⁸** | **~2 × 10⁻³** | **5 s** |

The 3,000–6,000 K rows are order-of-magnitude estimates (Saha equilibrium with NO at ~3% of molecules plus 1 ppm sodium; electron–neutral collision cross-section ~10⁻¹⁹ m²). Soil vapour of the kind seen in [1] (Si, Fe, Ca) could raise σ at ~4,000 K to ~10² S/m, and full ionization at that temperature cannot exceed the Spitzer value of ~10³ S/m [43]; neither changes the conclusion.

The crude estimate τ_η ≈ μ₀σL² is generous. The lowest free-decay mode of a conducting sphere of radius a decays as τ = μ₀σa²/(ka)² with ka ≈ π–4.5, and the magnetic energy and helicity e-fold in half that time. For a = 12.5 cm this shortens the decay times above by a factor of ~10–20, and raises the conductivity needed for a 5 s energy lifetime to ~5 × 10⁹–1 × 10¹⁰ S/m. **The required conductivity is therefore 7 times (crude estimate) to ~170 times (lowest decay mode) that of copper** (6 × 10⁷ S/m). For comparison, a solid copper ball 25 cm across loses its internal magnetic energy in 30–60 ms.

The magnetic Reynolds number Rm = vL/η_m, with L = 0.1 m, is at most ~0.4 even for v = 300 m/s (the Alfvén-limited maximum, 8A.3) and the most favourable η_m ≈ 80 m²/s. At 4,200 K it is ~10⁻⁴ or less. The field is therefore not frozen into the plasma, helicity is not conserved over the observed lifetime, and **topological protection does not operate**.

Nor can the field act as thermal insulation, as v0.7's Ch. 8 suggested ("topological structure suppresses radial diffusion"). At 10–100 mT the electron Hall parameter ω_ce/ν_en is only ~0.03–0.3, the ions are far less magnetized, and the neutral gas — 99.999% of the particles at 4,200 K — does not feel the field at all.

Two tempting escape routes do not work:

- **A hotter core.** Spitzer resistivity falls as T^(−3/2) [43], but even a fully ionized 10⁵ K (8.6 eV) core gives η_m ≈ 16 m²/s and τ_η ≈ 0.6 ms. Such a core at 1 atm would also be strongly over-pressured or extremely rarefied, and would radiate intensely.
- **"Helicity outlives energy."** For a single force-free (Beltrami) mode ∇ × B = αB, magnetic energy and helicity decay at the same rate, 2η_m α². Helicity outlasts energy only in multi-scale (turbulent) fields, and then by moving energy to large scales, not by halting the decay.

### 8A.2 — Energy Budget

| Component | Estimate | Notes |
|---|---|---|
| Magnetic, (B²/2μ₀)·V | 0.33 J (10 mT), 8 J (50 mT), 33 J (100 mT) | Storing 8 kJ magnetically needs B ≈ 1.6 T, a magnetic pressure of ~10 atm. The virial theorem caps the magnetic energy that 1 atm can contain in this volume at 3p_atm V ≈ 2.5 kJ, whatever the topology |
| Kinetic (rotation), ½Mv² | 0.3–33 J for v = 30–300 m/s | v0.7's 500–2,000 m/s would give 86–1,400 J, but is not self-consistent (8A.3) |
| Thermal, sensible enthalpy above ambient | ~3 kJ | c_p ≈ 1.25 kJ·kg⁻¹·K⁻¹, ΔT ≈ 3,900 K |
| Chemical, O₂ dissociation | ≤ ~2.5 kJ | released on recombination; upper bound assumes complete dissociation |
| **Total** | **~5–6 kJ, of which < 1% magnetic** | |

Survey-based estimates put the most probable energy at ~6–7 kJ [45]. If energies of that order are real, the magnetic field cannot be the reservoir. At most it shapes or insulates energy stored thermally or chemically.

Thermal storage raises its own problem: **buoyancy**. A pressure-balanced 4,200 K body has 6–7% of the ambient density and would rise at ~2–2.5 m/s (drag coefficient 0.5–1), covering its own diameter in ~0.1 s, whereas about half of reports describe mostly horizontal motion [4]. An isolated current system in the nearly uniform geomagnetic field feels a torque but no net force, so the field cannot cancel buoyancy; a net electric charge in the ambient electric field, or an unmodelled mass load such as soil-derived particles, would have to.

### 8A.3 — Rotation–Field Consistency

At 1 atm the ions are collisionally locked to the neutral gas, so the Alfvén speed uses the total density: v_A = B/√(μ₀ρ) ≈ 31, 154 and 308 m/s for 10, 50 and 100 mT.

v0.7's predicted rotation of 500–2,000 m/s is:

- super-Alfvénic, so the flow would wind up and dominate the field rather than be organized by it;
- faster than sound in the ambient air (343 m/s), so it should radiate strong acoustic noise, whereas ball lightning is mostly described as nearly silent;
- impossible to contain: its centrifugal pressure ρv² = 0.2–3.3 atm exceeds the magnetic pressure at 100 mT (0.04 atm) by 5–85 times; balance would need B ≈ 0.23–0.92 T.

The prediction is therefore replaced by v ≲ v_A (Ch. 10).

The bubble-ring analogy adds a sharper limit. If part of the internal flow is poloidal circulation — the flow that makes a smoke or bubble ring — the ring propels itself along its axis at a speed comparable to that circulation (~0.7× for the geometry here). Typical drift speeds of a few m/s [4, 45] therefore limit poloidal circulation to a few m/s.

### 8A.4 — Comparison with Laboratory Spheromaks

Spheromaks are laboratory compact tori with linked toroidal and poloidal flux. They form by helicity injection and relax to Taylor states — the closest existing analog of the proposed structure [38]. They are far hotter than any plausible atmospheric plasma (electron temperatures of tens to hundreds of eV, versus ~0.4 eV here), operate at densities around 10¹⁹–10²⁰ m⁻³, sit inside conducting flux conservers, and still decay within milliseconds [38].

Because the resistive decay time scales as T^(3/2), an atmospheric structure at ~0.4 eV should decay faster, not slower. Any viable version of this hypothesis must explain why it would outlive its laboratory counterpart by three or more orders of magnitude.

### 8A.5 — Status after the v0.8 Audit

In its v0.7 form — "topology alone gives seconds-long stability" — the hypothesis fails a quantitative self-consistency test: the resistive decay time falls short of observed lifetimes by four to eight orders of magnitude, depending on temperature. It can survive only in a modified form. Candidate directions, all open:

1. **Topologically organized, non-magnetically powered.** Helicity shapes the structure during its first millisecond or less, while a thermal or chemical reservoir powers the long-lived glow (for example, oxidation of soil-derived particles as in [14]; soil-element lines were observed in [1]). Test: the magnetic field should decay within ≲1 ms of formation, long before the glow fades.
2. **Non-MHD current carriers.** Currents carried by charged aerosols or nanoparticles, whose transport differs from that of free electrons. Speculative; no estimate yet.
3. **Externally sustained.** Energy or current fed continuously by the ambient storm field, as in charge-deposition models [15]. The structure is then not self-contained, and its lifetime should correlate with the ambient field. Sustaining even 10 mT in a 25 cm body against Ohmic loss would take ~10⁵–10⁸ W, depending on conductivity.
4. **Hydrodynamic ring.** A buoyant hot-gas thermal naturally rolls up into a vortex ring within a few diameters of rising. A ring morphology could therefore arise for purely hydrodynamic reasons, with zero magnetic helicity — consistent with the bubble-ring intuition, but not with topological protection, and in tension with reports of horizontal motion. Testable in laboratory plasmoids.

Each direction changes what the hypothesis claims about energy and lifetime, so they are listed as open questions rather than as part of the hypothesis.

---

## Chapter 9 — Observational Correspondence: From Spherical Illusion to Ring Reality

| Phenomenon | Challenge for Traditional Models | Hopfion (Ring) Lightning — v0.8 assessment |
|------------|-------------------------------|---------------------------------------|
| Round, stable appearance | Any model must explain a round, stable outline | Toroidal core inside a near-spherical glow, held by atmospheric pressure; requires a fat torus inside a glow comparable to its size (Appendix A) |
| Obstacle penetration (e.g., through glass) | Plasma cannot pass through solid glass | **Not explained.** The magnetic field passes through glass, but the current-carrying plasma cannot; re-forming on the far side would need a new current system. Open |
| Splitting events | Mechanism unclear | Splitting requires reconnection, which (at high Rm) approximately conserves total helicity: H_m ≈ H₁ + H₂ + 2Lk₁₂Φ₁Φ₂. Daughters should generally share the parent's handedness — testable in principle with vector magnetometry. (Integer additivity Q = Q₁ + Q₂ holds only for idealized Hopf-map fields) |
| Long lifetime | Insufficient energy and confinement | **Not explained by topology alone** (Ch. 8A: τ_η ≪ 1 s). Central open problem |
| Silent fade vs. explosive end | Unclear energy sink | Gradual decay → silent fade; sudden reconnection → abrupt end. But stored magnetic energy (≤ tens of J) cannot power kJ-scale explosions |
| Motion along conductors | Lacks driver | Requires a net electric charge (image-charge attraction) — an added assumption, not part of the MHD picture. A magnetic dipole alone would be repelled, not attracted, by eddy currents in a non-ferromagnetic conductor |

---

## Chapter 10 — Falsifiable Predictions: Experimental Signatures of Hopfion (Ring) Lightning

1. **Magnetic signature (the strongest and cheapest test).** Internal field 10–100 mT (an assumed scale, not derived). Its external (poloidal) part falls off roughly like a dipole: with 50 mT at the surface of a body of radius 12.5 cm, ~100 µT at 1 m and ~12 µT at 2 m; for 10–100 mT, ~20–200 nT at 10 m. That is comparable to or larger than the geomagnetic field at close range, measurable with fluxgate magnetometers, and — as a quasi-static signal lasting seconds — separable from the µs–ms transient of the return stroke. (A purely toroidal component would be invisible from outside.) Unless the open problem of Ch. 8A is solved, the field should decay within ≲1 ms; **the timing of the field's decay relative to the glow is the sharpest test.** A seconds-long field would overturn standard resistive-MHD expectations; its absence near well-instrumented events or laboratory analogues (water-discharge plasmoids [51], silicon-discharge balls [44], microwave fireballs [52]) would rule out all magnetically confined ball-lightning models, including this one.
2. **Rotation and polarization.** If rotation is present and organized by the field, it should be sub-Alfvénic: v ≲ v_A ≈ 30–300 m/s for 10–100 mT. The resulting Doppler shifts (≲ 6 × 10⁻⁴ nm at 600 nm) are below the thermal Doppler and pressure widths of emission lines at 4,000 K and 1 atm (several × 10⁻³ nm), so disk-integrated "rotation broadening" is not a usable signature. Rotation could be detected only as a spatially resolved limb-to-limb Doppler shift (resolving power ≳ 10⁵, realistic only for laboratory analogues) or through non-axisymmetric features in high-speed imaging — an axisymmetric, uniformly glowing torus spinning about its own axis looks static. The field itself can in principle be measured spectroscopically: Zeeman splitting (~2 × 10⁻⁴ to 2 × 10⁻³ nm at 10–100 mT) is unresolved, but a net line-of-sight field produces circular polarization (Stokes V) in line wings, detectable by spectropolarimetry. A purely toroidal field largely cancels in an unresolved observation.
3. **Lifetime–size relation.** If lifetime were limited by resistive decay, τ ∝ L² at fixed temperature (τ_η = μ₀σL²). Survey data on lifetime versus diameter can test this scaling, although the absolute values (Ch. 8A) already disagree by many orders of magnitude.
4. **Shape statistics.** If the luminous body is a torus with R ≳ a, high-speed images should show elongated outlines (axis ratio < 0.85) from most viewing directions and central dimming near face-on (Appendix A). Consistently round images from many angles would require a fat torus inside a glow, or falsify the visible-torus version.
5. **Energy.** Magnetic energy at 10–100 mT is ≤ ~33 J for a 25 cm body. If damage-based energy estimates of kilojoules or more are confirmed, the field cannot be the main reservoir (Ch. 8A.2).
6. **Handedness.** The sign of the helicity should be preserved through splitting; a pair of daughters with opposite handedness would contradict helicity-conserving splitting.

---

## Chapter 11 — Conclusion: The Electromagnetic Bubbles of the Cosmos & Scientific Positioning of Hopfion (Ring) Lightning

The intuitive starting point of this hypothesis is that the atmospheric electrostatic web blows a Hopfion ring bubble within its own field.

The hypothesis proposes that the luminous body's structure is organized by the **topological linkage of magnetic fields** and held in place by the surrounding atmosphere. The v0.8 audit shows that this linkage cannot by itself explain a multi-second lifetime (Ch. 8A); that is the problem a future version must solve.

- If validated, Hopfion (Ring) Lightning would be a free-floating atmospheric plasma structure with linked magnetic field lines — a natural relative of the laboratory spheromak. No such structure has been confirmed in Earth's atmosphere. (Macroscopic helicity-carrying structures do exist elsewhere: laboratory spheromaks [38] and interplanetary magnetic clouds, which have been interpreted as spheromak-like [55]. v0.7's "first macroscopic topological soliton observed in nature" is therefore withdrawn.)
- It would build a new bridge across **MHD, topological field theory, and atmospheric plasma physics**.
- It would offer a natural example of **energy self-organization constrained by topology**.
- It highlights a "field bubble-blowing" picture of nature — energy organizing itself in field form, with transient persistence.

---

*This hypothesis framework is designed as a falsifiable, physics-grounded theoretical proposal pending experimental verification. v0.8 states its central quantitative problem explicitly (Ch. 8A) so that it can be tested and, if necessary, falsified.*

---

## Prior Art and Intellectual Lineage

This hypothesis builds upon a well-established lineage of topological models for ball lightning, particularly the electromagnetic knot framework pioneered by **A. F. Ranada and J. L. Trueba** (1989–2000) [8–12]. Their foundational contributions include:

- Demonstrating that Maxwell's equations admit topological solutions characterized by the Hopf index [8, 9]
- Proposing ball lightning as a topologically stable electromagnetic knot [10]
- Developing the linked-streamer model explaining lifetime, energy, and radiated power [11]
- Analyzing stability via Taylor relaxation, Alfven conditions, and helicity conservation [12]

The present work extends the Ranada-Trueba framework by:

1. **Placing the Ranada–Trueba knots — already characterized by the Hopf index [8, 9] — within the broader hopfion literature**, including Faddeev-Niemi knot solitons [18] (v0.7's phrase "rather than generic electromagnetic knots" understated how much of the topology [8–10] already contained)
2. **Drawing the bubble-ring analogy** for physical intuition — comparing the electromagnetic ring to a diver's bubble ring
3. **Proposing that the observed sphere is a non-spinning thick luminous torus seen through its glow**, now with quantitative geometric constraints (Appendix A). Toroidal models of ball lightning predate this work — Johnson's toroidal-field model (1965) [48], Koloc's PLASMAK (a toroidal current ring inside a near-spherical plasma shell) [49], Seward's proposal that a spinning ring appears as a ball (1997) [50], and the linked-ring streamers of [11] — and ring- or torus-shaped ball lightning has occasionally been reported [47]. The contribution here is the specific geometric mechanism and its quantified, testable consequences, not the torus itself (v0.7 called it "an original observational prediction")
4. **Connecting to recent hopfion observations** (2015–2023) in condensed matter, optics, and BEC systems [28–34], and to numerical MHD work [27], which were unavailable when the Ranada-Trueba model was formulated
5. **Stating the model's quantitative self-consistency problems explicitly** (Ch. 6A, 8A)

Additional foundational contributions include the **Kamchatnov-Hopf topological MHD soliton** (1982) [26], which constructed exact soliton solutions via the Hopf mapping, and the **Smiet et al. MHD simulations** (2015) [27], which demonstrated self-organizing knotted magnetic structures in resistive plasma. The closest laboratory plasma analog is the **spheromak** [38].

---

## Comparison: This Hypothesis vs. Competing Models

| Feature | **Hopfion (Ring) Lightning** (this work, v0.8) | **Ranada-Trueba EM Knot** [10–12] | **Abrahamson-Dinniss Nanoparticle** [14] | **Tsui Force-Free Plasmoid** [13] | **Lowke Ion Model** [15] |
|---------|----------------------------------------|-----------------------------------|----------------------------------------|----------------------------------|--------------------------|
| **Core mechanism** | Compact torus with linked field lines (H_m ≠ 0) | Electromagnetic knot with linked field lines | Silicon nanoparticle oxidation network | Force-free magnetic field equilibrium | Ion accumulation on insulating (window) surfaces |
| **Energy source** | Magnetic + thermal; magnetic ≤ tens of J at 10–100 mT (Ch. 8A.2) | Magnetic field energy (helicity is a constraint, not a source) | Chemical (Si + O₂ → SiO₂) | Magnetic field energy (helicity-constrained) | External electric field |
| **Shape explanation** | Toroidal core in a near-spherical glow (Appendix A) | Magnetic knot with linked plasma streamers (closed, linked rings) | Fractal nanoparticle network (sphere) | Spherical plasmoid | Approximately spherical discharge at a window |
| **Stability mechanism** | Helicity constraint (requires Rm ≫ 1) + atmospheric pressure confinement | Helicity conservation + Taylor relaxation | Slow oxidation kinetics | Helicity conservation | Electric field sustenance |
| **Lifetime explanation** | τ ≈ E/P_loss; resistive limit τ_η ≪ 1 s — open problem (Ch. 8A) | Helicity dissipation timescale | Oxidation rate (~seconds) | Adiabatic force-free decay | Continuous energy input |
| **Requires lightning strike** | Yes (primary) or spontaneous (conjectural) | Not necessarily | Yes (soil vaporization) | Not necessarily | Not necessarily: needs an ion stream onto an insulating window; stepped leaders are the likeliest source, but one reported case had no thunderstorm |
| **Spectral prediction** | Air/plasma emission; Zeeman circular polarization (rotation broadening unmeasurable at 1 atm) | Plasma emission | Si, Fe, Ca lines (soil elements) | Plasma emission | Air molecule excitation |
| **Falsifiable signature** | B-field magnitude and decay timing (magnetometry); toroidal structure in non-saturated high-speed imaging; handedness in splitting | Magnetic field measurement | Soil-element spectral lines | Force-free field measurement | Surface charge measurement |
| **Experimental support** | Hopfion topology realized in BEC, magnets, liquid crystals, optics (2015–2023); no atmospheric evidence yet | Theoretical; BEC analog (2018) | Cen et al. 2014 spectral match [1]; lab Si discharge [44] | Theoretical | Eyewitness cases (aircraft) + electron/ion transport calculations; no lab test |

**Other relevant models and laboratory analogues (added in v0.8).** Luminous balls lasting from tens of milliseconds to seconds have been made in the laboratory without any magnetic confinement: silicon-discharge balls 1–4 cm across lasting 2–5 s [44]; "Gatchina" water-discharge plasmoids up to ~0.2 m across lasting some hundreds of milliseconds, whose light comes mostly from chemiluminescence [51]; and microwave fireballs ~3 cm across lasting 30–40 ms after the power is switched off [52]. These are natural test beds for the magnetometry prediction of Ch. 10. For some sightings, a perceptual explanation has also been proposed: phosphenes induced by the lightning's magnetic pulse [53]; its corrected field estimates make this plausible only within a few metres of the strike, with retinal stimulation the more likely route [54].

---

## Observational Data: Typical Ball Lightning Parameters

Based on compiled observational surveys [1–7, 45] (corrected in v0.8 against the cited sources):

| Property | Typical Value | Range | Key Sources |
|----------|--------------|-------|-------------|
| **Diameter** | ~20–35 cm | Few cm to >1 m | Smirnov (1992) [45]: mean 23 ± 5 cm; Rayle (1966) [4]: median ≈36 cm |
| **Lifetime** | ~3–10 s | ≲1 s to >1 min | Rayle [4]: median ≈6 s, 5–12% over 30 s; Smirnov [45]: ~8 s |
| **Shape** | Roughly spherical | Spherical, ovoid, irregular; ring/torus shapes occasionally reported | Rayle [4]: 87% round; Smirnov [45]: 91 ± 1% spherical; torus case: Keul (1999) [47] |
| **Color** | White, red, orange, yellow (~20% each) | Blue, violet, green together ~11% | Smirnov [45] |
| **Motion** | Often horizontal (54% in Rayle), a few m/s | Stationary to >27 m/s (17% of Rayle's cases) | Rayle [4]; 8.6 m/s measured in [1] |
| **Energy** | Most probable ~6–7 kJ; log-normal mean ~60 kJ | Very wide; some accounts imply ~10⁶ J | Smirnov [45]; Rayle [4] |
| **Temperature** (single event) | ~4,300 K (Si I), ~4,600 K (Fe I), ~8,750 K (O I), ~2,700 K (continuum) | — | An et al. (2022) [46], for the event of [1] |
| **Luminous intensity** (same event) | ~5.9 × 10⁴ cd for most of the lifetime; 1.24 × 10⁵ cd maximum, initial stage; optical power ~4 kW | — | Wang et al. (2018) [2] |
| **Thunderstorm association** | ~94% of Rayle's respondents; 80 ± 10% in Smirnov's compilation | Some indoor/aircraft reports | Rayle [4]; Smirnov [45] |
| **Termination** | Silent fade or explosion (~50% explode) | — | Smirnov [45] |
| **Impression of rotation** | 56% of Rayle's witnesses | ~10% volunteered in McNally's survey | Rayle [4] |

The temperature and luminous-intensity rows describe one well-documented event (Qinghai, 2012: observed from 0.9 km, apparent diameter ~5 m — which the authors stress is not the real diameter — lifetime 1.64 s, soil-element lines of Si, Fe and Ca throughout [1]). They are not typical values. v0.7 attributed a "~4,200 K core temperature" to [1]; that paper reports no numerical temperature, and the "8–80 kJ" energy it attributed to "Abrahamson et al. (2002)" has no matching source.

---

## Experimental and Numerical Hopfion Milestones (2015–2023)

| Year | Authors | Achievement | System | Journal | DOI |
|------|---------|------------|--------|---------|-----|
| 2015 | Smiet et al. | Self-organizing knotted magnetic structures in MHD simulation (numerical, not experimental) | Plasma (simulation) | *Phys. Rev. Lett.* 115, 095001 | [10.1103/PhysRevLett.115.095001](https://doi.org/10.1103/PhysRevLett.115.095001) |
| 2016 | Hall et al. | First quantum knot soliton in a spinor Bose-Einstein condensate (transient) | BEC | *Nature Phys.* 12, 478 | [10.1038/nphys3624](https://doi.org/10.1038/nphys3624) |
| 2017 | Ackerman & Smalyukh | Static 3D topological solitons in fluid chiral ferromagnets | Liquid crystal | *Nature Mater.* 16, 426 | [10.1038/nmat4826](https://doi.org/10.1038/nmat4826) |
| 2018 | Lee et al. | BEC quantum simulation whose synthetic field and current reproduce the knotted configuration of the Ranada-Trueba model (not evidence about real ball lightning) | BEC (synthetic EM fields) | *Sci. Adv.* 4, eaao3820 | [10.1126/sciadv.aao3820](https://doi.org/10.1126/sciadv.aao3820) |
| 2019 | Tai & Smalyukh | 3D crystals of adaptive knots (heliknotons) | Liquid crystal | *Science* 365, 1449 | [10.1126/science.aay1638](https://doi.org/10.1126/science.aay1638) |
| 2021 | Kent et al. | First magnetic hopfion in Ir/Co/Pt multilayers | Magnetic multilayer | *Nature Commun.* 12, 1562 | [10.1038/s41467-021-21846-5](https://doi.org/10.1038/s41467-021-21846-5) |
| 2021 | Sugic et al. | Optical skyrmionic hopfion (measured Skyrme number 0.945; ideal value 1) | Structured light | *Nature Commun.* 12, 6785 | [10.1038/s41467-021-26171-5](https://doi.org/10.1038/s41467-021-26171-5) |
| 2023 | Zheng et al. | First hopfion rings observed in a crystal (B20-type FeGe), coupled to skyrmion strings | Chiral magnet | *Nature* 623, 718 | [10.1038/s41586-023-06658-5](https://doi.org/10.1038/s41586-023-06658-5) |

These experimental milestones demonstrate that hopfion topology is physically realizable across multiple material platforms. They do not show that hopfion-type structures are stable in atmospheric plasma, where the stabilizing stiffness of these media is absent (Ch. 2.4).

---

## Appendix A — Projection Geometry of a Luminous Torus (added in v0.8)

**Model.** An optically thin torus with uniform emissivity, major radius R and minor radius a, viewed at inclination i (0° face-on, 90° edge-on). Random orientations are isotropic, so P(cos i ≥ c) = 1 − c. Script: [`analysis/torus_projection.py`](../../analysis/torus_projection.py).

**Silhouette.** The projected axis ratio is q(i) = (R cos i + a) / (R + a).

| R/a | Edge-on axis ratio | Fraction of view directions with q ≥ 0.85 | Central hole when face-on |
|---|---|---|---|
| 0.5 | 0.67 | 0.45 | no |
| 0.75 | 0.57 | 0.35 | no |
| 1.0 | 0.50 | 0.30 | no (pinch point) |
| 1.5 | 0.40 | 0.25 | yes |
| 2.0 | 0.33 | 0.23 | yes |
| 3.0 | 0.25 | 0.20 | yes |

**With emission and glow.** Line-of-sight-integrated emission, blurred by a Gaussian glow of width σ = f(R + a), measured at the 50%-of-peak contour:

| R/a | Glow f | Axis ratio q (face-on / 45° / edge-on) | Centre/peak brightness, face-on |
|---|---|---|---|
| 0.5 | 0 | 1.00 / 0.84 / 0.72 | 0.86 |
| 0.5 | 0.4 | 1.00 / 0.94 / 0.82 | 1.00 |
| 1.0 | 0 | 1.00 / 0.79 / 0.56 | 0.05 |
| 1.0 | 0.4 | 1.00 / 0.83 / 0.71 | 1.00 |
| 2.0 | 0 | 1.00 / 0.75 / 0.37 | 0.00 |
| 2.0 | 0.4 | 1.00 / 0.81 / 0.58 | 0.95 |

**Interpretation.** A ring-like torus (R ≥ a) stays visibly elongated edge-on even with a glow whose width is 40% of the torus's outer radius. Only a fat torus (R ≲ 0.5 a) inside a substantial glow looks nearly round (q ≳ 0.8) from every direction. If witness reports of round objects are accurate, the luminous body is at most a fat torus — essentially a sphere with toroidal internal structure, as in a spheromak — and the ring must be sought in its internal field and flow.

---

## References

### Ball Lightning Observations

[1] Cen, J., Yuan, P. & Xue, S. (2014). Observation of the optical and spectral characteristics of ball lightning. *Phys. Rev. Lett.* 112, 035001. DOI: [10.1103/PhysRevLett.112.035001](https://doi.org/10.1103/PhysRevLett.112.035001)

[2] Wang, H., Yuan, P., Cen, J. & Liu, G. (2018). Study on the luminous characteristics of a natural ball lightning. *Appl. Phys. Lett.* 112, 064103. DOI: [10.1063/1.5019318](https://doi.org/10.1063/1.5019318)

[3] Shmatov, M.L. & Stephan, K.D. (2019). Advances in ball lightning research. *J. Atmos. Sol.-Terr. Phys.* 195, 105115. DOI: [10.1016/j.jastp.2019.105115](https://doi.org/10.1016/j.jastp.2019.105115)

[4] Rayle, W.D. (1966). Ball lightning characteristics. NASA Technical Note TN D-3188. NTRS: [19660006027](https://ntrs.nasa.gov/citations/19660006027)

[5] Smirnov, B.M. (1987). The properties and the nature of ball lightning. *Phys. Rep.* 152, 177-226. DOI: [10.1016/0370-1573(87)90142-6](https://doi.org/10.1016/0370-1573(87)90142-6)

[6] Smirnov, B.M. (1993). Physics of ball lightning. *Phys. Rep.* 224, 151-236. DOI: [10.1016/0370-1573(93)90121-S](https://doi.org/10.1016/0370-1573(93)90121-S)

[7] Stenhoff, M. (1999). *Ball Lightning: An Unsolved Problem in Atmospheric Physics*. Kluwer Academic/Plenum. DOI: [10.1007/b115123](https://doi.org/10.1007/b115123)

### Electromagnetic Knot / Topological Ball Lightning Models

[8] Ranada, A.F. (1989). A topological theory of the electromagnetic field. *Lett. Math. Phys.* 18, 97-106. DOI: [10.1007/BF00401864](https://doi.org/10.1007/BF00401864)

[9] Ranada, A.F. (1990). Knotted solutions of the Maxwell equations in vacuum. *J. Phys. A* 23, L815-L820. DOI: [10.1088/0305-4470/23/16/007](https://doi.org/10.1088/0305-4470/23/16/007)

[10] Ranada, A.F. & Trueba, J.L. (1996). Ball lightning an electromagnetic knot? *Nature* 383, 32. DOI: [10.1038/383032a0](https://doi.org/10.1038/383032a0)

[11] Ranada, A.F., Soler, M. & Trueba, J.L. (1998). A model of ball lightning as a magnetic knot with linked streamers. *J. Geophys. Res.* 103, 23309-23313. DOI: [10.1029/98JD01539](https://doi.org/10.1029/98JD01539)

[12] Ranada, A.F., Soler, M. & Trueba, J.L. (2000). Ball lightning as a force-free magnetic knot. *Phys. Rev. E* 62, 7181-7190. DOI: [10.1103/PhysRevE.62.7181](https://doi.org/10.1103/PhysRevE.62.7181)

[13] Tsui, K.H. (2003). Ball lightning as a magnetostatic spherical force-free field plasmoid. *Phys. Plasmas* 10, 4112-4117. DOI: [10.1063/1.1605949](https://doi.org/10.1063/1.1605949)

### Competing Theoretical Models

[14] Abrahamson, J. & Dinniss, J. (2000). Ball lightning caused by oxidation of nanoparticle networks from normal lightning strikes on soil. *Nature* 403, 519-521. DOI: [10.1038/35000525](https://doi.org/10.1038/35000525)

[15] Lowke, J.J., Smith, D., Nelson, K.E., Crompton, R.W. & Murphy, A.B. (2012). Birth of ball lightning. *J. Geophys. Res.* 117, D19107. DOI: [10.1029/2012JD017921](https://doi.org/10.1029/2012JD017921)

### Hopfion Mathematics and Field Theory

[16] Hopf, H. (1931). Uber die Abbildungen der dreidimensionalen Sphare auf die Kugelflache. *Math. Ann.* 104, 637-665. DOI: [10.1007/BF01457962](https://doi.org/10.1007/BF01457962)

[17] Whitehead, J.H.C. (1947). An expression of Hopf's invariant as an integral. *PNAS* 33, 117-123. DOI: [10.1073/pnas.33.5.117](https://doi.org/10.1073/pnas.33.5.117)

[18] Faddeev, L. & Niemi, A.J. (1997). Stable knot-like structures in classical field theory. *Nature* 387, 58-61. DOI: [10.1038/387058a0](https://doi.org/10.1038/387058a0)

[19] Arrayas, M., Bouwmeester, D. & Trueba, J.L. (2017). Knots in electromagnetism. *Phys. Rep.* 667, 1-61. DOI: [10.1016/j.physrep.2016.11.001](https://doi.org/10.1016/j.physrep.2016.11.001)

[20] Irvine, W.T.M. & Bouwmeester, D. (2008). Linked and knotted beams of light. *Nature Phys.* 4, 716-720. DOI: [10.1038/nphys1056](https://doi.org/10.1038/nphys1056)

### MHD Topology and Magnetic Helicity

[21] Woltjer, L. (1958). A theorem on force-free magnetic fields. *PNAS* 44, 489-491. DOI: [10.1073/pnas.44.6.489](https://doi.org/10.1073/pnas.44.6.489)

[22] Moffatt, H.K. (1969). The degree of knottedness of tangled vortex lines. *J. Fluid Mech.* 35, 117-129. DOI: [10.1017/S0022112069000991](https://doi.org/10.1017/S0022112069000991)

[23] Taylor, J.B. (1974). Relaxation of toroidal plasma and generation of reverse magnetic fields. *Phys. Rev. Lett.* 33, 1139-1141. DOI: [10.1103/PhysRevLett.33.1139](https://doi.org/10.1103/PhysRevLett.33.1139)

[24] Taylor, J.B. (1986). Relaxation and magnetic reconnection in plasmas. *Rev. Mod. Phys.* 58, 741-763. DOI: [10.1103/RevModPhys.58.741](https://doi.org/10.1103/RevModPhys.58.741)

[25] Berger, M.A. & Field, G.B. (1984). The topological properties of magnetic helicity. *J. Fluid Mech.* 147, 133-148. DOI: [10.1017/S0022112084002019](https://doi.org/10.1017/S0022112084002019)

[26] Kamchatnov, A.M. (1982). Topological soliton in magnetohydrodynamics. *Sov. Phys. JETP* 55, 69-73. arXiv: [physics/0409093](https://arxiv.org/abs/physics/0409093)

### Experimental and Numerical Hopfion Realizations

[27] Smiet, C.B. et al. (2015). Self-organizing knotted magnetic structures in plasma. *Phys. Rev. Lett.* 115, 095001. DOI: [10.1103/PhysRevLett.115.095001](https://doi.org/10.1103/PhysRevLett.115.095001)

[28] Hall, D.S. et al. (2016). Tying quantum knots. *Nature Phys.* 12, 478-483. DOI: [10.1038/nphys3624](https://doi.org/10.1038/nphys3624)

[29] Lee, W. et al. (2018). Synthetic electromagnetic knot in a three-dimensional skyrmion. *Sci. Adv.* 4, eaao3820. DOI: [10.1126/sciadv.aao3820](https://doi.org/10.1126/sciadv.aao3820)

[30] Kent, N. et al. (2021). Creation and observation of Hopfions in magnetic multilayer systems. *Nature Commun.* 12, 1562. DOI: [10.1038/s41467-021-21846-5](https://doi.org/10.1038/s41467-021-21846-5)

[31] Sugic, D. et al. (2021). Particle-like topologies in light. *Nature Commun.* 12, 6785. DOI: [10.1038/s41467-021-26171-5](https://doi.org/10.1038/s41467-021-26171-5)

[32] Zheng, F. et al. (2023). Hopfion rings in a cubic chiral magnet. *Nature* 623, 718-723. DOI: [10.1038/s41586-023-06658-5](https://doi.org/10.1038/s41586-023-06658-5)

### Condensed Matter Hopfions

[33] Ackerman, P.J. & Smalyukh, I.I. (2017). Static three-dimensional topological solitons in fluid chiral ferromagnets and colloids. *Nature Mater.* 16, 426-432. DOI: [10.1038/nmat4826](https://doi.org/10.1038/nmat4826)

[34] Tai, J.-S.B. & Smalyukh, I.I. (2019). Three-dimensional crystals of adaptive knots. *Science* 365, 1449-1453. DOI: [10.1126/science.aay1638](https://doi.org/10.1126/science.aay1638)

[35] Rybakov, F.N. et al. (2022). Magnetic hopfions in solids. *APL Mater.* 10, 111113. DOI: [10.1063/5.0099942](https://doi.org/10.1063/5.0099942)

### Textbooks and Reviews

[36] Arnold, V.I. & Khesin, B.A. (2021). *Topological Methods in Hydrodynamics*. 2nd ed. Springer. DOI: [10.1007/978-3-030-74278-2](https://doi.org/10.1007/978-3-030-74278-2)

[37] Biskamp, D. (1993). *Nonlinear Magnetohydrodynamics*. Cambridge UP. DOI: [10.1017/CBO9780511599965](https://doi.org/10.1017/CBO9780511599965)

[38] Bellan, P.M. (2000). *Spheromaks: A Practical Application of Magnetohydrodynamic Dynamos and Plasma Self-Organization*. Imperial College Press. DOI: [10.1142/p121](https://doi.org/10.1142/p121)

### Added in v0.8

[39] Derrick, G.H. (1964). Comments on nonlinear wave equations as models for elementary particles. *J. Math. Phys.* 5, 1252-1254. DOI: [10.1063/1.1704233](https://doi.org/10.1063/1.1704233)

[40] Freidberg, J.P. (2014). *Ideal MHD*. Cambridge University Press.

[41] Rakov, V.A. & Uman, M.A. (2003). *Lightning: Physics and Effects*. Cambridge University Press.

[42] D'Angola, A. et al. (2008). Thermodynamic and transport properties in equilibrium air plasmas in a wide pressure and temperature range. *Eur. Phys. J. D* 46, 129-150. DOI: [10.1140/epjd/e2007-00305-4](https://doi.org/10.1140/epjd/e2007-00305-4)

[43] Spitzer, L. (1962). *Physics of Fully Ionized Gases*. 2nd ed. Interscience.

[44] Paiva, G.S., Pavão, A.C., de Vasconcelos, E.A., Mendes, O. Jr. & da Silva, E.F. Jr. (2007). Production of ball-lightning-like luminous balls by electrical discharges in silicon. *Phys. Rev. Lett.* 98, 048501. DOI: [10.1103/PhysRevLett.98.048501](https://doi.org/10.1103/PhysRevLett.98.048501)

[45] Smirnov, B.M. (1992). Observational properties of ball lightning. *Sov. Phys. Usp.* 35, 650-670. DOI: [10.1070/PU1992v035n08ABEH002254](https://doi.org/10.1070/PU1992v035n08ABEH002254)

[46] An, T., Yuan, P., Cen, J., Xue, S., Wan, R. & Deng, H. (2022). Temperature of apparent natural ball lightning obtained by examination of the spectra. *Phys. Plasmas* 29, 113503. DOI: [10.1063/5.0098329](https://doi.org/10.1063/5.0098329)

[47] Keul, A.G. (1999). Two exceptional ball lightning cases. *J. Meteorol. (UK)* 24, 178-179.

[48] Johnson, P.O. (1965). Ball lightning and self-containing electromagnetic fields. *Am. J. Phys.* 33, 119-123. DOI: [10.1119/1.1971261](https://doi.org/10.1119/1.1971261)

[49] Koloc, P.M. (1999). Some results of artificially produced ball lightning formation in atmospheric air. *IEEE ICOPS'99 Abstracts*, p. 191. DOI: [10.1109/PLASMA.1999.829470](https://doi.org/10.1109/PLASMA.1999.829470)

[50] Seward, C. (1997). Compact toroidal properties compared to ball lightning. *IEEE ICOPS'97 Abstracts*, pp. 320-321. DOI: [10.1109/PLASMA.1997.605182](https://doi.org/10.1109/PLASMA.1997.605182)

[51] Versteegh, A., Behringer, K., Fantz, U., Fussmann, G., Jüttner, B. & Noack, S. (2008). Long-living plasmoids from an atmospheric water discharge. *Plasma Sources Sci. Technol.* 17, 024014. DOI: [10.1088/0963-0252/17/2/024014](https://doi.org/10.1088/0963-0252/17/2/024014)

[52] Dikhtyar, V. & Jerby, E. (2006). Fireball ejection from a molten hot spot to air by localized microwaves. *Phys. Rev. Lett.* 96, 045002. DOI: [10.1103/PhysRevLett.96.045002](https://doi.org/10.1103/PhysRevLett.96.045002)

[53] Peer, J. & Kendl, A. (2010). Transcranial stimulability of phosphenes by long lightning electromagnetic pulses. *Phys. Lett. A* 374, 2932-2935. DOI: [10.1016/j.physleta.2010.05.023](https://doi.org/10.1016/j.physleta.2010.05.023)

[54] Peer, J., Cooray, V., Cooray, G. & Kendl, A. (2010). Erratum and addendum to "Transcranial stimulability of phosphenes by long lightning electromagnetic pulses". *Phys. Lett. A* 374, 4797-4799. DOI: [10.1016/j.physleta.2010.09.071](https://doi.org/10.1016/j.physleta.2010.09.071)

[55] Ivanov, K.G. & Harshiladze, A.F. (1985). Interplanetary hydromagnetic clouds as flare-generated spheromaks. *Solar Phys.* 98, 379-386. DOI: [10.1007/BF00152467](https://doi.org/10.1007/BF00152467)
