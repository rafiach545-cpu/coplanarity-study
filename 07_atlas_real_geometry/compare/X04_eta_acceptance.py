#!/usr/bin/env python3
"""07 X04 (2026-11-17): eta acceptance of the ideal (Stage 2 barrel) and ATLAS geometry. Per mass point at Lambda = 4 keV (server runs), the
|pseudorapidity| of the quirk PAIR (P1 + P2, initial momenta of signal/inputs_large; the individual quirk direction is a poor label because the string binds the pair) for: all propagated events, fid events, and Z0/A580-selected events,
in ideal and ATLAS; reported as |eta_pair|: quantiles 50/90/99/100%, and the fraction with |eta_pair| > 1.2.
Note: the fiducial rules use the hits, not the initial direction; the initial eta is only a label. Barrel rule (ideal) geometric limit: SCT barrel
half-length 74.9 cm at r = 51.4 cm -> |eta| < asinh(74.9 / 51.4) = 1.18 at z0 = 0 (T01: all 8 layers for |eta| <= 1.15). ATLAS: |eta| < 2.5 (D1).
Writes tables/X04_eta_acceptance.csv."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); LAM = 4.0
C = pd.read_csv(f"{R}/signal/inputs_large/counts.csv"); rows = []
eta = lambda px, py, pz: np.arcsinh(pz / np.hypot(px, py))
for r in C.itertuples():
    tag = f"{r.channel}_{r.mass_gev}gev"; f = {d: f"{R}/signal/runs/{d}/G01_{tag}_mid.jsonl" for d in ("large_ideal", "large_atlas")}
    if not all(os.path.exists(x) for x in f.values()): continue
    ev = pd.read_csv(f"{R}/signal/inputs_large/{tag}_events.csv").set_index("event_id")
    me = np.abs(eta(ev.px1 + ev.px2, ev.py1 + ev.py2, ev.pz1 + ev.pz2))   # |eta| of the pair momentum P1 + P2 (the hits follow the pair: bound by the string)
    for d, fn in f.items():
        rr = {}
        for l in open(fn):
            for x in json.loads(l):
                if abs(x["lambda_keV"] - LAM) < 1e-9: rr[x["event"]] = x
        for grp, sel in (("propagated", lambda x: True), ("fid", lambda x: x.get("fid")), ("Z0_final", lambda x: x.get("Z0_final")), ("A580_final", lambda x: x.get("A580_final"))):
            ids = [e for e, x in rr.items() if sel(x)]; v = me.loc[ids].values
            rows.append(dict(channel=r.channel, mass_gev=r.mass_gev, geometry={"large_ideal": "S1_Run3_Ideal", "large_atlas": "S2_Run3_ATLAS"}[d], group=grp, n=len(v),
                             **({f"q{q}": float(np.quantile(v, q / 100)) for q in (50, 90, 99, 100)} if len(v) else {}), frac_maxeta_gt_1p2=float((v > 1.2).mean()) if len(v) else np.nan))
D = pd.DataFrame(rows); D.to_csv(f"{R}/tables/X04_eta_acceptance.csv", index=False); pd.set_option("display.width", 250)
print(D[D.group != "propagated"].pivot_table(index=["channel", "mass_gev"], columns=["group", "geometry"], values="q90").round(2).to_string())
print(D[D.group == "Z0_final"].pivot_table(index=["channel", "mass_gev"], columns="geometry", values=["q99", "q100", "frac_maxeta_gt_1p2"]).round(2).to_string())
