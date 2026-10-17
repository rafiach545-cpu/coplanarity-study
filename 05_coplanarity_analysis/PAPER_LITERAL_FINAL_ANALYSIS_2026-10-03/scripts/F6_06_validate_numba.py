#!/usr/bin/env python3
"""Validation of the numba integrator in the full Figure 6 pipeline (2026-10-17): rerun the first NV events of several points/bands with FAST=1
(F6_02_grid.py, NMAX=NV) and compare every row (fid, plane, mult, final, ds, dw for SCT z none and 1.16 mm, error) with the stored v2 checkpoints.
Pass = identical booleans and identical ds/dw (exact float equality). Usage: F6_06_validate_numba.py (after the FAST pilots exist)."""
import os, sys, json, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LOG = f"{HERE}/../logs"; NV = int(os.environ.get("NV", 12))
COLS = ["fid", "Z0_plane", "Z0_mult", "Z0_final", "Z0_ds", "Z0_dw", "Z1160_plane", "Z1160_mult", "Z1160_final", "Z1160_ds", "Z1160_dw", "error"]
def rows(f): return pd.DataFrame([r for l in open(f) if l.strip() for r in json.loads(l)])
bad_total = 0
for tag, band in (("colored_1800gev", "mid"), ("EW_800gev", "mid"), ("EW_100gev", "mid"), ("colored_900gev", "mid"), ("EW_600gev", "low")):
    fnew = f"{LOG}/F6_{tag}{'' if band == 'mid' else '_' + band}_pilot{NV}_fast_events.jsonl"
    if not os.path.exists(fnew): print(f"{tag} {band}: no validation run, skipped"); continue
    ref = rows(f"{LOG}/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl"); new = rows(fnew); checked = checked + 1 if 'checked' in dir() else 1
    ref = ref[ref.event < NV].set_index(["event", "lambda_keV"]).sort_index(); new = new.set_index(["event", "lambda_keV"]).sort_index()
    assert list(ref.index) == list(new.index), (tag, "index mismatch")
    bad = 0
    for c in COLS:
        a, b = ref[c].astype(str).replace("nan", "NaN"), new[c].astype(str).replace("nan", "NaN")
        bad += int((a != b).sum())
    t_ref, t_new = ref.t_s.sum(), new.t_s.sum()
    print(f"{tag:16s} {band}: rows {len(new)}  mismatching values {bad}  time v2 {t_ref:.0f}s -> numba {t_new:.0f}s ({t_ref / max(t_new, 1e-9):.1f}x)")
    bad_total += bad
ok = bad_total == 0 and 'checked' in dir()
print("VALIDATION", "PASSED" if ok else f"FAILED ({bad_total} mismatches or nothing checked)"); sys.exit(0 if ok else 1)
