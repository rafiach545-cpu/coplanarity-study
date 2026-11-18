#!/usr/bin/env python3
"""07 X12 (2026-11-18): the merge-distance and threshold variation of the A580 signal efficiency (X11) converted into GeV of reach.
The signal grid of each geometry (ATLAS: tables/R01_N_grid_300fb.csv; Ideal 10k: tables/X02_N_grid_S1_Run3_Ideal_300fb.csv) is scaled by the
measured ratio k(variant) / k(a = 1, T = 15) of tables/X11_signal_sensitivity.csv (Lambda = all, mid band), measured at two masses per channel
(EW 600 and 800 GeV, colored 1500 and 1800 GeV; 2026-11-18): linear in m_Q between them, constant outside (with one mass only: flat). The reach is then recomputed with R01.reach_rows (unchanged)
at 332 fb^-1 with the central background of tables/X08_background_used.csv (A580, mu = 0/20/50), the same thresholds as X08.
Only the signal is varied: the background with a = 0 / 2 needs the server runs (SERVER_BACKGROUND_RUNS.md (e)).
Assumption: the ratio outside the measured masses equals the nearest measured one.
Writes tables/X12_merge_reach_shift.csv."""
import os, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"; L = 332.0
spec = importlib.util.spec_from_file_location("R01", f"{R}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
G = {"S2_Run3_ATLAS": pd.read_csv(f"{T}/R01_N_grid_300fb.csv"), "S1_Run3_Ideal": pd.read_csv(f"{T}/X02_N_grid_S1_Run3_Ideal_300fb.csv")}
S = pd.read_csv(f"{T}/X11_signal_sensitivity.csv"); S = S[(S.sct == "A580") & (S.lambda_keV.astype(str) == "all")]
B = pd.read_csv(f"{T}/X08_background_used.csv"); B = B[B.sct == "A580"]
MASSES = {"EW": (600, 800), "colored": (1500, 1800)}
VAR = [("a=0", 0, 15), ("a=2", 2, 15), ("T=14", 1, 14), ("T=16", 1, 16)]
rows = []
for setup, g0 in G.items():
    for b in B[B.setup == setup].itertuples():
        se, sd = R01.s95(b.N_bkg), R01.s5(b.N_bkg)
        for ch in ("EW", "colored"):
            nom = {r["contour"]: r["m_max_GeV"] for r in R01.reach_rows(g0, ch, "A580", L, se, sd, {})}
            for name, a, t in VAR:
                pts = []
                for mq in MASSES[ch]:
                    s = S[(S.setup == setup) & (S["sample"] == f"{ch}_{mq}gev") & (S.merge_adj == a) & (S.threshold == t)]
                    if len(s): pts.append((mq, float(s.ratio_to_reference.iloc[0])))
                if not pts: continue
                g = g0.copy(); m = (g.channel == ch) & (g.sct == "A580"); xs, ys = zip(*pts)
                fm = np.interp(g.loc[m, "mass_gev"].astype(float), xs, ys)
                for c in ("N_with_f", "N_with_f_lo", "N_with_f_hi"): g.loc[m, c] = g.loc[m, c] * fm
                f = ys[-1]
                for r in R01.reach_rows(g, ch, "A580", L, se, sd, {}):
                    rows.append(dict(setup=setup, channel=ch, mu=b.mu, N_bkg=round(b.N_bkg, 3), contour=r["contour"], variant=name, signal_ratio=round(f, 4), ratio_points=";".join(f"{x}:{y:.3f}" for x, y in pts),
                                     m_max_nominal_GeV=nom[r["contour"]], m_max_variant_GeV=r["m_max_GeV"], shift_GeV=r["m_max_GeV"] - nom[r["contour"]]))
X = pd.DataFrame(rows); X.to_csv(f"{T}/X12_merge_reach_shift.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); print(X.to_string(index=False)); print("X12_EXIT=0")
