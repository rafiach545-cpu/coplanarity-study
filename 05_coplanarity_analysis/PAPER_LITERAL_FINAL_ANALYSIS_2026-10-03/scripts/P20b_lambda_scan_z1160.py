#!/usr/bin/env python3
"""P20b (2026-10-08): P20 with the paper-text SCT z resolution (1.16 mm), 2000-event samples only, FIRST and ALL modes.
P20 docstring:
Lambda scan of the paper's Table I eps_reco column (paper: EW 800 GeV  1/2/3/4/5 keV -> 0.11/0.41/0.65/0.72/0.74;
colored 1.8 TeV 1/2/3/5/10 keV -> 0.083/0.35/0.59/0.74/0.58). The oscillation amplitude scales as 1/Lambda^2 (Eq. 1), so this tests
whether our eps_reco follows the paper's amplitude dependence or only matches at the benchmark point.
Same trigger events, vertices and SCT draws as P18; every layer crossing < 25 ns is a hit; Ref. [27] lengths; SCT z not smeared (Z0)
and 580 um (Z580); hit cut >= 2 (primary) and exactly 2. Fiducial recomputed per Lambda with the P18 definition (first crossing of all
16 quirk-layer pairs inside the lengths, t < 25 ns; colored: both charged). Validation: at the benchmark Lambda the fiducial flag and
the ALL-mode results must equal tables/all_crossings_per_event.csv. Output: tables/lambda_scan_per_event.csv, tables/lambda_scan_summary.csv"""
import os, sys, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18)
p4 = p18.p4
LAMS = {"EW": (1, 2, 3, 4, 5), "COL": (1, 2, 3, 5, 10)}
PAPER = {"EW": {1: .11, 2: .41, 3: .65, 4: .72, 5: .74}, "COL": {1: .083, 2: .35, 3: .59, 5: .74, 10: .58}}
def fid_of(cr, c1, c2):
    if c1 == 0 or c2 == 0: return False
    f = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}
    return all((q, L) in f and abs(f[(q, L)]["z_lab"]) < p4.HALF[L] and f[(q, L)]["t_ns"] < 25.0 for q in (1, 2) for L in range(1, 9))
def job(a):
    s, key, eid, P1, P2, c1, c2, z0, g = a; b = "EW" if s.startswith("EW") else "COL"; mq = p4.PAR[b][0]; out = []
    for lk in LAMS[b]:
        try: _, traj = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=mq, Lambda_gev=lk * 1e-6, B_tesla=2.0, charge1=c1, charge2=c2, rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
        except RuntimeError as err:   # step ceiling (near-threshold pair, very short period): logged, counted as not fiducial
            out += [dict(sample=s, key=key, event_id=eid, lambda_keV=lk, mode=mo, sct=sc, fid=False, final=False, technical_error=str(err)[:80]) for mo, sc in (("FIRST", "Z1160"), ("ALL", "Z1160"))]; continue
        cr = p18.all_crossings(traj); fid = fid_of(cr, c1, c2)
        for mode, sct in (("FIRST", "Z1160"), ("ALL", "Z1160")):
            r = p18.reco(cr, z0, g, sct, key, s, mode == "FIRST") if fid else dict(plane=False, mult=False, ds=np.nan, dw=np.nan, final=False, max_hits_per_layer=0, sel_layers="")
            ex2 = False
            if r["final"]:
                import ast; ex2 = sorted(ast.literal_eval(r["sel_layers"]).values()) in ([1] + [2] * 7, [2] * 8)
            out.append(dict(sample=s, key=key, event_id=eid, lambda_keV=lk, mode=mode, sct=sct, fid=fid, final_exact2=ex2, **r))
    return out
if __name__ == "__main__":
    ref = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); ref = ref[(ref.geom == "B") & (ref.bs == "CV")]
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); jobs = []
    for s in ("EW2000", "COL2000"):
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv"); m = p4.momenta(s)
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None; z0s = {}
        for e in ev.itertuples():
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"])
            if len(c) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()): continue
            rng = seq if seq is not None else np.random.default_rng(int(e.seed)); z0s[int(e.key)] = (p4.fp.stream_draws(rng, c)[0], e)
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        for key in sorted(z0s):
            z0, e = z0s[key]; rng = seq if seq is not None else np.random.default_rng(int(e.seed))
            exk = ex[(ex["sample"] == s) & (ex.key == key)].sort_values(["quirk", "layer"])
            z0b, g = p4.fp.stream_draws(rng, cr0[cr0.key == key].sort_values(["quirk", "layer"]), exk.copy() if len(exk) else None)
            if len(exk) == 0: continue
            r = m.iloc[int(key)]; jobs.append((s, int(key), int(e.event_id), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2), z0, g))
    LOG = f"{HERE}/../logs/P20b_lambda_scan_z1160_events.jsonl"; import json   # append-only, one line per finished event; rerun resumes
    done = set()
    if os.path.exists(LOG):
        for ln in open(LOG): o = json.loads(ln); done.add((o[0]["sample"], o[0]["key"]))
    todo = [j for j in jobs if (j[0], j[1]) not in done]; print("events", len(jobs), "already done", len(done), "to run", len(todo), flush=True)
    with mp.Pool(10, initializer=p4._init) as pool, open(LOG, "a") as fh:
        for i, rr in enumerate(pool.imap_unordered(job, todo, chunksize=1), 1):
            fh.write(json.dumps(rr, default=float) + "\n"); fh.flush()
            if i % 10 == 0: print(f"{i}/{len(todo)}", flush=True)
    out = [r for ln in open(LOG) for r in json.loads(ln)]
    d = pd.DataFrame(out); d.to_csv(f"{T}/lambda_scan_z1160_per_event.csv", index=False); TR = lambda x: x.astype(str) == "True"
    # validation at the benchmark point
    A = pd.read_csv(f"{T}/all_crossings_per_event.csv"); bad = 0  # FIRST at the benchmark is checked against mode FIRST below
    for s in ("EW2000", "COL2000"):
        lb = 4 if s.startswith("EW") else 2
        for md, sct in (("FIRST", "Z1160"), ("ALL", "Z1160")):
            x = d[(d["sample"] == s) & (d.lambda_keV == lb) & (d["mode"] == md) & (d.sct == sct)].set_index("key").sort_index(); y = A[(A["sample"] == s) & (A["mode"] == md) & (A.sct == sct)].set_index("key").loc[x.index]
            for c in ("fid", "plane", "mult", "final"): bad += int((TR(x[c]) != TR(y[c])).sum())
    print("validation vs all_crossings_per_event at benchmark Lambda (mismatches):", bad)
    rows = []
    for (s, lk, mode, sct), x in d.groupby(["sample", "lambda_keV", "mode", "sct"]):
        b = "EW" if s.startswith("EW") else "COL"; ch = x[x.key.isin(x.key)]; f = x[TR(x.fid)]
        rows.append(dict(sample=s, lambda_keV=lk, mode=mode, sct=sct, n_events=len(x), n_tech_error=int(x.technical_error.notna().sum()) if "technical_error" in x else 0, n_fid=len(f), k_ge2=int(TR(f.final).sum()), k_ex2=int(TR(f.final_exact2).sum()), paper_reco=PAPER[b][lk]))
    S = pd.DataFrame(rows); S.to_csv(f"{T}/lambda_scan_z1160_summary.csv", index=False); print(S.to_string())
