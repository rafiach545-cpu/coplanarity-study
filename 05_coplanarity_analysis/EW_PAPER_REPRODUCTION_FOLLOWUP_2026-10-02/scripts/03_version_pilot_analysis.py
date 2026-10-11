#!/usr/bin/env python3
"""
Version-matched EW trigger pilot: analysis of every shower variant.

Inputs (read-only): /home/rafia/hep_tools/EW_VERSION_PILOT_2026-10-02/
  inputs/*.lhe                    LHE files (frozen MG5 3.7.3 copies; MG5 2.3.3 pilot/production)
  runs/SHOWER_<lhe>_py<ver>_S<on|off>/events.csv   driver output, one row per matched event

Per variant:
  N_LHE (generated), N_matched, matching eff, N_trigger (final status-1 pair pT > 200, strict),
  trigger/matched with binomial SE, Wilson 68/95, Clopper-Pearson 95, exact two-sided
  binomial p vs paper 0.10, Fisher exact vs the frozen baseline (EW1000+EW2000 frozen
  counts 275/1556), two-sample KS test of matched-event pair-pT vs baseline.
LHE-level: fraction of 1-jet events, parton-level pair pT > 200 fraction, matching
efficiency per multiplicity, origin multiplicity of trigger events.
"""
import glob
import json
import math
import os
import re
import numpy as np
import pandas as pd
from scipy import stats

PILOT = "/home/rafia/hep_tools/EW_VERSION_PILOT_2026-10-02"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
AUD = "/home/rafia/coplanarity_study/05_coplanarity_analysis/EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/tables"
FROZEN_TRIG, FROZEN_MATCHED = 89 + 186, 511 + 1045


def read_lhe(path):
    ev, cur, inev = [], None, False
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s.startswith("<event"):
                inev, cur = True, []
                continue
            if s.startswith("</event"):
                inev = False
                n = int(cur[0].split()[0])
                parts = [l.split() for l in cur[1:1 + n]]
                q = [p for p in parts if abs(int(p[0])) == 9000011]
                jets = [p for p in parts if int(p[1]) == 1 and abs(int(p[0])) != 9000011]
                ev.append(dict(lhe_idx=len(ev), n_jets=len(jets),
                               pair_pt=math.hypot(float(q[0][6]) + float(q[1][6]), float(q[0][7]) + float(q[1][7])),
                               k=tuple(sorted([(round(float(x[6]), 2), round(float(x[8]), 2)) for x in q]))))
                continue
            if inev and s and not s.startswith("<"):
                cur.append(s)
    return pd.DataFrame(ev)


def wilson(k, n, z):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return c - h, c + h


def cp(k, n):
    return (0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1),
            1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k))


def main():
    # frozen baseline pT spectrum (matched events) for KS
    base = pd.concat([pd.read_csv(f"{AUD}/EW1000_hepmc_events.csv"),
                      pd.read_csv(f"{AUD}/EW2000_hepmc_events.csv")])["pair_pt_final_status1"].to_numpy()
    lhe_cache, rows, spectra = {}, [], {}
    for d in sorted(glob.glob(f"{PILOT}/runs/SHOWER_*")):
        name = os.path.basename(d)
        m = re.match(r"SHOWER_(.+)_py(\d+)_S(on|off)$", name)
        lhe_tag, py, S = m.group(1), m.group(2), m.group(3)
        lhe_path = f"{PILOT}/inputs/{lhe_tag}.lhe"
        if lhe_tag not in lhe_cache:
            lhe_cache[lhe_tag] = read_lhe(lhe_path)
        L = lhe_cache[lhe_tag]
        e = pd.read_csv(f"{d}/events.csv")
        assert (e.n_final_quirks == 2).all()
        key = {k: i for i, k in enumerate(L.k)}
        e["lhe_idx"] = [key.get(tuple(sorted([(round(a, 2), round(b, 2)), (round(c, 2), round(dd, 2))])))
                        for a, b, c, dd in zip(e.h_px1, e.h_pz1, e.h_px2, e.h_pz2)]
        e["n_jets"] = e.lhe_idx.map(L.n_jets)
        n, k = len(e), int((e.pair_pt_final > 200).sum())
        w68, w95, c95 = wilson(k, n, 1.0), wilson(k, n, 1.959964), cp(k, n)
        fis = stats.fisher_exact([[k, n - k], [FROZEN_TRIG, FROZEN_MATCHED - FROZEN_TRIG]])
        ks = stats.ks_2samp(e.pair_pt_final.to_numpy(), base)
        lhe_ver = "MG5 2.3.3" if "233" in lhe_tag else "MG5 3.7.3"
        valid = not ("233" in lhe_tag and S == "on")
        r = dict(variant=name, lhe=lhe_tag, me_generator=lhe_ver, pythia=f"8.{py[1:]}", S_prodScalesFromLHEF=S,
                 valid_combination=valid,
                 N_LHE=len(L), LHE_frac_1jet=float((L.n_jets == 1).mean()),
                 LHE_frac_pairpt_gt200=float((L.pair_pt > 200).mean()),
                 N_matched=n, matching_eff=n / len(L),
                 match_eff_0jet=float(e.n_jets.eq(0).sum() / (L.n_jets == 0).sum()),
                 match_eff_1jet=float(e.n_jets.eq(1).sum() / (L.n_jets == 1).sum()),
                 n_unmapped=int(e.lhe_idx.isna().sum()),
                 N_trigger=k, trig_over_matched=k / n, binom_se=math.sqrt(k / n * (1 - k / n) / n),
                 wilson68_lo=w68[0], wilson68_hi=w68[1], wilson95_lo=w95[0], wilson95_hi=w95[1],
                 cp95_lo=c95[0], cp95_hi=c95[1],
                 p_exact_vs_paper_0p10=stats.binomtest(k, n, 0.10).pvalue,
                 fisher_p_vs_frozen_275_1556=fis[1],
                 trig_from_1jet=int(((e.pair_pt_final > 200) & e.n_jets.eq(1)).sum()),
                 ks_D_vs_frozen=ks.statistic, ks_p_vs_frozen=ks.pvalue,
                 median_pair_pt=float(e.pair_pt_final.median()),
                 hard_status23_trig_over_matched=float((e.pair_pt_hard > 200).mean()))
        rows.append(r)
        spectra[name] = np.histogram(e.pair_pt_final, bins=[0, 25, 50, 75, 100, 150, 200, 300, 400, 600, 1000, 5000])[0].tolist()
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/version_pilot_variants.csv", index=False)
    json.dump(dict(bins=[0, 25, 50, 75, 100, 150, 200, 300, 400, 600, 1000, 5000], counts=spectra,
                   frozen_baseline=np.histogram(base, bins=[0, 25, 50, 75, 100, 150, 200, 300, 400, 600, 1000, 5000])[0].tolist()),
              open(f"{OUT}/version_pilot_pairpt_spectra.json", "w"), indent=1)
    pd.set_option("display.width", 300, "display.max_columns", 50)
    cols = ["variant", "valid_combination", "N_LHE", "LHE_frac_1jet", "N_matched", "matching_eff", "match_eff_0jet",
            "match_eff_1jet", "N_trigger", "trig_over_matched", "wilson95_lo", "wilson95_hi",
            "p_exact_vs_paper_0p10", "fisher_p_vs_frozen_275_1556", "ks_p_vs_frozen", "n_unmapped"]
    print(df[cols].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
