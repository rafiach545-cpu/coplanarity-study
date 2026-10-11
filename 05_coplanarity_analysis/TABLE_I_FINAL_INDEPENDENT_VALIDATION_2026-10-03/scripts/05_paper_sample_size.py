#!/usr/bin/env python3
"""
Task 5: infer the paper's Monte-Carlo sample sizes from the quantisation of its Fig. 5 signal
histograms (vector-extracted). For unweighted events every bin height is an integer multiple of a
single per-event weight w. We scan w = h_min / k (k = 1..6) and refine w by least squares on the
integer assignments; the solution is accepted only if every bin is within the digitisation
tolerance of an integer. N = sum(h)/w.

Digitisation tolerance: the vector paths are exact to ~0.01 pt; on the log axes this corresponds
to a relative height error of ~0.05%, so we allow |h/w - round| < 0.15 (generous).

The implied paper denominators are then propagated through Table I (labelled as INFERENCE).
"""
import json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
FOR = "/home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02"
fig = json.load(open(f"{FOR}/tables/paper_fig5_extracted.json"))
res = {}
for var in ("delta_s_cm", "delta_w_cm"):
    for lab in ("EW Quirk", "Colored Quirk"):
        h = np.array([b["height"] for b in fig[var]["histograms"][lab]])
        best = None
        for k in range(1, 7):
            w = h.min() / k
            n = np.round(h / w)
            w = float(np.sum(n * h) / np.sum(n * n))            # refine
            dev = np.abs(h / w - np.round(h / w))
            if best is None or dev.max() < best[1]:
                best = (w, float(dev.max()), k, np.round(h / w).astype(int).tolist())
        w, dmax, k, counts = best
        res[f"{var}|{lab}"] = dict(unit_weight=w, max_deviation_from_integer=dmax, accepted=dmax < 0.15,
                                   counts_per_bin=counts, N_in_plot=int(round(h.sum() / w)),
                                   sum_heights=float(h.sum()), units="fb per event" if var == "delta_s_cm" else "normalised (1/N)")
for k, v in res.items():
    print(k, {kk: vv for kk, vv in v.items() if kk != "counts_per_bin"}); print("   counts:", v["counts_per_bin"])
json.dump(res, open(f"{T}/paper_fig5_quantisation.json", "w"), indent=1)

# implied paper denominators (INFERENCE): Fig. 5 population = trigger AND fiducial AND plane (+ multiplicity?)
paper = {"EW": dict(trig=0.10, fid=0.28, reco=0.72, ds_pass=0.916), "COL": dict(trig=0.24, fid=0.28, reco=0.35, ds_pass=0.899)}
imp = {}
for B, lab in (("EW", "EW Quirk"), ("COL", "Colored Quirk")):
    Nw = res[f"delta_w_cm|{lab}"]["N_in_plot"]          # Delta_w plot covers the full Delta_w range
    pp = paper[B]
    for pop, nfid in (("Fig5 = plane+multiplicity", Nw * pp["ds_pass"] / pp["reco"]), ("Fig5 = plane only (upper bound on plane eff = 1)", Nw)):
        ntrig = nfid / pp["fid"]
        imp[f"{B}|{pop}"] = dict(N_fig5=Nw, N_fid=round(nfid), N_trig=round(ntrig), N_matched=round(ntrig / pp["trig"]),
                                 note="colored N_trig is after the charge requirement; matched-sample size also needs the charged fraction (~0.30)" if B == "COL" else "")
for k, v in imp.items():
    print(k, v)
json.dump(imp, open(f"{T}/paper_implied_denominators.json", "w"), indent=1)
