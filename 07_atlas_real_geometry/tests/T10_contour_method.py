#!/usr/bin/env python3
"""07 test T10 (2026-11-17): the contour code of FIGURES_ROOT_2026-11-17/prepare_data_07.py (zgrid, lines, scaled; taken from its source text) applied to the
Stage 2 grid (S2_N_grid_300fb.csv x 332/300, zero background) reproduces the 06 contour lines of scenario 13p6TeV_332fb in
06_publication/FIGURES_ROOT_2026-11-04/data/contours.csv: same segments and points, |d mass| < 1e-9 GeV and |d log10 Lambda| < 1e-12 for every point,
all channels, SCT settings, contours and bands. Prints T10_PASS / T10_FAIL."""
import os, numpy as np, pandas as pd
from scipy.interpolate import RegularGridInterpolator
import contourpy
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.abspath(f"{HERE}/../.."); src = open(f"{HERE}/../FIGURES_ROOT_2026-11-17/prepare_data_07.py").read()
exec(src[src.index("def zgrid"):src.index("BK = rd(")])
G2 = pd.read_csv(f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/S2_N_grid_300fb.csv"); g0 = scaled(G2, 332.0)
ref = pd.read_csv(f"{BASE}/06_publication/FIGURES_ROOT_2026-11-04/data/contours.csv"); ref = ref[ref.scenario == "13p6TeV_332fb"]
bad, n = 0, 0
for ch in ("colored", "EW"):
    for sct in ("Z1160", "Z0"):
        g = g0[(g0.channel == ch) & (g0.sct == sct)]
        for cn, t in (("exclusion", 3.0), ("discovery", 5.0)):
            for band, col in (("central", "N_with_f"), ("lo", "N_with_f_lo"), ("hi", "N_with_f_hi")):
                new = lines(g, col, t); r = ref[(ref.channel == ch) & (ref.sct == sct) & (ref.contour == cn) & (ref.band == band)]
                segs = [r[r.segment == s] for s in sorted(r.segment.unique())]
                ok = len(new) == len(segs) and all(len(a) == len(b) and np.abs(a[:, 0] - b.mass_gev.values).max() < 1e-9
                                                    and np.abs(a[:, 1] - np.log10(b.lambda_eV.values)).max() < 1e-12 for a, b in zip(new, segs))
                n += 1; bad += not ok
                if not ok: print("   differs:", ch, sct, cn, band, len(new), len(segs))
print(f"T10: {n} line sets compared ({len(ref)} reference points), differing {bad}"); print("T10_PASS" if bad == 0 and n == 24 else "T10_FAIL")
