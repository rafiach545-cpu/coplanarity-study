#!/usr/bin/env python3
"""07 test T05 (2026-11-15): the 07 chain in its stage2 configuration (backgrounds/C01_conversion_bkg.py stage2) must reproduce the Stage 2
13.6 TeV converted-photon background event by event: same hit counts (conversion raw, pile-up interactions, pile-up raw, merged), same number of
plane candidates and best layer count, same plane / multiplicity / final decisions, |d Delta_s| and |d Delta_w| < 1e-6 cm (absolute).
Why absolute: the pair crossings differ by <= 1.3e-8 cm (Stage 2 finds them with brentq on a grid, 07 analytically; T02 (b)); for planes with
Delta_s ~ 1e-5 cm this gives a relative difference of up to ~3e-3 (2026-11-15: max |d Delta_s| = 3.3e-8 cm), 1e6 times below the 0.01 cm cut.
This validates in one go: detsim07 (pair propagation = Stage 2 track34, pile-up response and sampling, hit response, merging) and cop07 (stations
reduce to the 8 barrel layers; seeding / iterative fit / selection identical to coplanarity_fit).
Usage: T05_stage2_reproduction.py <C01 run folder> <Stage 2 folder> [config LITERAL] [sct Z0]"""
import sys, glob, numpy as np, pandas as pd
new = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{sys.argv[1]}/chunk_*.csv")))
old = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{sys.argv[2]}/chunk_*.csv")))
cfg = sys.argv[3] if len(sys.argv) > 3 else "LITERAL"; sct = sys.argv[4] if len(sys.argv) > 4 else "Z0"
old = old[old.config == cfg].set_index("event"); new = new[(new.status == "ok") & (new.sct == sct)].set_index("event")
ev = new.index.intersection(old.index); o, n = old.loc[ev], new.loc[ev]
print(f"events compared: {len(ev)} (new run {len(new)}, Stage 2 rows {len(old)})")
ok = True
for c in ("n_conv_hits_raw", "n_pu_interactions", "n_pu_hits_raw", "n_hits_merged", "n_candidates", "best_layers"):
    d = int((o[c].astype(int) != n[c].astype(int)).sum()); ok &= d == 0; print(f"  {c:20s} differing events: {d}")
for c in ("plane", "mult", "dw_pass", "ds_pass", "final"):
    d = int((o[c].astype(str) != n[c].astype(str)).sum()); ok &= d == 0; print(f"  {c:20s} differing events: {d}   (Stage 2 True: {int((o[c].astype(str) == 'True').sum())}, new True: {int((n[c].astype(str) == 'True').sum())})")
for c in ("ds", "dw"):
    a, b = o[c].to_numpy(float), n[c].to_numpy(float); both = ~np.isnan(a) & ~np.isnan(b)
    ad = np.max(np.abs(a[both] - b[both])) if both.any() else 0.0; rel = np.max(np.abs(a[both] - b[both]) / np.maximum(np.abs(a[both]), 1e-30)) if both.any() else 0.0
    nanmis = int((np.isnan(a) != np.isnan(b)).sum()); ok &= ad < 1e-6 and nanmis == 0
    print(f"  {c:20s} max |difference| {ad:.1e} cm (max relative {rel:.1e}), NaN mismatches {nanmis}")
print("T05_PASS" if ok and len(ev) > 0 else "T05_FAIL")
