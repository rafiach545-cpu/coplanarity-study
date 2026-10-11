#!/usr/bin/env python3
"""v7 primary Table I (2026-10-06): Ref. [27] barrel lengths; EVERY layer crossing within 25 ns is a hit (paper: "The intersections
of the trajectories ... are calculated"); hit multiplicity read as ">= 2 hits in 7 layers, >= 1 in the 8th" (primary) and
"exactly 2 hits in 7 layers" (sensitivity). Trigger and fiducial unchanged. Inputs: P3 recount, all_crossings_per_event.csv.
Output: tables/v7_primary_table_I.csv"""
import os, sys, json, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
from stats_utils import row
G = json.load(open(f"{T}/P3_raw_trigger_recount.json")); M = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv"); A = pd.read_csv(f"{T}/all_crossings_per_event.csv")
PAP = {"EW": {"trigger": .10, "fiducial": .28, "reconstruction": .72}, "COL": {"trigger": .24, "fiducial": .28, "reconstruction": .35}}
TR = lambda s: s.astype(str) == "True"; out = []
def cat(p): return "Strongly inconsistent" if p < .01 else "Statistically inconsistent" if p < .05 else "Borderline / mild tension" if p < .10 else "No statistically significant inconsistency"
for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
    b = "EW" if s.startswith("EW") else "COL"; g = G[s]
    r = row(int(g["trigger_final"]), int(g["matched"]), PAP[b]["trigger"]); out.append(dict(sample=s, quantity="trigger", sct="—", multiplicity="—", **r, category=cat(r["p_exact_vs_paper"])))
    f = M[(M["sample"] == s) & (M.acceptance == "B") & (M.beamspot == "CV") & (M.sct_z == "Z0")].iloc[0]
    r = row(int(f.fiducial), int(f.trigger_analysed), PAP[b]["fiducial"]); out.append(dict(sample=s, quantity="fiducial", sct="—", multiplicity="—", **r, category=cat(r["p_exact_vs_paper"])))
    for sct in ["Z0", "Z580", "Z1160"]:
        x = A[(A["sample"] == s) & (A["mode"] == "ALL") & (A.sct == sct) & TR(A.fid)]; assert len(x) == int(f.fiducial)
        for mult, col in (("at least 2 (primary)", "final"), ("exactly 2 (sensitivity)", "final_exact2")):
            k = int(TR(x[col]).sum()); r = row(k, len(x), PAP[b]["reconstruction"])
            out.append(dict(sample=s, quantity="reconstruction", sct=sct, multiplicity=mult, **r, category=cat(r["p_exact_vs_paper"])))
d = pd.DataFrame(out); d.to_csv(f"{T}/v7_primary_table_I.csv", index=False)
print(d[d.quantity == "reconstruction"][["sample", "sct", "multiplicity", "k", "n", "frac", "p_exact_vs_paper"]].round(3).to_string())
