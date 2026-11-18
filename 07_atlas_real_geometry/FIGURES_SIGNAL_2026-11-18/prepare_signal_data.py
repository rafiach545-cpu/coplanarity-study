#!/usr/bin/env python3
"""07 signal figures (2026-11-18), step 1 of 2: plot-ready CSVs for the paper-style signal figures, Stage 2 · Run 3 · ATLAS vs Stage 1 · Run 3 · Ideal,
both with the same 10k-generated events (server runs signal/runs/large_atlas, large_ideal; inputs signal/inputs_large/counts.csv).
Benchmarks as in the paper's Table I: colored 1800 GeV at Lambda = 2 keV and EW 800 GeV at Lambda = 4 keV.
  data/cutflow.csv: per (geometry, benchmark, SCT setting): matched, triggered, propagated (colored: both quirk-hadrons charged), fiducial, plane
                    (Delta_w < 1 cm), + multiplicity, + Delta_s < 0.01 cm (= final); efficiencies eps_trig = triggered / matched, f_ch, eps_fid = fiducial /
                    propagated, eps_reco = final / fiducial, each step / previous step; Wilson 68% intervals.
  data/ds_dw.csv:   Delta_s and Delta_w of every fiducial benchmark event with a plane (per SCT setting), and n_fid for the normalisation.
  data/sensitivity.csv: copy of tables/X11_signal_sensitivity.csv (merge adjacency 0/1/2, multiplicity threshold 14/15/16), if present.
  data/sources.json: sha256 of every input."""
import os, json, hashlib, shutil, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); D = f"{HERE}/data"; os.makedirs(D, exist_ok=True)
GEO = {"S2_Run3_ATLAS": "large_atlas", "S1_Run3_Ideal": "large_ideal"}; BENCH = [("colored", 1800, 2), ("EW", 800, 4)]; SCTS = ("A580", "Z1160", "Z0")
src = {}


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def wilson(k, n, z=1.0):
    if n == 0: return np.nan, np.nan
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h


cnt = f"{R}/signal/inputs_large/counts.csv"; CN = pd.read_csv(cnt).set_index(["channel", "mass_gev"]); src[os.path.relpath(cnt, R)] = sha(cnt)
CF, DS = [], []
for setup, folder in GEO.items():
    for ch, m, lam in BENCH:
        f = f"{R}/signal/runs/{folder}/G01_{ch}_{m}gev_mid.jsonl"; src[os.path.relpath(f, R)] = sha(f)
        rr = [r for l in open(f) if l.strip() for r in json.loads(l) if r["lambda_keV"] == lam]
        c = CN.loc[(ch, m)]; n_m, n_t = int(c.n_matched), int(c.n_trigger); n_p = len(rr); assert n_p == int(c.n_trigger_both_charged)
        fid = [r for r in rr if r["fid"]]
        for s in SCTS:
            pl = [r for r in fid if r.get(f"{s}_plane")]; mu = [r for r in pl if r.get(f"{s}_mult")]; fi = [r for r in mu if r.get(f"{s}_final")]
            assert len(fi) == sum(1 for r in fid if r.get(f"{s}_final"))
            steps = [("matched", n_m, n_m), ("triggered", n_t, n_m), ("propagated", n_p, n_t), ("fiducial", len(fid), n_p), ("plane", len(pl), len(fid)),
                     ("multiplicity", len(mu), len(pl)), ("delta_s", len(fi), len(mu))]
            for k, (st, n, prev) in enumerate(steps):
                lo, hi = wilson(n, prev); CF.append(dict(setup=setup, channel=ch, mass_gev=m, lambda_keV=lam, sct=s, step_index=k, step=st, n=n, n_prev=prev,
                                                         frac_of_prev=n / prev if prev else np.nan, frac_lo=lo, frac_hi=hi))
            lo, hi = wilson(len(fi), len(fid))
            CF.append(dict(setup=setup, channel=ch, mass_gev=m, lambda_keV=lam, sct=s, step_index=9, step="eps_reco", n=len(fi), n_prev=len(fid),
                           frac_of_prev=len(fi) / len(fid) if fid else np.nan, frac_lo=lo, frac_hi=hi))
            for r in pl: DS.append(dict(setup=setup, channel=ch, mass_gev=m, lambda_keV=lam, sct=s, ds_cm=r[f"{s}_ds"], dw_cm=r[f"{s}_dw"], final=bool(r[f"{s}_final"]),
                                        endcap=bool(r.get(f"{s}_endcap")), n_fid=len(fid)))
pd.DataFrame(CF).to_csv(f"{D}/cutflow.csv", index=False); pd.DataFrame(DS).to_csv(f"{D}/ds_dw.csv", index=False)
x = f"{R}/tables/X11_signal_sensitivity.csv"
if os.path.exists(x): shutil.copy(x, f"{D}/sensitivity.csv"); src[os.path.relpath(x, R)] = sha(x)
json.dump(src, open(f"{D}/sources.json", "w"), indent=1)
C = pd.DataFrame(CF); print(C[C.step.isin(["fiducial", "plane", "multiplicity", "delta_s", "eps_reco"])].pivot_table(index=["channel", "sct", "step_index", "step"], columns="setup", values="frac_of_prev").round(3).to_string())
print("PREP_EXIT=0")
