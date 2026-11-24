#!/usr/bin/env python3
"""09 / G07 summary (2026-11-22): per (sample, Lambda, sigma_z) and step factor F = 1, 4, 16:
  n_fid, k (SR pass), eps_reco = k / n_fid with the Wilson 68% interval, median ds and dw (events with a selected plane),
  SR flips between F = 1 and F = 16 (same event, pass <-> fail), and the first-crossing position change F = 1 -> 16 split into the
  component normal to the event plane (out of plane) and in it. Plane: through the primary vertex, fitted (SVD, no centring) to the 16
  F = 16 first crossings relative to the vertex. Fiducial changes are counted separately.
Output: out_G01/G07_impact_table.csv and a printed table."""
import os, json, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = f"{HERE}/out_G01/G07"
TAGS = [("colored_1800gev", "2-4-7-10"), ("EW_800gev", "2-4-7-10"), ("EW_600gev", "4-5")]


def wilson(k, n, z=1.0):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def load(tag, lams, F):
    f = f"{D}/{tag}_L{lams}_F{F}.jsonl"
    return {(r["event"], r["lambda_keV"]): r for l in open(f) if l.strip() for r in json.loads(l)} if os.path.exists(f) else {}


rows = []
for tag, lams in TAGS:
    R = {F: load(tag, lams, F) for F in (1, 4, 16)}
    if not R[1] or not R[16]: continue
    for lam in sorted({k[1] for k in R[1]}):
        keys = sorted(k for k in R[1] if k[1] == lam and k in R[16] and k in R[4])
        # position change F1 -> F16, events fiducial in both
        din, dout = [], []
        for k in keys:
            a, b = R[1][k], R[16][k]
            if not (a["fid"] and b["fid"]): continue
            A = {(c[0], c[1]): np.array(c[2:5]) for c in a["first"]}
            Bv = {(c[0], c[1]): np.array(c[2:5]) for c in b["first"]}
            v = np.array([0.0, 0.0, b["z0"]]); P = np.array([Bv[q] - v for q in sorted(Bv)])
            n = np.linalg.svd(P, full_matrices=False)[2][-1]
            for q in Bv:
                if q in A:
                    d = A[q] - Bv[q]; o = abs(d @ n); dout.append(o); din.append(np.sqrt(max(d @ d - o * o, 0)))
        for sct in ("Z1160", "Z580"):
            row = dict(sample=tag, lambda_keV=lam, sct=sct, n_events=len(keys))
            for F in (1, 4, 16):
                rr = [R[F][k] for k in keys]; nf = sum(bool(r["fid"]) for r in rr); kk = sum(bool(r.get(f"{sct}_final")) for r in rr)
                lo, hi = wilson(kk, nf); pl = [r for r in rr if r.get(f"{sct}_plane") in (True, "True")]
                row.update({f"nfid_F{F}": nf, f"k_F{F}": kk, f"eps_F{F}": kk / nf if nf else np.nan, f"eps_lo_F{F}": lo, f"eps_hi_F{F}": hi,
                            f"med_ds_um_F{F}": 1e4 * np.nanmedian([r[f"{sct}_ds"] for r in pl]) if pl else np.nan,
                            f"med_dw_um_F{F}": 1e4 * np.nanmedian([r[f"{sct}_dw"] for r in pl]) if pl else np.nan,
                            f"n_err_F{F}": sum(bool(r.get("error")) for r in rr)})
            row["flips_F1_F16"] = sum(bool(R[1][k].get(f"{sct}_final")) != bool(R[16][k].get(f"{sct}_final")) for k in keys)
            row["fid_flips_F1_F16"] = sum(bool(R[1][k]["fid"]) != bool(R[16][k]["fid"]) for k in keys)
            row["within_wilson"] = bool(row["eps_lo_F1"] <= row["eps_F16"] <= row["eps_hi_F1"]) if row["nfid_F1"] else None
            row.update(dpos_in_med_um=1e4 * np.median(din) if din else np.nan, dpos_in_p90_um=1e4 * np.percentile(din, 90) if din else np.nan,
                       dpos_out_med_um=1e4 * np.median(dout) if dout else np.nan, dpos_out_p90_um=1e4 * np.percentile(dout, 90) if dout else np.nan)
            rows.append(row)
T = pd.DataFrame(rows); T.to_csv(f"{HERE}/out_G01/G07_impact_table.csv", index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 50)
show = ["sample", "lambda_keV", "sct", "nfid_F1", "k_F1", "k_F4", "k_F16", "eps_F1", "eps_lo_F1", "eps_hi_F1", "eps_F16", "within_wilson", "flips_F1_F16",
        "fid_flips_F1_F16", "med_ds_um_F1", "med_ds_um_F16", "med_dw_um_F1", "med_dw_um_F16", "dpos_in_med_um", "dpos_out_med_um", "dpos_out_p90_um"]
print(T[show].round(3).to_string(index=False))
