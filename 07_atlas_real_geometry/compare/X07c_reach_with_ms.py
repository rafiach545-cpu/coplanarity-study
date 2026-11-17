#!/usr/bin/env python3
"""07 X07c (2026-11-17): rough effect of the X07b multiple-scattering estimate on the reach (332 fb^-1). The ATLAS grid (tables/R01_N_grid_300fb.csv) is
scaled per (channel, SCT) by the survival fraction of the Delta_s cut found at Lambda = 4 keV (X07b; selected-event-weighted over both groups), applied to all
Lambda and masses (an approximation), and the reach is recomputed with the unchanged method (reach/R01_reach_07.py reach_rows). Writes tables/X07c_reach_with_ms.csv."""
import os, importlib.util, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); T = f"{R}/tables"
spec = importlib.util.spec_from_file_location("R01", f"{R}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
G = pd.read_csv(f"{T}/R01_N_grid_300fb.csv"); S = pd.read_csv(f"{T}/X07b_ds_with_ms.csv"); rows = []
for var, col in (("no MS (as simulated)", None), ("MS, initial p", "still_pass_initial_p"), ("MS, conservative p_min", "still_pass_pmin")):
    g = G.copy()
    if col:
        f = S.groupby(["channel", "sct"]).apply(lambda x: (x[col] * x.n_selected).sum() / x.n_selected.sum(), include_groups=False)
        for (ch, s), v in f.items():
            m = (g.channel == ch) & (g.sct == s)
            for c in ("N_with_f", "N_with_f_lo", "N_with_f_hi"): g.loc[m, c] *= v
    for ch in ("colored", "EW"):
        for s in ("Z0", "A580", "Z1160"):
            for r in R01.reach_rows(g, ch, s, 332.0, 3.0, 5.0, {}): rows.append(dict(variant=var, **{k: r[k] for k in ("channel", "sct", "contour", "m_max_GeV")}))
X = pd.DataFrame(rows).pivot_table(index=["channel", "sct", "contour"], columns="variant", values="m_max_GeV").reset_index()
X.to_csv(f"{T}/X07c_reach_with_ms.csv", index=False); print(X.to_string(index=False))
