#!/usr/bin/env python3
"""07 X11 (2026-11-17): robustness of the background and the signal to the pixel-merge distance and the multiplicity threshold.
Variants:
  merge adjacency a (pixel-index units; production a = 1 = touching pixels). Pixel indices are integers, so a distance of 0.5 pixel (-50%) merges
  only hits in the same pixel (= a 0) and 1.5 pixels (+50%) merges exactly what a = 1 merges; the variants run are therefore a = 0 (-50%/-100%)
  and a = 2 (+100%), with a = 1 = production (+50% is identical to it).
  multiplicity threshold T (total hits on the winning plane's 8 stations): all 8 stations hit and >= T - 8 stations with 2 hits
  (T = 15 = the paper's "all but one layer with 2 hits" = production; T = 14 one hit looser; T = 16 all 8 stations with 2 hits).
  The threshold is applied after the fact to the stored winner (C01 winner_layers; G01 station counts n1, n2): the winner plane does not depend
  on the multiplicity cut (select_reconstructed_plane), checked by T13 (a), (c).
Background: C01 runs, N at 332 fb^-1 with the S01 normalisation (per region L sigma/photon * N_photons / photons in region * p_conv), MC error sqrt(sum w^2).
  Production (a = 1): runs/C01_atlas_mu{mu} (Z0), C01_atlas_A580_mu{mu}, C01_stage2_A580_mu{mu}, C01_stage2_sens_a1_mu50 (Ideal Z0, server);
  merge variants: runs/C01_<geom>_sens_<sct>_a<a>_mu50, a = 0, 1, 2 (server, SERVER_BACKGROUND_RUNS.md (e), laptop pool copied): each variant is
  compared with the server a = 1 run (column ratio_to_reference), so machine and pool differences cancel. Missing runs are skipped.
Signal: signal/runs/sens_merge/<geom>/G01_<tag>_mid.jsonl (S01_sens_chain.sh): k/n = final / fiducial per Lambda and summed over the mid band.
Writes tables/X11_background_sensitivity.csv, tables/X11_signal_sensitivity.csv."""
import os, glob, json, numpy as np, pandas as pd
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); T = f"{R}/tables"
BASE = os.environ.get("COPLANARITY_BASE", os.path.abspath(f"{R}/.."))
X = dict(l.split()[:2] for l in open(f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_xsec_13p6TeV.txt") if len(l.split()) >= 2)
SIG = float(X["sigma_generated_pb"]) / float(X.get("n_generated", 10000)); NPH = float(X["n_events_after_MET"]); L_PB = 332.0e3
THR = (14, 15, 16)


def counts(s):
    c = Counter(json.loads(s)) if isinstance(s, str) and s.startswith("[") else Counter()
    return sum(1 for k in range(1, 9) if c.get(k, 0) >= 1), sum(1 for k in range(1, 9) if c.get(k, 0) >= 2)


def bkg(run, sct):
    fs = sorted(glob.glob(f"{R}/backgrounds/runs/{run}/chunk_*.csv"))
    if not fs: return None
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True); d = d[(d.sct == sct) & (d.status == "ok")].copy()
    for c in ("plane", "ds_pass"): d[c] = d[c].astype(str).str.lower().eq("true")
    n12 = d.winner_layers.map(counts); d["n1"] = [a for a, b in n12]; d["n2"] = [b for a, b in n12]
    d["w"] = L_PB * SIG * NPH * d.p_conv / d.groupby("region").event.transform("nunique")
    out = []
    for t in THR:
        f = d.plane & d.ds_pass & (d.n1 == 8) & (d.n2 >= t - 8)
        out.append(dict(run=run, photons=d.event.nunique(), threshold=t, n_pass=int(f.sum()), N_bkg_332fb=float((d.w * f).sum()), err=float(np.sqrt((d.w**2 * f).sum())),
                        n_plane_ds=int((d.plane & d.ds_pass).sum())))
    return out


rows = []
SETS = [("S2_Run3_ATLAS", "Z0", "C01_atlas_mu{mu}", "C01_atlas_sens_Z0_a{a}_mu50"), ("S2_Run3_ATLAS", "A580", "C01_atlas_A580_mu{mu}", "C01_atlas_sens_A580_a{a}_mu50"),
        ("S1_Run3_Ideal", "Z0", "C01_stage2_sens_Z0_a1_mu{mu}", "C01_stage2_sens_Z0_a{a}_mu50"), ("S1_Run3_Ideal", "A580", "C01_stage2_A580_mu{mu}", "C01_stage2_sens_A580_a{a}_mu50")]
for setup, sct, prod, var in SETS:
    for mu in (0, 20, 50):
        for r in bkg(prod.format(mu=mu), sct) or []: rows.append(dict(setup=setup, sct=sct, mu=mu, merge_adj=1, source="production", **r))
    for a in (0, 1, 2):
        if prod.startswith("C01_stage2_sens_Z0") and a == 1: continue                 # Ideal Z0 production is itself the server a = 1 run
        for r in bkg(var.format(a=a), sct) or []: rows.append(dict(setup=setup, sct=sct, mu=50, merge_adj=a, source="server_sens", **r))
B = pd.DataFrame(rows)
if len(B):
    B["source"] = B.source.fillna("production")
    B.loc[B.run.str.startswith("C01_stage2_sens_Z0_a1"), "source"] = "server_sens"
    # reference = threshold 15, a = 1 of the SAME source (server variants are compared with the server a = 1 run: same machine and pool)
    ref = B[(B.merge_adj == 1) & (B.threshold == 15)].set_index(["setup", "sct", "mu", "source"]).N_bkg_332fb
    B["ratio_to_reference"] = [r.N_bkg_332fb / ref.get((r.setup, r.sct, r.mu, r.source), np.nan) if ref.get((r.setup, r.sct, r.mu, r.source), 0) > 0 else np.nan
                               for r in B.itertuples()]
B.to_csv(f"{T}/X11_background_sensitivity.csv", index=False)

S = []
for g, setup in (("atlas", "S2_Run3_ATLAS"), ("stage2", "S1_Run3_Ideal")):
    for f in sorted(glob.glob(f"{R}/signal/runs/sens_merge/{g}/G01_*_mid.jsonl")):
        tag = os.path.basename(f)[4:-10]; rr = [r for l in open(f) if l.strip() for r in json.loads(l)]
        for sct in ("Z0", "Z1160", "A580"):
            for a in (0, 1, 2):
                for t in THR:
                    for lam in sorted({r["lambda_keV"] for r in rr}) + ["all"]:
                        sel = [r for r in rr if lam == "all" or r["lambda_keV"] == lam]; fid = [r for r in sel if r["fid"]]
                        k = sum(1 for r in fid if r.get(f"{sct}_a{a}_plane") and (r.get(f"{sct}_a{a}_ds", 1) or 1) < 0.01
                                and r.get(f"{sct}_a{a}_n1") == 8 and r.get(f"{sct}_a{a}_n2", 0) >= t - 8)
                        S.append(dict(setup=setup, sample=tag, sct=sct, merge_adj=a, threshold=t, lambda_keV=lam, n_events=len({r["event"] for r in rr}),
                                      n_fid=len(fid), k=k, eps_reco=k / len(fid) if fid else np.nan))
S = pd.DataFrame(S)
if len(S):
    ref = S[(S.merge_adj == 1) & (S.threshold == 15)].set_index(["setup", "sample", "sct", "lambda_keV"]).k
    S["ratio_to_reference"] = [r.k / ref[(r.setup, r.sample, r.sct, r.lambda_keV)] if ref[(r.setup, r.sample, r.sct, r.lambda_keV)] > 0 else np.nan for r in S.itertuples()]
S.to_csv(f"{T}/X11_signal_sensitivity.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
if len(B): print(B.drop(columns=["run"]).round(4).to_string(index=False))
if len(S): print(S[S.lambda_keV == "all"].round(4).to_string(index=False))
print("X11_EXIT=0")
