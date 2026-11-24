#!/usr/bin/env python3
"""regen_dop853 sanity checks, old (fixed-step RK4) vs new (DOP853), per point. PASS / FLAG only; nothing is changed.
Rules (user, 2026-11-23):
  n_fid: PASS if old <= new <= ceil(1.05 * old)  (DOP853 has no step ceiling, so RK4 integration failures can only become fiducial events);
  k:     FLAG if |k_new - k_old| > 3 sqrt(k_old + 1);
  background: the converted-photon counts used by the reach must equal the old ones exactly (X08_background_used.csv vs KF6 fig6_reach.csv).
Points: C = 13.6 TeV, 07 stage2 / atlas, SR setting A580 (Z0 and Z1160 also listed); A = 13 TeV 8-layer (old = 05 F6 grid logs), SR Z1160 and Z0;
D = 13.6 TeV full events (old = 09 data/B08_EW_<m>gev_L0.1-10.csv), inputs qrk and iso20; B = 13 TeV full events: no old run exists, listed as INFO.
Usage: checks.py <regen_dop853 dir>. Writes <dir>/out/CHECKS.csv."""
import os, sys, json, glob, math, numpy as np, pandas as pd
RD = os.path.abspath(sys.argv[1]); B = f"{RD}/base"; OUT = f"{RD}/out"; rows = []
TR = lambda v: str(v) == "True" or v is True


def verdict(nf_o, nf_n, k_o, k_n):
    v1 = "PASS" if nf_o <= nf_n <= math.ceil(1.05 * nf_o) else "FLAG"
    v2 = "FLAG" if abs(k_n - k_o) > 3 * math.sqrt(k_o + 1) else "PASS"
    return v1, v2


def jl(f):
    return [r for l in open(f) if l.strip() for r in json.loads(l)] if os.path.exists(f) else []


def add(step, point, nprop_o, nprop_n, nf_o, nf_n, ks):
    for sct, (k_o, k_n) in ks.items():
        if nprop_o != nprop_n:
            rows.append(dict(step=step, point=point, sct=sct, n_events_old=nprop_o, n_events_new=nprop_n, nfid_old=nf_o, nfid_new=nf_n, k_old=k_o, k_new=k_n,
                             nfid_check="missing" if nprop_n < nprop_o else "FLAG", k_check="missing" if nprop_n < nprop_o else "FLAG")); continue
        v1, v2 = verdict(nf_o, nf_n, k_o, k_n)
        rows.append(dict(step=step, point=point, sct=sct, n_events_old=nprop_o, n_events_new=nprop_n, nfid_old=nf_o, nfid_new=nf_n, k_old=k_o, k_new=k_n, nfid_check=v1, k_check=v2))


# ---- C
R7 = f"{B}/07_atlas_real_geometry"
for geom, old in (("stage2", "large_ideal"), ("atlas", "large_atlas")):
    for f in sorted(glob.glob(f"{R7}/signal/runs/{old}/G01_*.jsonl")):
        name = os.path.basename(f); O = jl(f); N = jl(f"{OUT}/C_13p6TeV_{geom}/{name}")
        for lam in sorted({r["lambda_keV"] for r in O}):
            o = [r for r in O if r["lambda_keV"] == lam]; n = [r for r in N if r["lambda_keV"] == lam]
            add("C", f"{geom} {name[4:-6]} L={lam:g}", len(o), len(n), sum(TR(r["fid"]) for r in o), sum(TR(r["fid"]) for r in n),
                {s: (sum(TR(r.get(f"{s}_final")) for r in o), sum(TR(r.get(f"{s}_final")) for r in n)) for s in ("A580", "Z1160", "Z0")})
# ---- A
L5 = f"{B}/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/logs"; NA = {}
for f in glob.glob(f"{OUT}/A_13TeV_8layer/*_FS10.jsonl"):
    for r in jl(f): NA.setdefault(os.path.basename(f).split("_L")[0], []).append(r)
for f in sorted(glob.glob(f"{L5}/F6_*gev*_events.jsonl")):
    b = os.path.basename(f)[3:-13]; tag = b.replace("_low", "").replace("_high_a", "")
    if "pilot" in b or tag.count("_") != 1: continue
    O = jl(f); N = NA.get(tag, [])
    for lam in sorted({r["lambda_keV"] for r in O}):
        o = [r for r in O if r["lambda_keV"] == lam]; n = [r for r in N if r["lambda_keV"] == lam]
        add("A", f"{tag} L={lam:g}", len(o), len(n), sum(TR(r["fid"]) for r in o), sum(TR(r["fid"]) for r in n),
            {s: (sum(TR(r.get(f"{s}_final")) for r in o), sum(TR(r.get(f"{s}_final")) for r in n)) for s in ("Z1160", "Z0")})
# ---- D
D9 = f"{B}/09_stage1_run2_ideal_zvv_background/data"
for f in sorted(glob.glob(f"{D9}/B08_EW_*gev_L0.1-10.csv")):
    m = os.path.basename(f).split("_")[2]; o = pd.read_csv(f); nf = f"{D9}/B08_13p6TeV_dop853_EW_{m}.csv"
    n = pd.read_csv(nf) if os.path.exists(nf) else pd.DataFrame(columns=o.columns)
    for lam in sorted(o.lambda_keV.unique()):
        a = o[o.lambda_keV == lam]; c = n[n.lambda_keV == lam] if len(n) else n
        fid = lambda x: int((x.fiducial.astype(str) == "True").sum()) if len(x) else 0
        add("D", f"EW {m} L={lam:g}", len(a), len(c), fid(a), fid(c),
            {s: (int((a[f"{s}_sr_pass"].astype(str) == "True").sum()), int((c[f"{s}_sr_pass"].astype(str) == "True").sum()) if len(c) else 0) for s in ("qrk", "iso20")})
# ---- B (no old run)
for f in sorted(glob.glob(f"{D9}/B08_13TeV_dop853_EW_*.csv")):
    n = pd.read_csv(f)
    for lam, c in n.groupby("lambda_keV"):
        rows.append(dict(step="B", point=f"{os.path.basename(f)[19:-4]} L={lam:g}", sct="qrk", n_events_new=len(c), nfid_new=int((c.fiducial.astype(str) == "True").sum()),
                         k_new=int((c.qrk_sr_pass.astype(str) == "True").sum()), nfid_check="INFO (no old run)", k_check="INFO (no old run)"))
# ---- background
BU = pd.read_csv(f"{R7}/tables/X08_background_used.csv"); F6 = pd.read_csv(f"{R7}/REPORT_KNAPEN_FIGURES_2026-11-18/data/fig6_reach.csv")
for (setup, sct, mu), g in F6.groupby(["setup", "sct", "mu"]):
    b = BU[(BU.setup == setup) & (BU.sct == sct) & (BU.mu == mu)]
    same = len(b) == 1 and float(b.N_bkg.iloc[0]) == float(g.N_bkg.iloc[0]) and int(b.n_final.iloc[0]) == int(g.n_bkg_mc.iloc[0])
    rows.append(dict(step="bkg", point=f"{setup} {sct} mu={mu}", sct=sct, k_old=int(g.n_bkg_mc.iloc[0]), k_new=int(b.n_final.iloc[0]) if len(b) else -1,
                     nfid_check="", k_check="PASS" if same else "FLAG", note=f"N_bkg old {g.N_bkg.iloc[0]:.4f} used {float(b.N_bkg.iloc[0]) if len(b) else float('nan'):.4f}"))
T = pd.DataFrame(rows); T.to_csv(f"{OUT}/CHECKS.csv", index=False)
print(T.groupby(["step", "k_check"]).size().to_string()); print("CHECKS_EXIT=0")
