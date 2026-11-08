"""Order-of-magnitude self-consistency checks for the Hopfion (Ring) Lightning Hypothesis (v0.8, Ch. 6A and 8A).

Standard library only. Run: python3 analysis/self_consistency.py

All inputs are stated explicitly. The weakly ionized conductivity estimates (3,000-6,000 K) are
order-of-magnitude only: Saha equilibrium for NO (assumed 3 % of molecules) plus 1 ppm sodium, with
electron-neutral collisions (cross-section 1e-19 m^2). The 1e4 K and 2e4 K conductivities are round
values for equilibrium air at 1 atm from tabulated transport data.
"""
import math

MU0 = 4e-7 * math.pi
KB = 1.380649e-23
E = 1.602176634e-19
ME = 9.1093837e-31
P_ATM = 101325.0
R_GAS = 8.314
M_AIR = 0.029

R_BALL = 0.125           # m, 25 cm diameter reference body
V_BALL = 4 / 3 * math.pi * R_BALL**3
T_CORE = 4200.0          # K, measured ball-lightning temperature quoted in the hypothesis
L_SCALE = 0.1            # m, field gradient scale used for decay times


def header(title):
    print("\n" + title)
    print("-" * len(title))


def main():
    rho_in = P_ATM * M_AIR / (R_GAS * T_CORE)
    rho_out = P_ATM * M_AIR / (R_GAS * 293.0)
    mass = rho_in * V_BALL

    header("Reference body")
    print(f"volume = {V_BALL:.3e} m^3, density = {rho_in:.4f} kg/m^3 ({rho_in / rho_out:.1%} of ambient), mass = {mass * 1e3:.2f} g")

    header("8A.2 Energy budget")
    for b in (0.01, 0.05, 0.10):
        u = b**2 / (2 * MU0)
        print(f"B = {b * 1e3:5.0f} mT: magnetic energy = {u * V_BALL:7.2f} J, magnetic pressure = {u / P_ATM:.1e} atm, beta(total) = {P_ATM / u:7.0f}")
    for e_tot in (8e3, 80e3):
        b = math.sqrt(2 * MU0 * e_tot / V_BALL)
        print(f"field needed to store {e_tot / 1e3:.0f} kJ magnetically: {b:.2f} T (magnetic pressure {b**2 / 2 / MU0 / P_ATM:.0f} atm)")
    sensible = mass * 1250.0 * (T_CORE - 293.0)
    o2_dissociation = mass * 0.232 * (5.12 * E / (0.032 / 6.02214076e23))
    print(f"sensible enthalpy above ambient ~ {sensible:.0f} J; O2 dissociation (if complete) <= {o2_dissociation:.0f} J")

    header("8A.2 Buoyancy")
    cd = 0.5
    v_rise = math.sqrt(8 / 3 * 9.81 * R_BALL * (rho_out - rho_in) / (rho_out * cd))
    print(f"terminal rise speed of a pressure-balanced {T_CORE:.0f} K body (Cd = {cd}): {v_rise:.1f} m/s")

    header("8A.3 Rotation vs field")
    c_ambient = math.sqrt(1.4 * R_GAS * 293.0 / M_AIR)
    print(f"sound speed in ambient air = {c_ambient:.0f} m/s")
    for b in (0.01, 0.05, 0.10):
        print(f"B = {b * 1e3:5.0f} mT: Alfven speed (total density) = {b / math.sqrt(MU0 * rho_in):5.0f} m/s, rotational KE at v_A = {0.5 * mass * b**2 / (MU0 * rho_in):5.1f} J")
    for v in (500.0, 1000.0, 2000.0):
        p_cf = rho_in * v**2
        print(f"v = {v:6.0f} m/s: rho v^2 = {p_cf / P_ATM:.2f} atm = {p_cf / (0.1**2 / 2 / MU0):.0f} x magnetic pressure at 100 mT; "
              f"B for balance = {math.sqrt(2 * MU0 * p_cf):.2f} T; KE = {0.5 * mass * v**2:.0f} J")
    print(f"rim speed implied by v0.7's L = 1e-3 kg m^2/s at R = 0.1 m: {1e-3 / (mass * 0.1):.0f} m/s")

    header("8A.1 Resistive decay")

    def saha_ne(t, n_species, ion_ev):
        s = 2.415e21 * t**1.5 * math.exp(-ion_ev * E / (KB * t))
        return (-s + math.sqrt(s * s + 4 * s * n_species)) / 2

    def sigma_weak(ne, nn, t, cross=1e-19):
        v_th = math.sqrt(8 * KB * t / (math.pi * ME))
        return ne * E**2 / (ME * nn * cross * v_th)

    rows = []
    for t in (3000.0, 4200.0, 6000.0):
        n = P_ATM / (KB * t)
        ne = saha_ne(t, 0.03 * n, 9.26) + saha_ne(t, 1e-6 * n, 5.14)
        rows.append((f"{t:.0f} K (estimate, x_e = {ne / n:.0e})", sigma_weak(ne, n, t)))
    rows += [("1e4 K (tabulated equilibrium air)", 3e3), ("2e4 K (tabulated equilibrium air)", 1e4)]
    for label, sigma in rows:
        eta = 1 / (MU0 * sigma)
        print(f"{label:38s}: sigma ~ {sigma:8.2g} S/m, eta_m ~ {eta:8.2g} m^2/s, tau_eta(L = {L_SCALE} m) ~ {L_SCALE**2 / eta:.1e} s")
    sigma_needed = 5.0 / (MU0 * L_SCALE**2)
    print(f"conductivity needed for tau_eta = 5 s at L = {L_SCALE} m (crude): {sigma_needed:.1e} S/m ({sigma_needed / 5.96e7:.0f} x copper)")
    # lowest free-decay mode of a conducting sphere: field e-folds in mu0 sigma a^2/(ka)^2, energy/helicity in half that
    for ka, label in ((math.pi, "dipole mode, ka = pi"), (4.493, "force-free mode, ka = 4.49")):
        sigma_mode = 5.0 * 2 * ka**2 / (MU0 * R_BALL**2)
        t_copper = MU0 * 5.96e7 * R_BALL**2 / ka**2 / 2
        print(f"{label}: sigma for 5 s energy e-fold = {sigma_mode:.1e} S/m ({sigma_mode / 5.96e7:.0f} x copper); "
              f"solid copper ball of radius {R_BALL} m: energy e-folds in {t_copper * 1e3:.0f} ms")
    for t in (1e4, 1e5):
        t_ev = KB * t / E
        eta_res = 5.2e-5 * 10 / t_ev**1.5  # Spitzer, ln(Lambda) = 10
        print(f"Spitzer, T = {t:.0e} K: eta_m = {eta_res / MU0:.1f} m^2/s, tau_eta = {L_SCALE**2 / (eta_res / MU0):.1e} s")
    for v in (1.0, 300.0):
        for eta in (80.0, 1e5):
            print(f"Rm (v = {v:.0f} m/s, L = {L_SCALE} m, eta_m = {eta:.0e} m^2/s) = {v * L_SCALE / eta:.1e}")

    header("6A Helicity injection")
    phi = 0.05 * math.pi * R_BALL**2
    print(f"flux of a 50 mT, R = {R_BALL} m body: {phi:.2e} Wb -> required helicity ~ Phi^2 = {phi**2:.1e} Wb^2")
    b_geo, r_tube, current, length, ln_ratio = 50e-6, 0.15, 3e4, 0.3, math.log(10)
    phi_ax = b_geo * math.pi * r_tube**2
    phi_az = MU0 * current / (2 * math.pi) * length * ln_ratio
    h_geo = 2 * phi_ax * phi_az
    print(f"geomagnetic mutual helicity ~ 2 Phi_ax Phi_az = 2 x {phi_ax:.1e} x {phi_az:.1e} = {h_geo:.1e} Wb^2 ({phi**2 / h_geo:.0f} x too small)")

    header("Ch. 10 Observables")
    for b in (0.01, 0.10):
        print(f"Zeeman splitting (g = 1, 600 nm) at {b * 1e3:.0f} mT: {4.67e-13 * 6000**2 * b * 1e4 * 0.1:.1e} nm")
    for v in (30.0, 300.0):
        print(f"Doppler shift at 600 nm for {v:.0f} m/s: {600 * v / 2.998e8:.1e} nm")
    for r in (0.5, 1.0, 2.0):
        print(f"dipole field at {r} m from a body with 50 mT at its surface: {0.05 * (R_BALL / r)**3 * 1e6:.0f} uT")


if __name__ == "__main__":
    main()
