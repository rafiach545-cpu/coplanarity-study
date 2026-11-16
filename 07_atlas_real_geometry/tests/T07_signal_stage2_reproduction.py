#!/usr/bin/env python3
"""07 test T07 (2026-11-16): signal/G01_signal_07.py in the stage2 configuration (8 barrel layers) must reproduce the Stage 2 signal
(06_publication/S2_.../logs/F6_<tag>[_<band>]_events.jsonl, made by F6_02_grid.py) event by event and Lambda by Lambda:
  fid (07 station rule) == fid_stage2 (F6_02 rule recomputed by G01) == Stage 2 fid;
  Z0 and Z1160: plane, mult, final identical; Delta_s and Delta_w equal within 1e-9 cm (both NaN when no plane).
Usage: T07_signal_stage2_reproduction.py <G01 jsonl> [<G01 jsonl> ...]  (the Stage 2 file is found from the G01 name). Prints T07_PASS / T07_FAIL."""
import os, sys, json, math, re
S2L = "/home/rafia/coplanarity_study/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/logs"
ok_all, n_rows, n_fid, n_final = True, 0, 0, {"Z0": 0, "Z1160": 0}
for f in sys.argv[1:]:
    m = re.match(r"G01_(.+?)_(mid|low|high_a)(_n\d+)?\.jsonl", os.path.basename(f)); tag, band = m.group(1), m.group(2)
    ref = {json.loads(l)[0]["event"]: json.loads(l) for l in open(f"{S2L}/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl") if l.strip()}
    bad = 0
    for l in open(f):
        if not l.strip(): continue
        new = json.loads(l); old = ref[new[0]["event"]]
        for a, b in zip(new, old):
            assert a["lambda_keV"] == b["lambda_keV"]; n_rows += 1; d = []
            if not (a["fid"] == a["fid_stage2"] == b["fid"]): d.append(f"fid {a['fid']}/{a['fid_stage2']} vs {b['fid']}")
            n_fid += bool(b["fid"])
            for s in ("Z0", "Z1160"):
                for k in ("plane", "mult", "final"):
                    if bool(a.get(f"{s}_{k}", False)) != bool(b.get(f"{s}_{k}", False)): d.append(f"{s}_{k}")
                for k in ("ds", "dw"):
                    x, y = float(a.get(f"{s}_{k}", math.nan)), float(b.get(f"{s}_{k}", math.nan))
                    if not ((math.isnan(x) and math.isnan(y)) or abs(x - y) < 1e-9): d.append(f"{s}_{k} {x} vs {y}")
                n_final[s] += bool(b.get(f"{s}_final", False))
            if d: bad += 1; print(f"   DIFFERENT {tag} {band} event {a['event']} Lambda {a['lambda_keV']}: {d}")
    ok_all &= bad == 0; print(f"{os.path.basename(f)}: rows compared so far {n_rows}, differing rows in this file {bad}")
print(f"T07: {n_rows} (event, Lambda) rows, Stage 2 fiducial {n_fid}, Stage 2 final Z0 {n_final['Z0']} / Z1160 {n_final['Z1160']}; identical: {ok_all}")
print("T07_PASS" if ok_all and n_final["Z0"] > 0 else "T07_FAIL")
