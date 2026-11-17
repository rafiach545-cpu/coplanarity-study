#!/usr/bin/env python3
"""07 test T11 (2026-11-17): independent checks of tables/R01_N_grid_300fb.csv (07 large samples), recounted from the raw files without R01 code:
(a) n_prop = n_trigger (EW) or n_trigger_both_charged (colored) of signal/inputs_large/counts.csv, and = the number of G01 events in each complete band file;
(b) for every computed row: 0 <= k_endcap <= k <= n_prop, n_fid <= n_prop, n_fid_barrel_rule <= n_prop; and k = 0 whenever n_fid = 0;
(c) n_fid, n_fid_barrel_rule (raw field fid_stage2), k, k_endcap recounted directly from signal/runs/large_atlas/G01_<tag>_<band>.jsonl;
(d) N_with_f recomputed: 300 fb^-1 * sigma * (n_trigger / n_matched) * (n_prop / n_trigger) * k / n_prop, relative difference < 1e-12;
(e) every selected event is fiducial (no row with <sct>_final true and fid false) in the raw files.
Prints T11_PASS / T11_FAIL and the number of computed rows."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); ok = {k: True for k in "abcde"}
G = pd.read_csv(f"{R}/tables/R01_N_grid_300fb.csv"); C = pd.read_csv(f"{R}/signal/inputs_large/counts.csv").set_index(["channel", "mass_gev"])
raw = {}
for (ch, m), c in C.iterrows():
    n = c.n_trigger_both_charged if ch == "colored" else c.n_trigger
    for band in ("low", "mid", "high_a"):
        f = f"{R}/signal/runs/large_atlas/G01_{ch}_{m}gev_{band}.jsonl"
        if not os.path.exists(f): continue
        ev = [json.loads(l) for l in open(f) if l.strip()]
        if len(ev) != n: continue
        for e in ev:
            for r in e:
                raw.setdefault((ch, m, round(r["lambda_keV"], 6)), []).append(r)
                if not r["fid"] and any(r.get(f"{s}_final") for s in ("Z0", "A580", "Z1160")): ok["e"] = False
nrow = 0
for r in G.itertuples():
    c = C.loc[(r.channel, r.mass_gev)]; n = c.n_trigger_both_charged if r.channel == "colored" else c.n_trigger
    ok["a"] &= r.n_prop == n
    if r.status != "computed": continue
    nrow += 1; x = raw.get((r.channel, r.mass_gev, round(r.lambda_keV, 6)), [])
    ok["a"] &= len(x) == n
    ok["b"] &= 0 <= r.k_endcap <= r.k <= r.n_prop and r.n_fid <= r.n_prop and r.n_fid_barrel_rule <= r.n_prop and (r.n_fid > 0 or r.k == 0)
    rc = (sum(bool(e["fid"]) for e in x), sum(bool(e["fid_stage2"]) for e in x), sum(bool(e.get(f"{r.sct}_final", False)) for e in x), sum(bool(e.get(f"{r.sct}_final", False)) and bool(e.get(f"{r.sct}_endcap", False)) for e in x))
    if rc != (r.n_fid, r.n_fid_barrel_rule, r.k, r.k_endcap): ok["c"] = False; print("   (c) differs", r.channel, r.mass_gev, r.lambda_keV, r.sct, rc)
    N = 300.0 * c.sigma_matched_fb * (c.n_trigger / c.n_matched) * (n / c.n_trigger) * r.k / n
    if abs(N - r.N_with_f) > 1e-12 * max(1.0, abs(N)): ok["d"] = False; print("   (d) differs", r.channel, r.mass_gev, r.lambda_keV, r.sct, N, r.N_with_f)
print(f"T11: {nrow} computed rows of {len(G)}; checks {ok}"); print("T11_PASS" if all(ok.values()) and nrow > 0 else "T11_FAIL")
