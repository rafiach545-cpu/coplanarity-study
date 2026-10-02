import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis")
import trajectory_to_hits as tth
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
tth.integrate_trajectory = integrate_trajectory_fast_v2
from coplanarity_fit import seeding_and_iterative_fit, select_reconstructed_plane, vertex_relative_hits

LAYER_NAME_TO_IDX = {'L1_IBL':1,'L2_PixelB0':2,'L3_PixelB1':3,'L4_PixelB2':4,'L5_SCT_B3':5,'L6_SCT_B4':6,'L7_SCT_B5':7,'L8_SCT_B6':8}
BASE = "/home/rafia/coplanarity_study"

trig = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/trigger_passing_events.csv")
recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv")
row = trig.iloc[182]
rrow = recon[recon["event_idx"]==182].iloc[0]
seed = int(rrow["seed"])
rng = np.random.default_rng(seed)
p1 = (row["px1"],row["py1"],row["pz1"],row["E1"])
p2 = (row["px2"],row["py2"],row["pz2"],row["E2"])
hits, traj = tth.simulate_quirk_hits(p1,p2,mass_gev=800.0,Lambda_gev=4e-6,B_tesla=2.0,
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
df = pd.DataFrame(rows)
df.to_csv(f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_2026-09-28/SOURCE_DATA/FIGURE_C_EW_hits.csv", index=False)
print("saved", len(df), "hits")
print("winner ds,dw:", winner["fit"]["delta_s"], winner["fit"]["delta_w"])
print("stored ds,dw:", rrow["sec3c_ds_cm"], rrow["sec3c_dw_cm"])
