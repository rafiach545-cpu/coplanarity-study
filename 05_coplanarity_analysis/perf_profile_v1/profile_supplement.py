"""
Supplement to profile_pipeline.py: 3 targeted single-Lambda probes to
confirm the RK4 bottleneck holds outside colored/low-boost (the only
category covered before the main run hit its time cap):
  - colored, event 34, high boost, Lambda=2keV (benchmark)
  - EW, event 438, low boost, Lambda=4keV (benchmark)
  - EW, event 417, high boost, Lambda=4keV (benchmark)
Reuses run_one() from profile_pipeline.py unchanged -- same instrumentation,
same baseline call sequence.
"""
import sys
import pandas as pd

sys.path.insert(0, "/home/rafia/coplanarity_study/05_coplanarity_analysis/perf_profile_v1")
from profile_pipeline import run_one, BASE, OUT

colored = pd.read_csv(f"{BASE}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv")
ew = pd.read_csv(f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv")

targets = [
    ("colored", 34, colored[colored["event"] == 34].iloc[0], 1800.0, 2e-6, "high"),
    ("EW", 438, ew[ew["event"] == 438].iloc[0], 800.0, 4e-6, "low"),
    ("EW", 417, ew[ew["event"] == 417].iloc[0], 800.0, 4e-6, "high"),
]

results = []
for benchmark, eid, row, mq, lam, boost in targets:
    print(f"Running {benchmark} event {eid} ({boost} boost) Lambda={lam*1e6:.0f}keV ...", flush=True)
    r, hit_rows, plane_rows, full_stats = run_one(benchmark, eid, row, mq, lam, boost)
    results.append(r)
    tag = f"{benchmark}_ev{eid}_lam{lam*1e6:.0f}keV"
    pd.DataFrame(hit_rows).to_csv(f"{OUT}/profiles/{tag}_hits_BASELINE.csv", index=False)
    pd.DataFrame(plane_rows).to_csv(f"{OUT}/profiles/{tag}_plane_BASELINE.csv", index=False)
    with open(f"{OUT}/profiles/{tag}_full_cprofile.txt", "w") as f:
        f.write(full_stats)
    print(f"  wall={r['wall_time_s']:.3f}s traj={r['time_integrate_trajectory_s']:.3f}s "
          f"({100*r['time_integrate_trajectory_s']/r['wall_time_s']:.1f}% of wall) "
          f"ds={r['sec3c_ds_cm']} final={r['final_sec_iv_pass']}", flush=True)

pd.DataFrame(results).to_csv(f"{OUT}/profiles/SUPPLEMENT_SUMMARY.csv", index=False)
print("Saved SUPPLEMENT_SUMMARY.csv")
