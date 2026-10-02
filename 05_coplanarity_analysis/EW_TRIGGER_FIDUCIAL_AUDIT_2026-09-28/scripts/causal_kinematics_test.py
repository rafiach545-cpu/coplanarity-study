"""
Causal test (not just plausibility argument): does higher post-shower
quirk-pair pT actually correlate with higher fiducial acceptance, using
ONLY already-stored data (no replay, no new simulation)?
"""
import numpy as np, pandas as pd
from scipy.stats import pointbiserialr, spearmanr

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28"

matched = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/matched_events_full.csv")
recon = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv")

matched = matched.reset_index().rename(columns={"index": "matched_row_idx"})

# beta of each quirk from stored truth 4-momenta (no simulation needed)
p1 = np.sqrt(matched["px1"]**2 + matched["py1"]**2 + matched["pz1"]**2)
p2 = np.sqrt(matched["px2"]**2 + matched["py2"]**2 + matched["pz2"]**2)
matched["beta1"] = p1 / matched["E1"]
matched["beta2"] = p2 / matched["E2"]
matched["beta_min"] = matched[["beta1", "beta2"]].min(axis=1)
matched["max_abs_eta"] = matched[["eta1", "eta2"]].abs().max(axis=1)

# Reconstruct the CORRECT trigger-passing subset with the same positional
# index the original driver used (event_idx in recon refers to THIS ordering)
trig_subset = matched[matched["trigger_proxy_pass"] == True].reset_index(drop=True)  # noqa: E712
trig_subset = trig_subset.reset_index().rename(columns={"index": "event_idx"})
trig_subset = trig_subset.merge(
    recon[["event_idx", "truth_fiducial", "geometric_fiducial", "n_hits_premerge", "first_failure_reason"]],
    on="event_idx", how="left")

n_fid_check = int(trig_subset["truth_fiducial"].sum())
assert n_fid_check == 94, f"closure check failed: {n_fid_check} != 94"

# ---------------------------------------------------------------
# 1. Fiducial efficiency binned by quirk_pair_pt_gev
# ---------------------------------------------------------------
def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0.0, center - half), min(1.0, center + half))


def binned_efficiency(df, var, bins, label):
    rows = []
    cats = pd.cut(df[var], bins=bins)
    for cat, grp in df.groupby(cats, observed=True):
        n = len(grp)
        k = int(grp["truth_fiducial"].sum())
        eff = k / n if n else np.nan
        lo, hi = wilson(k, n)
        rows.append({"variable": label, "bin": str(cat), "n": n, "n_fiducial": k,
                      "efficiency": eff, "wilson95_lo": lo, "wilson95_hi": hi})
    return pd.DataFrame(rows)


pt_bins = [200, 300, 400, 600, 900, 1400, 5000]
eta_bins = [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8]
beta_bins = [0, 0.90, 0.95, 0.98, 0.99, 0.995, 1.0]
nhits_bins = [-0.5, 3.5, 7.5, 11.5, 14.5, 15.5, 16.5]

out_pt = binned_efficiency(trig_subset, "quirk_pair_pt_gev", pt_bins, "quirk_pair_pt_gev")
out_eta1 = binned_efficiency(trig_subset, trig_subset["eta1"].abs().rename("abs_eta1"), eta_bins, "abs_eta1") if False else None
trig_subset["abs_eta1"] = trig_subset["eta1"].abs()
trig_subset["abs_eta2"] = trig_subset["eta2"].abs()
out_eta1 = binned_efficiency(trig_subset, "abs_eta1", eta_bins, "abs_eta1_quirk1")
out_eta2 = binned_efficiency(trig_subset, "abs_eta2", eta_bins, "abs_eta2_quirk2")
out_maxeta = binned_efficiency(trig_subset, "max_abs_eta", eta_bins, "max_abs_eta_of_pair")
out_betamin = binned_efficiency(trig_subset, "beta_min", beta_bins, "beta_min_of_pair")
out_nhits = binned_efficiency(trig_subset, "n_hits_premerge", nhits_bins, "n_hits_premerge_TOTAL_both_quirks (layer-coverage PROXY, not per-quirk minimum -- see caveat)")

all_bins = pd.concat([out_pt, out_eta1, out_eta2, out_maxeta, out_betamin, out_nhits], ignore_index=True)
all_bins.to_csv(f"{OUT}/tables/fiducial_efficiency_binned.csv", index=False)

# ---------------------------------------------------------------
# 3. Kinematic distributions: all matched vs trigger-passing vs fiducial-passing
# ---------------------------------------------------------------
fid_subset = trig_subset[trig_subset["truth_fiducial"] == True]
dist_rows = []
for name, df, cols in [
    ("all_matched", matched, ["quirk_pair_pt_gev", "eta1", "eta2", "max_abs_eta", "beta_min"]),
    ("trigger_passing", trig_subset, ["quirk_pair_pt_gev", "eta1", "eta2", "max_abs_eta", "beta_min"]),
    ("fiducial_passing", fid_subset, ["quirk_pair_pt_gev", "eta1", "eta2", "max_abs_eta", "beta_min"]),
]:
    for col in cols:
        s = df[col]
        dist_rows.append({"population": name, "variable": col, "n": len(df),
                           "mean": s.mean(), "median": s.median(), "std": s.std(),
                           "p25": s.quantile(0.25), "p75": s.quantile(0.75)})
dist_df = pd.DataFrame(dist_rows)
dist_df.to_csv(f"{OUT}/tables/kinematic_distribution_comparison.csv", index=False)

# ---------------------------------------------------------------
# 4. Fiducial failure sub-categorization (geometric/barrel vs propagation vs timing)
# ---------------------------------------------------------------
ok = trig_subset[trig_subset["first_failure_reason"].notna() | (trig_subset["truth_fiducial"] == True)].copy()
# propagation failure: n_hits_premerge == 0 (quirk(s) never registered ANY hit)
# partial geometric/barrel failure: 0 < n_hits_premerge < 16
# timing failure: geometric_fiducial True but truth_fiducial False
def categorize(row):
    if row["truth_fiducial"] == True:
        return "pass"
    if row.get("first_failure_reason") == "technical_exception":
        return "technical_exception"
    if row["n_hits_premerge"] == 0:
        return "propagation_failure (zero hits, quirk(s) never reached any layer)"
    if row["geometric_fiducial"] == False:
        return "geometric/barrel_failure (partial layer coverage, 0<hits<16)"
    return "timing_failure (25ns cut, geometric OK)"

trig_subset["fail_category"] = trig_subset.apply(categorize, axis=1)
cat_counts = trig_subset["fail_category"].value_counts().reset_index()
cat_counts.columns = ["category", "count"]
cat_counts.to_csv(f"{OUT}/tables/fiducial_failure_subcategories_kinematic.csv", index=False)

# ---------------------------------------------------------------
# 5. Correlation quantification
# ---------------------------------------------------------------
corr_rows = []
for var in ["quirk_pair_pt_gev", "max_abs_eta", "beta_min", "n_hits_premerge"]:
    x = trig_subset[var].values.astype(float)
    y = trig_subset["truth_fiducial"].values.astype(int)
    r_pb, p_pb = pointbiserialr(y, x)
    r_sp, p_sp = spearmanr(x, y)
    corr_rows.append({"variable": var, "point_biserial_r": r_pb, "point_biserial_p": p_pb,
                       "spearman_r": r_sp, "spearman_p": p_sp, "n": len(x)})
corr_df = pd.DataFrame(corr_rows)
corr_df.to_csv(f"{OUT}/tables/kinematic_fiducial_correlation.csv", index=False)

print("=== binned efficiency (pT_pair) ===")
print(out_pt.to_string(index=False))
print()
print("=== correlation summary ===")
print(corr_df.to_string(index=False))
print()
print("=== failure subcategories ===")
print(cat_counts.to_string(index=False))
print()
print("Closure: trigger_subset truth_fiducial sum =", n_fid_check, "(expected 94)")
