#!/usr/bin/env python3
"""07 X08 (2026-11-17): reach WITH the converted-photon background for Stage 1 · Run 3 · Ideal (10k) and Stage 2 · Run 3 · ATLAS, at 332 fb^-1, mu = 0 / 20 / 50
(and 60 where both exist), each geometry with ITS OWN background:
  ATLAS: tables/R01_background.csv (C01 atlas: barrel + end-caps, material conversion probability M01; b_used = central value if any photon passed,
         else the largest per-region 95% upper limit, D5).
  Ideal: Z0, Z1160 from 06 S2_background_13p6TeV.csv (barrel only, flat 1% conversion at the beam pipe; C01 stage2 mode reproduces it event by event, T05);
         A580 from the C01 stage2 A580 runs with 90 980 photons (tables/S01_C01_stage2_A580_100k_mu*.csv, 2026-11-18, same conventions; 06 S2 had no A580 setting).
Two variants for exclusion when no MC photon passed: the central value b = 0 (main result, 2026-11-17) and b = the MC 95% UL (systematic variant). Statistics: the unchanged method of R01 / S2_09: exclusion s95(b_used) = 95% CL_s with n_obs = round(b_used); discovery s5(N_bkg) = max(5, Asimov Z = 5).
Signal grids: tables/R01_N_grid_300fb.csv (ATLAS), tables/X02_N_grid_S1_Run3_Ideal_300fb.csv (Ideal 10k); reach: reach_rows of R01 (unchanged).
The 2k Ideal sample (06 S2_reach_with_background.csv, Z0 and Z1160) is listed for reference.
Column b_used = the systematic-variant value (MC 95% UL if no photon passed, else the central value); N_bkg = central.
Writes tables/X08_background_used.csv and tables/X08_reach_with_background.csv."""
import os, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"; BASE = os.path.abspath(f"{R}/..")
S2 = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop"; L = 332.0
spec = importlib.util.spec_from_file_location("R01", f"{R}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
B = []
for r in pd.read_csv(f"{T}/R01_background.csv").itertuples():
    B.append(dict(setup="S2_Run3_ATLAS", sct=r.sct, mu=int(r.mu), N_bkg=r.N_bkg_332fb, b_used=r.b_UL_332fb, n_final=r.n_final, source="R01_background.csv (C01 atlas)"))
s2 = pd.read_csv(f"{S2}/S2_background_13p6TeV.csv"); s2 = s2[s2.process == "conversion + pile-up"]
for r in s2.itertuples():
    B.append(dict(setup="S1_Run3_Ideal", sct=r.sct, mu=int(r.mu), N_bkg=r.N_bkg_332fb, b_used=r.b_used_332fb, n_final=int(r.sr), source="06 S2_background_13p6TeV.csv"))
for mu in (0, 20, 50):
    f = f"{T}/S01_C01_stage2_A580_100k_mu{mu}.csv"                    # 2026-11-18: 100k (90 980 Z01 photons, server) replaces the 9130-photon run
    if not os.path.exists(f): continue
    s = pd.read_csv(f); s = s[s.sct == "A580"]; N = float(s.N_bkg_332fb.sum()); nf = int(s.final.sum())
    B.append(dict(setup="S1_Run3_Ideal", sct="A580", mu=mu, N_bkg=N, b_used=N if nf else float(s.N_UL95_332fb_if_zero.max()), n_final=nf, source=os.path.basename(f) + " (C01 stage2)"))
B = pd.DataFrame(B); B["s_excl"] = [R01.s95(b) for b in B.b_used]; B["s_disc"] = [R01.s5(n) for n in B.N_bkg]
B.to_csv(f"{T}/X08_background_used.csv", index=False)
G = {"S2_Run3_ATLAS": pd.read_csv(f"{T}/R01_N_grid_300fb.csv"), "S1_Run3_Ideal": pd.read_csv(f"{T}/X02_N_grid_S1_Run3_Ideal_300fb.csv")}
rows = []
for b in B.itertuples():
    for var, se in (("central b", R01.s95(b.N_bkg)), ("UL if 0 passed (systematic)", b.s_excl)):
        for ch in ("colored", "EW"):
            for r in R01.reach_rows(G[b.setup], ch, b.sct, L, se, b.s_disc, {}):
                rows.append(dict(setup=b.setup, variant=var, channel=ch, sct=b.sct, mu=b.mu, contour=r["contour"], N_bkg=round(b.N_bkg, 3),
                                 b_used=round(b.b_used if var.startswith("UL") else b.N_bkg, 3), s_required=r["s_required"], m_max_GeV=r["m_max_GeV"],
                                 m_max_lo=r["m_max_lo"], m_max_hi=r["m_max_hi"], at_lambda_keV=r["at_lambda_keV"]))
for r in pd.read_csv(f"{S2}/S2_reach_with_background.csv").itertuples():
    if r.lumi_fb == L:
        rows.append(dict(setup="S1_Run3_Ideal_2k", variant="UL if 0 passed (systematic)", channel=r.channel, sct=r.sct, mu=int(r.mu), contour=r.contour, N_bkg=getattr(r, "N_bkg", np.nan),
                         b_used=getattr(r, "b_used", np.nan), s_required=r.s_required, m_max_GeV=r.m_max_GeV, m_max_lo=r.m_max_lo, m_max_hi=r.m_max_hi, at_lambda_keV=r.at_lambda_keV))
X = pd.DataFrame(rows); X.to_csv(f"{T}/X08_reach_with_background.csv", index=False)
pd.set_option("display.width", 250)
print(B[["setup", "sct", "mu", "n_final", "N_bkg", "b_used", "s_excl", "s_disc"]].sort_values(["sct", "mu", "setup"]).round(3).to_string(index=False))
P = X.pivot_table(index=["variant", "channel", "sct", "contour", "mu"], columns="setup", values="m_max_GeV").reset_index()
print(P.to_string(index=False))
