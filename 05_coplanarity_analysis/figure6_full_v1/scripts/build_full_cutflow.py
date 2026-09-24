"""
Post-hoc cutflow, failure-reason, and confidence-interval builder.
Reads only completed-cell checkpoint data (checkpoints/cell_stats.json +
checkpoints/progress.json under each grid cell's directory) -- never touches
the live production driver. Safe to rerun at any time; only processes cells
with a DONE marker.

Implements Section K (18-stage cutflow, conditional + cumulative efficiency,
Wilson + Clopper-Pearson intervals), Section L (failure-reason accounting),
and the recoverable subset of Section M (weights/cross-sections/yields).
See DOWNSTREAM_SCHEMA_LIMITATIONS.md for what is and is not derivable.
"""
import os
import glob
import json
import math
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

FIG6 = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1"
LUMI_FB = 300.0  # paper's stated integrated luminosity, Fig. 6 caption
DS_MAX_CM = 0.01
DW_MAX_CM = 1.0

FAILURE_CATEGORIES = [
    "charge_filter_failure", "trigger_failure", "fiducial_failure",
    "no_accepted_detector_hits", "no_valid_seed_or_candidate",
    "delta_w_failure", "multiplicity_failure", "delta_s_failure",
    "final_pass", "technical_error_failure",
]


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    hw = (z / denom) * math.sqrt(max(0.0, phat * (1 - phat) / n + z**2 / (4 * n**2)))
    return (max(0.0, center - hw), min(1.0, center + hw))


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (None, None)
    lo = scipy_stats.beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = scipy_stats.beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return (lo, hi)


def find_done_cells():
    cells = []
    for cell_dir in glob.glob(f"{FIG6}/generation/*/downstream_L*keV"):
        done = f"{cell_dir}/checkpoints/DONE.txt"
        if os.path.exists(done):
            cells.append(cell_dir)
    return sorted(cells)


def classify_failure(row):
    """Map first_failure_reason (as saved) onto Section L's taxonomy."""
    if row.get("nan_ds") or row.get("inf_ds"):
        return "technical_error_failure"
    r = row.get("first_failure_reason")
    if r is None:
        return "final_pass"
    return {
        "fiducial": "fiducial_failure",
        "no_plane_reconstructed": "no_valid_seed_or_candidate",
        "hit_multiplicity": "multiplicity_failure",
        "signal_region_cuts": None,  # needs ds/dw sub-split, handled below
        "technical_exception": "technical_error_failure",
    }.get(r, "technical_error_failure")


def build_cell_row(cell_dir):
    stats_path = f"{cell_dir}/checkpoints/cell_stats.json"
    progress_path = f"{cell_dir}/checkpoints/progress.json"
    if not (os.path.exists(stats_path) and os.path.exists(progress_path)):
        return None
    stats = json.load(open(stats_path))
    progress = json.load(open(progress_path))
    df = pd.DataFrame(list(progress.values()))
    n_trigger = stats["n_trigger"]

    # Recoverable post-hoc: Delta_s / Delta_w independent pass flags
    if len(df):
        has_plane = df["sec3c_plane_found"] == True  # noqa: E712
        df["ds_pass"] = has_plane & (df["sec3c_ds_cm"].astype(float) < DS_MAX_CM)
        df["dw_pass"] = has_plane & (df["sec3c_dw_cm"].astype(float) < DW_MAX_CM)
        df["any_hit"] = df["n_hits_premerge"] > 0
        df["failure_category"] = df.apply(classify_failure, axis=1)
        # refine signal_region_cuts split into ds/dw once plane+multiplicity passed
        mask_sr = df["first_failure_reason"] == "signal_region_cuts"
        df.loc[mask_sr & ~df["dw_pass"], "failure_category"] = "delta_w_failure"
        df.loc[mask_sr & df["dw_pass"] & ~df["ds_pass"], "failure_category"] = "delta_s_failure"
    else:
        for c in ["ds_pass", "dw_pass", "any_hit", "failure_category"]:
            df[c] = pd.Series(dtype=object)

    n_any_hit = int(df["any_hit"].sum()) if len(df) else 0
    n_candidate = int((df["n_candidates"] > 0).sum()) if len(df) else 0
    n_plane = int(df["sec3c_plane_found"].sum()) if len(df) else 0
    n_mult = int(df["hit_multiplicity_pass"].sum()) if len(df) else 0
    n_dw = int(df["dw_pass"].sum()) if len(df) else 0
    n_ds = int(df["ds_pass"].sum()) if len(df) else 0
    n_final = stats["n_final"]
    n_fid = stats["n_fiducial"]
    n_tech_fail = int((df["failure_category"] == "technical_error_failure").sum()) if len(df) else 0

    row = {
        "channel": stats["channel"], "mass_gev": stats["mass_gev"], "lambda_kev": stats["lambda_kev"],
        "N_requested": 2000, "N_generated": stats.get("n_generated_lhe", stats["n_generated"]),
        "N_matched": stats["n_matched"], "N_charge_filtered": stats["n_charge_filtered"],
        "N_trigger": n_trigger, "N_trigger_fail": stats["n_charge_filtered"] - n_trigger,
        "N_fiducial": n_fid, "N_any_detector_hit": n_any_hit,
        "N_seed": "UNAVAILABLE (see DOWNSTREAM_SCHEMA_LIMITATIONS.md)",
        "N_candidate": n_candidate, "N_selected_plane": n_plane,
        "N_ge4_layers": "UNAVAILABLE (see DOWNSTREAM_SCHEMA_LIMITATIONS.md)",
        "N_8_layers": "UNAVAILABLE (see DOWNSTREAM_SCHEMA_LIMITATIONS.md)",
        "N_hit_multiplicity": n_mult, "N_Delta_s_pass": n_ds, "N_Delta_w_pass": n_dw,
        "N_final_SecIV": n_final, "N_technical_failure": n_tech_fail,
    }

    # conditional + cumulative efficiencies with CIs at each defined transition
    transitions = [
        ("matched_to_trigger", n_trigger, stats["n_charge_filtered"]),
        ("trigger_to_fiducial", n_fid, n_trigger),
        ("fiducial_to_plane", n_plane, n_fid),
        ("plane_to_multiplicity", n_mult, n_plane),
        ("multiplicity_to_dw", n_dw, n_mult),
        ("dw_to_ds", n_ds, n_dw),
        ("ds_to_final", n_final, n_ds),
    ]
    for name, k, n in transitions:
        eff = k / n if n else None
        wlo, whi = wilson(k, n) if n else (None, None)
        clo, chi = clopper_pearson(k, n) if n else (None, None)
        row[f"eff_{name}"] = eff
        row[f"eff_{name}_wilson95_lo"] = wlo
        row[f"eff_{name}_wilson95_hi"] = whi
        row[f"eff_{name}_cp95_lo"] = clo
        row[f"eff_{name}_cp95_hi"] = chi

    # cumulative: N_final / N_trigger (this project's actual eps_total definition)
    row["eff_cumulative_trigger_to_final"] = n_final / n_trigger if n_trigger else None
    wlo, whi = wilson(n_final, n_trigger) if n_trigger else (None, None)
    clo, chi = clopper_pearson(n_final, n_trigger) if n_trigger else (None, None)
    row["eff_cumulative_wilson95_lo"], row["eff_cumulative_wilson95_hi"] = wlo, whi
    row["eff_cumulative_cp95_lo"], row["eff_cumulative_cp95_hi"] = clo, chi

    # paper-defined eps_reco = N_selected_plane / N_fiducial ONLY (not reused elsewhere)
    row["eps_reconstruction_paper_defined"] = n_plane / n_fid if n_fid else None

    # yield projection at L=300 fb^-1 (recoverable from generation stats once available)
    gen_stats_path = f"/home/rafia/hep_tools/figure6_full_v1_runs/{stats['channel']}_{stats['mass_gev']}gev/metadata/generation_stats.json"
    if os.path.exists(gen_stats_path):
        gstats = json.load(open(gen_stats_path))
        xsec_pb = gstats.get("matched_xsec_pb")
        if xsec_pb is not None and n_trigger:
            xsec_fb = xsec_pb * 1000.0
            eps_total_from_matched = n_final / stats["n_matched"] if stats["n_matched"] else None
            row["matched_xsec_pb"] = xsec_pb
            row["eps_total_of_matched"] = eps_total_from_matched
            row["expected_yield_L300fb"] = xsec_fb * LUMI_FB * eps_total_from_matched if eps_total_from_matched else None

    # failure-reason fractions (must sum to n_trigger, the correct parent denominator)
    if len(df):
        fc = df["failure_category"].value_counts().to_dict()
        total_failure_categorized = sum(fc.values())
        row["failure_category_counts"] = json.dumps(fc)
        row["failure_categories_sum_check"] = (total_failure_categorized == n_trigger)
    else:
        row["failure_category_counts"] = "{}"
        row["failure_categories_sum_check"] = (n_trigger == 0)

    return row


def main():
    cells = find_done_cells()
    print(f"Found {len(cells)} completed (DONE) cells out of 91")
    rows = [r for r in (build_cell_row(c) for c in cells) if r is not None]
    if not rows:
        print("No completed cells yet -- nothing to write.")
        return
    df = pd.DataFrame(rows)
    os.makedirs(f"{FIG6}/TABLES", exist_ok=True)
    df.to_csv(f"{FIG6}/TABLES/cutflow_91point.csv", index=False)
    print(f"Wrote {len(df)} rows to TABLES/cutflow_91point.csv")

    # low-statistics flag (Section S): relative uncertainty > 40% on cumulative eff
    def rel_unc(row):
        if row["eff_cumulative_trigger_to_final"] in (None, 0) or pd.isna(row["eff_cumulative_trigger_to_final"]):
            return None
        lo, hi = row["eff_cumulative_wilson95_lo"], row["eff_cumulative_wilson95_hi"]
        if lo is None or hi is None:
            return None
        hw = (hi - lo) / 2
        return hw / row["eff_cumulative_trigger_to_final"]
    df["relative_uncertainty_cumulative"] = df.apply(rel_unc, axis=1)
    df["LOW_STATISTICS"] = df["relative_uncertainty_cumulative"].apply(
        lambda x: True if (x is not None and not pd.isna(x) and x > 0.4) else (False if x is not None else None))
    df.to_csv(f"{FIG6}/TABLES/cutflow_91point.csv", index=False)
    low = df[df["LOW_STATISTICS"] == True]  # noqa: E712
    print(f"LOW_STATISTICS points (rel. unc. > 40%): {len(low)}")
    if len(low):
        print(low[["channel", "mass_gev", "lambda_kev", "relative_uncertainty_cumulative"]].to_string(index=False))


if __name__ == "__main__":
    main()
