"""
Figure 2 audit -- Phases 2,3,4,5,6,8 combined single-process script.
Read-mostly: reads existing stored CSVs, replays event 65's trajectory
via the UNMODIFIED existing integrator (single process, no multiprocessing),
and writes ONLY into FIGURE2_ROOT_AUDIT_2026-09-30/.
Run with: nice -n 19 <hep-python> phase2to8_audit.py
"""
import sys, os, json
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
import trajectory_to_hits as tth
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
tth.integrate_trajectory = integrate_trajectory_fast_v2

BASE = "/home/rafia/coplanarity_study"
SRC = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
OUT = f"{BASE}/05_coplanarity_analysis/FIGURE2_ROOT_AUDIT_2026-09-30"
HBARC_GEV_CM = 1.973269804e-14  # hbar*c in GeV*cm (== CM_PER_NATURAL used by project code)
EVENT_IDX = 65

recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/colored_1800GeV_L2keV/per_event_results.csv")
trig = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")

rrow = recon[recon["event_idx"] == EVENT_IDX].iloc[0]
row = trig.iloc[EVENT_IDX]
seed = int(rrow["seed"])
assert seed == 2123515583, f"seed mismatch: {seed}"

# ---- Phase 1 support: save the exact original input row, unaltered ----
orig_row_df = pd.DataFrame([row])
orig_row_df.insert(0, "source_file", "trigger_passing_events.csv")
orig_row_df.to_csv(f"{OUT}/EVENT65_ORIGINAL_INPUT_ROW.csv", index=False)

# ==================== PHASE 2: initial kinematics ====================
mass_gev = 1800.0
Lambda_gev = 2e-6
B_tesla = 2.0
charge1 = float(row["charge1"]); charge2 = float(row["charge2"])

p1 = np.array([row["px1"], row["py1"], row["pz1"]], dtype=float)
p2 = np.array([row["px2"], row["py2"], row["pz2"]], dtype=float)
E1_supplied = float(row["E1"]); E2_supplied = float(row["E2"])
E1_onshell = np.sqrt(np.dot(p1, p1) + mass_gev**2)
E2_onshell = np.sqrt(np.dot(p2, p2) + mass_gev**2)

P_total = p1 + p2
E_total_supplied = E1_supplied + E2_supplied
E_total_onshell = E1_onshell + E2_onshell
inv_mass_supplied = np.sqrt(max(E_total_supplied**2 - np.dot(P_total, P_total), 0.0))
inv_mass_onshell = np.sqrt(max(E_total_onshell**2 - np.dot(P_total, P_total), 0.0))
pT_pair = np.hypot(P_total[0], P_total[1])

beta_cm_vec = P_total / E_total_onshell
beta_cm2 = np.dot(beta_cm_vec, beta_cm_vec)
gamma_cm = 1.0 / np.sqrt(max(1.0 - beta_cm2, 1e-15))
beta_hat = beta_cm_vec / np.sqrt(beta_cm2)

p1_par = np.dot(p1, beta_hat)
p1_perp = p1 - p1_par * beta_hat
beta_cm_mag = np.sqrt(beta_cm2)
p1_par_cm = gamma_cm * (p1_par - beta_cm_mag * E1_onshell)
E1_cm = gamma_cm * (E1_onshell - beta_cm_mag * p1_par)
p1_cm_3vec = p1_perp + p1_par_cm * beta_hat
v_int = np.linalg.norm(p1_cm_3vec) / E1_cm
gamma_int = E1_cm / mass_gev

kinem = {
    "event_idx": EVENT_IDX, "seed": seed,
    "px1_gev": p1[0], "py1_gev": p1[1], "pz1_gev": p1[2],
    "E1_supplied_gev": E1_supplied, "E1_onshell_gev": E1_onshell,
    "m1_supplied_gev": float(row["m1"]), "mass_used_in_integrator_gev": mass_gev,
    "px2_gev": p2[0], "py2_gev": p2[1], "pz2_gev": p2[2],
    "E2_supplied_gev": E2_supplied, "E2_onshell_gev": E2_onshell,
    "m2_supplied_gev": float(row["m2"]),
    "charge1": charge1, "charge2": charge2,
    "pair_px_gev": P_total[0], "pair_py_gev": P_total[1], "pair_pz_gev": P_total[2],
    "pair_E_supplied_gev": E_total_supplied, "pair_E_onshell_gev": E_total_onshell,
    "pair_pT_gev": pT_pair,
    "pair_invmass_supplied_gev": inv_mass_supplied,
    "pair_invmass_onshell_gev": inv_mass_onshell,
    "beta_cm_x": beta_cm_vec[0], "beta_cm_y": beta_cm_vec[1], "beta_cm_z": beta_cm_vec[2],
    "beta_cm_mag": beta_cm_mag, "gamma_cm": gamma_cm,
    "v_internal_cm_frame": v_int, "gamma_internal_cm_frame": gamma_int,
    "Lambda_gev": Lambda_gev, "B_tesla": B_tesla,
}
pd.DataFrame([kinem]).to_csv(f"{OUT}/EVENT65_INITIAL_KINEMATICS.csv", index=False)
print("Phase 2 kinematics written.")
print(f"  E1: supplied={E1_supplied:.6f} onshell={E1_onshell:.6f} rel_diff={abs(E1_supplied-E1_onshell)/E1_onshell:.3e}")
print(f"  E2: supplied={E2_supplied:.6f} onshell={E2_onshell:.6f} rel_diff={abs(E2_supplied-E2_onshell)/E2_onshell:.3e}")
print(f"  pair invmass supplied={inv_mass_supplied:.3f} onshell={inv_mass_onshell:.3f} pT={pT_pair:.3f}")
print(f"  beta_cm_mag={beta_cm_mag:.6f} gamma_cm={gamma_cm:.6f} v_int={v_int:.6f} gamma_int={gamma_int:.6f}")

# ==================== PHASE 8: independent regeneration ====================
rng = np.random.default_rng(seed)
p1_4 = (row["px1"], row["py1"], row["pz1"], row["E1"])
p2_4 = (row["px2"], row["py2"], row["pz2"], row["E2"])
hits, traj = tth.simulate_quirk_hits(p1_4, p2_4, mass_gev=1800.0, Lambda_gev=2e-6, B_tesla=2.0,
    charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0)

x1 = traj["x1"]; x2 = traj["x2"]; p1a = traj["p1"]; p2a = traj["p2"]; t_arr = traj["t_gev_inv"]
n = len(t_arr)
print(f"Regenerated trajectory: {n} steps")

x1_cm = x1 * HBARC_GEV_CM
x2_cm = x2 * HBARC_GEV_CM
xcm_cm = 0.5 * (x1_cm + x2_cm)
r_cm_new = np.linalg.norm(xcm_cm, axis=1)
d_cm_new = np.linalg.norm(x1_cm - x2_cm, axis=1)

# ---- ORIGINAL project formula (as in replay_figure2_colored_event65.py) ----
rel_x_natural = x1 - x2
rel_p = 0.5 * (p1a - p2a)
Lvec_orig = np.cross(rel_x_natural, rel_p)
L_hbar_orig = np.linalg.norm(Lvec_orig, axis=1)

# ---- INDEPENDENT from-scratch recomputation (Phase 3/4): explicit r1,r2,
#      per-particle CM-relative positions and FULL (not halved) lab momenta,
#      summing L1+L2 directly -- genuinely different code path from the
#      project's shortcut formula, to test the algebraic identity claimed
#      in the task brief.
R_cm_particle_avg = 0.5 * (x1 + x2)          # natural units (GeV^-1)
r1_rel = x1 - R_cm_particle_avg               # quirk-1 position relative to pair CM
r2_rel = x2 - R_cm_particle_avg               # quirk-2 position relative to pair CM
L1_vec = np.cross(r1_rel, p1a)                # L1 = r1 x p1 (lab momentum)
L2_vec = np.cross(r2_rel, p2a)                # L2 = r2 x p2 (lab momentum)
Ltot_vec_indep = L1_vec + L2_vec
L_hbar_indep = np.linalg.norm(Ltot_vec_indep, axis=1)

max_abs_diff_L = np.max(np.abs(L_hbar_indep - L_hbar_orig))
max_rel_diff_L = np.max(np.abs(L_hbar_indep - L_hbar_orig) / np.maximum(L_hbar_orig, 1e-30))
print(f"Independent-vs-original |L| max abs diff = {max_abs_diff_L:.3e}, max rel diff = {max_rel_diff_L:.3e}")

# signed component along z (dominant axis since B is along z and pair is
# roughly transverse-oscillating) -- also report full 3-vector components.
Lx = Lvec_orig[:, 0]; Ly = Lvec_orig[:, 1]; Lz = Lvec_orig[:, 2]

# ==================== PHASE 5: full timeseries export ====================
mask22 = r_cm_new <= 22.0
ts_df = pd.DataFrame({
    "step_index": np.arange(n)[mask22],
    "t_gev_inv": t_arr[mask22],
    "r_cm": r_cm_new[mask22],
    "x1_natural_x": x1[mask22, 0], "x1_natural_y": x1[mask22, 1], "x1_natural_z": x1[mask22, 2],
    "x2_natural_x": x2[mask22, 0], "x2_natural_y": x2[mask22, 1], "x2_natural_z": x2[mask22, 2],
    "p1_x": p1a[mask22, 0], "p1_y": p1a[mask22, 1], "p1_z": p1a[mask22, 2],
    "p2_x": p2a[mask22, 0], "p2_y": p2a[mask22, 1], "p2_z": p2a[mask22, 2],
    "d_cm": d_cm_new[mask22],
    "Lx_hbar": Lx[mask22], "Ly_hbar": Ly[mask22], "Lz_hbar": Lz[mask22],
    "L_abs_hbar_original_formula": L_hbar_orig[mask22],
    "L_abs_hbar_independent_formula": L_hbar_indep[mask22],
})
ts_df.to_csv(f"{OUT}/EVENT65_FULL_TIMESERIES.csv", index=False)
print(f"Phase 5 timeseries written: {len(ts_df)} rows (r<=22cm displayed range)")

# Monotonicity check of r_cm over displayed range
r_disp = ts_df["r_cm"].values
is_monotonic = np.all(np.diff(r_disp) >= -1e-12)
n_decreasing_steps = np.sum(np.diff(r_disp) < -1e-12)
print(f"r_cm monotonic over displayed range: {is_monotonic}; # decreasing steps: {n_decreasing_steps}/{len(r_disp)-1}")

# ==================== PHASE 6: zeros & extrema ====================
Lz_disp = ts_df["Lz_hbar"].values
Labs_disp = ts_df["L_abs_hbar_original_formula"].values
d_disp = ts_df["d_cm"].values
r_disp2 = ts_df["r_cm"].values
t_disp = ts_df["t_gev_inv"].values

def find_sign_changes(y):
    s = np.sign(y)
    idx = np.where(np.diff(s) != 0)[0]
    return idx

def find_local_extrema(y):
    idx = np.where((np.diff(np.sign(np.diff(y))) != 0))[0] + 1
    return idx

zero_idx_signedL = find_sign_changes(Lz_disp)
extrema_idx_absL = find_local_extrema(Labs_disp)
extrema_idx_d = find_local_extrema(d_disp)

rows = []
for i in zero_idx_signedL:
    rows.append({"kind": "signed_Lz_zero_crossing", "step_index": int(i),
                 "r_cm": r_disp2[i], "t_gev_inv": t_disp[i],
                 "Lz_hbar": Lz_disp[i], "Labs_hbar": Labs_disp[i], "d_cm": d_disp[i]})
for i in extrema_idx_absL:
    rows.append({"kind": "Labs_local_extremum", "step_index": int(i),
                 "r_cm": r_disp2[i], "t_gev_inv": t_disp[i],
                 "Lz_hbar": Lz_disp[i], "Labs_hbar": Labs_disp[i], "d_cm": d_disp[i]})
for i in extrema_idx_d:
    rows.append({"kind": "d_local_extremum", "step_index": int(i),
                 "r_cm": r_disp2[i], "t_gev_inv": t_disp[i],
                 "Lz_hbar": Lz_disp[i], "Labs_hbar": Labs_disp[i], "d_cm": d_disp[i]})

extrema_df = pd.DataFrame(rows).sort_values(["kind", "step_index"])
extrema_df.to_csv(f"{OUT}/EVENT65_L_ZERO_AND_EXTREMA_TABLE.csv", index=False)
print(f"Phase 6: {len(zero_idx_signedL)} signed-Lz zero-crossings, "
      f"{len(extrema_idx_absL)} |L| extrema, {len(extrema_idx_d)} d extrema (displayed range)")

# ==================== PHASE 4: paper Eq.6-7 comparison ====================
e_charge = 0.30282212  # matches project's e_charge_natural default
v_cm = beta_cm_mag
v = v_int
gamma_paper = gamma_int
mQ = mass_gev
Lam = Lambda_gev
B = B_tesla
# Eq.6: L ~ e * v_cm * gamma_cm * v * gamma * (gamma-1) * mQ^2 * B / Lambda^4
L_eq6_natural = e_charge * v_cm * gamma_cm * v * gamma_paper * (gamma_paper - 1) * mQ**2 * B / Lam**4
TESLA_TO_GEV2 = 1.9535e-16
L_eq6_natural_Bconverted = e_charge * v_cm * gamma_cm * v * gamma_paper * (gamma_paper - 1) * mQ**2 * (B * TESLA_TO_GEV2) / Lam**4
# Eq.7: L ~ 1e12 hbar * (v_cm * v^3 / 0.1) * (2keV/Lambda)^4 * (mQ/1.8TeV)^2 * (B/2T)
L_eq7 = 1e12 * (v_cm * v**3 / 0.1) * (2e-6 / Lam)**4 * (mQ / 1800.0)**2 * (B / 2.0)

L_numeric_max = np.max(L_hbar_orig)  # over full integrated range (not just r<=22cm display window)
L_numeric_max_displayed = np.max(Labs_disp)

paper_compare = {
    "v_internal_cm_frame": v, "v_cm_boost": v_cm, "gamma_internal": gamma_paper, "gamma_cm": gamma_cm,
    "mQ_gev": mQ, "Lambda_gev": Lam, "B_tesla": B,
    "L_eq6_natural_units_B_in_tesla_UNCONVERTED": L_eq6_natural,
    "L_eq6_with_B_converted_to_GeV2_TESLA_TO_GEV2": L_eq6_natural_Bconverted,
    "L_eq7_paper_numeric_estimate_hbar": L_eq7,
    "L_numeric_max_over_full_trajectory_hbar": L_numeric_max,
    "L_numeric_max_over_displayed_r22cm_hbar": L_numeric_max_displayed,
    "ratio_numeric_max_full_over_Eq7": L_numeric_max / L_eq7,
    "ratio_numeric_max_displayed_over_Eq7": L_numeric_max_displayed / L_eq7,
}
pd.DataFrame([paper_compare]).to_csv(f"{OUT}/EVENT65_PAPER_EQ6_EQ7_COMPARISON.csv", index=False)
print("Phase 4 paper-formula comparison:")
for k, v_ in paper_compare.items():
    print(f"  {k} = {v_}")

# ==================== PHASE 8 CSV export + comparison to original ====================
regen_df = pd.DataFrame({
    "r_cm": r_cm_new[mask22], "L_hbar": L_hbar_orig[mask22], "d_cm": d_cm_new[mask22],
})
regen_df.to_csv(f"{OUT}/EVENT65_ROOT_RECOMPUTED_VALUES.csv", index=False)

orig_csv = pd.read_csv(f"{SRC}/SOURCE_DATA/FIGURE_2_2000event_colored_event65_source.csv")
print(f"\nPhase 8 comparison: original rows={len(orig_csv)}, regenerated rows={len(regen_df)}")
if len(orig_csv) == len(regen_df):
    for col in ["r_cm", "L_hbar", "d_cm"]:
        diff = np.abs(orig_csv[col].values - regen_df[col].values)
        rel = diff / np.maximum(np.abs(orig_csv[col].values), 1e-300)
        first_div = np.argmax(diff > 1e-9) if np.any(diff > 1e-9) else -1
        print(f"  {col}: max_abs_diff={diff.max():.3e} max_rel_diff={rel.max():.3e} "
              f"bit_identical={(diff.max()==0.0)} first_divergent_row={first_div}")
else:
    print("  ROW COUNT MISMATCH -- cannot do direct point-by-point comparison; investigate.")

print("\nDONE Phase 2/3/4/5/6/8 script.")

# ==================== Extra: period accounting for the Eq.6 vs Eq.7 gap ====================
period_est = 2.0 * v_int * gamma_int * mass_gev / (Lambda_gev ** 2)
t_at_max_L_full = t_arr[np.argmax(L_hbar_orig)]
t_at_r22 = t_disp[-1] if len(t_disp) else np.nan
n_periods_to_max_L = t_at_max_L_full / period_est
n_periods_to_r22 = t_at_r22 / period_est
L_eq6_times_Nperiods = L_eq6_natural_Bconverted * n_periods_to_r22
L_eq7_times_Nperiods = L_eq7 * n_periods_to_r22

extra = {
    "period_est_gev_inv": period_est,
    "t_at_max_L_gev_inv": t_at_max_L_full,
    "t_at_r22cm_gev_inv": t_at_r22,
    "n_oscillation_periods_elapsed_to_max_L": n_periods_to_max_L,
    "n_oscillation_periods_elapsed_to_r22cm": n_periods_to_r22,
    "L_eq6_times_N_periods_to_r22": L_eq6_times_Nperiods,
    "L_eq7_times_N_periods_to_r22": L_eq7_times_Nperiods,
    "ratio_numeric_max_over_[Eq7_times_Nperiods]": L_numeric_max_displayed / L_eq7_times_Nperiods,
}
print("\n--- Period accounting for Eq6/7 gap ---")
for k, v_ in extra.items():
    print(f"  {k} = {v_}")

# merge into the comparison CSV
cmp_df = pd.read_csv(f"{OUT}/EVENT65_PAPER_EQ6_EQ7_COMPARISON.csv")
for k, v_ in extra.items():
    cmp_df[k] = v_
cmp_df.to_csv(f"{OUT}/EVENT65_PAPER_EQ6_EQ7_COMPARISON.csv", index=False)
