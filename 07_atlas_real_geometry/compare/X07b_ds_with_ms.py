#!/usr/bin/env python3
"""07 X07b (2026-11-17): effect of multiple scattering (X07 estimate) on the Delta_s selection. Delta_s is the RMS out-of-plane distance of the hits
(smallest eigenvalue of the hit tensor, coplanarity_fit.py), so the per-event MS term is the RMS of the projected displacement over the 8 measurements of
both quirks, ms = sqrt((rms_q1^2 + rms_q2^2) / 2). For every selected event (Lambda = 4 keV, server runs) the simulated Delta_s of each SCT setting is combined in
quadrature, ds' = sqrt(ds^2 + ms^2), and the fraction still passing Delta_s < 0.01 cm is reported, per group and momentum choice
(initial p; conservative p_min of X07). This treats the MS term as its RMS value (no event-by-event fluctuation; the plane fit absorbs part of a common tilt,
so it is an estimate, not a simulation). Writes tables/X07b_ds_with_ms.csv."""
import os, json, numpy as np, pandas as pd
R = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/.."); E = pd.read_csv(f"{R}/tables/X07_multiple_scattering_events.csv")
ms = E.groupby(["channel", "mass_gev", "event", "group"]).agg(ms_um=("sigma_rms_um", lambda v: float(np.sqrt(np.mean(np.square(v))))),
                                                               ms_um_pmin=("sigma_rms_um_pmin", lambda v: float(np.sqrt(np.mean(np.square(v)))))).reset_index()
rows = []
for (ch, m), x in ms.groupby(["channel", "mass_gev"]):
    A = {}
    for l in open(f"{R}/signal/runs/large_atlas/G01_{ch}_{m}gev_mid.jsonl"):
        for r in json.loads(l):
            if abs(r["lambda_keV"] - 4.0) < 1e-9: A[r["event"]] = r
    for r in x.itertuples():
        a = A[r.event]
        for s in ("Z0", "A580", "Z1160"):
            if not a.get(f"{s}_final"): continue
            ds = a[f"{s}_ds"] * 1e4
            rows.append(dict(channel=ch, mass_gev=m, event=r.event, group=r.group, sct=s, ds_um=ds, ms_um=r.ms_um, ms_um_pmin=r.ms_um_pmin,
                             pass_p=np.hypot(ds, r.ms_um) < 100.0, pass_pmin=np.hypot(ds, r.ms_um_pmin) < 100.0))
D = pd.DataFrame(rows)
S = D.groupby(["sct", "channel", "group"]).agg(n_selected=("event", "size"), median_ds_um=("ds_um", "median"), median_ms_um=("ms_um", "median"),
                                               median_ms_um_pmin=("ms_um_pmin", "median"), still_pass_initial_p=("pass_p", "mean"), still_pass_pmin=("pass_pmin", "mean")).reset_index()
S.to_csv(f"{R}/tables/X07b_ds_with_ms.csv", index=False); pd.set_option("display.width", 250); pd.set_option("display.float_format", lambda v: f"{v:.3g}")
print(S.to_string(index=False))
