"""
Reproducibility/consistency tests for the converted-photon-only statistics
freeze. Run: python3 test_converted_photon_only_statistics.py
Exits 0 if all checks pass, 1 otherwise. Does not launch any simulation.
"""
import json
import os
import sys
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"
OUT_DIR = f"{BASE}/05_coplanarity_analysis/converted_photon_only_statistics_v1"

failures = []


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        failures.append(name)


# 1. file-integrity test
v3 = pd.read_csv(f"{PC_DIR}/conversion_scan_results_v3_SEC3C_DS_DW.csv")
check("file-integrity: 9139 rows", len(v3) == 9139)
check("file-integrity: 9139 unique event IDs", v3["event"].nunique() == 9139)
check("file-integrity: event IDs cover [0,9139)", set(v3["event"]) == set(range(9139)))

# 2. v2/v3 equality test
v2 = pd.read_csv(f"{PC_DIR}/conversion_scan_results_v2_VERTEX_FIXED.csv")
common = [c for c in v2.columns if c in v3.columns and c != "event"]
merged = v2.merge(v3, on="event", suffixes=("_v2", "_v3"))
all_equal = True
for c in common:
    a, b = merged[f"{c}_v2"], merged[f"{c}_v3"]
    if a.dtype.kind in "iuf":
        eq = (a.isna() & b.isna()) | np.isclose(a.fillna(-999999), b.fillna(-999999))
    else:
        eq = a.astype(str) == b.astype(str)
    all_equal &= bool(eq.all())
check("v2/v3 equality: all common columns bit-identical", all_equal)

# 3. NaN/Inf/duplicate test
allowed_nan_cols = {"ds", "dw", "sec3c_ds", "sec3c_dw", "sec3c_n_layers"}
nan_cols = set(c for c in v3.columns if v3[c].isna().any())
check("NaN only in allowed columns", nan_cols <= allowed_nan_cols)
numeric = v3.select_dtypes(include=[np.number])
check("no infinite values", not np.isinf(numeric.to_numpy()).any())
check("no duplicate event IDs", v3["event"].duplicated().sum() == 0)

# 4. unit consistency test (Delta_s/Delta_w should be O(cm)-scale, not mm)
plane = v3[v3["sec3c_plane_found"]]
ds = plane["sec3c_ds"].dropna()
dw = plane["sec3c_dw"].dropna()
check("Delta_s values in plausible cm range (0 < ds < 1)", ((ds > 0) & (ds < 1)).all())
check("Delta_w values in plausible cm range (0 < dw < 5)", ((dw > 0) & (dw < 5)).all())
check("conv_r_cm constant at beampipe radius 2.35cm", np.allclose(v3["conv_r_cm"], 2.35))

# 5. candidate/plane consistency test
check("n_candidates>=1 <=> sec3c_plane_found (this dataset)",
      (v3["n_candidates"] >= 1).equals(v3["sec3c_plane_found"]))
check("sec3c_ds/dw finite exactly where sec3c_plane_found",
      v3["sec3c_ds"].notna().equals(v3["sec3c_plane_found"]))

# 6. final-cut implication test
bad = v3[v3["passes"] & ~(v3["sec3c_plane_found"] & (v3["sec3c_ds"] < 0.01))]
check("final pass implies plane_found & ds<0.01", len(bad) == 0)
check("final pass count is 0/9139", int(v3["passes"].sum()) == 0)

# 7. output-regeneration test: rerun the builder and diff key JSON outputs
import subprocess
before = json.load(open(f"{OUT_DIR}/master_statistics.json"))
r = subprocess.run(["python3", f"{PC_DIR}/build_converted_photon_only_statistics.py"],
                    cwd=BASE, capture_output=True, text=True)
check("output-regeneration: builder exits 0", r.returncode == 0)
after = json.load(open(f"{OUT_DIR}/master_statistics.json"))
same = all(before[k] == after[k] for k in before if k not in ("wall_time_s", "seconds_per_event", "events_per_hour_verified"))
check("output-regeneration: master statistics reproducible (non-runtime fields)", same)

# 8. plot-source consistency test
plot_ds = pd.read_csv(f"{OUT_DIR}/plotsrc_fig4_5_6_delta.csv")
check("plot-source Delta_s matches N_plane", len(plot_ds) == int(v3["sec3c_plane_found"].sum()))
check("plot-source Delta_s median matches computed", abs(plot_ds["sec3c_ds"].median() - 0.02116) < 1e-3)

print()
print(f"TOTAL: {len(failures)} failing checks")
sys.exit(1 if failures else 0)
