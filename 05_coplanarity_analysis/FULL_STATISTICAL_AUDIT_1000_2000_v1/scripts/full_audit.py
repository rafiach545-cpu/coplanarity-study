"""
Complete read-only statistical audit, recomputed from raw event-level
files, for Colored (1800GeV/2keV) and EW (800GeV/4keV), both the
original 1000-event samples and the fresh 2000-event regeneration.
No simulation is run here. No frozen file is written to.
"""
import pandas as pd, numpy as np, json, hashlib, os
from scipy.stats import norm, binomtest, fisher_exact

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/05_coplanarity_analysis/FULL_STATISTICAL_AUDIT_1000_2000_v1"

PAPER = {"colored": {"trig": 0.24, "fid": 0.28, "reco": 0.35},
         "EW":      {"trig": 0.10, "fid": 0.28, "reco": 0.72}}


def wilson(k, n, z):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0.0, center - half), min(1.0, center + half))


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (float("nan"), float("nan"))
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)


def std_binom_err(k, n):
    if n == 0:
        return float("nan")
    p = k / n
    return np.sqrt(p * (1 - p) / n)


def row(label, k, n, paper_val=None, note=""):
    p = k / n if n else float("nan")
    se = std_binom_err(k, n)
    w68 = wilson(k, n, 1.0)
    w95 = wilson(k, n, 1.96)
    cp95 = clopper_pearson(k, n)
    pval = binomtest(k, n, paper_val).pvalue if (paper_val is not None and n) else None
    if paper_val is None or n == 0:
        verdict = "NOT_DIRECTLY_COMPARABLE"
    elif pval < 0.01:
        verdict = "INCONSISTENT"
    elif pval < 0.05:
        verdict = "BORDERLINE"
    else:
        verdict = "CONSISTENT"
    return {
        "label": label, "numerator": k, "denominator": n, "value": p,
        "std_binom_err": se,
        "wilson68_lo": w68[0], "wilson68_hi": w68[1],
        "wilson95_lo": w95[0], "wilson95_hi": w95[1],
        "cp95_lo": cp95[0], "cp95_hi": cp95[1],
        "paper_value": paper_val, "binomial_p_value": pval,
        "verdict": verdict, "note": note,
    }


# =========================================================================
# Load raw per-event files
# =========================================================================

colored2000 = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/colored_1800GeV_L2keV/per_event_results.csv")
ew2000 = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv")
colored1000 = pd.read_csv(f"{BASE}/05_coplanarity_analysis/colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv")
ew1000 = pd.read_csv(f"{BASE}/05_coplanarity_analysis/ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv")

with open(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/cutflows/colored_1800GeV_L2keV_charge_trigger_accounting.json") as f:
    colored2000_acct = json.load(f)
with open(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/cutflows/EW_800GeV_L4keV_charge_trigger_accounting.json") as f:
    ew2000_acct = json.load(f)

# Upstream (generator-level) counts, from generator_cutflow_EW_and_colored.csv
# and COLORED_INCONSISTENCY_AUDIT_v1/tables/colored_complete_cutflow.csv
upstream = {
    "colored1000": {"N_requested": 1000, "N_lhe": 1000, "N_showered": 419, "N_matched": 419,
                     "N_charge_eligible": 125, "N_trigger_of_matched": 101, "N_trigger_of_charge": 27},
    "EW1000":      {"N_requested": 1000, "N_lhe": 1000, "N_showered": 511, "N_matched": 511,
                     "N_charge_eligible": None, "N_trigger_of_matched": 89, "N_trigger_of_charge": None},
    "colored2000": {"N_requested": 2000, "N_lhe": None, "N_showered": 873, "N_matched": 873,
                     "N_charge_eligible": colored2000_acct["N_both_charged"],
                     "N_trigger_of_matched": colored2000_acct["N_trigger_of_full_matched"],
                     "N_trigger_of_charge": colored2000_acct["N_trigger_AND_charge_filtered"]},
    "EW2000":      {"N_requested": 2000, "N_lhe": None, "N_showered": 1045, "N_matched": 1045,
                     "N_charge_eligible": None,
                     "N_trigger_of_matched": ew2000_acct["N_trigger_of_full_matched"],
                     "N_trigger_of_charge": None},
}

recon = {
    "colored1000": dict(df=colored1000, fid="truth_fiducial", plane="seed_found",
                          mult="best_candidate_passes_hit_multiplicity", final="passes_signal_region",
                          ds="ds", dw="dw", key="colored", n_trig=upstream["colored1000"]["N_trigger_of_charge"]),
    "EW1000":      dict(df=ew1000, fid="truth_fiducial", plane="seed_found",
                          mult="best_candidate_passes_hit_multiplicity", final="passes_signal_region",
                          ds="ds", dw="dw", key="EW", n_trig=upstream["EW1000"]["N_trigger_of_matched"]),
    "colored2000": dict(df=colored2000, fid="truth_fiducial", plane="sec3c_plane_found",
                          mult="hit_multiplicity_pass", final="final_sec_iv_pass",
                          ds="sec3c_ds_cm", dw="sec3c_dw_cm", key="colored", n_trig=upstream["colored2000"]["N_trigger_of_charge"]),
    "EW2000":      dict(df=ew2000, fid="truth_fiducial", plane="sec3c_plane_found",
                          mult="hit_multiplicity_pass", final="final_sec_iv_pass",
                          ds="sec3c_ds_cm", dw="sec3c_dw_cm", key="EW", n_trig=upstream["EW2000"]["N_trigger_of_matched"]),
}

all_rows = []
intersection_rows = []
raw_counts_rows = []

for name, cfg in recon.items():
    df = cfg["df"]
    key = cfg["key"]
    fid = df[cfg["fid"]].fillna(False).astype(bool)
    plane = df[cfg["plane"]].fillna(False).astype(bool)
    mult = df[cfg["mult"]].fillna(False).astype(bool)
    final = df[cfg["final"]].fillna(False).astype(bool)
    ds_pass = df[cfg["ds"]].notna() & (df[cfg["ds"]] < 0.01)
    dw_pass = df[cfg["dw"]].notna() & (df[cfg["dw"]] < 1.0)

    n_prop = len(df)
    n_fid = int(fid.sum())
    n_plane_total = int(plane.sum())
    n_fid_plane = int((fid & plane).sum())
    n_mult_total = int(mult.sum())
    n_fid_plane_mult = int((fid & plane & mult).sum())
    n_ds_pass = int(ds_pass.sum())
    n_dw_pass = int(dw_pass.sum())
    n_final_total = int(final.sum())
    n_fid_final = int((fid & final).sum())

    up = upstream[name]

    raw_counts_rows.append({
        "sample": name,
        "N_requested": up["N_requested"], "N_lhe": up["N_lhe"], "N_showered": up["N_showered"],
        "N_matched": up["N_matched"], "N_charge_eligible": up["N_charge_eligible"],
        "N_trigger_only": up["N_trigger_of_matched"], "N_trigger_AND_charge": up["N_trigger_of_charge"],
        "N_propagated_downstream": n_prop,
        "N_truth_fiducial": n_fid,
        "N_plane_found_total": n_plane_total, "N_fiducial_AND_plane": n_fid_plane,
        "N_hit_multiplicity_total": n_mult_total, "N_fid_AND_plane_AND_mult": n_fid_plane_mult,
        "N_delta_s_pass": n_ds_pass, "N_delta_w_pass": n_dw_pass,
        "N_final_SecIV_total": n_final_total, "N_fiducial_AND_final": n_fid_final,
    })

    # parent-child closure check
    closure_ok = (n_prop == cfg["n_trig"]) if cfg["n_trig"] is not None else None
    intersection_rows.append({
        "sample": name, "N_downstream_rows": n_prop, "N_expected_from_trigger_accounting": cfg["n_trig"],
        "closure_verified": closure_ok,
        "duplicate_event_idx": int(df["event_idx"].duplicated().sum()) if "event_idx" in df.columns else (int(df["event"].duplicated().sum()) if "event" in df.columns else None),
    })

    # ---- named efficiencies ----
    all_rows.append(row(f"{name}: matching_efficiency (N_matched/N_requested)", up["N_matched"], up["N_requested"], None,
                         "Generator-level; no paper Table I analog (paper does not quote a matching efficiency)."))
    all_rows.append(row(f"{name}: trigger_only_efficiency (N_trigger_of_matched/N_matched)", up["N_trigger_of_matched"], up["N_matched"], PAPER[key]["trig"],
                         "Trigger applied to the FULL matched sample, irrespective of charge. Directly comparable to paper's eps_trig."))
    if up["N_charge_eligible"] is not None:
        all_rows.append(row(f"{name}: charge_acceptance_efficiency (N_charge_eligible/N_matched)", up["N_charge_eligible"], up["N_matched"], None,
                             "Colored only; fraction of matched events where both R-hadrons carry nonzero charge. No paper Table I analog."))
        all_rows.append(row(f"{name}: trigger_conditional_on_charge (N_trigger_AND_charge/N_charge_eligible)", up["N_trigger_of_charge"], up["N_charge_eligible"], PAPER[key]["trig"],
                             "Colored only; trigger efficiency conditional on charge-eligibility -- a DIFFERENT population than trigger_only_efficiency above. Do not average these two."))
        all_rows.append(row(f"{name}: joint_trigger_and_charge_fraction (N_trigger_AND_charge/N_matched)", up["N_trigger_of_charge"], up["N_matched"], None,
                             "Colored only; NOT a trigger efficiency by itself -- explicitly NOT compared to paper's eps_trig."))
    all_rows.append(row(f"{name}: fiducial_efficiency (N_fiducial/N_downstream_propagated)", n_fid, n_prop, PAPER[key]["fid"],
                         "Downstream-propagated population = trigger-AND-charge-filtered for colored, trigger-only for EW (colored requires the charge filter to be physically detectable; EW quirks have fixed unit charge, no filter needed)."))
    all_rows.append(row(f"{name}: eps_plane_conditional (N(fid AND plane)/N_fiducial)", n_fid_plane, n_fid, PAPER[key]["reco"],
                         "Interpretation A of paper's eps_reco: algorithm finds >=1 coplanar-plane candidate."))
    all_rows.append(row(f"{name}: eps_secIV_conditional (N(fid AND final SecIV)/N_fiducial)", n_fid_final, n_fid, PAPER[key]["reco"],
                         "Interpretation B of paper's eps_reco: event survives the FULL Sec IV signal-region selection (plane found AND hit-multiplicity AND tight Ds/Dw cuts)."))
    all_rows.append(row(f"{name}: final_efficiency_vs_matched (N_fid_AND_final/N_matched)", n_fid_final, up["N_matched"], None,
                         "End-to-end efficiency relative to the full matched sample -- no paper Table I analog (paper reports factorized stages only)."))
    all_rows.append(row(f"{name}: final_efficiency_vs_requested (N_fid_AND_final/N_requested)", n_fid_final, up["N_requested"], None,
                         "End-to-end efficiency relative to requested/generated events -- no paper Table I analog."))

master = pd.DataFrame(all_rows)
master.to_csv(f"{OUT}/tables/master_efficiency_table.csv", index=False)

raw_counts = pd.DataFrame(raw_counts_rows)
raw_counts.to_csv(f"{OUT}/tables/raw_counts_all_samples.csv", index=False)

intersections = pd.DataFrame(intersection_rows)
intersections.to_csv(f"{OUT}/tables/event_intersection_closure_audit.csv", index=False)

print("=== RAW COUNTS ===")
print(raw_counts.to_string(index=False))
print()
print("=== CLOSURE CHECK ===")
print(intersections.to_string(index=False))
print()
print(f"Master efficiency table: {len(master)} rows written.")
