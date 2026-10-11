#!/usr/bin/env python3
"""v2 classification tables (correction of 2026-10-03). Inputs: acceptance_longitudinal_matrix.csv (P4c),
P3_raw_trigger_recount.json, background tables. No new events.
PRIMARY  = acceptance A (paper-stated effective |eta|<1.8, barrel only, no finite-z boundary), beam spot CV
           (one common 45 mm z shift per event, fit relative to the true vertex), SCT R-phi 34 um,
           SCT z reported for every treatment: Z1160 (2x Ref.[27] z, INFERRED), Z580 (1x, sensitivity), Z0 (UNDOCUMENTED).
SENSITIVITY = acceptance B (finite barrel of Ref. [27], INFERRED); beam-spot readings CO / PH."""
import os, sys, json, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
from stats_utils import row
M = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv"); G = json.load(open(f"{T}/P3_raw_trigger_recount.json"))
PAPER = {"EW": {"trigger": .10, "fiducial": .28, "reco": .72}, "COL": {"trigger": .24, "fiducial": .28, "reco": .35}}
def cat(p):
    return "n/a" if p is None or (isinstance(p, float) and np.isnan(p)) else ("Strongly inconsistent" if p < .01 else "Statistically inconsistent" if p < .05 else "Borderline / mild tension" if p < .10 else "Consistent")
SZLAB = {"Z1160": "SCT z 1160 um (2x580, INFERRED)", "Z580": "SCT z 580 um (1x Ref.[27], sensitivity)", "Z0": "no SCT z smearing (UNDOCUMENTED)"}
def table(acc, bs="CV"):
    out = []
    for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
        b = "EW" if s.startswith("EW") else "COL"; g = G[s]
        r = row(int(g["trigger_final"]), int(g["matched"]), PAPER[b]["trigger"])
        out.append(dict(sample=s, quantity="trigger", treatment="—", **r, category=cat(r["p_exact_vs_paper"])))
        x = M[(M["sample"] == s) & (M.acceptance == acc) & (M.beamspot == bs)]
        f = x.iloc[0]; r = row(int(f.fiducial), int(f.trigger_analysed), PAPER[b]["fiducial"])
        out.append(dict(sample=s, quantity="fiducial", treatment="—", **r, category=cat(r["p_exact_vs_paper"])))
        for sz in ["Z1160", "Z580", "Z0"]:
            y = x[x.sct_z == sz].iloc[0]; r = row(int(y.final), int(y.fiducial), PAPER[b]["reco"])
            out.append(dict(sample=s, quantity="reconstruction", treatment=SZLAB[sz], plane=int(y.plane), mult=int(y.mult), **r, category=cat(r["p_exact_vs_paper"])))
    return pd.DataFrame(out)
P = table("A"); P.insert(0, "acceptance", "A: paper-stated |eta|<1.8"); P.to_csv(f"{T}/v2_primary_table_I.csv", index=False)
S = table("B"); S.insert(0, "acceptance", "B: finite barrel Ref.[27] (INFERRED)"); S.to_csv(f"{T}/v2_finite_barrel_sensitivity.csv", index=False)
bsr = M[["sample", "acceptance", "sct_z", "beamspot", "fiducial", "plane", "mult", "final", "eps_reco"]].copy()
bsr["beamspot_reading"] = bsr.beamspot.map({"CV": "one common shift/event, fit from true vertex", "CO": "one common shift/event, fit from origin", "PH": "independent 45 mm shift of every hit"})
bsr.to_csv(f"{T}/v2_beamspot_readings.csv", index=False)
print(P[["sample", "quantity", "treatment", "k", "n", "frac", "wilson95_lo", "wilson95_hi", "p_exact_vs_paper", "category"]].to_string())
