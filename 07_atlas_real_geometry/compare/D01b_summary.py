#!/usr/bin/env python3
"""07 D01b (2026-11-17): summary of compare/D01_runs/*.jsonl. Per SCT setting, for the ATLAS-only selected events (server: ATLAS final, ideal not)
and for the control events (selected in both): winner-plane class barrel-only / end-cap-only / mixed (stations 1-8 elements), how many of the 8
stations are end-cap elements, whether the laptop rerun reproduces the server flags, and for the control events whether any quirk has end-cap hits.
Writes tables/D01_endcap_gain.csv; prints the table."""
import os, glob, json, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); SET = ("Z0", "Z1160", "A580")
rows = []
for f in sorted(glob.glob(f"{HERE}/D01_runs/D01_*.jsonl")):
    tag, lam = os.path.basename(f)[4:-6].rsplit("_", 1)
    for l in open(f):
        d = json.loads(l); r = d["rows"][0]; pl = d["planes"]; qh = d["quirk_hits"]
        ec_hits = [sum(1 for n in h if not n.startswith("L")) for h in qh]
        for k, s in enumerate(SET):
            sa, si = d["server_atlas"].get(f"{s}_final"), d["server_ideal"].get(f"{s}_final")
            grp = "atlas_only" if (sa and not si) else ("both" if (sa and si) else "other")
            if grp == "other": continue
            st = pl[k]["stations"] if r.get("fid") and k < len(pl) and pl[k]["stations"] else None
            nE = sum(1 for x in st for n in x if not n.startswith("L")) if st else None
            nstE = sum(1 for x in st if any(not n.startswith("L") for n in x)) if st else None
            nstB = sum(1 for x in st if any(n.startswith("L") for n in x)) if st else None
            cls = None if st is None else ("barrel-only" if nstE == 0 else ("end-cap-only" if nstB == 0 else "mixed"))
            rows.append(dict(tag=tag, lambda_keV=float(lam), sct=s, group=grp, event=d["event"], laptop_final=bool(r.get(f"{s}_final")), plane_class=cls,
                             n_endcap_stations=nstE, n_barrel_stations=nstB, endcap_hits_q1=ec_hits[0] if ec_hits else None, endcap_hits_q2=ec_hits[1] if len(ec_hits) > 1 else None,
                             barrel_hits_q1=sum(1 for n in qh[0] if n.startswith("L")) if qh else None, barrel_hits_q2=sum(1 for n in qh[1] if n.startswith("L")) if len(qh) > 1 else None))
D = pd.DataFrame(rows); D.to_csv(f"{R}/tables/D01_endcap_gain_events.csv", index=False)
x = D[D.laptop_final]
S = x.groupby(["tag", "lambda_keV", "sct", "group", "plane_class"]).size().unstack(fill_value=0).reset_index()
N = D.groupby(["tag", "lambda_keV", "sct", "group"]).agg(n_server=("event", "size"), n_laptop_reproduced=("laptop_final", "sum")).reset_index()
S = N.merge(S, on=["tag", "lambda_keV", "sct", "group"], how="left").fillna(0)
c = D[D.group == "both"]; S2 = c.assign(any_endcap_hit=(c.endcap_hits_q1 > 0) | (c.endcap_hits_q2 > 0)).groupby(["tag", "lambda_keV", "sct"]).agg(n=("event", "size"), with_endcap_hits=("any_endcap_hit", "sum")).reset_index()
S.to_csv(f"{R}/tables/D01_endcap_gain.csv", index=False); S2.to_csv(f"{R}/tables/D01_control_endcap_hits.csv", index=False)
pd.set_option("display.width", 250); print(S.to_string(index=False)); print(S2.to_string(index=False))
