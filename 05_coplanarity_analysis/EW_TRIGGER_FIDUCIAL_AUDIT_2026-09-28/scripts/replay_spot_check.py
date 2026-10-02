"""
Minimal spot-check replay: 3 EW-2000 trigger-passing events (deterministic,
stored seeds), generous per-event timeout, to empirically confirm the
structural code-level proof that n_hits_premerge==16 implies both quirks
independently covered all 8 layers (8+8), not a false-accepted 16-total
from an asymmetric split. Not new event generation.
"""
import sys, signal, time
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim")
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
import trajectory_to_hits as tth
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2
tth.integrate_trajectory = integrate_trajectory_fast_v2

BASE = "/home/rafia/coplanarity_study"


class TimeoutErr(Exception):
    pass


def _handler(signum, frame):
    raise TimeoutErr()


signal.signal(signal.SIGALRM, _handler)

trig = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/trigger_passing_events.csv")
recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv")

# pick 5 events spanning the fastest-likely cases: prefer events recon marks
# with SMALL wall_time_s originally (faster integrations), for a tractable spot check.
# Exclude known technical_exception rows (status != "ok") outright.
recon_ok = recon[recon["status"] == "ok"] if "status" in recon.columns else recon
recon_sorted = recon_ok.sort_values("wall_time_s").head(15)
targets = [int(x) for x in recon_sorted["event_idx"].head(5).tolist()]
print("targets (event_idx):", targets)

rows = []
for i in targets:
    row = trig.iloc[i]
    rrow = recon[recon["event_idx"] == i]
    seed = int(rrow["seed"].iloc[0])
    orig_wall = float(rrow["wall_time_s"].iloc[0])
    p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
    p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
    t0 = time.time()
    signal.alarm(300)
    try:
        rng = np.random.default_rng(seed)
        hits, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=800.0, Lambda_gev=4e-6, B_tesla=2.0,
            charge1=float(row["charge1"]), charge2=float(row["charge2"]), rng=rng, max_layer_r_cm=60.0)
        signal.alarm(0)
    except TimeoutErr:
        print(f"event_idx={i}: TIMEOUT after 300s, skipping")
        continue
    except RuntimeError as e:
        signal.alarm(0)
        print(f"event_idx={i}: RuntimeError (known technical-exception class), skipping: {e}")
        continue
    wall = time.time() - t0
    layers_q1 = set(h["layer"] for h in hits if h["quirk_index"] == 1)
    layers_q2 = set(h["layer"] for h in hits if h["quirk_index"] == 2)
    n_prem = traj["n_hits_premerge"]
    max_t = traj["max_hit_t_ns_premerge"]
    geo_ok = (n_prem == 16)
    timing_ok = (not np.isnan(max_t)) and (max_t < 25.0)
    rows.append({
        "trig_row_idx": i, "seed": seed, "orig_wall_time_s": orig_wall, "replay_wall_time_s": wall,
        "n_hits_premerge": n_prem, "n_layers_q1": len(layers_q1), "n_layers_q2": len(layers_q2),
        "geometric_fiducial": geo_ok, "max_hit_t_ns": max_t, "timing_ok": timing_ok,
        "truth_fiducial": geo_ok and timing_ok,
    })
    print(f"event_idx={i}: replay_wall={wall:.1f}s (orig={orig_wall:.1f}s), n_prem={n_prem}, "
          f"q1_layers={len(layers_q1)}, q2_layers={len(layers_q2)}, geo_ok={geo_ok}, timing_ok={timing_ok}")

df = pd.DataFrame(rows)
df.to_csv(f"{BASE}/05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/tables/EW2000_fiducial_replay_detail.csv", index=False)
print(f"\nDONE. Replayed {len(df)}/{len(targets)} targeted events.")
if len(df):
    mismatch = ((df["geometric_fiducial"]) != ((df["n_layers_q1"]==8)&(df["n_layers_q2"]==8))).sum()
    print("MISMATCH (geo_ok vs both==8):", mismatch)
    merged = recon.merge(df, left_on="event_idx", right_on="trig_row_idx", suffixes=("_stored","_replay"))
    print("mismatches stored vs replay truth_fiducial:", (merged["truth_fiducial_stored"] != merged["truth_fiducial_replay"]).sum())
