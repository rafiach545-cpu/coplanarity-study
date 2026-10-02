import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
import trajectory_to_hits as tth
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
tth.integrate_trajectory = integrate_trajectory_fast_v2
from coplanarity_fit import seeding_and_iterative_fit, select_reconstructed_plane, vertex_relative_hits, check_hit_multiplicity, apply_signal_region_cuts

LAYER_NAME_TO_IDX = {'L1_IBL':1,'L2_PixelB0':2,'L3_PixelB1':3,'L4_PixelB2':4,'L5_SCT_B3':5,'L6_SCT_B4':6,'L7_SCT_B5':7,'L8_SCT_B6':8}
BASE = "/home/rafia/coplanarity_study"
EVENT_IDX = 65

trig = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv")
recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/colored_1800GeV_L2keV/per_event_results.csv")
row = trig.iloc[EVENT_IDX]
rrow = recon[recon["event_idx"]==EVENT_IDX].iloc[0]
seed = int(rrow["seed"])
rng = np.random.default_rng(seed)
p1 = (row["px1"],row["py1"],row["pz1"],row["E1"])
p2 = (row["px2"],row["py2"],row["pz2"],row["E2"])
hits, traj = tth.simulate_quirk_hits(p1,p2,mass_gev=1800.0,Lambda_gev=2e-6,B_tesla=2.0,
    charge1=float(row["charge1"]),charge2=float(row["charge2"]),rng=rng,max_layer_r_cm=60.0)
merged = tth.merge_neighboring_pixel_hits(hits)
vertex_cm = traj["vertex_cm"]
hits_by_layer = {k: [] for k in range(1,9)}
rows=[]
for h in merged:
    hx,hy,hz = vertex_relative_hits([(h["x"],h["y"],h["z"])], vertex_cm)[0]
    li = LAYER_NAME_TO_IDX[h["layer"]]
    hits_by_layer[li].append((hx,hy,hz))
    rows.append({"layer_idx":li,"layer":h["layer"],"x_vtxrel":hx,"y_vtxrel":hy,"z_vtxrel":hz})
candidates = seeding_and_iterative_fit(hits_by_layer)
winner = select_reconstructed_plane(candidates)
hit_mult_pass = check_hit_multiplicity(winner["layers"]) if winner else False
secIV_winner = apply_signal_region_cuts(candidates)
df = pd.DataFrame(rows)
df.to_csv(f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30/SOURCE_DATA/FIGURE_4_colored_hits.csv", index=False)
print("saved", len(df), "hits")
print("winner ds,dw:", winner["fit"]["delta_s"], winner["fit"]["delta_w"])
print("stored ds,dw:", rrow["sec3c_ds_cm"], rrow["sec3c_dw_cm"])
print("hit_mult_pass (replay):", hit_mult_pass, " stored:", rrow["hit_multiplicity_pass"])
print("final_secIV_pass (replay):", secIV_winner is not None, " stored:", rrow["final_sec_iv_pass"])
