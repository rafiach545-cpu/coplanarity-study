#!/usr/bin/env python3
"""07 X01b (2026-11-17): classifies the laptop vs server atlas differences of X01 per row: (1) identical; (2) floats only, largest relative difference;
(3) discrete fields differ (fid, fid_stage2, n_true_hits, error, <sct>_plane/_mult/_final/_endcap). Also the net change of the counts used by the reach
(n_fid, k per SCT) per file. Writes tables/X01b_difference_classes.csv."""
import os, json, glob, math, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); A = f"{R}/signal/runs/atlas_large_laptop_INTERIM_2026-11-17"; S = f"{R}/signal/runs/large_atlas"
def load(f):
    d = {}
    for l in open(f):
        try: ev = json.loads(l)
        except json.JSONDecodeError: continue
        for r in ev: d[(r["event"], round(r["lambda_keV"], 6))] = r
    return d
DISC = ["fid", "fid_stage2", "n_true_hits", "error"] + [f"{s}_{x}" for s in ("Z0", "A580", "Z1160") for x in ("plane", "mult", "final", "endcap")]
out = []
for f in sorted(glob.glob(f"{A}/G01_*.jsonl")):
    a = load(f); s = load(f"{S}/{os.path.basename(f)}"); c = dict(file=os.path.basename(f), rows=len(a), identical=0, float_only=0, discrete=0, max_rel_float=0.0)
    for x in ("fid", "Z0_final", "A580_final", "Z1160_final"): c[f"d_{x}"] = 0; c[f"flip_{x}"] = 0
    first_lam = {}
    for k, r in a.items():
        q = s[k]; dd = [x for x in DISC if r.get(x) != q.get(x)]
        fl = [x for x in r if x not in DISC and x not in ("t_s", "event", "lambda_keV") and not (isinstance(r[x], float) and isinstance(q.get(x), float) and math.isnan(r[x]) and math.isnan(q[x])) and r[x] != q.get(x)]
        if dd: c["discrete"] += 1
        elif fl: c["float_only"] += 1
        else: c["identical"] += 1
        for x in fl:
            if isinstance(r[x], float) and isinstance(q.get(x), float): c["max_rel_float"] = max(c["max_rel_float"], abs(r[x] - q[x]) / max(abs(q[x]), 1e-300))
        for x in ("fid", "Z0_final", "A580_final", "Z1160_final"):
            c[f"d_{x}"] += bool(r.get(x)) - bool(q.get(x)); c[f"flip_{x}"] += bool(r.get(x)) != bool(q.get(x))
    out.append(c)
D = pd.DataFrame(out); D.to_csv(f"{R}/tables/X01b_difference_classes.csv", index=False); pd.set_option("display.width", 250); print(D.to_string(index=False))
t = D.sum(numeric_only=True); print(f"total rows {int(t.rows)}: identical {int(t.identical)}, float only {int(t.float_only)}, discrete {int(t.discrete)}; largest relative float difference {D.max_rel_float.max():.2e}")
print("flips (laptop != server):", {x: int(t[f'flip_{x}']) for x in ("fid", "Z0_final", "A580_final", "Z1160_final")}, " net (laptop - server):", {x: int(t[f'd_{x}']) for x in ("fid", "Z0_final", "A580_final", "Z1160_final")})
