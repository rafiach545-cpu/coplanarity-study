#!/usr/bin/env python3
"""07 X01c (2026-11-17): effect of the laptop-vs-server numerical differences (X01) on N and on the reach. Both grids are built with the R01 method
(reach/R01_reach_07.py grid(), strict) from the bands that the laptop finished for all 13 points (low + mid: Lambda = 0.1-10 keV), from
signal/runs/atlas_large_laptop_INTERIM_2026-11-17 and from signal/runs/large_atlas (server), and the reach at 332 fb^-1 is compared.
Writes tables/X01c_reach_laptop_vs_server.csv and tables/X01c_N_laptop_vs_server.csv."""
import os, importlib.util, numpy as np, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); T = f"{R}/tables"
spec = importlib.util.spec_from_file_location("R01", f"{R}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
R01.BANDS = ("low", "mid"); SET = ("Z0", "A580", "Z1160"); INP = f"{R}/signal/inputs_large"
D = {"laptop": f"{R}/signal/runs/atlas_large_laptop_INTERIM_2026-11-17", "server": f"{R}/signal/runs/large_atlas"}
C, _ = R01.with_runs(pd.read_csv(f"{INP}/counts.csv"), D["laptop"]); G = {}
for nm, d in D.items():
    G[nm], notes = R01.grid(C, INP, lambda tag, d=d: R01.load_07(tag, d), SET, strict=True); assert not notes, notes
rows = []
for ch in ("colored", "EW"):
    for s in SET:
        a, b = (R01.reach_rows(G[nm], ch, s, 332.0, 3.0, 5.0, {}) for nm in ("laptop", "server"))
        for x, y in zip(a, b):
            rows.append(dict(channel=ch, sct=s, contour=x["contour"], m_max_laptop=x["m_max_GeV"], m_max_server=y["m_max_GeV"], diff_GeV=x["m_max_GeV"] - y["m_max_GeV"],
                             wilson_lo_server=y["m_max_lo"], wilson_hi_server=y["m_max_hi"], lambda_laptop=x["at_lambda_keV"], lambda_server=y["at_lambda_keV"]))
X = pd.DataFrame(rows); X.to_csv(f"{T}/X01c_reach_laptop_vs_server.csv", index=False)
k = ["channel", "mass_gev", "lambda_keV", "sct"]; M = G["laptop"].merge(G["server"], on=k, suffixes=("_laptop", "_server"))
M["dk"] = M.k_laptop - M.k_server; M["rel_dN"] = (M.N_with_f_laptop - M.N_with_f_server) / M.N_with_f_server.replace(0, np.nan)
M["dk_over_sigma"] = M.dk / np.sqrt(np.maximum(M.k_server, 1)); M[k + ["n_prop_server", "k_laptop", "k_server", "dk", "rel_dN", "dk_over_sigma"]].to_csv(f"{T}/X01c_N_laptop_vs_server.csv", index=False)
pd.set_option("display.width", 250); print(X.to_string(index=False))
print(f"grid rows {len(M)}: k differs in {(M.dk != 0).sum()}; max |dk| {M.dk.abs().max()}; max |dk|/sqrt(k) {M.dk_over_sigma.abs().max():.2f}; "
      f"median |rel dN| where k > 0: {M[M.k_server > 0].rel_dN.abs().median():.4f}; max |reach diff| {X.diff_GeV.abs().max()} GeV")
