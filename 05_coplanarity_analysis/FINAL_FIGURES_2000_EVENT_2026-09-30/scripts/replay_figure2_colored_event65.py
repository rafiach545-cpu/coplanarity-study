"""
Figure 2 (fresh 2000-event version): replay a REAL selected event from the
fresh Colored 2000-event sample (not a synthetic/hand-tuned trajectory).
Selection criterion (declared, reproducible): fastest-converging
(smallest recorded wall_time_s) event among the 12 corrected
fiducial-AND-plane-found colored events. Deterministic replay from
stored seed/momenta -- not new event generation.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
import trajectory_to_hits as tth
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
tth.integrate_trajectory = integrate_trajectory_fast_v2

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
CM_PER_NATURAL = 1.973269804e-14

EVENT_IDX = 65  # declared selection: fastest wall_time_s among 12 fid&plane colored events
recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/colored_1800GeV_L2keV/per_event_results.csv")
trig = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")

rrow = recon[recon["event_idx"] == EVENT_IDX].iloc[0]
row = trig.iloc[EVENT_IDX]
seed = int(rrow["seed"])
print(f"Selected event_idx={EVENT_IDX}, seed={seed}, stored wall_time_s={rrow['wall_time_s']}")

rng = np.random.default_rng(seed)
p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
hits, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=1800.0, Lambda_gev=2e-6, B_tesla=2.0,
    charge1=float(row["charge1"]), charge2=float(row["charge2"]), rng=rng, max_layer_r_cm=60.0)

x1_cm = traj["x1"] * CM_PER_NATURAL
x2_cm = traj["x2"] * CM_PER_NATURAL
p1_arr = traj["p1"]
p2_arr = traj["p2"]

xcm = 0.5 * (x1_cm + x2_cm)
r_cm_cm = np.linalg.norm(xcm, axis=1)
rel_x = x1_cm - x2_cm
d_cm = np.linalg.norm(rel_x, axis=1)
rel_p = 0.5 * (p1_arr - p2_arr)
# L must use natural-unit positions (GeV^-1) for cross product with momentum (GeV) to be
# dimensionless (hbar units) -- use traj["x1"]/traj["x2"] (natural units), not x1_cm/x2_cm
rel_x_natural = traj["x1"] - traj["x2"]
Lvec = np.cross(rel_x_natural, rel_p)
L_hbar = np.linalg.norm(Lvec, axis=1)

# restrict to the valid, physically meaningful range: up to where the trajectory was
# actually integrated for detector purposes (r_cm up to ~20-25cm covers paper's display range)
mask = r_cm_cm <= 22.0
out = pd.DataFrame({
    "r_cm": r_cm_cm[mask], "L_hbar": L_hbar[mask], "d_cm": d_cm[mask],
})
out.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_2_2000event_colored_event{EVENT_IDX}_source.csv", index=False)

n_near_origin = (d_cm[mask] < 1e-6).sum()
print(f"rows saved: {len(out)}, r range [{out['r_cm'].min():.3f},{out['r_cm'].max():.3f}] cm")
print(f"d vanishes (< 1e-6 cm) at {n_near_origin} points (expect only near r=0)")
print(f"d range: [{out['d_cm'].min():.4e}, {out['d_cm'].max():.4e}] cm")
print(f"L range: [{out['L_hbar'].min():.4e}, {out['L_hbar'].max():.4e}] hbar")

meta = {
    "event_idx": EVENT_IDX, "seed": seed, "mQ_GeV": 1800.0, "Lambda_GeV": 2e-6, "B_tesla": 2.0,
    "selection_criterion": "fastest-converging (smallest wall_time_s) among the 12 corrected fiducial-AND-plane-found colored events",
    "sample": "fresh Colored 2000-event (quirk_2000_event_fresh_regeneration_v1)",
    "label": "representative project event -- NOT a claimed exact reproduction of the paper's own (unpublished) representative event",
}
import json
with open(f"{OUT}/SOURCE_DATA/FIGURE_2_2000event_metadata.json", "w") as f:
    json.dump(meta, f, indent=2)
print("DONE")
