#!/usr/bin/env python3
"""
Delta_w stage audit (existing fiducial events, geometry A where the exact project hits are known).

Stages (all with the paper Eq. 10-11 statistic sqrt(lambda_2), plane through the vertex, cm):
  S0 truth crossings, all 16 hits (unsmeared, unmerged)
  S1 detector hits after pixel quantisation + SCT smearing (R0 and R2), before merging
  S2 after pixel merging
  S3 selected Sec. III C candidate (only plane-associated hits)       [R2/A0 and R0/A0]
plus the per-event Eq. (1)/(4) amplitude prediction A = (gamma-1) mQ/Lambda^2 (CM frame, per quirk).

Compared with the paper's Fig. 5 Delta_w (vector-extracted) and the Fig. 4 finding
  paper_quoted_Delta_w = 0.50 x sqrt(lambda_2)   (tables/paper_fig4_event_digitised_bandcal.json).
"""
import importlib.util, json, math, os, sys
import numpy as np, pandas as pd
from scipy.stats import kstwobign
B = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
FOR = f"{B}/05_coplanarity_analysis/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02"
spec = importlib.util.spec_from_file_location("fp", f"{FOR}/scripts/02_forensic_pipeline.py")
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
HBARC = 1.973269804e-14
PAR = {"EW": (800.0, 4e-6), "COL": (1800.0, 2e-6)}


def sqrt_l2(P, vtx=None):
    P = np.asarray(P, float)
    if vtx is not None:
        P = P - vtx
    w = np.linalg.eigvalsh(P.T @ P / (len(P) - 1)); return math.sqrt(max(w[1], 0.0))


def gamma_minus_1(r, m):
    E = r.E1 + r.E2; px = r.px1 + r.px2; py = r.py1 + r.py2; pz = r.pz1 + r.pz2
    M = math.sqrt(max(E * E - px * px - py * py - pz * pz, 0)); return M / (2 * m) - 1


rows = []
var = pd.read_csv(f"{FOR}/tables/variant_event_results.csv")
for s in ("EW1000", "EW2000", "COL1000", "COL2000"):
    bench = "EW" if s.startswith("EW") else "COL"; mq, lam = PAR[bench]
    ev = fp.load_sample(s).sort_values("key")
    cr_all = pd.read_csv(f"{FOR}/tables/truth_crossings_{s}.csv"); ex_all = pd.read_csv(f"{FOR}/tables/exact_crossings_fiducial_{s}.csv")
    if s in ("EW2000", "COL2000"):
        tag = "EW_800GeV_L4keV" if s == "EW2000" else "colored_1800GeV_L2keV"
        mom = pd.read_csv(f"{B}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{tag}/trigger_passing_events.csv")
    else:
        f = "ew_quirk_pair_momenta_800gev_4kev.csv" if s == "EW1000" else "quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv"
        mom = pd.read_csv(f"{B}/01_signal_generation/{f}"); mom = mom[mom.pT_pair > 200].reset_index(drop=True)
    seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
    for e in ev.itertuples():
        cr = cr_all[cr_all.key == e.key].sort_values(["quirk", "layer"])
        if e.technical or len(cr) == 0 or ("technical_error" in cr.columns and cr.technical_error.notna().any()):
            continue
        rng = seq if seq is not None else np.random.default_rng(int(e.seed))
        ex = ex_all[ex_all.key == e.key].sort_values(["quirk", "layer"])
        z0, g = fp.stream_draws(rng, cr, ex if e.stored_fid else None)
        if not e.stored_fid:
            continue
        vtx = np.array([0.0, 0.0, z0])
        truth = np.c_[ex.x, ex.y, ex.z_lab]
        r = dict(sample=s, bench=bench, key=int(e.key), event_id=int(e.event_id),
                 gm1=gamma_minus_1(mom.iloc[int(e.key)], mq),
                 S0_truth=sqrt_l2(truth, vtx))
        r["amp_pred_cm"] = r["gm1"] * mq / lam ** 2 * HBARC
        for model in ("R0", "R2"):
            _, raw, merged = fp.build_hits(ex, z0, g, model, e.key)
            r[f"S1_hits_{model}"] = sqrt_l2([(h["x"], h["y"], h["z"]) for h in raw], vtx)
            r[f"S2_merged_{model}"] = sqrt_l2([(h["x"], h["y"], h["z"]) for h in merged], vtx)
            v = var[(var["sample"] == s) & (var.key == e.key) & (var.model == model) & (var.alg == "A0")]
            r[f"S3_selected_{model}"] = float(v.dw.iloc[0]) if len(v) and v.plane.iloc[0] else np.nan
        rows.append(r)
d = pd.DataFrame(rows); d.to_csv(f"{T}/delta_w_stages_per_event.csv", index=False)

fig5 = json.load(open(f"{FOR}/tables/paper_fig5_extracted.json"))["delta_w_cm"]["histograms"]
summ = []
for bench, lab in (("EW", "EW Quirk"), ("COL", "Colored Quirk")):
    h = fig5[lab]; edges = [t["lo"] for t in h] + [h[-1]["hi"]]; ph = np.array([t["height"] for t in h])
    pc = np.cumsum(ph) / ph.sum(); pmed = float(np.interp(0.5, pc, [t["hi"] for t in h]))
    x = d[d.bench == bench]
    for col in ("S0_truth", "S1_hits_R0", "S1_hits_R2", "S2_merged_R0", "S2_merged_R2", "S3_selected_R0", "S3_selected_R2"):
        for defn, f in (("Eq11_sqrt_lambda2", 1.0), ("paper_quoted_=0.5*sqrt_lambda2", 0.5)):
            vals = (x[col].dropna() * f).to_numpy()
            oh = np.histogram(vals, bins=edges)[0].astype(float); n = int(oh.sum())
            D = float(np.max(np.abs(pc - np.cumsum(oh) / max(oh.sum(), 1)))) if n else np.nan
            summ.append(dict(bench=bench, stage=col, definition=defn, n=len(vals), median=float(np.median(vals)),
                             paper_fig5_median=pmed, ratio_to_paper=float(np.median(vals)) / pmed,
                             ks_D=D, ks_p=float(kstwobign.sf(D * math.sqrt(n))) if n else np.nan))
    summ.append(dict(bench=bench, stage="amp_pred_cm (Eq.1/4, per quirk)", definition="-", n=len(x),
                     median=float(x.amp_pred_cm.median()), paper_fig5_median=pmed, ratio_to_paper=np.nan))
    summ.append(dict(bench=bench, stage="S0_truth / amp_pred (median ratio)", definition="-", n=len(x),
                     median=float((x.S0_truth / x.amp_pred_cm).median()), paper_fig5_median=np.nan, ratio_to_paper=np.nan))
S = pd.DataFrame(summ); S.to_csv(f"{T}/delta_w_stages_summary.csv", index=False)
pd.set_option("display.width", 220); print(S.round(4).to_string(index=False))
EOF_MARK = None
