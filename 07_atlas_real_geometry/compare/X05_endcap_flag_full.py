#!/usr/bin/env python3
"""07 X05 (2026-11-17): over the full server grid (13 points x 15 Lambda, signal/runs/large_atlas vs large_ideal), per SCT setting: number of
ATLAS-selected rows, of them selected also in ideal, ATLAS-only; and the G01 flag <sct>_endcap (the winner plane uses at least one end-cap element)
for both groups. ATLAS-only with endcap False would be a barrel-only gain. Writes tables/X05_endcap_flag_full.csv."""
import os, json, glob, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); rows = []
for f in sorted(glob.glob(f"{R}/signal/runs/large_atlas/G01_*.jsonl")):
    A, I = {}, {}
    for d, fn in ((A, f), (I, f.replace("large_atlas", "large_ideal"))):
        for l in open(fn):
            for r in json.loads(l): d[(r["event"], r["lambda_keV"])] = r
    for s in ("Z0", "A580", "Z1160"):
        for k, r in A.items():
            if r.get(f"{s}_final"):
                rows.append(dict(file=os.path.basename(f), sct=s, both=bool(I[k].get(f"{s}_final")), endcap=bool(r.get(f"{s}_endcap"))))
D = pd.DataFrame(rows); S = D.groupby(["sct", "both", "endcap"]).size().unstack(fill_value=0).reset_index()
S["group"] = S.both.map({True: "selected in S1_Run3_Ideal and S2_Run3_ATLAS", False: "S2_Run3_ATLAS only"}); S = S.drop(columns="both"); S.to_csv(f"{R}/tables/X05_endcap_flag_full.csv", index=False)
print(S.to_string(index=False))
