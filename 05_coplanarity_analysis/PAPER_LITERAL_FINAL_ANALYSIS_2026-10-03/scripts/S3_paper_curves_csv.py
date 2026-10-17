#!/usr/bin/env python3
"""Writes the paper's Fig. 2, 3 and 5 curves as CSV (2026-10-13), from the vector extractions of the arXiv:1708.02243 source figures
(tables/paper_fig23_vector.json: figures/angular_momentum.pdf, figures/steps.pdf; tables/paper_fig5_vector.json: figures/Deltat.pdf, figures/Deltaw.pdf;
scripts S1/S2). Points are the path vertices of the PDF curves converted with the axis ticks (calibration residuals in the JSON).
Outputs:
  tables/paper_fig2_curves.csv      curve (L or d), r_cm, value, unit          (L and d have their own r points)
  tables/paper_fig3_curves.csv      curve (benchmark), r_cm, dphi_1e-3        (Delta phi in units of 1e-3 rad, as the paper's axis)
  tables/paper_fig5_histograms.csv  panel, sample, bin_lo_cm, bin_hi_cm, height, y_quantity, filled_zero
     bins are 0.1 dex wide (10^(k/10)); bins between the first and last drawn bin that the paper does not draw are added with height 0
     (filled_zero = True) so that a step line can be drawn through the edges."""
import os, json, numpy as np, pandas as pd
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
A = json.load(open(f"{T}/paper_fig23_vector.json")); B = json.load(open(f"{T}/paper_fig5_vector.json"))
c = A["fig2"]["curves"]
f2 = pd.concat([pd.DataFrame(dict(curve="L", r_cm=c["L_1e12_hbar"]["x"], value=c["L_1e12_hbar"]["y"], unit="1e12 hbar")),
                pd.DataFrame(dict(curve="d", r_cm=c["d_cm"]["x"], value=c["d_cm"]["y"], unit="cm"))]).sort_values(["curve", "r_cm"])
f2.to_csv(f"{T}/paper_fig2_curves.csv", index=False, float_format="%.6g")
c = A["fig3"]["curves"]; lab = {"colored_1800GeV_2keV": "m_Q = 1.8 TeV, Lambda = 2 keV", "EW_800GeV_2keV": "m_Q = 800 GeV, Lambda = 2 keV"}
f3 = pd.concat([pd.DataFrame(dict(curve=lab[k], r_cm=v["x"], **{"dphi_1e-3": v["y"]})) for k, v in c.items()]).sort_values(["curve", "r_cm"])
f3.to_csv(f"{T}/paper_fig3_curves.csv", index=False, float_format="%.6g")
YQ = {"delta_s_cm": "dsigma/dlog(Delta_s) [fb/bin]", "delta_w_cm": "(1/sigma) dsigma/dlog(Delta_w)"}; rows = []
for panel, d in B.items():
    if panel not in YQ: continue
    for sample, bins in d["histograms"].items():
        k = {int(round(10 * np.log10(b["lo"]))): b for b in bins}
        for i in range(min(k), max(k) + 1):
            lo, hi = 10 ** (i / 10), 10 ** ((i + 1) / 10)
            if i in k: rows.append(dict(panel=panel.replace("_cm", ""), sample=sample, bin_lo_cm=k[i]["lo"], bin_hi_cm=k[i]["hi"], height=k[i]["height"], y_quantity=YQ[panel], filled_zero=False))
            else: rows.append(dict(panel=panel.replace("_cm", ""), sample=sample, bin_lo_cm=lo, bin_hi_cm=hi, height=0.0, y_quantity=YQ[panel], filled_zero=True))
f5 = pd.DataFrame(rows); f5.to_csv(f"{T}/paper_fig5_histograms.csv", index=False, float_format="%.6g")
print(f2.groupby("curve").size().to_dict(), f3.groupby("curve").size().to_dict())
print(f5.groupby(["panel", "sample"]).agg(bins=("height", "size"), zero_filled=("filled_zero", "sum"), lo=("bin_lo_cm", "min"), hi=("bin_hi_cm", "max")).to_string())
