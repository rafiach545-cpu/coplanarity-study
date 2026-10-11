#!/usr/bin/env python3
"""v3 primary background tables (paper-stated |eta|<1.8, SCT 34/1160 um, pixel merging, primary-vertex fit; existing events only).
Inputs: logs/P8_chunks_ETA_MERGE (pile-up), logs/P10_chunks_ETA (conversion + pile-up), tables/conversion_acceptance_A_per_event.csv.
Self-checks: conversion part of P10e (n_conv_hits_raw) equals P9d A_Z1160_PV n_raw_hits event by event.
Output: tables/v3_pileup_primary.csv, tables/v3_conversion_primary.csv"""
import os, sys, glob, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; L = f"{HERE}/../logs"; sys.path.insert(0, HERE)
from stats_utils import row
TR = lambda s: s.astype(str) == "True"
pu = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{L}/P8_chunks_ETA_MERGE/chunk_*.csv"))); assert pu.event_i.is_unique
N = len(pu); out = []
prev = pd.Series(True, index=pu.index)
for st, m, seq, paper in [("plane with >=1 hit in >=4 of 8 layers", pu.best_layers >= 4, False, 1e-3), ("plane with >=1 hit in all 8 layers", pu.best_layers >= 8, False, 6e-5),
                          ("Sec. III C plane", TR(pu.sec3c_plane_found), True, None), ("hit multiplicity 7x2+1", TR(pu.hit_multiplicity_pass), True, None),
                          ("dw < 1 cm", TR(pu.delta_w_pass), True, None), ("ds < 0.01 cm = signal region", TR(pu.delta_s_pass_0p01), True, None)]:
    if seq: m = prev & m; prev = m
    r = row(int(m.sum()), N, paper); r["stage"] = st; r["paper_approx"] = paper
    if paper: r["comparison"] = "compatible with the paper's approximate rate" if r["wilson95_lo"] <= paper <= r["wilson95_hi"] else ("higher than the paper's approximate rate" if r["frac"] > paper else "lower than the paper's approximate rate")
    out.append(r)
P = pd.DataFrame(out); assert (P.iloc[-1].k == int(TR(pu.final_sec_iv_pass).sum())); P.to_csv(f"{T}/v3_pileup_primary.csv", index=False)
cA = pd.read_csv(f"{T}/conversion_acceptance_A_per_event.csv")
ov = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{L}/P10_chunks_ETA/chunk_*.csv"))); ov = ov[ov.config == "LITERAL"].set_index("event").sort_index()
a = cA[cA.config == "A_Z1160_PV"].set_index("event").loc[ov.index]
assert (ov.n_conv_hits_raw.fillna(-1).astype(int) == a.n_raw_hits.fillna(-1).astype(int)).all(), "conversion hits differ between P10e and P9d"
rows = []
def flow(name, d, pl, mu, fi):
    n = len(d)
    for st, m in [("plane", pl), ("hit multiplicity", pl & mu), ("signal region", pl & mu & fi)]:
        r = row(int(m.sum()), n); r.update(setup=name, stage=st, event_ids=" ".join(map(str, d.index[m])) if m.sum() <= 30 else "")
        rows.append(r)
for cfg, name in [("A_Z1160_PV", "conversion only, SCT z 1.16 mm"), ("A_Z580_PV", "conversion only, SCT z 0.58 mm"), ("A_Z0_PV", "conversion only, no SCT z smearing")]:
    d = cA[cA.config == cfg].set_index("event"); flow(name, d, TR(d.plane), TR(d.mult), TR(d.final))
flow("conversion + pile-up (mu=50), SCT z 1.16 mm", ov, TR(ov.plane), TR(ov.mult), TR(ov.final))
C = pd.DataFrame(rows); C.to_csv(f"{T}/v3_conversion_primary.csv", index=False)
print(P[["stage", "k", "n", "frac", "wilson95_lo", "wilson95_hi", "cp95_upper_one_sided"]].to_string()); print(C[["setup", "stage", "k", "n", "cp95_upper_one_sided", "event_ids"]].to_string())
anc = ov[TR(ov.plane) & TR(ov.mult)][["ds", "dw", "winner_conv_hits", "winner_pileup_hits"]]
print("overlay plane+mult:", len(anc), "min ds", anc.ds.min() if len(anc) else None)
