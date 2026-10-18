#!/usr/bin/env python3
"""Figure 6, step 2 (2026-10-17): epsilon_fid and epsilon_reco on the (m_Q, Lambda) grid with the Table I (paper-literal) pipeline.
Input: fig6/inputs/<tag>_events.csv (step 1). Events used: trigger (pT(QQ) > 200 GeV); colored: both quirk-hadrons charged (|q| > 0.5, as Table I).
Per event i: z0 ~ N(0, 4.5 cm) and SCT draws from SeedSequence([6, mass, i]); for each Lambda in LAMS: production integrator (analysis config: 300 steps
per period, B = 2 T), first crossings, fiducial (all 16 first crossings inside the Ref. [27] lengths, t < 25 ns), p18.reco with SCT z none (Z0) and 1.16 mm
(Z1160) using the same draws, first crossing. Integration failures are counted as not fiducial (as Table I).
Usage: F6_02_grid.py <tag> [NMAX]  (NMAX: first NMAX events only; separate checkpoint).
Lambda band (env BAND): mid = 1,2,3,4,5,7,10 keV (default, checkpoint name without band suffix); low = 0.1,0.2,0.3,0.5,0.7 keV;
high = 15,20,25,30,35 keV. Env LAMS="a,b,..." overrides the list (keV).
Env FAST=1: the numba-compiled integrator (03_trajectory_sim/quirk_trajectory_numba.py, bitwise identical to v2; validated by F6_06_validate_numba.py);
checkpoint name gets the suffix _fast only for pilots/validation (NMAX set).
Checkpoint (append-only, one line per event, ordered): logs/F6_<tag>[_<band>][_pilotN[_fast]]_events.jsonl; a rerun resumes."""
import os, sys, json, time, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
BANDS = {"mid": (1, 2, 3, 4, 5, 7, 10), "low": (0.1, 0.2, 0.3, 0.5, 0.7), "high": (15, 20, 25, 30, 35),
         "high_a": (15, 20, 25)}   # high_a: the part of the high band where the 20-million-step ceiling removes <= 13% of the events fiducial at 10 keV
                                   # (scan: fig6/F6_high_step_ceiling_scan.csv); at 30-35 keV it removes up to 56% and needs a larger ceiling and more memory
BAND = os.environ.get("BAND", "mid")
LAMS = tuple(float(x) for x in os.environ["LAMS"].split(",")) if os.environ.get("LAMS") else BANDS[BAND]
TAG = sys.argv[1]; NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else None
CH, MQ = TAG.split("_")[0], float(TAG.split("_")[1].replace("gev", ""))
SNAME = f"F6_{TAG}"; p18.SID[SNAME] = 1000 + int(MQ)                     # own random stream id for reco (not shared with the Table I samples)
FAST = os.environ.get("FAST") == "1"
def _init_worker():
    p4._init()
    if FAST:
        sys.path.insert(0, f"{p4.BASE}/03_trajectory_sim")
        from quirk_trajectory_numba import integrate_trajectory_numba, integrate_trajectory_numba_xonly
        p4.tth.integrate_trajectory = integrate_trajectory_numba_xonly if os.environ.get("XONLY") == "1" else integrate_trajectory_numba
def fid_of(cr):
    f = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}
    return all((q, L) in f and abs(f[(q, L)]["z_lab"]) < p4.HALF[L] and f[(q, L)]["t_ns"] < p4.R["timing_ns"] for q in (1, 2) for L in range(1, 9))
def job(a):
    i, P1, P2, c1, c2 = a; p18.SID[SNAME] = 1000 + int(MQ)
    rng = np.random.default_rng(np.random.SeedSequence([6, int(MQ), i])); z0 = rng.normal(0.0, p4.R["beamspot_cm"])
    g = {(q, L): rng.standard_normal(2) for q in (1, 2) for L in range(1, 9)}; out = []
    for lam in LAMS:
        t0 = time.time()
        try:
            _, tr = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=MQ, Lambda_gev=lam * 1e-6, B_tesla=p4.R["B_tesla"], charge1=c1, charge2=c2,
                                               rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=p4.R["max_layer_r_cm"])
        except Exception as e:
            out.append(dict(event=i, lambda_keV=lam, fid=False, error=str(e)[:80], t_s=round(time.time() - t0, 2))); continue
        cr = p18.all_crossings(tr); del tr, _                                  # free the trajectory before the next Lambda (memory)
        f = fid_of(cr); row = dict(event=i, lambda_keV=lam, fid=f, error="")
        for sct in ("Z0", "Z1160"):
            r = p18.reco(cr, z0, g, sct, i, SNAME, True) if f else dict(plane=False, mult=False, final=False, ds=np.nan, dw=np.nan)
            row.update({f"{sct}_plane": r["plane"], f"{sct}_mult": r["mult"], f"{sct}_final": r["final"], f"{sct}_ds": r["ds"], f"{sct}_dw": r["dw"]})
        row["t_s"] = round(time.time() - t0, 2); row["integrator"] = "numba" if FAST else "v2"; out.append(row)
    return out
if __name__ == "__main__":
    ev = pd.read_csv(f"{HERE}/../fig6/inputs/{TAG}_events.csv")
    sel = ev.trigger_proxy_pass.astype(str) == "True"
    if CH == "colored": sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    ev = ev[sel].reset_index(drop=True)
    if NMAX: ev = ev.iloc[:NMAX]
    jobs = [(i, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for i, r in enumerate(ev.itertuples())]
    LOG = f"{HERE}/../logs/F6_{TAG}{'' if BAND == 'mid' and not os.environ.get('LAMS') else '_' + (BAND if not os.environ.get('LAMS') else 'L' + os.environ['LAMS'].replace(',', '-'))}{f'_pilot{NMAX}' if NMAX else ''}{'_fast' if FAST and NMAX else ''}_events.jsonl"; done = set()
    if os.path.exists(LOG): done = {json.loads(l)[0]["event"] for l in open(LOG) if l.strip()}
    todo = [j for j in jobs if j[0] not in done]; print(f"{TAG} band {BAND} Lambda {LAMS} keV: events {len(jobs)}, done {len(done)}, to run {len(todo)} -> {os.path.basename(LOG)}", flush=True)
    NW = int(os.environ.get("NWORKERS", 3))
    if NW == 1:                                                              # in-process, no pool: if the process is killed (e.g. out of memory)
        _init_worker(); it = map(job, todo)                                  # it simply exits and a rerun resumes (a killed pool worker would hang)
        with open(LOG, "a") as fh:
            for k, rr in enumerate(it, 1):
                fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else str(v)) + "\n"); fh.flush()
                if k % 10 == 0: print(f"{k}/{len(todo)}", flush=True)
    else:
      with mp.Pool(NW, initializer=_init_worker) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap(job, todo), 1):
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else str(v)) + "\n"); fh.flush()
            if k % 10 == 0: print(f"{k}/{len(todo)}", flush=True)
    print("finished", TAG, flush=True)
