#!/usr/bin/env python3
"""
Part C: fiducial efficiency under the two defensible geometry models, kept SEPARATE
(no cone+finite-z combination, which the paper does not describe):
  A  project model : every crossing |eta_lab| < 1.8 (infinite cylinders), max t < 25 ns
  B  finite barrel : |z_lab| < half-length (IBL 33.015, pixel 40.05, SCT 74.9 cm), max t < 25 ns
Both require all 16 (2 quirks x 8 layers) first crossings to exist.
Inputs: tables/truth_crossings_<sample>.csv (all trigger events) and the project's z0 stream
(02_forensic_pipeline.stream_draws). Model A must reproduce the stored fiducial flag.
"""
import importlib.util, math, os
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("fp", f"{HERE}/02_forensic_pipeline.py")
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
HALF = {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9}


def wil(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h


rows = []
for s in ("EW1000", "EW2000", "COL1000", "COL2000"):
    ev = fp.load_sample(s).sort_values("key")
    cr_all = pd.read_csv(f"{T}/truth_crossings_{s}.csv")
    ex_all = pd.read_csv(f"{T}/exact_crossings_fiducial_{s}.csv")
    seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
    for e in ev.itertuples():
        cr = cr_all[cr_all.key == e.key].sort_values(["quirk", "layer"])
        tech = e.technical or len(cr) == 0 or ("technical_error" in cr.columns and cr.technical_error.notna().any())
        if tech:
            rows.append(dict(sample=s, key=e.key, event_id=e.event_id, technical=True, A=False, B=False, stored_fid=bool(e.stored_fid)))
            continue
        rng = seq if seq is not None else np.random.default_rng(int(e.seed))
        ex = ex_all[ex_all.key == e.key].sort_values(["quirk", "layer"])
        z0, _ = fp.stream_draws(rng, cr, ex if len(ex) else None)
        use = ex if len(ex) else cr
        all16 = len(use) == 16 and bool(use.crossed.all())
        if not all16:
            A = B = False
        else:
            zl = [fp.zlab(r, z0) for r in use.itertuples()]
            t_ok = float(use.t_ns.max()) < 25.0
            A = t_ok and all(abs(fp.eta_lab(r, z)) < 1.8 for r, z in zip(use.r, zl))
            B = t_ok and all(abs(z) < HALF[int(L)] for L, z in zip(use.layer, zl))
        rows.append(dict(sample=s, key=e.key, event_id=e.event_id, technical=False, z0_cm=z0, A=A, B=B,
                         stored_fid=bool(e.stored_fid)))
d = pd.DataFrame(rows)
d.to_csv(f"{T}/fiducial_models_per_event.csv", index=False)
out = []
for name, ss in (("EW1000", ["EW1000"]), ("EW2000", ["EW2000"]), ("EW pooled", ["EW1000", "EW2000"]),
                 ("COL1000", ["COL1000"]), ("COL2000", ["COL2000"]), ("COL pooled", ["COL1000", "COL2000"])):
    x = d[d["sample"].isin(ss)]
    for m in ("A", "B"):
        k, n = int(x[m].sum()), len(x)
        lo, hi = wil(k, n)
        out.append(dict(set=name, model=m, k=k, n=n, eff=k / n, w95_lo=lo, w95_hi=hi,
                        p_vs_0p28=stats.binomtest(k, n, 0.28).pvalue, paper_in_w95=lo <= 0.28 <= hi,
                        A_reproduces_stored=bool((x.A == x.stored_fid).all()) if m == "A" else None))
o = pd.DataFrame(out); o.to_csv(f"{T}/fiducial_models_summary.csv", index=False)
print(o.round(4).to_string(index=False))
