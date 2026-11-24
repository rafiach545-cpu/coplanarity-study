#!/usr/bin/env python3
"""regen_dop853 STEP 0: the server's S10 run must reproduce the laptop reference event by event.
Compared for every (event, Lambda): fiducial flag; SR decision for Z0, Z1160, Z580; the set of first crossings (quirk, layer) and every crossing
position within 1e-6 mm (1e-7 cm). Writes <out>/STEP0.txt: 'PASS ...' or 'FAIL ...' with the first differing event; exit 1 on FAIL.
Usage: step0_compare.py <reference.jsonl> <new.jsonl> <out_dir>"""
import sys, json, math
ref_f, new_f, out = sys.argv[1:4]
import os
TOL_CM = float(os.environ.get("STEP0_TOL_MM", "1e-6")) / 10.0      # default 1e-6 mm (user); STEP0_TOL_MM overrides
load = lambda f: {(r["event"], r["lambda_keV"]): r for l in open(f) if l.strip() for r in json.loads(l)}
R, N = load(ref_f), load(new_f); first, n_cmp = None, 0
for k in sorted(R):
    if k not in N:
        first = first or f"event {k[0]}, Lambda {k[1]} keV: missing in the new run"; break
    a, b = R[k], N[k]; n_cmp += 1
    for c in ("fid", "Z0_final", "Z1160_final", "Z580_final"):
        if bool(a.get(c)) != bool(b.get(c)):
            first = f"event {k[0]}, Lambda {k[1]} keV: {c} reference {a.get(c)} new {b.get(c)}"; break
    if first: break
    A = {(c[0], c[1]): c[2:5] for c in a["first"]}; B = {(c[0], c[1]): c[2:5] for c in b["first"]}
    if set(A) != set(B):
        first = f"event {k[0]}, Lambda {k[1]} keV: different crossing sets ({sorted(set(A) ^ set(B))})"; break
    for q in A:
        d = max([abs(x - y) for x, y in zip(A[q], B[q]) if not (math.isnan(x) and math.isnan(y))] or [0.0])
        if d > TOL_CM:
            first = f"event {k[0]}, Lambda {k[1]} keV: crossing {q} differs by {d * 10:.3g} mm (> {TOL_CM * 10:g} mm)"; break
    if first: break
# diagnostics over all rows (also after the first difference): decision differences and the largest crossing difference
ndec, dmax, nmiss = 0, 0.0, 0
for k in R:
    if k not in N: nmiss += 1; continue
    a, b = R[k], N[k]; ndec += sum(bool(a.get(c)) != bool(b.get(c)) for c in ("fid", "Z0_final", "Z1160_final", "Z580_final"))
    A = {(c[0], c[1]): c[2:5] for c in a["first"]}; B = {(c[0], c[1]): c[2:5] for c in b["first"]}
    for q in set(A) & set(B):
        vals = [abs(x - y) for x, y in zip(A[q], B[q]) if not (math.isnan(x) and math.isnan(y))]
        if vals: dmax = max(dmax, max(vals))
diag = f"[all rows: decision differences {ndec}, largest crossing difference {dmax * 10:.3g} mm, rows missing {nmiss}, tolerance {TOL_CM * 10:g} mm]"
extra = sorted(set(N) - set(R))
if not first and extra: first = f"new run has {len(extra)} rows not in the reference, first {extra[0]}"
txt = (f"PASS: {n_cmp} rows (events x Lambda) identical to the laptop reference (fid, SR Z0/Z1160/Z580, crossings within 1e-6 mm)"
       if not first else f"FAIL: first difference: {first}  (compared {n_cmp} rows before it)")
txt += " " + diag
open(f"{out}/STEP0.txt", "w").write(txt + "\n"); print(txt)
sys.exit(0 if not first else 1)
