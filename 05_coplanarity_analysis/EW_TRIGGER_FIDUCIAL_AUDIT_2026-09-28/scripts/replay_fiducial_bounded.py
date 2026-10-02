"""
Bounded, timeout-protected replay of EW-2000 trigger-passing events to
check per-quirk layer coverage (item 7's "one-quirk-only" concern).
Deterministic replay from stored seeds -- NOT new event generation.
Single-process, signal-based timeout (no orphaned worker processes).
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


def replay_one(seed, p1, p2, charge1, charge2, timeout_s=8):
    signal.alarm(timeout_s)
    try:
        rng = np.random.default_rng(seed)
        hits, traj = tth.simulate_quirk_hits(p1, p2, mass_gev=800.0, Lambda_gev=4e-6, B_tesla=2.0,
            charge1=charge1, charge2=charge2, rng=rng, max_layer_r_cm=60.0)
    finally:
        signal.alarm(0)
    layers_q1 = set(h["layer"] for h in hits if h["quirk_index"] == 1)
    layers_q2 = set(h["layer"] for h in hits if h["quirk_index"] == 2)
    return {
        "n_hits_premerge": traj["n_hits_premerge"],
        "max_hit_t_ns": traj["max_hit_t_ns_premerge"],
        "n_layers_q1": len(layers_q1), "n_layers_q2": len(layers_q2),
    }


if __name__ == "__main__":
    trig = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/trigger_passing_events.csv")
    recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv")

    rows = []
    skipped = []
    t0 = time.time()
    for i, row in trig.iterrows():
        rrow = recon[recon["event_idx"] == i]
        if len(rrow) == 0:
            continue
        seed = int(rrow["seed"].iloc[0])
        p1 = (row["px1"], row["py1"], row["pz1"], row["E1"])
        p2 = (row["px2"], row["py2"], row["pz2"], row["E2"])
        try:
            res = replay_one(seed, p1, p2, float(row["charge1"]), float(row["charge2"]))
        except TimeoutErr:
            skipped.append(int(i))
            print(f"SKIP (timeout) event_idx={i}", flush=True)
            continue
        n_prem = res["n_hits_premerge"]
        max_t = res["max_hit_t_ns"]
        geo_ok = (n_prem == 16)
        timing_ok = (not np.isnan(max_t)) and (max_t < 25.0)
        rows.append({
            "trig_row_idx": int(i), "seed": seed,
            "n_hits_premerge": n_prem, "n_layers_q1": res["n_layers_q1"], "n_layers_q2": res["n_layers_q2"],
            "geometric_fiducial": geo_ok, "max_hit_t_ns": max_t, "timing_ok": timing_ok,
            "truth_fiducial": geo_ok and timing_ok,
        })
        if len(rows) % 20 == 0:
            print(f"progress: {len(rows)} done, {len(skipped)} skipped, {time.time()-t0:.0f}s elapsed", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(f"{BASE}/05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/tables/EW2000_fiducial_replay_detail.csv", index=False)
    print(f"DONE: N replayed={len(df)}, N skipped(timeout)={len(skipped)}, skipped_idx={skipped}")
    print("geometric_fiducial True:", df["geometric_fiducial"].sum())
    print("both quirks 8 layers:", ((df["n_layers_q1"]==8)&(df["n_layers_q2"]==8)).sum())
    print("MISMATCH (geo_ok vs both==8):", ((df["geometric_fiducial"]) != ((df["n_layers_q1"]==8)&(df["n_layers_q2"]==8))).sum())
    fail = df[~df["geometric_fiducial"]]
    both_fail = ((fail["n_layers_q1"]<8) & (fail["n_layers_q2"]<8)).sum()
    one_fail  = (((fail["n_layers_q1"]<8) & (fail["n_layers_q2"]==8)) | ((fail["n_layers_q1"]==8) & (fail["n_layers_q2"]<8))).sum()
    print("both-fail:", both_fail, "one-fail:", one_fail, "total geo failures:", len(fail))
    geo_true = df[df["geometric_fiducial"]]
    print("geo True but timing fails:", (~geo_true["timing_ok"]).sum(), "of", len(geo_true))
    merged = recon.merge(df, left_on="event_idx", right_on="trig_row_idx", suffixes=("_stored","_replay"))
    print("mismatches stored vs replay truth_fiducial:", (merged["truth_fiducial_stored"] != merged["truth_fiducial_replay"]).sum())
