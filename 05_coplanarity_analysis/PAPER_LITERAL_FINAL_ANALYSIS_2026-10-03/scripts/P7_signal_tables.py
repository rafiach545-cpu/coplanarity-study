#!/usr/bin/env python3
"""
Phases 6-7: Table I signal results, each frozen sample SEPARATELY (no pooling for the primary comparison).

LITERAL configuration: geometry B (finite barrel, ref [27]), SCT 34 um R-phi / 1160 um z, Delta_w per Eqs. 10-11
(W1), literal Sec. III C algorithm, full Sec. IV signal region.
Systematic variants: geometry A; SCT z 580 / 34 / 0 um; Delta_w convention W2.

Trigger numerators/denominators come from this directory's independent raw LHE/HepMC recount (P3_raw_trigger.py).
Statistics: binomial SE, Wilson 68 / 95, Clopper-Pearson 95, exact two-sided binomial p vs the paper's quoted
central value. The paper publishes no raw counts or uncertainties: exact paper-vs-project significance
cannot be fully determined.
"""
import json, math, os
import numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
B5 = "/home/rafia/coplanarity_study/05_coplanarity_analysis"
PAPER = {"EW": dict(trigger=0.10, fiducial=0.28, reconstruction=0.72), "COL": dict(trigger=0.24, fiducial=0.28, reconstruction=0.35)}
RAW = json.load(open(f"{T}/P3_raw_trigger_recount.json"))      # Phase 3 independent raw recount (this directory)
GEN = {k: (v["generated"], v["matched"], v["trigger_final"]) for k, v in RAW.items()}


def statrow(k, n, paper):
    p = k / n
    def wil(z):
        d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h
    w68, w95 = wil(1.0), wil(1.959964)
    cp = (stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0, stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0)
    return dict(N_pass=k, N_total=n, eff=p, percent=100 * p, binom_se=math.sqrt(p * (1 - p) / n),
                wilson68_lo=w68[0], wilson68_hi=w68[1], wilson95_lo=w95[0], wilson95_hi=w95[1], cp95_lo=cp[0], cp95_hi=cp[1],
                paper=paper, paper_inside_wilson95=bool(w95[0] <= paper <= w95[1]), paper_inside_cp95=bool(cp[0] <= paper <= cp[1]),
                p_exact_vs_paper_quoted=stats.binomtest(k, n, paper).pvalue)


def main():
    d = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
    for c in ("fid", "plane", "mult", "dw_pass", "ds_pass", "final"):
        d[c] = d[c].fillna(False).astype(bool)
    eff, cut, closure, raw = [], [], [], []
    for s in ("COL1000", "COL2000", "EW1000", "EW2000"):
        B = "EW" if s.startswith("EW") else "COL"
        gen, matched, trig = GEN[s]
        raw.append(dict(sample=s, generated=gen, showered=gen, matched=matched, trigger=trig,
                        trigger_events_analysed=int(d[(d["sample"] == s)].key.nunique()),
                        note=("colored analysed events = trigger AND both R-hadrons non-zero charge" if B == "COL" else "")))
        for (g, sc, w), x in d[d["sample"] == s].groupby(["geom", "sct", "wconv"]):
            label = "LITERAL" if (g, sc, w) == ("B", "Z1160", "W1") else "systematic"
            f = x[x.fid]
            rows = [("trigger", trig, matched), ("fiducial", len(f), len(x)), ("reconstruction (full Sec. IV SR)", int(f.final.sum()), len(f)),
                    ("DIAGNOSTIC plane-found only (NOT Table I eps_reco)", int(f.plane.sum()), len(f))]
            for q, k, n in rows:
                pv = PAPER[B]["trigger" if q == "trigger" else "fiducial" if q == "fiducial" else "reconstruction"]
                eff.append(dict(sample=s, benchmark=B, config=label, geometry=g, sct_z=sc, dw_convention=w, quantity=q, **statrow(k, n, pv)))
            # cutflow with lost event IDs
            stages = [("trigger (analysed)", x), ("fiducial", f), ("plane found", f[f.plane]), ("hit multiplicity", f[f.plane & f.mult]),
                      ("Delta_w < cut", f[f.plane & f.mult & f.dw_pass]), ("Delta_s < 0.01 cm", f[f.plane & f.mult & f.dw_pass & f.ds_pass]),
                      ("final Sec. IV", f[f.final])]
            prev = None
            for j, (nm, y) in enumerate(stages):
                ids = set(y.event_id.astype(int))
                lost = sorted(prev - ids) if prev is not None else []
                cut.append(dict(sample=s, config=label, geometry=g, sct_z=sc, dw_convention=w, step=j, stage=nm, events=len(ids),
                                lost_here=len(lost), lost_event_ids=" ".join(map(str, lost))))
                if prev is not None:
                    closure.append(dict(sample=s, geometry=g, sct_z=sc, dw_convention=w, stage=nm, subset_of_previous=ids <= prev,
                                        duplicates=int(y.event_id.duplicated().sum())))
                prev = ids
            assert set(f[f.final].event_id) <= set(f.event_id)
    E = pd.DataFrame(eff); E.to_csv(f"{T}/signal_efficiency_statistics.csv", index=False)
    pd.DataFrame(cut).to_csv(f"{T}/signal_cutflow_with_event_ids.csv", index=False)
    C = pd.DataFrame(closure); C.to_csv(f"{T}/signal_event_closure.csv", index=False)
    pd.DataFrame(raw).to_csv(f"{T}/signal_raw_counts.csv", index=False)
    assert C.subset_of_previous.all() and (C.duplicates == 0).all()
    # stale-value guard: contaminated numerators 84 (EW2000) / 20 (COL2000) must not appear as fiducial-intersection plane counts
    lit = E[(E.config == "LITERAL")]
    pd.set_option("display.width", 250)
    print(lit[["sample", "quantity", "N_pass", "N_total", "percent", "wilson95_lo", "wilson95_hi", "cp95_lo", "cp95_hi", "paper", "paper_inside_wilson95", "p_exact_vs_paper_quoted"]].round(4).to_string(index=False))
    print("\nclosure: all conditional numerators subsets, no duplicates:", bool(C.subset_of_previous.all() and (C.duplicates == 0).all()))
    sy = E[E.quantity.str.startswith("reconstruction") | (E.quantity == "fiducial")].pivot_table(index=["sample", "quantity", "geometry", "dw_convention"], columns="sct_z", values="eff")
    print(sy.round(3).to_string())


if __name__ == "__main__":
    main()
