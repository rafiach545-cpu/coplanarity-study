#!/usr/bin/env python3
"""
Part B trigger screen analysis. Reads /home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/runs/<ID>/<EW|COL>/
(settings.cmd, events.csv, run.log) and the LHE inputs, and reports per configuration:
  N_LHE, N_matched, N_trigger, eps = trigger/matched, SE, Wilson 68/95, CP95,
  exact two-sided binomial p vs paper (EW 0.10, COL 0.24), Fisher vs B0 (same benchmark),
  joint compatibility = paper inside Wilson 95% for BOTH benchmarks.
"""
import math, os, re, glob, json
import numpy as np, pandas as pd
from scipy import stats

W = "/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
PAPER = {"EW": 0.10, "COL": 0.24}


def wil(k, n, z):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h


def lhe_count(path):
    n = 0
    with open(path) as f:
        for l in f:
            if l.lstrip().startswith("<event"):
                n += 1
    return n


def main():
    rows = []
    base = {}
    for d in sorted(glob.glob(f"{W}/runs/*/*/events.csv")):
        B = d.split("/")[-2]; ID = d.split("/")[-3]
        st = open(os.path.dirname(d) + "/settings.cmd").read()
        lhe = re.search(r"Beams:LHEF = (\S+)", st).group(1)
        e = pd.read_csv(d)
        assert (e.n_final_quirks == 2).all(), d
        n, k = len(e), int((e.pair_pt_final > 200).sum())
        nl = lhe_count(lhe)
        w68, w95 = wil(k, n, 1.0), wil(k, n, 1.959964)
        c = (stats.beta.ppf(0.025, k, n - k + 1), stats.beta.ppf(0.975, k + 1, n - k))
        r = dict(config=ID, bench=B, lhe=os.path.basename(lhe), N_LHE=nl, N_matched=n, match_eff=n / nl,
                 N_trigger=k, eps_trig=k / n, se=math.sqrt(k / n * (1 - k / n) / n),
                 w68_lo=w68[0], w68_hi=w68[1], w95_lo=w95[0], w95_hi=w95[1], cp95_lo=c[0], cp95_hi=c[1],
                 paper=PAPER[B], p_vs_paper=stats.binomtest(k, n, PAPER[B]).pvalue,
                 paper_in_w95=bool(w95[0] <= PAPER[B] <= w95[1]),
                 eps_trig_over_generated=k / nl,
                 overrides=" | ".join(l for l in st.splitlines() if l and not l.startswith("!") and l not in open(f"{W}/runs/base_{B}.cmd").read() and not l.startswith("Beams:LHEF")),
                 pt_hash=float(e.pair_pt_final.sum()))
        rows.append(r)
        if ID == "B0_frozenLHE":
            base[B] = (k, n)
    df = pd.DataFrame(rows)
    df["fisher_p_vs_B0"] = [stats.fisher_exact([[r.N_trigger, r.N_matched - r.N_trigger],
                                                [base[r.bench][0], base[r.bench][1] - base[r.bench][0]]])[1]
                            for r in df.itertuples()]
    j = df.pivot_table(index="config", columns="bench", values="paper_in_w95", aggfunc="first")
    df["joint_compatible"] = df.config.map(lambda c: bool(j.loc[c].all()) if c in j.index and j.loc[c].notna().all() else False)
    df.to_csv(f"{OUT}/trigger_screen_results.csv", index=False)
    pd.set_option("display.width", 250, "display.max_colwidth", 60)
    t = df.pivot_table(index="config", columns="bench", values=["eps_trig", "N_matched", "p_vs_paper", "fisher_p_vs_B0"], aggfunc="first")
    print(t.round(4).to_string())
    print("\nJOINT-COMPATIBLE:", sorted(df[df.joint_compatible].config.unique()))
    s = df.set_index(["config", "bench"])
    for c in ("S8_pTmaxMatch1", "S9_pTmaxMatch2"):
        if (c, "EW") in s.index:
            print(c, "identical to B0 (pT sum EW, COL):",
                  s.loc[(c, "EW"), "pt_hash"] == s.loc[("B0_frozenLHE", "EW"), "pt_hash"],
                  s.loc[(c, "COL"), "pt_hash"] == s.loc[("B0_frozenLHE", "COL"), "pt_hash"])


if __name__ == "__main__":
    main()
