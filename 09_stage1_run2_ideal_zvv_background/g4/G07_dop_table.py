#!/usr/bin/env python3
"""09 / G07 with DOP853 (2026-11-22): production RK4 (F1), RK4 dt/16 (F16) and DOP853 at rtol 1e-10 (D10) / 1e-11 (D11), same events.
Per (sample, Lambda, sigma_z): n_fid, k, eps (Wilson 68 %), paired SR flips F1<->D10, F16<->D10, D10<->D11 (rtol check, must be 0),
fiducial flips, integration failures (RK4: 20M-step ceiling; DOP853 has none), median ds / dw, first-crossing shift F1 -> D10 in / out of
the event plane (plane fitted to the D10 crossings through the vertex). Output: out_G01/G07_dop_table.csv."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = f"{HERE}/out_G01/G07"
TAGS = [("colored_1800gev", "2-4-7-10"), ("EW_800gev", "2-4-7-10"), ("EW_600gev", "4-5")]
def wilson(k, n, z=1.0):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return (c - h, c + h)
def load(tag, lams, F):
    return {(r["event"], r["lambda_keV"]): r for l in open(f"{D}/{tag}_L{lams}_F{F}.jsonl") if l.strip() for r in json.loads(l)}
rows = []
for tag, lams in TAGS:
    R = {F: load(tag, lams, F) for F in ("1", "16", "D10", "D11")}
    for lam in sorted({k[1] for k in R["1"]}):
        keys = sorted(k for k in R["1"] if k[1] == lam and all(k in R[F] for F in R))
        din, dout = [], []
        for k in keys:
            a, b = R["1"][k], R["D10"][k]
            if not (a["fid"] and b["fid"]): continue
            A = {(c[0], c[1]): np.array(c[2:5]) for c in a["first"]}; Bv = {(c[0], c[1]): np.array(c[2:5]) for c in b["first"]}
            v = np.array([0.0, 0.0, b["z0"]]); n = np.linalg.svd(np.array([Bv[q] - v for q in sorted(Bv)]), full_matrices=False)[2][-1]
            for q in Bv:
                if q in A: d = A[q] - Bv[q]; o = abs(d @ n); dout.append(o); din.append(np.sqrt(max(d @ d - o * o, 0)))
        for sct in ("Z1160", "Z580"):
            fin = lambda F, k: bool(R[F][k].get(f"{sct}_final"))
            row = dict(sample=tag, lambda_keV=lam, sct=sct, n_events=len(keys))
            for F in R:
                rr = [R[F][k] for k in keys]; nf = sum(bool(r["fid"]) for r in rr); kk = sum(fin(F, k) for k in keys); lo, hi = wilson(kk, nf)
                pl = [r for r in rr if r.get(f"{sct}_plane") in (True, "True")]
                row.update({f"nfid_{F}": nf, f"k_{F}": kk, f"eps_{F}": kk / nf if nf else np.nan, f"lo_{F}": lo, f"hi_{F}": hi,
                            f"err_{F}": sum(bool(r.get("error")) for r in rr),
                            f"ds_{F}": 1e4 * np.nanmedian([r[f"{sct}_ds"] for r in pl]) if pl else np.nan,
                            f"dw_{F}": 1e4 * np.nanmedian([r[f"{sct}_dw"] for r in pl]) if pl else np.nan})
            for a, b in (("1", "D10"), ("16", "D10"), ("D10", "D11")):
                row[f"flips_{a}_{b}"] = sum(fin(a, k) != fin(b, k) for k in keys)
                row[f"fidflips_{a}_{b}"] = sum(bool(R[a][k]["fid"]) != bool(R[b][k]["fid"]) for k in keys)
            row.update(dpos_in_med=1e4 * np.median(din) if din else np.nan, dpos_out_med=1e4 * np.median(dout) if dout else np.nan,
                       dpos_out_p90=1e4 * np.percentile(dout, 90) if dout else np.nan)
            row["t_s_F1"] = np.mean([R["1"][k]["t_s"] for k in keys]); row["t_s_D10"] = np.mean([R["D10"][k]["t_s"] for k in keys]); row["t_s_D11"] = np.mean([R["D11"][k]["t_s"] for k in keys])
            rows.append(row)
T = pd.DataFrame(rows); T.to_csv(f"{HERE}/out_G01/G07_dop_table.csv", index=False)
pd.set_option("display.width", 320); pd.set_option("display.max_columns", 60)
print(T[["sample", "lambda_keV", "sct", "nfid_1", "nfid_D10", "err_1", "err_D10", "k_1", "k_16", "k_D10", "k_D11", "eps_D10", "lo_D10", "hi_D10",
         "flips_1_D10", "flips_16_D10", "flips_D10_D11", "fidflips_1_D10", "fidflips_D10_D11", "ds_1", "ds_D10", "dw_1", "dw_D10",
         "dpos_in_med", "dpos_out_med", "dpos_out_p90", "t_s_F1", "t_s_D10", "t_s_D11"]].round(3).to_string(index=False))
