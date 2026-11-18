#!/usr/bin/env python3
"""07 X13 (2026-11-18): pixel merging as ONE correlated variation of signal and background; reach for each full scenario (A580, 332 fb^-1).
Scenarios: nominal (a = 1); a = 0 (merge only same-pixel hits = -50% distance); a = 2 (+100%). In each, the signal AND the background change together:
  signal: R01 / X02 grid scaled by the measured k ratio (tables/X11_signal_sensitivity.csv, A580, T = 15, Lambda = all), linear in m_Q between
          EW 600 / 800 and colored 1500 / 1800 GeV, constant outside (as X12);
  background: the 100k A580 central value (tables/X08_background_used.csv) times a background merge ratio N(a) / N(a = 1), from the server
          step (e) runs (tables/S01_C01_atlas_sens_<sct>_a<a>_mu50.csv; same photons, machine and pool for a = 0 / 1 / 2):
            'main'        = the ATLAS Z0 ratio (1189 / 663 / 584 passing rows: small MC error);
            'pessimistic' = the ATLAS A580-own ratio (12 / 3 / 1 passing rows: large MC error, a = 0 gives x4.4).
  The ratios are measured at mu = 50 in the ATLAS geometry; they are applied also to mu = 20 and to the Ideal geometry (assumption; no Ideal
  merge runs). At mu = 0 the central background is 0 in every scenario.
Statistics and reach: R01.s95 / R01.s5 / R01.reach_rows, unchanged (exclusion: 95% CL_s with n_obs = round(b); discovery: max(5, Asimov Z = 5)).
Writes tables/X13_merge_scenarios.csv and tables/X13_background_ratios.csv."""
import os, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"; L = 332.0
spec = importlib.util.spec_from_file_location("R01", f"{R}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
G = {"S2_Run3_ATLAS": pd.read_csv(f"{T}/R01_N_grid_300fb.csv"), "S1_Run3_Ideal": pd.read_csv(f"{T}/X02_N_grid_S1_Run3_Ideal_300fb.csv")}
S = pd.read_csv(f"{T}/X11_signal_sensitivity.csv"); S = S[(S.sct == "A580") & (S.lambda_keV.astype(str) == "all") & (S.threshold == 15)]
B = pd.read_csv(f"{T}/X08_background_used.csv"); B = B[B.sct == "A580"]
MASSES = {"EW": (600, 800), "colored": (1500, 1800)}

# background merge ratios from the server step (e) runs
rat = []
for sct in ("Z0", "A580"):
    n = {a: pd.read_csv(f"{T}/S01_C01_atlas_sens_{sct}_a{a}_mu50.csv") for a in (0, 1, 2)}
    for a in (0, 1, 2):
        N, N1, k, k1 = n[a].N_bkg_332fb.sum(), n[1].N_bkg_332fb.sum(), int(n[a].final.sum()), int(n[1].final.sum())
        rat.append(dict(sct_source=sct, merge_adj=a, N_bkg_332fb=N, n_final=k, ratio=N / N1, ratio_err_poisson=(N / N1) * np.sqrt(1 / max(k, 1) + 1 / max(k1, 1)) if a != 1 else 0.0))
RT = pd.DataFrame(rat); RT.to_csv(f"{T}/X13_background_ratios.csv", index=False)
BR = {("main", a): float(RT[(RT.sct_source == "Z0") & (RT.merge_adj == a)].ratio.iloc[0]) for a in (0, 1, 2)}
BR.update({("pessimistic", a): float(RT[(RT.sct_source == "A580") & (RT.merge_adj == a)].ratio.iloc[0]) for a in (0, 1, 2)})
SCEN = [("nominal", 1, "main"), ("a=0 main", 0, "main"), ("a=0 pessimistic", 0, "pessimistic"), ("a=2 main", 2, "main"), ("a=2 pessimistic", 2, "pessimistic")]

rows = []
for setup, g0 in G.items():
    for b in B[B.setup == setup].itertuples():
        for ch in ("EW", "colored"):
            for name, a, bv in SCEN:
                g = g0.copy(); m = (g.channel == ch) & (g.sct == "A580"); pts = []
                for mq in MASSES[ch]:
                    s = S[(S.setup == setup) & (S["sample"] == f"{ch}_{mq}gev") & (S.merge_adj == a)]
                    if len(s): pts.append((mq, float(s.ratio_to_reference.iloc[0])))
                xs, ys = zip(*pts); fm = np.interp(g.loc[m, "mass_gev"].astype(float), xs, ys)
                for c in ("N_with_f", "N_with_f_lo", "N_with_f_hi"): g.loc[m, c] = g.loc[m, c] * fm
                nb = b.N_bkg * BR[(bv, a)]
                for r in R01.reach_rows(g, ch, "A580", L, R01.s95(nb), R01.s5(nb), {}):
                    rows.append(dict(setup=setup, channel=ch, mu=b.mu, scenario=name, merge_adj=a, bkg_ratio=round(BR[(bv, a)], 3), N_bkg=round(nb, 3),
                                     signal_ratio_points=";".join(f"{x}:{y:.3f}" for x, y in pts), contour=r["contour"], s_required=r["s_required"], m_max_GeV=r["m_max_GeV"]))
X = pd.DataFrame(rows)
nom = X[X.scenario == "nominal"].set_index(["setup", "channel", "mu", "contour"]).m_max_GeV
X["shift_GeV"] = [r.m_max_GeV - nom[(r.setup, r.channel, r.mu, r.contour)] for r in X.itertuples()]
X.to_csv(f"{T}/X13_merge_scenarios.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); print(RT.round(4).to_string(index=False)); print()
print(X.pivot_table(index=["setup", "channel", "mu", "scenario"], columns="contour", values=["N_bkg", "s_required", "m_max_GeV", "shift_GeV"]).round(2).to_string())
print("X13_EXIT=0")
