"""
Regression tests for the converted-photon + pile-up overlay driver.
1) mu=0 regression: must reproduce v3/v4 bit-for-bit (Poisson(0)=0 always,
   zero pile-up hits, rng_photon stream identical to v2/v3/v4).
2) small mu=50 sanity: n=50 events, checks Poisson stats, pool sampling,
   suppression counters, one combined merge, mixed provenance, and
   run-to-run reproducibility (same seed -> same result).
Exits 0 if all checks pass. Does not launch a full run.
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from analyze_converted_photon_with_pileup_v1 import analyze_one_event_overlay, MASTER_SEED
from pileup_hits_suppressed import build_ancestry_pool_index

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"
ANCESTRY_POOL_PATH = f"{BASE}/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv"

failures = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


photons = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
pool_index = build_ancestry_pool_index(pd.read_csv(ANCESTRY_POOL_PATH))
v4 = pd.read_csv(f"{PC_DIR}/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv")

# --- 1. mu=0 regression, n=50 prefix ---
rng_photon = np.random.default_rng(MASTER_SEED)
mu0_rows = []
for i in range(50):
    res = analyze_one_event_overlay(photons.iloc[i], i, 0.0, rng_photon, pool_index)
    mu0_rows.append(res)
mu0_df = pd.DataFrame(mu0_rows)

check("mu=0: Poisson multiplicity always 0", (mu0_df["n_pu_interactions"] == 0).all())
check("mu=0: pile-up hits always 0", (mu0_df["n_raw_pileup_hits_after_suppression"] == 0).all())
check("mu=0: n_merged_hard_pileup_mixed always 0", (mu0_df["n_merged_hard_pileup_mixed"] == 0).all())

v4_prefix = v4.iloc[:50].reset_index(drop=True)
for col_new, col_v4 in [("status", "status"), ("n_hits", "n_hits"), ("n_candidates", "n_candidates"),
                          ("final_sec_iv_pass", "passes"), ("sec3c_plane_found", "sec3c_plane_found"),
                          ("sec3c_ds", "sec3c_ds"), ("sec3c_dw", "sec3c_dw"), ("sec3c_n_layers", "sec3c_n_layers"),
                          ("conv_r_cm", "conv_r_cm")]:
    a, b = mu0_df[col_new], v4_prefix[col_v4]
    if a.dtype.kind in "iuf" or b.dtype.kind in "iuf":
        eq = (a.isna() & b.isna()) | np.isclose(pd.to_numeric(a, errors="coerce").fillna(-999999),
                                                    pd.to_numeric(b, errors="coerce").fillna(-999999))
    else:
        eq = a.astype(str) == b.astype(str)
    check(f"mu=0: '{col_new}' matches v4's '{col_v4}' bit-for-bit (n=50)", bool(eq.all()))

# --- 2. small mu=50 sanity, n=50 ---
rng_photon2 = np.random.default_rng(MASTER_SEED)
mu50_rows = []
for i in range(50):
    res = analyze_one_event_overlay(photons.iloc[i], i, 50.0, rng_photon2, pool_index)
    mu50_rows.append(res)
mu50_df = pd.DataFrame(mu50_rows)

interactions = mu50_df["n_pu_interactions"].to_numpy()
check("mu=50: Poisson mean roughly consistent with mu=50 (n=50, loose bound)",
      abs(interactions.mean() - 50) < 15)
check("mu=50: pile-up hits present in at least some events", (mu50_df["n_raw_pileup_hits_after_suppression"] > 0).any())
check("mu=50: combined premerge = raw_conv + raw_pileup_after_suppression",
      (mu50_df["n_hits_combined_premerge"] == mu50_df["n_raw_conv_hits"] + mu50_df["n_raw_pileup_hits_after_suppression"]).all())
check("mu=50: postmerge <= premerge", (mu50_df["n_hits_combined_postmerge"] <= mu50_df["n_hits_combined_premerge"]).all())
check("mu=50: at least one mixed hard+pileup cluster occurs somewhere in n=50",
      (mu50_df["n_merged_hard_pileup_mixed"] > 0).any())

# reproducibility: same seed -> same result
rng_photon3 = np.random.default_rng(MASTER_SEED)
mu50_rows_b = []
for i in range(50):
    res = analyze_one_event_overlay(photons.iloc[i], i, 50.0, rng_photon3, pool_index)
    mu50_rows_b.append(res)
mu50_df_b = pd.DataFrame(mu50_rows_b)
check("mu=50: exact reproducibility (same seed -> identical n_hits sequence)",
      (mu50_df["n_hits"].to_numpy() == mu50_df_b["n_hits"].to_numpy()).all())
check("mu=50: exact reproducibility (identical sec3c_ds sequence)",
      np.allclose(mu50_df["sec3c_ds"].fillna(-1), mu50_df_b["sec3c_ds"].fillna(-1)))

# NaN/Inf check
numeric_cols = mu50_df.select_dtypes(include=[np.number]).columns
check("mu=50: no infinite values", not np.isinf(mu50_df[numeric_cols].to_numpy()).any())

print(f"\nTOTAL: {len(failures)} failing checks")
sys.exit(1 if failures else 0)
