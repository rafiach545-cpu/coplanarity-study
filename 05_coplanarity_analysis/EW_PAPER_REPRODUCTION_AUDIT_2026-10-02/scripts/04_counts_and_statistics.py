#!/usr/bin/env python3
"""
Counts and statistics for the EW benchmark (mQ=800 GeV, Lambda=4 keV).

Every count is recomputed here from event-level evidence:
  generated / matched / trigger : raw LHE + HepMC (01_raw_event_recount.py tables)
  fiducial / plane / final      : project per-event CSVs, joined to the raw
                                  trigger set by event id (closure is asserted)
Cached summary files are NOT read.

Statistics per efficiency k/n:
  binomial SE sqrt(p(1-p)/n); Wilson 68.27% and 95%; Clopper-Pearson 95%;
  exact two-sided binomial p-value vs the paper value (scipy binomtest,
  'two-sided' = sum of outcomes no more likely than observed);
  Fisher exact test EW1000 vs EW2000 (2x2).
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

AUD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T = f"{AUD}/tables"
BASE = "/home/rafia/coplanarity_study/05_coplanarity_analysis"
PAPER = {"trigger": 0.10, "fiducial": 0.28, "plane_given_fiducial": 0.72, "secIV_given_fiducial": 0.72}


def wilson(k, n, z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z / d * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, c - h), min(1.0, c + h)


def cp95(k, n):
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    return lo, hi


def row(sample, name, k, n, paper=None):
    p = k / n
    w68 = wilson(k, n, stats.norm.ppf(0.5 + 0.6827 / 2))
    w95 = wilson(k, n, 1.959964)
    c95 = cp95(k, n)
    r = dict(sample=sample, efficiency=name, k=k, n=n, p_hat=p, binom_se=np.sqrt(p * (1 - p) / n),
             wilson68_lo=w68[0], wilson68_hi=w68[1], wilson95_lo=w95[0], wilson95_hi=w95[1],
             cp95_lo=c95[0], cp95_hi=c95[1], paper_value=paper)
    if paper is not None:
        r["exact_binom_p_two_sided_vs_paper"] = stats.binomtest(k, n, paper, alternative="two-sided").pvalue
        r["paper_inside_wilson95"] = bool(w95[0] <= paper <= w95[1])
        r["paper_inside_cp95"] = bool(c95[0] <= paper <= c95[1])
    return r


def stage_counts():
    out = {}
    # ---- EW2000 ----
    hep = pd.read_csv(f"{T}/EW2000_hepmc_events.csv")
    trig_ids = set(hep.loc[hep["trigger_strict_gt200_final"], "hepmc_seq"].astype(int))
    d = f"{BASE}/quirk_2000_event_fresh_regeneration_v1"
    te = pd.read_csv(f"{d}/events/EW_800GeV_L4keV/trigger_passing_events.csv")
    pe = pd.read_csv(f"{d}/reconstruction/EW_800GeV_L4keV/per_event_results.csv")
    te["row_index"] = np.arange(len(te))
    m = te[["row_index", "hepmc_event_idx"]].merge(pe, on="row_index", validate="1:1")
    assert set(m["hepmc_event_idx"].astype(int)) == trig_ids, "EW2000 closure: per-event set != raw trigger set"
    fid = m["truth_fiducial"].astype(bool)
    plane = m["sec3c_plane_found"].astype(bool)
    final = m["final_sec_iv_pass"].astype(bool)
    assert not (final & ~fid).any(), "EW2000: final pass outside fiducial"
    out["EW2000"] = dict(
        generated=2000 if len(pd.read_csv(f"{T}/EW2000_lhe_events.csv")) == 2000 else None,
        matched=len(hep), trigger=len(trig_ids), fiducial=int(fid.sum()),
        fid_and_plane=int((fid & plane).sum()), fid_and_final=int((fid & final).sum()),
        plane_any_trigger_STALE_DEFINITION=int(plane.sum()),
        plane_found_outside_fiducial=int((plane & ~fid).sum()),
        technical_exceptions=int((m["status"] == "error").sum()))
    # ---- EW1000 ----
    hep1 = pd.read_csv(f"{T}/EW1000_hepmc_events.csv")
    trig1 = set(hep1.loc[hep1["trigger_strict_gt200_final"], "hepmc_seq"].astype(int))
    pe1 = pd.read_csv(f"{BASE}/ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv")
    assert set(pe1["event"].astype(int)) == trig1, "EW1000 closure: per-event set != raw trigger set"
    fid1 = pe1["truth_fiducial"].astype(bool)
    plane1 = pe1["seed_found"].astype(bool)
    final1 = pe1["passes_signal_region"].astype(bool)
    assert not (final1 & ~fid1).any(), "EW1000: final pass outside fiducial"
    out["EW1000"] = dict(
        generated=len(pd.read_csv(f"{T}/EW1000_lhe_events.csv")),
        matched=len(hep1), trigger=len(trig1), fiducial=int(fid1.sum()),
        fid_and_plane=int((fid1 & plane1).sum()), fid_and_final=int((fid1 & final1).sum()),
        plane_any_trigger_STALE_DEFINITION=int(plane1.sum()),
        plane_found_outside_fiducial=int((plane1 & ~fid1).sum()),
        plane_column_used="seed_found (= >=1 candidate after seeding+iterative fit incl. final dw<1cm)")
    out["EW2000"]["generated"] = len(pd.read_csv(f"{T}/EW2000_lhe_events.csv"))
    return out


def main():
    c = stage_counts()
    rows = []
    for s in ("EW1000", "EW2000"):
        x = c[s]
        rows += [row(s, "matching = matched/generated", x["matched"], x["generated"]),
                 row(s, "trigger = trigger/matched", x["trigger"], x["matched"], PAPER["trigger"]),
                 row(s, "fiducial = fiducial/trigger", x["fiducial"], x["trigger"], PAPER["fiducial"]),
                 row(s, "plane = (fid AND plane)/fiducial", x["fid_and_plane"], x["fiducial"], PAPER["plane_given_fiducial"]),
                 row(s, "SecIV = (fid AND final)/fiducial", x["fid_and_final"], x["fiducial"], PAPER["secIV_given_fiducial"]),
                 row(s, "REJECTED stale: plane(any trigger)/fiducial", x["plane_any_trigger_STALE_DEFINITION"], x["fiducial"]),
                 row(s, "trigger/generated (undocumented-denominator hypothesis)", x["trigger"], x["generated"], PAPER["trigger"])]
    # fiducial variants from the replay
    for s in ("EW1000", "EW2000", "COL2000"):
        f = f"{T}/{s}_fiducial_variants_per_event.csv"
        if not os.path.exists(f):
            continue
        v = pd.read_csv(f)
        for col in ("A_project_baseline", "B_finite_barrel_nominal", "B2_finite_barrel_sct80",
                    "C_eta1p8_and_finite_barrel", "A0_baseline_no_vertex_smear"):
            rows.append(row(s, f"fiducial variant {col}", int(v[col].sum()), len(v), PAPER["fiducial"]))
    # pooled EW
    ew = [pd.read_csv(f"{T}/{s}_fiducial_variants_per_event.csv") for s in ("EW1000", "EW2000")]
    pool = pd.concat(ew)
    for col in ("A_project_baseline", "B_finite_barrel_nominal", "C_eta1p8_and_finite_barrel"):
        rows.append(row("EW1000+EW2000", f"fiducial variant {col}", int(pool[col].sum()), len(pool), PAPER["fiducial"]))
    t = c["EW1000"]["trigger"] + c["EW2000"]["trigger"]
    mm = c["EW1000"]["matched"] + c["EW2000"]["matched"]
    rows.append(row("EW1000+EW2000", "trigger = trigger/matched", t, mm, PAPER["trigger"]))
    tr = json.load(open(f"{T}/trigger_variants_summary.json"))
    for s in ("EW1000", "EW2000"):
        rows.append(row(s, "trigger variant T2 hard-process status-23 pT>200 / matched", tr[s]["N_T2"], tr[s]["N_matched"], PAPER["trigger"]))
    for s in ("COL1000", "COL2000"):
        rows.append(row(s, "COLORED trigger/matched (cross-check)", tr[s]["N_trigger_pair_pt_gt200"], tr[s]["N_hepmc_events"], 0.24))
        rows.append(row(s, "COLORED trigger/generated (cross-check)", tr[s]["N_trigger_pair_pt_gt200"], tr[s]["N_generated"], 0.24))

    df = pd.DataFrame(rows)
    df.to_csv(f"{T}/efficiency_statistics.csv", index=False)

    fis = []
    pairs = [("matching", "matched", "generated"), ("trigger", "trigger", "matched"),
             ("fiducial", "fiducial", "trigger"), ("plane|fid", "fid_and_plane", "fiducial"),
             ("SecIV|fid", "fid_and_final", "fiducial")]
    for name, k, n in pairs:
        a, b = c["EW1000"], c["EW2000"]
        tab = [[a[k], a[n] - a[k]], [b[k], b[n] - b[k]]]
        odds, p = stats.fisher_exact(tab, alternative="two-sided")
        fis.append(dict(efficiency=name, EW1000=f"{a[k]}/{a[n]}", EW2000=f"{b[k]}/{b[n]}",
                        p1=a[k] / a[n], p2=b[k] / b[n], fisher_odds_ratio=odds, fisher_p_two_sided=p))
    pd.DataFrame(fis).to_csv(f"{T}/fisher_stability_1000_vs_2000.csv", index=False)
    json.dump(c, open(f"{T}/stage_counts_recomputed.json", "w"), indent=2)
    pd.set_option("display.width", 250)
    print(json.dumps(c, indent=2))
    print(df[["sample", "efficiency", "k", "n", "p_hat", "binom_se", "wilson95_lo", "wilson95_hi",
              "cp95_lo", "cp95_hi", "paper_value", "exact_binom_p_two_sided_vs_paper"]].to_string(index=False))
    print(pd.DataFrame(fis).to_string(index=False))


if __name__ == "__main__":
    main()
