#!/usr/bin/env python3
"""07 X01 (2026-11-17): laptop G01 atlas rows (signal/runs/atlas_large_laptop_INTERIM_2026-11-17, G02 on the laptop, stopped 2026-11-17) vs server G01 atlas rows (signal/runs/large_atlas), row by row
for the same (event_id, Lambda). Every field is compared except t_s (wall-clock time); floats must be bit-identical (NaN == NaN).
Writes tables/X01_laptop_vs_server_atlas.csv (one row per file) and prints X01_IDENTICAL / X01_DIFFER."""
import os, json, glob, math, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); A = f"{R}/signal/runs/atlas_large_laptop_INTERIM_2026-11-17"; S = f"{R}/signal/runs/large_atlas"
def load(f):
    d, bad = {}, 0
    for l in open(f):
        if not l.strip(): continue
        try: ev = json.loads(l)
        except json.JSONDecodeError: bad += 1; continue
        for r in ev: d[(r["event"], round(r["lambda_keV"], 6))] = {k: v for k, v in r.items() if k != "t_s"}
    return d, bad
same = lambda a, b: (isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b)) or a == b
rows, alld = [], 0
for f in sorted(glob.glob(f"{A}/G01_*.jsonl")):
    n = os.path.basename(f); a, bad = load(f); s, _ = load(f"{S}/{n}")
    miss = [k for k in a if k not in s]; diff = []
    for k in a:
        if k in s:
            fl = [x for x in set(a[k]) | set(s[k]) if not same(a[k].get(x), s[k].get(x))]
            if fl: diff.append((k, fl))
    rows.append(dict(file=n, laptop_rows=len(a), server_rows=len(s), compared=len(a) - len(miss), missing_on_server=len(miss), differing_rows=len(diff),
                     differing_fields=";".join(sorted({x for _, fl in diff for x in fl})), unparsable_laptop_lines=bad))
    alld += len(diff) + len(miss)
    for k, fl in diff[:3]: print("   differs", n, k, fl, [(a[k].get(x), s[k].get(x)) for x in fl][:3])
D = pd.DataFrame(rows); D.to_csv(f"{R}/tables/X01_laptop_vs_server_atlas.csv", index=False); print(D.to_string(index=False))
print(f"X01: {D.compared.sum()} rows compared in {len(D)} files, differing {D.differing_rows.sum()}, missing on server {D.missing_on_server.sum()}")
print("X01_IDENTICAL" if alld == 0 else "X01_DIFFER")
