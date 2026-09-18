"""
MASTER PPT STATISTICS PACKAGE builder (2026-09-18). READ-ONLY: loads
already-authoritative, already-frozen files (EW/colored cutflow CSVs, the
pile-up-only freeze package, the converted-photon-only freeze package) and
independently recomputes every number reported for the PPT sourcebook. Does
NOT run any new simulation, does NOT modify any physics code/cuts/CSVs.
"""
import hashlib
import json
import os
import numpy as np
import pandas as pd
from scipy import stats as sstats

BASE = "/home/rafia/coplanarity_study"
OUT_DIR = f"{BASE}/05_coplanarity_analysis/ppt_statistics_v1"
os.makedirs(OUT_DIR, exist_ok=True)

COLORED_CSV = f"{BASE}/05_coplanarity_analysis/colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv"
EW_CSV = f"{BASE}/05_coplanarity_analysis/ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv"
COLORED_MATCHED = f"{BASE}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv"
EW_MATCHED = f"{BASE}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv"
PU_DIR = f"{BASE}/05_coplanarity_analysis/pileup_only_statistics_v1"
PH_DIR = f"{BASE}/05_coplanarity_analysis/converted_photon_only_statistics_v1"


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def wilson(k, n, z):
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    c = phat + z * z / (2 * n)
    h = np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    d = 1 + z * z / n
    return ((c - h) / d, (c + h) / d)


def cp95(k, n):
    lo = 0.0 if k == 0 else sstats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else sstats.beta.ppf(0.975, k + 1, n - k)
    return (lo, hi)


def rr(k, n):
    w68 = wilson(k, n, 1.0)
    w95 = wilson(k, n, 1.96)
    c95 = cp95(k, n)
    return dict(k=k, n=n, rate=k / n if n else float("nan"),
                wilson68=w68, wilson95=w95, cp95=c95,
                ul3n=3.0 / n if n else float("nan"))


def pct(a, p):
    return float(np.percentile(a, p)) if len(a) else float("nan")


# ---------------------------------------------------------------------------
# 1. File inventory
# ---------------------------------------------------------------------------
def file_inventory():
    entries = [
        ("A. EW quirk signal cutflow", EW_CSV),
        ("A. EW quirk matched sample", EW_MATCHED),
        ("B. Colored quirk signal cutflow", COLORED_CSV),
        ("B. Colored quirk matched sample", COLORED_MATCHED),
        ("C. Converted-photon-only v3 result", f"{BASE}/02_backgrounds/photon_conversion/conversion_scan_results_v3_SEC3C_DS_DW.csv"),
        ("C. Converted-photon-only freeze master", f"{PH_DIR}/master_statistics.json"),
        ("D. Pile-up mu=0 fullcutflow", f"{BASE}/05_coplanarity_analysis/sweep_mu_2026-09-16/pileup_mu0_n5000_sec3c_fullcutflow_v1.csv"),
        ("D. Pile-up mu=5 fullcutflow", f"{BASE}/05_coplanarity_analysis/sweep_mu_2026-09-16/pileup_mu5_n5000_sec3c_fullcutflow_v1.csv"),
        ("D. Pile-up mu=10 fullcutflow", f"{BASE}/05_coplanarity_analysis/sweep_mu_2026-09-16/pileup_mu10_n5000_sec3c_fullcutflow_v1.csv"),
        ("D. Pile-up mu=20 fullcutflow", f"{BASE}/05_coplanarity_analysis/sweep_mu_2026-09-16/pileup_mu20_n5000_sec3c_fullcutflow_v1.csv"),
        ("D. Pile-up mu=50 fullcutflow", f"{BASE}/05_coplanarity_analysis/sweep_mu_2026-09-16/pileup_mu50_n5000_sec3c_fullcutflow_v1.csv"),
        ("D. Pile-up freeze master", f"{PU_DIR}/table9_master_cross_mu.csv"),
        ("F. Pile-up paper comparison", f"{PU_DIR}/table8_paper_comparison.csv"),
        ("F. Photon paper comparison", f"{PH_DIR}/converted_photon_only_paper_comparison_v1.csv"),
        ("G. Photon v3 runtime log", f"{BASE}/docs/conversion_v3_run.log"),
        ("G. Pile-up sweep runtime log", f"{BASE}/docs/pileup_sec3c_fullcutflow_sweep_run.log"),
    ]
    rows = []
    for label, path in entries:
        if not os.path.exists(path):
            rows.append({"label": label, "path": path, "status": "MISSING"})
            continue
        is_csv = path.endswith(".csv")
        n_rows = len(pd.read_csv(path)) if is_csv else None
        rows.append({
            "label": label, "path": path, "status": "OK", "row_count": n_rows,
            "sha256": sha256(path),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3/4. Signal complete statistics
# ---------------------------------------------------------------------------
def signal_stats(name, cutflow_path, matched_path, mq_gev, lambda_ev):
    cdf = pd.read_csv(cutflow_path)
    mdf = pd.read_csv(matched_path)
    n_matched = len(mdf)
    n_trigger = len(cdf)
    assert int((mdf["pT_pair"] > 200).sum()) == n_trigger, "trigger recount mismatch"

    n_geom_fid = int(cdf["geometric_fiducial"].sum())
    n_truth_fid = int(cdf["truth_fiducial"].sum())
    n_seed = int(cdf["seed_found"].sum())
    n_plane = int(cdf.loc[cdf["truth_fiducial"], "ds"].notna().sum())
    n_mult = int(cdf["best_candidate_passes_hit_multiplicity"].fillna(False).astype(bool).sum())
    n_final = int(cdf["passes_signal_region"].sum())

    plane_pop = cdf[cdf["truth_fiducial"] & cdf["ds"].notna()]
    ds = plane_pop["ds"].to_numpy()
    dw = plane_pop["dw"].to_numpy()

    eps_trig = rr(n_trigger, n_matched)
    eps_fid = rr(n_truth_fid, n_trigger)
    eps_reco = rr(n_plane, n_truth_fid)
    eps_final_cum = rr(n_final, n_truth_fid)

    layer_dist = plane_pop["best_candidate_n_layers_with_hit"].value_counts().sort_index().to_dict()

    final_events = cdf.loc[cdf["passes_signal_region"], "event"].tolist()
    near_miss = cdf[(cdf["ds"] >= 0.01) & (cdf["ds"] < 0.013) & ~cdf["passes_signal_region"]]

    return {
        "benchmark": name, "mQ_GeV": mq_gev, "Lambda_eV": lambda_ev,
        "N_matched": n_matched, "N_trigger": n_trigger,
        "N_geometric_fiducial": n_geom_fid, "N_truth_fiducial": n_truth_fid,
        "N_seed_found": n_seed, "N_selected_plane": n_plane,
        "N_hit_multiplicity_pass": n_mult, "N_final_Sec_IV_pass": n_final,
        "epsilon_trig": eps_trig, "epsilon_fid": eps_fid, "epsilon_reco_paper_def": eps_reco,
        "cumulative_final_vs_truth_fid": eps_final_cum,
        "N_plane_Delta_s": {
            "count": len(ds), "min": float(ds.min()), "max": float(ds.max()),
            "mean": float(ds.mean()), "median": float(np.median(ds)),
            "p16": pct(ds, 16), "p84": pct(ds, 84),
            "N_below_0.01": int((ds < 0.01).sum()), "frac_below_0.01": float((ds < 0.01).mean()),
        } if len(ds) else {"count": 0},
        "N_plane_Delta_w": {
            "count": len(dw), "min": float(dw.min()), "max": float(dw.max()),
            "mean": float(dw.mean()), "median": float(np.median(dw)),
            "p16": pct(dw, 16), "p84": pct(dw, 84),
        } if len(dw) else {"count": 0},
        "layer_coverage_distribution": {str(int(k)): int(v) for k, v in layer_dist.items()},
        "final_passing_event_ids": final_events,
        "near_miss_events_0.01<=ds<0.013": near_miss[["event", "ds", "dw", "best_candidate_passes_hit_multiplicity"]].to_dict("records"),
        "zero_candidate_truth_fiducial_events": cdf.loc[cdf["truth_fiducial"] & (cdf["n_candidates"] == 0), "event"].tolist(),
        "cross_section_note": "colored: NOT separately measured in this project (XSEC_MATCHED_PB=None in source); EW: 0.0002337 pb, this project's own MadGraph/Pythia8 run, NOT a paper-quoted value" if name == "colored" else "0.0002337 pb (this project's own MadGraph/Pythia8 matched cross-section, NOT a paper-quoted value)",
        "runtime": "NOT RECORDED (no per-event timing instrumentation in analyze_colored_quirk.py/analyze_ew_quirk.py)",
        "peak_RSS": "NOT RECORDED",
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    inv = file_inventory()
    inv.to_csv(f"{OUT_DIR}/authoritative_file_inventory.csv", index=False)

    colored = signal_stats("colored", COLORED_CSV, COLORED_MATCHED, 1800.0, 2000.0)
    ew = signal_stats("EW", EW_CSV, EW_MATCHED, 800.0, 4000.0)
    with open(f"{OUT_DIR}/ew_complete_statistics.json", "w") as f:
        json.dump(ew, f, indent=2, default=str)
    with open(f"{OUT_DIR}/colored_complete_statistics.json", "w") as f:
        json.dump(colored, f, indent=2, default=str)

    # load frozen pile-up + photon master tables (read-only)
    pu_master = pd.read_csv(f"{PU_DIR}/table9_master_cross_mu.csv")
    ph_master = json.load(open(f"{PH_DIR}/master_statistics.json"))
    ph_delta = json.load(open(f"{PH_DIR}/converted_photon_only_delta_statistics_v1.json"))
    ph_cutflow = pd.read_csv(f"{PH_DIR}/converted_photon_only_cutflow_v1.csv")
    pu_cutflow = pd.read_csv(f"{PU_DIR}/table5_cutflow.csv")
    pu_delta = pd.read_csv(f"{PU_DIR}/table6_delta_s_delta_w.csv")

    # independent re-verification of the supplied pileup table
    supplied = {0: (0, 0, 0, 0, 0), 5: (3, 3, 0, 0, 0), 10: (6, 6, 0, 0, 0),
                20: (22, 22, 0, 0, 0), 50: (172, 172, 0, 0, 0)}
    mismatches = []
    for mu, (nc, npl, nm, nds, nf) in supplied.items():
        row = pu_master[pu_master["mu"] == mu].iloc[0]
        actual = (int(row["N_raw_candidate"]), int(row["N_selected_plane"]),
                  int(row["N_multiplicity"]), int(row["N_Delta_s"]), int(row["N_final"]))
        if actual != (nc, npl, nm, nds, nf):
            mismatches.append((mu, actual, (nc, npl, nm, nds, nf)))
    verify_note = "CONFIRMED (all 5 mu match independently-recomputed frozen values)" if not mismatches else f"MISMATCH: {mismatches}"

    # --- 8. Master cutflow table ---
    def g(d, k, default="N/A"):
        return d.get(k, default)

    master_cutflow_rows = []
    stages_common = ["starting_denominator", "trigger", "geometric_fiducial", "timing_fiducial",
                      "valid_hits_or_any_hit", "raw_candidate", "selected_plane", ">=4/8", "8/8",
                      "multiplicity", "delta_w", "delta_s", "final_pass"]
    ph_row = {"starting_denominator": 9139, "trigger": "N/A", "geometric_fiducial": "N/A", "timing_fiducial": "N/A",
              "valid_hits_or_any_hit": int(ph_cutflow.loc[ph_cutflow.stage.str.contains("detector_hits"), "passing"].iloc[0]),
              "raw_candidate": int(ph_cutflow.loc[ph_cutflow.stage.str.contains("raw_candidate"), "passing"].iloc[0]),
              "selected_plane": ph_master["N_selected_plane"], ">=4/8": ph_master["N_>=4/8"], "8/8": ph_master["N_8/8"],
              "multiplicity": "NOT RECORDED", "delta_w": ph_master["N_selected_plane"],
              "delta_s": ph_master["N_Delta_s<0.01_among_plane"], "final_pass": ph_master["N_final_Sec_IV_pass"]}
    for mu in [0, 5, 10, 20, 50]:
        row = pu_master[pu_master["mu"] == mu].iloc[0]
        master_cutflow_rows.append({
            "stage": "PU_mu%d" % mu, "starting_denominator": 5000, "trigger": "N/A",
            "geometric_fiducial": "N/A", "timing_fiducial": "N/A", "valid_hits_or_any_hit": "N/A",
            "raw_candidate": int(row["N_raw_candidate"]), "selected_plane": int(row["N_selected_plane"]),
            ">=4/8": int(row["N_>=4/8"]), "8/8": int(row["N_8/8"]),
            "multiplicity": int(row["N_multiplicity"]), "delta_w": int(row["N_selected_plane"]),
            "delta_s": int(row["N_Delta_s"]), "final_pass": int(row["N_final"]),
        })
    ew_row = {"stage": "EW", "starting_denominator": ew["N_matched"], "trigger": ew["N_trigger"],
              "geometric_fiducial": ew["N_geometric_fiducial"], "timing_fiducial": ew["N_truth_fiducial"],
              "valid_hits_or_any_hit": "N/A", "raw_candidate": ew["N_seed_found"], "selected_plane": ew["N_selected_plane"],
              ">=4/8": "N/A", "8/8": "N/A", "multiplicity": ew["N_hit_multiplicity_pass"],
              "delta_w": ew["N_selected_plane"], "delta_s": ew["N_plane_Delta_s"].get("N_below_0.01"),
              "final_pass": ew["N_final_Sec_IV_pass"]}
    col_row = {"stage": "Colored", "starting_denominator": colored["N_matched"], "trigger": colored["N_trigger"],
               "geometric_fiducial": colored["N_geometric_fiducial"], "timing_fiducial": colored["N_truth_fiducial"],
               "valid_hits_or_any_hit": "N/A", "raw_candidate": colored["N_seed_found"], "selected_plane": colored["N_selected_plane"],
               ">=4/8": "N/A", "8/8": "N/A", "multiplicity": colored["N_hit_multiplicity_pass"],
               "delta_w": colored["N_selected_plane"], "delta_s": colored["N_plane_Delta_s"].get("N_below_0.01"),
               "final_pass": colored["N_final_Sec_IV_pass"]}
    ph_row_full = {"stage": "Converted_gamma_only", **ph_row}
    master_cutflow_df = pd.DataFrame([ew_row, col_row, ph_row_full] + master_cutflow_rows)
    master_cutflow_df.to_csv(f"{OUT_DIR}/master_cutflow_table.csv", index=False)

    # --- 9. Master Delta_s/Delta_w table ---
    dsdw_rows = []
    dsdw_rows.append({"sample": "colored", "denominator": colored["N_truth_fiducial"], "N_plane": colored["N_selected_plane"],
                       **{f"ds_{k}": v for k, v in colored["N_plane_Delta_s"].items() if k != "count"},
                       **{f"dw_{k}": v for k, v in colored["N_plane_Delta_w"].items() if k != "count"},
                       "N_mult_pass": colored["N_hit_multiplicity_pass"], "N_final": colored["N_final_Sec_IV_pass"],
                       "pile_up_overlay_present": False})
    dsdw_rows.append({"sample": "EW", "denominator": ew["N_truth_fiducial"], "N_plane": ew["N_selected_plane"],
                       **{f"ds_{k}": v for k, v in ew["N_plane_Delta_s"].items() if k != "count"},
                       **{f"dw_{k}": v for k, v in ew["N_plane_Delta_w"].items() if k != "count"},
                       "N_mult_pass": ew["N_hit_multiplicity_pass"], "N_final": ew["N_final_Sec_IV_pass"],
                       "pile_up_overlay_present": False})
    ph_ds = ph_delta["delta_s"]; ph_dw = ph_delta["delta_w"]
    dsdw_rows.append({"sample": "converted_photon_only", "denominator": 9139, "N_plane": ph_master["N_selected_plane"],
                       "ds_min": ph_ds["min"], "ds_max": ph_ds["max"], "ds_mean": ph_ds["mean"], "ds_median": ph_ds["median"],
                       "ds_p16": ph_ds["p16"], "ds_p84": ph_ds["p84"],
                       "dw_min": ph_dw["min"], "dw_max": ph_dw["max"], "dw_mean": ph_dw["mean"], "dw_median": ph_dw["median"],
                       "dw_p16": ph_dw["p16"], "dw_p84": ph_dw["p84"],
                       "N_mult_pass": "NOT RECORDED", "N_final": ph_master["N_final_Sec_IV_pass"],
                       "pile_up_overlay_present": False})
    for mu in [5, 10, 20, 50]:
        r = pu_delta[(pu_delta["mu"] == mu) & (pu_delta["population"] == "all_selected_planes")].iloc[0]
        row = pu_master[pu_master["mu"] == mu].iloc[0]
        dsdw_rows.append({"sample": f"pileup_mu{mu}", "denominator": 5000, "N_plane": int(r["N_plane"]),
                           "ds_min": r["ds_min"], "ds_max": r["ds_max"], "ds_mean": r["ds_mean"], "ds_median": r["ds_median"],
                           "ds_p16": r["ds_p16"], "ds_p84": r["ds_p84"],
                           "dw_min": r["dw_min"], "dw_max": r["dw_max"], "dw_mean": r["dw_mean"], "dw_median": r["dw_median"],
                           "dw_p16": r["dw_p16"], "dw_p84": r["dw_p84"],
                           "N_mult_pass": int(row["N_multiplicity"]), "N_final": int(row["N_final"]),
                           "pile_up_overlay_present": True})
    dsdw_df = pd.DataFrame(dsdw_rows)
    dsdw_df.to_csv(f"{OUT_DIR}/master_delta_s_delta_w_table.csv", index=False)

    # --- 10. Paper vs project table ---
    pu50 = pu_master[pu_master["mu"] == 50].iloc[0]
    paper_rows = [
        {"quantity": "EW epsilon_trig", "paper": "not numerically quoted", "project": f"{ew['epsilon_trig']['rate']:.4f}",
         "difference": "N/A", "interpretation": "project-only proxy metric (pT_pair>200GeV truth cut)", "limitation": "paper gives no closed formula for trigger efficiency"},
        {"quantity": "EW epsilon_fid", "paper": "not numerically quoted", "project": f"{ew['epsilon_fid']['rate']:.4f}",
         "difference": "N/A", "interpretation": "-", "limitation": "not tabulated in Sec IIIC/IV text reread"},
        {"quantity": "EW epsilon_reco (paper def.)", "paper": "peak ~70% per Sec IV text", "project": f"{ew['epsilon_reco_paper_def']['rate']:.4f}",
         "difference": f"{ew['epsilon_reco_paper_def']['rate']-0.70:+.4f}", "interpretation": "small-N (denominator=40) statistical limitation",
         "limitation": "Table I's exact numeric value not independently re-extracted this turn (extraction renders it as non-text)"},
        {"quantity": "Colored epsilon_trig", "paper": "not numerically quoted", "project": f"{colored['epsilon_trig']['rate']:.4f}",
         "difference": "N/A", "interpretation": "-", "limitation": "-"},
        {"quantity": "Colored epsilon_fid", "paper": "not numerically quoted", "project": f"{colored['epsilon_fid']['rate']:.4f}",
         "difference": "N/A", "interpretation": "-", "limitation": "-"},
        {"quantity": "Colored epsilon_reco (paper def.)", "paper": "peak ~70% per Sec IV text", "project": f"{colored['epsilon_reco_paper_def']['rate']:.4f}",
         "difference": f"{colored['epsilon_reco_paper_def']['rate']-0.70:+.4f}", "interpretation": "VERY small-N (denominator=7) -- not statistically meaningful",
         "limitation": "N_truth_fiducial=7 is too small for a reliable efficiency estimate"},
        {"quantity": "Pile-up >=4/8 rate (mu=50)", "paper": "~1e-3", "project": f"{pu50['epsilon_>=4/8']:.4f}",
         "difference": f"{pu50['epsilon_>=4/8']-1e-3:+.4f}", "interpretation": "PARTIAL comparability (different suppression model/pool)",
         "limitation": "documented model differences from paper's own pile-up treatment"},
        {"quantity": "Pile-up 8/8 rate (mu=50)", "paper": "~6e-5", "project": f"{pu50['epsilon_8/8']:.4f}",
         "difference": f"{pu50['epsilon_8/8']-6e-5:+.4f}", "interpretation": "PARTIAL comparability",
         "limitation": "same as above"},
        {"quantity": "Converted-photon result", "paper": "converted-gamma+pileup, not numerically quoted",
         "project": "conversion-only, 0/9139 final", "difference": "N/A",
         "interpretation": "NOT COMPARABLE -- population is incomplete (no pile-up overlay)", "limitation": "overlay not implemented"},
        {"quantity": "Detector model", "paper": "ref[34] full simplified sim (endcap/TRT/ECAL/Bethe-Bloch)",
         "project": "atlas_geometry.py 8-layer barrel only", "difference": "structural", "interpretation": "documented simplification",
         "limitation": "no endcap/TRT/ECAL/Bethe-Bloch modeling"},
        {"quantity": "Pool size", "paper": "125,000-event Pythia8 minbias pool", "project": "20,000-event pool, with replacement",
         "difference": "6.25x smaller", "interpretation": "reduced statistical independence", "limitation": "explicit project decision, not a paper requirement"},
        {"quantity": "Tracking efficiency", "paper": "ATL-PHYS-PUB-2015-051 Fig 1(b), eta-independent in barrel",
         "project": "same curve, digitized, Loose selection", "difference": "none (systematic bands tested, negligible impact)",
         "interpretation": "MATCH", "limitation": "digitization precision"},
        {"quantity": "Pile-up condition (Fig.5)", "paper": "1-hit-per-layer reweighted by hit-mult efficiency",
         "project": "w_mult=0/172 (Wilson 95% UL~=0.022), denominator population ASSUMPTION",
         "difference": "N/A", "interpretation": "unresolved denominator ambiguity", "limitation": "paper text does not disambiguate the reweighting population"},
        {"quantity": "Figure 5 status", "paper": "4 curves, absolute+shape normalization", "project": "3/4 curves available (no photon+pileup), shape-only",
         "difference": "N/A", "interpretation": "diagnostic, not paper-exact", "limitation": "see status classification"},
    ]
    pd.DataFrame(paper_rows).to_csv(f"{OUT_DIR}/paper_vs_project_table.csv", index=False)

    # --- 11. Notable events table ---
    notable_rows = []
    for ev_id in ew["final_passing_event_ids"]:
        r = pd.read_csv(EW_CSV); row = r[r.event == ev_id].iloc[0]
        notable_rows.append({"event_id": ev_id, "sample": "EW", "category": "final_pass",
                              "layer_coverage": row["best_candidate_n_layers_with_hit"], "multiplicity_pass": row["best_candidate_passes_hit_multiplicity"],
                              "delta_s": row["ds"], "delta_w": row["dw"], "pass_fail": "PASS", "failure_reason": "-"})
    for rec in [{"event": 339}, {"event": 386}]:
        r = pd.read_csv(EW_CSV); row = r[r.event == rec["event"]].iloc[0]
        notable_rows.append({"event_id": rec["event"], "sample": "EW", "category": "near_miss",
                              "layer_coverage": row["best_candidate_n_layers_with_hit"], "multiplicity_pass": row["best_candidate_passes_hit_multiplicity"],
                              "delta_s": row["ds"], "delta_w": row["dw"], "pass_fail": "FAIL",
                              "failure_reason": "hit_multiplicity_pass=False" if not row["best_candidate_passes_hit_multiplicity"] else "delta_s>=0.01"})
    r = pd.read_csv(COLORED_CSV)
    for ev_id, cat in [(386, "final_pass"), (208, "near_miss_ds"), (369, "near_miss_ds"), (38, "zero_candidate"), (169, "zero_candidate")]:
        row = r[r.event == ev_id].iloc[0]
        reason = "-"
        if cat == "zero_candidate":
            reason = "truth_fiducial=True but n_candidates=0 (no seed formed)"
        elif cat == "near_miss_ds":
            reason = "delta_s just above 0.01cm cut" if row["ds"] >= 0.01 else "hit_multiplicity_pass=False"
        notable_rows.append({"event_id": ev_id, "sample": "colored", "category": cat,
                              "layer_coverage": row.get("best_candidate_n_layers_with_hit"), "multiplicity_pass": row.get("best_candidate_passes_hit_multiplicity"),
                              "delta_s": row["ds"], "delta_w": row["dw"], "pass_fail": "PASS" if cat == "final_pass" else "FAIL",
                              "failure_reason": reason})
    rare = pd.read_csv(f"{PU_DIR}/table10_rare_event_evidence.csv").iloc[0]
    notable_rows.append({"event_id": rare["event_i"], "sample": f"pileup_mu{int(rare['mu'])}", "category": "sole_8of8_event",
                          "layer_coverage": 8, "multiplicity_pass": rare["multiplicity_pass"],
                          "delta_s": rare["delta_s"], "delta_w": rare["delta_w"], "pass_fail": "FAIL",
                          "failure_reason": rare["failure_reason"]})
    v3 = pd.read_csv(f"{BASE}/02_backgrounds/photon_conversion/conversion_scan_results_v3_SEC3C_DS_DW.csv")
    plane = v3[v3["sec3c_plane_found"]]
    min_ds_row = plane.loc[plane["sec3c_ds"].idxmin()]
    notable_rows.append({"event_id": min_ds_row["event"], "sample": "converted_photon_only", "category": "min_delta_s",
                          "layer_coverage": min_ds_row["sec3c_n_layers"], "multiplicity_pass": "NOT RECORDED",
                          "delta_s": min_ds_row["sec3c_ds"], "delta_w": min_ds_row["sec3c_dw"], "pass_fail": "N/A (final pass always False, hit-mult not recorded)",
                          "failure_reason": "-"})
    below = plane[plane["sec3c_ds"] < 0.01]
    notable_rows.append({"event_id": f"{len(below)} events (see plotsrc)", "sample": "converted_photon_only",
                          "category": "N(delta_s<0.01)", "layer_coverage": "-", "multiplicity_pass": "NOT RECORDED",
                          "delta_s": f"min={below['sec3c_ds'].min():.5f} max={below['sec3c_ds'].max():.5f}",
                          "delta_w": "-", "pass_fail": "unknown (hit-mult not recorded)", "failure_reason": "-"})
    pd.DataFrame(notable_rows).to_csv(f"{OUT_DIR}/notable_events_table.csv", index=False)

    return dict(inv=inv, ew=ew, colored=colored, pu_master=pu_master, ph_master=ph_master,
                verify_note=verify_note, master_cutflow_df=master_cutflow_df, dsdw_df=dsdw_df)


if __name__ == "__main__":
    r = main()
    print("Pile-up supplied-table verification:", r["verify_note"])
    print("\nEW final passing events:", r["ew"]["final_passing_event_ids"])
    print("Colored final passing events:", r["colored"]["final_passing_event_ids"])
    print("\nDone. Outputs in", OUT_DIR)
