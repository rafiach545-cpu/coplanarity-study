#!/usr/bin/env python3
"""07 test T09 (2026-11-17): reach/R01_reach_07.py uses exactly the Stage 2 method. Its functions run on the Stage 2 inputs must reproduce
(a) S2_N_grid_300fb.csv (grid(), strict, settings Z0 / Z1160; every column of the Stage 2 file, numbers to 1e-12 relative, NaN = NaN);
(b) S2_reach.csv (reach_rows(), thresholds 3 / 5; m_max, Lambda, lo, hi, N at the highest mass; for 300 / 332 / 355 fb^-1);
(c) S2_reach_with_background.csv (s95 / s5 on b_used / N_bkg of S2_background_13p6TeV.csv, then reach_rows()).
Prints T09_PASS / T09_FAIL."""
import os, sys, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("R01", f"{HERE}/../reach/R01_reach_07.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
S2 = R.S2; ok = {}
# (a)
C = pd.read_csv(f"{S2}/inputs/counts.csv"); G, notes = R.grid(C, f"{S2}/inputs", R.load_s2, ("Z0", "Z1160"), strict=True)
ref = pd.read_csv(f"{S2}/S2_N_grid_300fb.csv"); key = ["channel", "mass_gev", "lambda_keV", "sct"]
m = ref.merge(G, on=key, suffixes=("_r", "_n"), how="outer", indicator=True); bad = []
assert (m._merge == "both").all() and len(m) == len(ref), "row sets differ"
for c in ref.columns:
    if c in key: continue
    a, b = m[f"{c}_r"], m[f"{c}_n"]
    if a.dtype == object or b.dtype == object:
        same = (a.astype(str) == b.astype(str)) | (a.isna() & b.isna())
    else:
        a, b = a.astype(float), b.astype(float); same = (np.isnan(a) & np.isnan(b)) | (np.abs(a - b) <= 1e-12 * np.maximum(1, np.abs(a)))
    if not same.all(): bad.append((c, int((~same).sum())))
ok["a"] = not bad; print(f"(a) grid: {len(ref)} rows x {len(ref.columns)} columns, differing columns {bad}")
# (b)
S2R = pd.read_csv(f"{S2}/S2_reach.csv"); GC = ref; nb = 0
for r in S2R.itertuples():
    new = [x for x in R.reach_rows(GC, r.channel, r.sct, r.lumi_fb, 3.0, 5.0, {}) if x["contour"] == r.contour][0]
    same = all((pd.isna(getattr(r, k)) and pd.isna(new[k2])) or getattr(r, k) == new[k2] for k, k2 in (("m_max_GeV", "m_max_GeV"), ("at_lambda_keV", "at_lambda_keV"),
               ("m_max_lo", "m_max_lo"), ("m_max_hi", "m_max_hi"), ("N_max_at_highest_mass", "N_max_at_highest_mass")))
    if not same: nb += 1; print("   (b) differs:", r, new)
ok["b"] = nb == 0; print(f"(b) zero-background reach: {len(S2R)} rows, differing {nb}")
# (c)
BK = pd.read_csv(f"{S2}/S2_background_13p6TeV.csv"); BK = BK[BK.process.str.startswith("conversion")]; RB = pd.read_csv(f"{S2}/S2_reach_with_background.csv"); nb = 0; n = 0
for b in BK.itertuples():
    for L in R.LUMIS:
        bu, Nb = getattr(b, f"b_used_{L:g}fb"), getattr(b, f"N_bkg_{L:g}fb"); te, td = R.s95(bu), R.s5(Nb)
        if abs(te - getattr(b, f"s_excl_{L:g}fb")) > 1e-9 or abs(td - getattr(b, f"s_disc_{L:g}fb")) > 1e-9: nb += 1; print("   (c) threshold differs", b.sct, b.mu, L)
        for ch in ("colored", "EW"):
            for new in R.reach_rows(GC, ch, b.sct, L, te, td, {}):
                r = RB[(RB.channel == ch) & (RB.sct == b.sct) & (RB.mu == b.mu) & (RB.lumi_fb == L) & (RB.contour == new["contour"])].iloc[0]; n += 1
                same = all((pd.isna(r[k]) and pd.isna(new[k])) or r[k] == new[k] for k in ("m_max_GeV", "at_lambda_keV", "m_max_lo", "m_max_hi", "s_required"))
                if not same: nb += 1; print("   (c) differs:", dict(r), new)
ok["c"] = nb == 0 and n == len(RB); print(f"(c) reach with background: {n} of {len(RB)} rows compared, differing {nb}")
print("T09:", ok); print("T09_PASS" if all(ok.values()) else "T09_FAIL")
