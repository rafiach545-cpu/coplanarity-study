#!/usr/bin/env python3
"""
Summarise the pre-registered reconstruction variants (tables/variant_event_results.csv).

Per (benchmark, sample-set, model, alg):
  plane/fid and finalSR/fid with SE, Wilson 68/95, Clopper-Pearson 95, exact two-sided
  binomial p vs Table I (EW 0.72, colored 0.35)
Event-level changes vs R0/A0 with old/new first-failed requirement.
Fig. 5 shape test (paper histograms extracted by 00_extract_paper_fig5.py): our selected-plane
Delta_s / Delta_w (plane-found fiducial events) histogrammed in the paper's own log bins,
restricted to the plotted range; reported: fraction < cut, median, max |CDF difference|.
"""
import json
import math
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
T = f"{HERE}/../tables"
PAPER = {"EW": 0.72, "COL": 0.35}


def wil(k, n, z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return c - h, c + h


def cp(k, n):
    return (0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1), 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k))


def effrow(k, n, paper):
    w68, w95, c = wil(k, n, 1.0), wil(k, n, 1.959964), cp(k, n)
    return dict(k=k, n=n, eff=k / n, se=math.sqrt(k / n * (1 - k / n) / n), w68_lo=w68[0], w68_hi=w68[1],
                w95_lo=w95[0], w95_hi=w95[1], cp95_lo=c[0], cp95_hi=c[1],
                p_vs_tableI=stats.binomtest(k, n, paper).pvalue, paper=paper,
                paper_in_w95=bool(w95[0] <= paper <= w95[1]))


def shape(vals, hist, cut, lo_edge):
    """Compare our values with a paper histogram on the paper's own bins (plotted range only)."""
    edges = [b["lo"] for b in hist] + [hist[-1]["hi"]]
    ph = np.array([b["height"] for b in hist])
    ours = np.histogram(vals, bins=edges)[0].astype(float)
    if ours.sum() == 0:
        return dict(n_in_range=0)
    pc, oc = np.cumsum(ph) / ph.sum(), np.cumsum(ours) / ours.sum()
    return dict(n_in_range=int(ours.sum()), n_below_plot=int((np.array(vals) < lo_edge).sum()),
                frac_lt_cut_ours=float((np.array(vals) < cut).mean()),
                median_ours=float(np.median(vals)), max_cdf_diff_vs_paper=float(np.max(np.abs(pc - oc))))


def main():
    v = pd.read_csv(f"{T}/variant_event_results.csv")
    fig = json.load(open(f"{T}/paper_fig5_extracted.json"))
    v["bench"] = v["sample"].str[:3].replace({"EW1": "EW", "EW2": "EW", "COL": "COL"})
    v.loc[v["sample"].str.startswith("EW"), "bench"] = "EW"
    v.loc[v["sample"].str.startswith("COL"), "bench"] = "COL"
    rows, shp = [], []
    sets = {"EW1000": ["EW1000"], "EW2000": ["EW2000"], "EW pooled": ["EW1000", "EW2000"],
            "COL1000": ["COL1000"], "COL2000": ["COL2000"], "COL pooled": ["COL1000", "COL2000"]}
    for (m, a), g in v.groupby(["model", "alg"]):
        for name, ss in sets.items():
            x = g[g["sample"].isin(ss)]
            b = "EW" if name.startswith("EW") else "COL"
            n = len(x)
            for what, col in (("plane|fid", "plane"), ("finalSR|fid", "final")):
                rows.append(dict(model=m, alg=a, set=name, quantity=what, **effrow(int(x[col].sum()), n, PAPER[b])))
            ff = x.first_failure.value_counts().to_dict()
            rows[-1]["first_failure_counts"] = json.dumps(ff)
        for b, lab in (("EW", "EW Quirk"), ("COL", "Colored Quirk")):
            x = g[(g.bench == b) & g.plane]
            for var, col, cut in (("delta_s_cm", "ds", 0.01), ("delta_w_cm", "dw", 1.0)):
                h = fig[var]["histograms"][lab]
                shp.append(dict(model=m, alg=a, bench=b, variable=var, n_plane=len(x),
                                paper_frac_lt_cut=float(sum(t["height"] for t in h if t["hi"] <= cut * 1.0001) / sum(t["height"] for t in h)),
                                paper_median_bin=None, **shape(x[col].to_numpy(), h, cut, h[0]["lo"])))
    eff = pd.DataFrame(rows)
    eff.to_csv(f"{T}/variant_efficiencies.csv", index=False)
    sh = pd.DataFrame(shp)
    sh.to_csv(f"{T}/variant_fig5_shape_comparison.csv", index=False)

    base = v[(v.model == "R0") & (v.alg == "A0")].set_index(["sample", "key"])
    ch = []
    for (m, a), g in v.groupby(["model", "alg"]):
        if (m, a) == ("R0", "A0"):
            continue
        gg = g.set_index(["sample", "key"])
        for idx, r in gg.iterrows():
            b0 = base.loc[idx]
            if bool(r.final) != bool(b0.final) or bool(r.plane) != bool(b0.plane):
                ch.append(dict(model=m, alg=a, sample=idx[0], key=idx[1], event_id=int(r.event_id),
                               plane_R0A0=bool(b0.plane), plane_variant=bool(r.plane),
                               final_R0A0=bool(b0.final), final_variant=bool(r.final),
                               first_failure_R0A0=b0.first_failure, first_failure_variant=r.first_failure,
                               ds_R0A0=b0.ds, ds_variant=r.ds, layers_R0A0=b0.sel_layer_counts,
                               layers_variant=r.sel_layer_counts))
    pd.DataFrame(ch).to_csv(f"{T}/variant_changed_events.csv", index=False)

    pd.set_option("display.width", 250)
    pv = eff[eff.set.isin(["EW pooled", "COL pooled"])].pivot_table(index=["model", "alg"], columns=["set", "quantity"], values="eff")
    print(pv.round(3).to_string())
    print()
    print(sh[sh.variable == "delta_s_cm"][["model", "alg", "bench", "n_plane", "paper_frac_lt_cut", "frac_lt_cut_ours",
                                            "median_ours", "max_cdf_diff_vs_paper", "n_below_plot"]].round(4).to_string(index=False))
    print(sh[sh.variable == "delta_w_cm"][["model", "alg", "bench", "median_ours", "max_cdf_diff_vs_paper"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
