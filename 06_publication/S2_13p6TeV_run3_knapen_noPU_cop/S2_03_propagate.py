#!/usr/bin/env python3
"""Stage 2, step 3: eps_fid and eps_reco on the (m_Q, Lambda) grid for the 13.6 TeV samples. The reproduction's F6_02_grid.py is loaded unchanged (same
integrator settings, B = 2 T, Ref. [27] lengths, t < 25 ns, plane search, signal region, both SCT z settings, same per-event seeds SeedSequence([6, mass, i])
and reco stream); only the input (inputs/<tag>_events.csv here) and the checkpoint folder (logs/ here) differ. Run in-process (NWORKERS = 1 behaviour of
F6_02): a process killed by the memory watchdog exits and its lane resumes from the checkpoint. numba integrator (FAST=1, XONLY=1: validated bitwise identical).
Usage: BAND={low|mid|high_a} S2_03_propagate.py <tag>. Validation only: env S2_INPUTS, S2_LOGS (folders), NMAX (first NMAX events). Checkpoint: logs/F6_<tag>[_<band>]_events.jsonl (same naming as the reproduction)."""
import os, sys, json, importlib.util
os.environ.setdefault("FAST", "1"); os.environ.setdefault("XONLY", "1")
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
import pandas as pd
spec = importlib.util.spec_from_file_location("f6grid", f"{REP}/F6_02_grid.py"); F = importlib.util.module_from_spec(spec); sys.modules["f6grid"] = F; spec.loader.exec_module(F)
assert F.FAST and not os.environ.get("LAMS")
if __name__ == "__main__":
    IN, LOGD = os.environ.get("S2_INPUTS", f"{HERE}/inputs"), os.environ.get("S2_LOGS", f"{HERE}/logs")
    ev = pd.read_csv(f"{IN}/{F.TAG}_events.csv"); sel = ev.trigger_proxy_pass.astype(str) == "True"
    if F.CH == "colored": sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    ev = ev[sel].reset_index(drop=True)
    if os.environ.get("NMAX"): ev = ev.iloc[:int(os.environ["NMAX"])]
    jobs = [(i, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for i, r in enumerate(ev.itertuples())]
    LOG = f"{LOGD}/F6_{F.TAG}{'' if F.BAND == 'mid' else '_' + F.BAND}_events.jsonl"
    done = {json.loads(l)[0]["event"] for l in open(LOG) if l.strip()} if os.path.exists(LOG) else set()
    todo = [j for j in jobs if j[0] not in done]; print(f"{F.TAG} band {F.BAND} Lambda {F.LAMS} keV: events {len(jobs)}, done {len(done)}, to run {len(todo)}", flush=True)
    F._init_worker()
    with open(LOG, "a") as fh:
        for k, rr in enumerate(map(F.job, todo), 1):
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else str(v)) + "\n"); fh.flush()
            if k % 10 == 0: print(f"{k}/{len(todo)}", flush=True)
    print("finished", F.TAG, F.BAND, flush=True)
