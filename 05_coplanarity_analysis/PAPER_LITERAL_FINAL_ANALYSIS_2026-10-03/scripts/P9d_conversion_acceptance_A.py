#!/usr/bin/env python3
"""Correction audit: converted-photon background (existing 9139 photons, same per-event seeds as P9) under the paper-stated
|eta| < 1.8 acceptance (geometry A) for SCT z in {1160, 580, 0} um, primary-vertex fit origin. Uses P9's own literal_event
with its CONFIGS replaced; A/Z1160 must equal P9's stored SYS_ETA rows (asserted).
Output: tables/conversion_acceptance_A_per_event.csv, tables/conversion_acceptance_A_cutflow.csv"""
import os, sys, glob, importlib.util, multiprocessing as mp, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
spec = importlib.util.spec_from_file_location("p9", f"{HERE}/P9_literal_conversion.py"); p9 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p9)
sys.path.insert(0, HERE); from stats_utils import row
p9.CONFIGS = {"A_Z1160_PV": ("A", "Z1160", "PV"), "A_Z580_PV": ("A", "Z580", "PV"), "A_Z0_PV": ("A", "Z0", "PV")}
def init():
    p9._init(); p9.CONFIGS = {"A_Z1160_PV": ("A", "Z1160", "PV"), "A_Z580_PV": ("A", "Z580", "PV"), "A_Z0_PV": ("A", "Z0", "PV")}
def job(i): return p9.literal_event(i)
if __name__ == "__main__":
    n = len(pd.read_csv(f"{p9.PC}/zgamma_photons.csv")); out = []
    with mp.Pool(10, initializer=init) as pool:
        for r in pool.imap_unordered(job, range(n), chunksize=50): out += r
    d = pd.DataFrame(out).sort_values(["config", "event"]); d.to_csv(f"{T}/conversion_acceptance_A_per_event.csv", index=False)
    old = pd.concat(pd.read_csv(f) for f in glob.glob(f"{HERE}/../logs/P9_chunks_LITERAL/chunk_*.csv"))
    a = d[d.config == "A_Z1160_PV"].set_index("event").sort_index(); b = old[old.config == "SYS_ETA"].set_index("event").sort_index()
    for c in ("plane", "mult", "final"): assert (a[c].astype(str) == b[c].astype(str)).all(), c
    print("self-check: A_Z1160_PV identical to stored SYS_ETA (plane/mult/final)")
    TR = lambda s: s.astype(str) == "True"; rows = []
    for c, g in d.groupby("config"):
        pl = TR(g.plane); mu = pl & TR(g.mult); fi = mu & TR(g.final)
        for st, m in [("Sec. III C plane", pl), ("hit multiplicity", mu), ("final Sec. IV", fi)]:
            rows.append(dict(config=c, stage=st, **row(int(m.sum()), len(g)), event_ids=" ".join(map(str, g.event[m])) if m.sum() <= 40 else ""))
    cf = pd.DataFrame(rows); cf.to_csv(f"{T}/conversion_acceptance_A_cutflow.csv", index=False); print(cf[["config", "stage", "k", "n", "cp95_upper_one_sided"]].to_string())
