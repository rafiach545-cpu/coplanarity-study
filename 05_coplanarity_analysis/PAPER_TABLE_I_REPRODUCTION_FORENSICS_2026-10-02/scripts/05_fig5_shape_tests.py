#!/usr/bin/env python3
"""
Pre-registered selection criterion: agreement of our selected-plane Delta_s / Delta_w with
the paper's Fig. 5 signal shapes (EW and colored), for two candidate Fig. 5 populations:
  P1 = plane found (cut 1)            P2 = plane found AND hit multiplicity (cuts 1+2)
("before the final cut on those variables" = before cut 3).
Statistic: binned KS (max |CDF diff|) on the paper's own log bins within the plotted range;
p-value from the asymptotic KS distribution with n = our event count in range (paper
histogram treated as the reference shape; its own MC uncertainty is unknown, so p-values
are optimistic for rejection).
"""
import json, os
import numpy as np, pandas as pd
from scipy.stats import kstwobign
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
v = pd.read_csv(f"{T}/variant_event_results.csv"); fig = json.load(open(f"{T}/paper_fig5_extracted.json"))
v["bench"] = np.where(v["sample"].str.startswith("EW"), "EW", "COL")
rows = []
for (m, a), g in v.groupby(["model", "alg"]):
    for b, lab in (("EW", "EW Quirk"), ("COL", "Colored Quirk")):
        for pop, sel in (("P1_plane", g.plane), ("P2_plane_and_mult", g.plane & g.mult)):
            x = g[(g.bench == b) & sel]
            for var, col in (("delta_s_cm", "ds"), ("delta_w_cm", "dw")):
                h = fig[var]["histograms"][lab]; e = [t["lo"] for t in h] + [h[-1]["hi"]]
                ph = np.array([t["height"] for t in h]); oh = np.histogram(x[col], bins=e)[0].astype(float)
                n = int(oh.sum())
                D = float(np.max(np.abs(np.cumsum(ph) / ph.sum() - np.cumsum(oh) / max(oh.sum(), 1))))
                rows.append(dict(model=m, alg=a, bench=b, population=pop, variable=var, n=n, D=D,
                                 ks_p=float(kstwobign.sf(D * np.sqrt(n))) if n else np.nan))
d = pd.DataFrame(rows); d.to_csv(f"{T}/fig5_shape_tests.csv", index=False)
pv = d.pivot_table(index=["model", "alg"], columns=["population", "variable", "bench"], values="ks_p")
pd.set_option("display.width", 250)
print("KS p-values vs paper Fig.5 (higher = more compatible)")
print(pv.round(4).to_string())
s = d[d.variable == "delta_s_cm"].pivot_table(index=["model", "alg"], columns=["population", "bench"], values="D")
print("\nDelta_s max CDF difference"); print(s.round(3).to_string())
