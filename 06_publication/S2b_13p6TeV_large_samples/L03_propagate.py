#!/usr/bin/env python3
"""Stage 2b, step 3: eps_fid and eps_reco for the large samples, Lambda = 2, 3, 4, 5, 7, 10 keV. The reproduction's F6_02_grid.py is loaded unchanged (as
S2_03_propagate.py: same integrator settings, geometry, plane search, signal region, both SCT z settings, numba integrator FAST=1 XONLY=1); the Lambda list is
set with its LAMS option, and the event number passed to it is event_id (100000 + index, see L02), so the per-event seeds differ from Stage 2.
Events: triggered and (colored) both quirk-hadrons charged. Parallel over events (fork pool, F6_02 worker initialiser).
Usage: L03_propagate.py <channel> <mass> [n_workers]. Env NMAX: first NMAX events (timing test). Checkpoint: logs/F6_<tag>_L2-10_events.jsonl (resumable)."""
import os, sys, json, time, importlib.util, multiprocessing as mp
os.environ.setdefault("FAST", "1"); os.environ.setdefault("XONLY", "1"); os.environ["LAMS"] = "2,3,4,5,7,10"
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
ch, m = sys.argv[1], int(sys.argv[2]); NW = int(sys.argv[3]) if len(sys.argv) > 3 else 4; TAG = f"{ch}_{m}gev"
sys.argv = [sys.argv[0], TAG]                                                       # F6_02 reads TAG (channel, mass) from argv[1]
import pandas as pd
spec = importlib.util.spec_from_file_location("f6grid", f"{REP}/F6_02_grid.py"); F = importlib.util.module_from_spec(spec); sys.modules["f6grid"] = F; spec.loader.exec_module(F)
assert F.FAST and F.LAMS == (2.0, 3.0, 4.0, 5.0, 7.0, 10.0) and F.TAG == TAG and F.MQ == m
def run(j):
    t0 = time.time(); r = F.job(j); return r, time.time() - t0
if __name__ == "__main__":
    ev = pd.read_csv(f"{HERE}/inputs/{TAG}_events.csv"); sel = ev.trigger_proxy_pass.astype(str) == "True"
    if ch == "colored": sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    ev = ev[sel].reset_index(drop=True)
    if os.environ.get("NMAX"): ev = ev.iloc[:int(os.environ["NMAX"])]
    jobs = [(int(r.event_id), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for r in ev.itertuples()]
    LOG = f"{HERE}/logs/F6_{TAG}_L2-10_events.jsonl"
    done = {json.loads(l)[0]["event"] for l in open(LOG) if l.strip()} if os.path.exists(LOG) else set()
    todo = [j for j in jobs if j[0] not in done]; t0 = time.time(); print(f"{TAG} Lambda {F.LAMS} keV: events {len(jobs)}, done {len(done)}, to run {len(todo)}, workers {NW}", flush=True)
    with mp.get_context("fork").Pool(NW, initializer=F._init_worker) as pool, open(LOG, "a") as fh:
        for k, (rr, dt) in enumerate(pool.imap_unordered(run, todo), 1):
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else str(v)) + "\n"); fh.flush()
            if k % 25 == 0: print(f"{k}/{len(todo)} {time.time() - t0:.0f}s", flush=True)
    print(f"finished {TAG} {len(todo)} events in {time.time() - t0:.1f}s with {NW} workers", flush=True); print("L03_EXIT=0")
