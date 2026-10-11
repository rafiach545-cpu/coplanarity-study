#!/usr/bin/env python3
"""Pre-registered trigger combination test (trigger_combinations/PREREGISTERED_COMBINATIONS.md, sha256 b7112dc2...).
Same definition as the one-at-a-time screen (PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/scripts/06_trigger_screen_analysis.py):
eps_trig = N(final-state pair pT > 200 GeV) / N(matched), Wilson 95%, exact binomial p vs paper (EW 0.10, colored 0.24).
Pass = paper inside Wilson 95% for BOTH benchmarks. Reads hep_tools runs C1..C6; writes tables/trigger_combinations.csv only."""
import os, re, math, pandas as pd, numpy as np
from scipy import stats
W = "/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02"; T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
PAPER = {"EW": 0.10, "COL": 0.24}
DESC = {"C1": "xqcut 60 + cteq6l1 + scalefact 2", "C2": "C1 + production scales off", "C3": "C1 + showerKt", "C4": "C1 + showerKt + production scales off",
        "C5": "0 jets, no matching + cteq6l1 + scalefact 2 (contradicts paper)", "C6": "C5 + production scales off (contradicts paper)"}
def wil(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h
rows = []
for c in ["C1", "C2", "C3", "C4", "C5", "C6"]:
    for b in ["EW", "COL"]:
        e = pd.read_csv(f"{W}/runs/{c}/{b}/events.csv"); assert (e.n_final_quirks == 2).all()
        n, k = len(e), int((e.pair_pt_final > 200).sum()); lo, hi = wil(k, n)
        lhe = re.search(r"Beams:LHEF = (\S+)", open(f"{W}/runs/{c}/{b}/settings.cmd").read()).group(1)
        rows.append(dict(config=c, description=DESC[c], bench=b, lhe=os.path.basename(lhe), N_matched=n, N_trigger=k, eps_trig=k / n, se=math.sqrt(k / n * (1 - k / n) / n),
                         w95_lo=lo, w95_hi=hi, paper=PAPER[b], p_vs_paper=stats.binomtest(k, n, PAPER[b]).pvalue, paper_in_w95=bool(lo <= PAPER[b] <= hi)))
d = pd.DataFrame(rows)
j = d.pivot_table(index="config", columns="bench", values="paper_in_w95", aggfunc="first"); d["joint_pass"] = d.config.map(j.EW & j.COL)
r = d.pivot_table(index="config", columns="bench", values="eps_trig"); d["ratio_EW_over_COL"] = d.config.map(r.EW / r.COL)
d.to_csv(f"{T}/trigger_combinations.csv", index=False)
print(d[["config", "bench", "N_trigger", "N_matched", "eps_trig", "w95_lo", "w95_hi", "p_vs_paper", "paper_in_w95", "joint_pass", "ratio_EW_over_COL"]].round(4).to_string())
