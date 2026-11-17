#!/usr/bin/env python3
"""07 D01 (2026-11-17): what the ATLAS-only selected events are. For one mass point and one Lambda, reruns G01 atlas (signal/G01_signal_07.py,
its code executed unchanged up to its __main__ block; cop07.analyse wrapped only to record the winner plane) on
  (a) every event selected in ATLAS (server large_atlas, <sct>_final) but not in ideal (server large_ideal), for any SCT setting, and
  (b) up to 150 events selected in both (control),
and records per SCT setting the element of every station of the winner plane, and per quirk the elements hit (true hits within 25 ns).
Classes of the winner plane: barrel-only (all 8 stations on barrel layers), end-cap-only (no barrel element), mixed (barrel + end-cap).
Runs on the laptop: server and laptop agree in ~97% of rows (X01), so a few events may not be selected here; they are counted.
Usage: D01_endcap_gain.py <tag> <lambda_keV> [--workers 3]. Output: compare/D01_runs/D01_<tag>_<lambda>.jsonl"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); OUTD = f"{HERE}/D01_runs"
ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("lam", type=float); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
sys.argv = [f"{R}/signal/G01_signal_07.py", "atlas", a.tag, "mid" if 1 <= a.lam <= 10 else ("low" if a.lam < 1 else "high_a")]
src = open(f"{R}/signal/G01_signal_07.py").read(); __file__ = f"{R}/signal/G01_signal_07.py"
exec(compile(src[:src.index('if __name__ == "__main__":')], __file__, "exec"))
assert any(abs(l - a.lam) < 1e-9 for l in F.LAMS); F.LAMS = [l for l in F.LAMS if abs(l - a.lam) < 1e-9]
_an = cop07.analyse; REC = []
def analyse_rec(hits, origin, els):
    res, w = _an(hits, origin, els); REC.append(dict(stations=w["stations"] if w else None, final=res["final"])); return res, w
cop07.analyse = analyse_rec
_cr = crossings; CR = []
def crossings_rec(x, t):
    out = _cr(x, t); CR.append([ELS[c[0]]["name"] for c in out if c[5] and c[4] < F.p4.R["timing_ns"]]); return out
crossings = crossings_rec
def job_rec(j):
    REC.clear(); CR.clear(); rows = job(j)
    return dict(event=j[0], rows=rows, planes=list(REC), quirk_hits=list(CR))
if __name__ == "__main__":
    import pandas as pd
    def load(d):
        out = {}
        for l in open(f"{R}/signal/runs/{d}/G01_{a.tag}_{sys.argv[3]}.jsonl"):
            for r in json.loads(l):
                if abs(r["lambda_keV"] - a.lam) < 1e-9: out[r["event"]] = r
        return out
    S, I = load("large_atlas"), load("large_ideal")
    extra = sorted(e for e in S if any(S[e].get(f"{s}_final") and not I[e].get(f"{s}_final") for s in SETTINGS))
    both = sorted(e for e in S if S[e].get("Z0_final") and I[e].get("Z0_final"))[:150]
    ev = pd.read_csv(f"{R}/signal/inputs_large/{a.tag}_events.csv").set_index("event_id"); want = set(extra) | set(both)
    jobs = [(int(e), (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for e, r in ev.loc[sorted(want)].iterrows()]
    od = OUTD; os.makedirs(od, exist_ok=True); out = f"{od}/D01_{a.tag}_{a.lam:g}.jsonl"
    print(f"D01 {a.tag} Lambda {a.lam} keV: extra {len(extra)}, control {len(both)} -> {out}", flush=True)
    enc = lambda v: v.item() if hasattr(v, "item") else str(v)
    with mp.Pool(a.workers, initializer=F._init_worker) as pool, open(out, "w") as fh:
        for r in pool.imap(job_rec, jobs):
            r["group"] = "extra" if r["event"] in extra else "both"; r["server_atlas"] = S[r["event"]]; r["server_ideal"] = I[r["event"]]
            fh.write(json.dumps(r, default=enc) + "\n")
    print("D01_DONE", flush=True)
