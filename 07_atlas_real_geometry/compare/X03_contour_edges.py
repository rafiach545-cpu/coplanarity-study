#!/usr/bin/env python3
"""07 X03 (2026-11-17): is the N >= threshold region closed inside the (m, Lambda) grid? For ideal and ATLAS (tables/X02_N_grid_*_300fb.csv x 332/300)
and Stage 2 (S2_N_grid_300fb.csv x 332/300), per channel, SCT and threshold (3, 5): the grid points ON THE GRID EDGE with N >= threshold
(rows used by the reach method: computed with k > 0, or bound). Edge = top (Lambda = 25 keV), bottom (0.1 keV), left (lowest mass), right (highest mass).
A non-empty edge means the contour is open there (it leaves the grid). Writes tables/X03_contour_edges.csv."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"
G = {"S2_Run3_ATLAS": pd.read_csv(f"{T}/X02_N_grid_S2_Run3_ATLAS_300fb.csv"), "S1_Run3_Ideal": pd.read_csv(f"{T}/X02_N_grid_S1_Run3_Ideal_300fb.csv"),
     "S1_Run3_Ideal_2k": pd.read_csv(f"{os.path.abspath(f'{R}/..')}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/S2_N_grid_300fb.csv")}
rows = []
for nm, g in G.items():
    g = g.copy(); g["N"] = g.N_with_f * 332.0 / 300.0; ok = (g.status_with_f == "bound") | ((g.status_with_f == "computed") & (g.k > 0))
    for (ch, sct), x0 in g.groupby(["channel", "sct"]):
        lmin, lmax, mmin, mmax = x0.lambda_keV.min(), x0.lambda_keV.max(), x0.mass_gev.min(), x0.mass_gev.max()   # edges of the full grid
        x = x0[ok[x0.index]]
        for thr in (3.0, 5.0):
            y = x[x.N >= thr]; e = {}
            e["top_25keV"] = sorted(y[np.isclose(y.lambda_keV, lmax)].mass_gev.astype(int))
            e["bottom_lowest_lambda"] = sorted(y[np.isclose(y.lambda_keV, lmin)].mass_gev.astype(int))
            e["left_lowest_mass"] = sorted(y[y.mass_gev == mmin].lambda_keV)
            e["right_highest_mass"] = sorted(y[y.mass_gev == mmax].lambda_keV)
            top = x[np.isclose(x.lambda_keV, lmax)]
            rows.append(dict(setup=nm, channel=ch, sct=sct, threshold=thr, lambda_max_keV=lmax, mass_max_gev=mmax, closed=not any(e.values()),
                             **{k: " ".join(f"{v:g}" for v in vv) for k, vv in e.items()}, N_max_at_top=round(float(top.N.max()), 2) if len(top) else np.nan))
D = pd.DataFrame(rows); D.to_csv(f"{T}/X03_contour_edges.csv", index=False); pd.set_option("display.width", 250); print(D.to_string(index=False))
