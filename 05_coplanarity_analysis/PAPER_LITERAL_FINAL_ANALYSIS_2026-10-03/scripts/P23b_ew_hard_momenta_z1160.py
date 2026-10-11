#!/usr/bin/env python3
"""P23b (2026-10-09, DECISIONS_LOG D15): P23 with SCT z 1.16 mm. P23 docstring: P23 (pre-registered in D13): EW trajectories from pre-shower quirk momenta.
Events: EW2000 matched events whose pre-shower (Pythia status 23) quirk pair has pT > 200 GeV.
Column H: trajectories from the status-23 momenta; column S (control): same events from the final-state (status 1) momenta.
Per event, identical random draws for both columns: z0 ~ N(0, 4.5 cm) and SCT R-phi normals from SeedSequence([23, hepmc_event_index]).
Pipeline as P20 (one hit per quirk per layer = first crossing, SCT z not smeared, Ref. [27] lengths, t < 25 ns, plane fit from the true vertex);
Lambda = 1, 2, 4 keV. A trajectory that stops with a numerical error counts as not fiducial (as in all earlier runs).
Output: logs/P23b_events.jsonl (append-only, resumable), tables/ew_hard_momenta_test_z1160.csv. Usage: P23_ew_hard_momenta.py [n_events_limit]"""
import os, sys, gzip, json, math, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p20", f"{HERE}/P20_lambda_scan.py"); p20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p20)
p18, p4 = p20.p18, p20.p4
HEPMC = "/home/rafia/hep_tools/quirk_2000_fresh_regen_runs/EW_800GeV_L4keV/Events/run_fresh/tag_1_pythia8_events.hepmc.gz"
MATCHED = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/matched_events_full.csv"
QID, MQ, LAMS = 9000011, 800.0, (1, 2, 4)
def read_hepmc():
    out, ev = [], None
    def flush():
        if ev is None: return
        h = {p[0]: p[1:] for p in ev if abs(p[0]) == QID and p[5] == 23}; f = {p[0]: p[1:] for p in ev if abs(p[0]) == QID and p[5] == 1}
        out.append(dict(hard=(h[QID][:4], h[-QID][:4]), final=(f[QID][:4], f[-QID][:4])))
    for ln in gzip.open(HEPMC, "rt"):
        if ln.startswith("E "): flush(); ev = []
        elif ln.startswith("P "):
            x = ln.split(); ev.append((int(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[6]), int(x[8])))
    flush(); return out
def job(a):
    idx, mom = a; rng = np.random.default_rng(np.random.SeedSequence([23, idx])); z0 = rng.normal(0.0, 4.5)
    g = {(q, L): tuple(rng.standard_normal(2)) for q in (1, 2) for L in range(5, 9)}; rows = []
    for col in ("H", "S"):
        (p1, p2) = mom[col]
        for lk in LAMS:
            r = dict(hepmc_index=idx, column=col, lambda_keV=lk, z0_cm=z0)
            try:
                _, traj = p4.tth.simulate_quirk_hits(tuple(p1), tuple(p2), mass_gev=MQ, Lambda_gev=lk * 1e-6, B_tesla=2.0, charge1=-1.0, charge2=1.0,
                                                     rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
            except RuntimeError as err:
                rows.append(dict(r, fid=False, final=False, technical_error=str(err)[:80])); continue
            cr = p18.all_crossings(traj); fid = p20.fid_of(cr, -1.0, 1.0)
            rr = p18.reco(cr, z0, g, "Z1160", idx, "EW2000", True) if fid else dict(plane=False, mult=False, ds=np.nan, dw=np.nan, final=False)
            rows.append(dict(r, fid=fid, plane=rr["plane"], mult=rr["mult"], ds=rr["ds"], dw=rr["dw"], final=rr["final"]))
    return rows
if __name__ == "__main__":
    ev = read_hepmc(); M = pd.read_csv(MATCHED); assert len(ev) == len(M) == 1045
    for e, m in zip(ev, M.itertuples()):   # status-1 momenta must equal the analysis momenta (q1 = positive PDG)
        assert np.allclose(e["final"][0], (m.px1, m.py1, m.pz1, m.E1), rtol=1e-7) and np.allclose(e["final"][1], (m.px2, m.py2, m.pz2, m.E2), rtol=1e-7)
    pth = np.array([math.hypot(e["hard"][0][0] + e["hard"][1][0], e["hard"][0][1] + e["hard"][1][1]) for e in ev]); sel = np.where(pth > 200)[0]
    print("pre-shower trigger:", len(sel), "of 1045; also after-shower trigger:", int((M.quirk_pair_pt_gev.values[sel] > 200).sum()), flush=True)
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else len(sel)
    LOG = f"{HERE}/../logs/P23b_events{'_TEST' if lim < len(sel) else ''}.jsonl"; done = set()
    if os.path.exists(LOG): done = {json.loads(l)[0]["hepmc_index"] for l in open(LOG)}
    jobs = [(int(i), dict(H=ev[i]["hard"], S=ev[i]["final"])) for i in sel[:lim] if int(i) not in done]; print("to run", len(jobs), flush=True)
    with mp.Pool(10, initializer=p4._init) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap_unordered(job, jobs), 1):
            fh.write(json.dumps(rr, default=float) + "\n"); fh.flush()
            if k % 10 == 0: print(f"{k}/{len(jobs)}", flush=True)
    d = pd.DataFrame([r for l in open(LOG) for r in json.loads(l)])
    d["after_shower_trigger"] = M.quirk_pair_pt_gev.values[d.hepmc_index] > 200
    if lim == len(sel): d.to_csv(f"{T}/ew_hard_momenta_test_z1160.csv", index=False)
    TR = lambda s: s.astype(str) == "True"; n = d.hepmc_index.nunique()
    for col in ("H", "S"):
        x = d[(d.column == col)]; f = x[x.lambda_keV == 2]; nf = int(TR(f.fid).sum())
        print(f"column {col}: fiducial (2 keV) {nf}/{n} = {nf/n:.3f}", " | ".join(f"{lk} keV: fid {int(TR(y.fid).sum())}, SR {int(TR(y.final).sum())}/{int(TR(y.fid).sum())}" for lk, y in x.groupby("lambda_keV")))
