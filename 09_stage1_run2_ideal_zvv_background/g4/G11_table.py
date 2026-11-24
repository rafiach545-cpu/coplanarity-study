#!/usr/bin/env python3
"""09 / G11 table (2026-11-24): Athena string model (Geant4, QuirkPheno_fix, maxBoost 0.01) vs Eq. 3 (DOP853 rtol 1e-10, G07 FD10), same events.
Conventions as G07_dop_table.py: n_fid, k, eps with Wilson 68 % interval; paired SR flips and fiducial flips; first-crossing shift split in / out of
the event plane (SVD plane of the D10 first crossings relative to the vertex (0, 0, z0), as G07_dop_table). Added here:
  - the shift only for the crossings reco uses (t < 25 ns and |z_lab| < HALF[layer], P18 reco / grid fid_of), p90 and max;
  - per event the largest out-of-plane shift: median and the number of fiducial events with > 50 um and > 100 um (Delta_s cut 100 um);
  - for reference the production RK4 (G07 F1) vs D10 on the same events;
  - Geant4 convergence: maxBoost 0.001 vs 0.01 (EW 800 GeV, 4 and 10 keV, first 40 events), flips and shift.
Output: out_G01/G11_table.csv, out_G01/G11_convergence.csv."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D7, D11 = f"{HERE}/out_G01/G07", f"{HERE}/out_G01/G11"
HALF = {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9}     # cm, P4 (T1_config_check.py 3a)
TAGS = [("colored_1800gev", "2-4-7-10"), ("EW_800gev", "2-4-7-10"), ("EW_600gev", "4-5")]


def wilson(k, n, z=1.0):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return (c - h, c + h)


def load(path):
    return {(r["event"], r["lambda_keV"]): r for l in open(path) if l.strip() for r in json.loads(l)}


def shifts(a, b):
    """a vs reference b (both fiducial): per crossing (in, out) in cm, all first crossings and the reco-used ones; plane from b."""
    A = {(c[0], c[1]): np.array(c[2:5]) for c in a["first"]}; B = {(c[0], c[1]): np.array(c[2:5]) for c in b["first"]}
    tb = {(c[0], c[1]): c[5] for c in b["first"]}
    v = np.array([0.0, 0.0, b["z0"]]); n = np.linalg.svd(np.array([B[q] - v for q in sorted(B)]), full_matrices=False)[2][-1]
    out = []
    for q in B:
        if q not in A: continue
        d = A[q] - B[q]; o = abs(d @ n); used = tb[q] < 25.0 and abs(B[q][2]) < HALF[q[1]]
        out.append((np.sqrt(max(d @ d - o * o, 0)), o, used))
    return out


def compare(Ra, Rb, keys, name_a, name_b):
    din, dout, ev_out = [], [], []
    for k in keys:
        a, b = Ra[k], Rb[k]
        if not (a["fid"] and b["fid"]): continue
        s = [x for x in shifts(a, b) if x[2]]
        if not s: continue
        din += [x[0] for x in s]; dout += [x[1] for x in s]; ev_out.append(max(x[1] for x in s))
    f = lambda v, q: 1e4 * np.percentile(v, q) if v else np.nan
    return {f"in_med_um": f(din, 50), f"in_p90_um": f(din, 90), f"in_max_um": f(din, 100), f"out_med_um": f(dout, 50), f"out_p90_um": f(dout, 90),
            f"out_max_um": f(dout, 100), "ev_outmax_med_um": f(ev_out, 50), "n_ev_out_gt50": int(sum(x > 50e-4 for x in ev_out)),
            "n_ev_out_gt100": int(sum(x > 100e-4 for x in ev_out)), "n_ev_shift": len(ev_out)}


rows = []
for tag, lams in TAGS:
    R = {"G4": load(f"{D11}/{tag}_L{lams}_FG4mb01.jsonl"), "D10": load(f"{D7}/{tag}_L{lams}_FD10.jsonl"), "F1": load(f"{D7}/{tag}_L{lams}_F1.jsonl")}
    for lam in sorted({k[1] for k in R["D10"]}):
        keys = sorted(k for k in R["D10"] if k[1] == lam and all(k in R[F] for F in R))
        pos = {p: compare(R[a], R["D10"], keys, a, "D10") for p, a in (("G4", "G4"), ("F1", "F1"))}
        for sct in ("Z1160", "Z580"):
            fin = lambda F, k: bool(R[F][k].get(f"{sct}_final"))
            row = dict(sample=tag, lambda_keV=lam, sct=sct, n_events=len(keys))
            for F in R:
                rr = [R[F][k] for k in keys]; nf = sum(bool(r["fid"]) for r in rr); kk = sum(fin(F, k) for k in keys); lo, hi = wilson(kk, nf)
                pl = [r for r in rr if r.get(f"{sct}_plane") in (True, "True")]
                row.update({f"nfid_{F}": nf, f"k_{F}": kk, f"eps_{F}": kk / nf if nf else np.nan, f"lo_{F}": lo, f"hi_{F}": hi, f"err_{F}": sum(bool(r.get("error")) for r in rr),
                            f"ds_{F}": 1e4 * np.nanmedian([r[f"{sct}_ds"] for r in pl]) if pl else np.nan})
            for a in ("G4", "F1"):
                row[f"up_{a}"] = sum((not fin("D10", k)) and fin(a, k) for k in keys); row[f"dn_{a}"] = sum(fin("D10", k) and not fin(a, k) for k in keys)
                row[f"fidflips_{a}"] = sum(bool(R[a][k]["fid"]) != bool(R["D10"][k]["fid"]) for k in keys)
            row["deps_G4"] = row["eps_G4"] - row["eps_D10"]; row["eps_ratio_G4"] = row["eps_G4"] / row["eps_D10"] if row["eps_D10"] else np.nan
            row.update({f"G4_{x}": v for x, v in pos["G4"].items()}); row.update({f"F1_{x}": v for x, v in pos["F1"].items()})
            rows.append(row)
T = pd.DataFrame(rows); T.to_csv(f"{HERE}/out_G01/G11_table.csv", index=False)
pd.set_option("display.width", 320); pd.set_option("display.max_columns", 80)
print("Athena (Geant4 maxBoost 0.01) vs Eq. 3 (DOP853 D10), paired; production RK4 (F1) vs D10 for scale")
print(T[["sample", "lambda_keV", "sct", "n_events", "nfid_D10", "nfid_G4", "fidflips_G4", "k_D10", "k_G4", "up_G4", "dn_G4", "eps_D10", "eps_G4", "lo_G4", "hi_G4",
         "eps_ratio_G4", "k_F1", "up_F1", "dn_F1", "ds_D10", "ds_G4"]].round(3).to_string(index=False))
print("\nfirst-crossing shift vs D10, reco-used crossings of events fiducial in both (um)")
print(T[T.sct == "Z1160"][["sample", "lambda_keV", "G4_n_ev_shift", "G4_in_med_um", "G4_in_p90_um", "G4_out_med_um", "G4_out_p90_um", "G4_out_max_um", "G4_ev_outmax_med_um",
                          "G4_n_ev_out_gt50", "G4_n_ev_out_gt100", "F1_out_med_um", "F1_out_p90_um", "F1_ev_outmax_med_um", "F1_n_ev_out_gt100"]].round(1).to_string(index=False))
# Geant4 convergence
cf = f"{D11}/EW_800gev_L4-10_FG4mb001_n40.jsonl"
if os.path.exists(cf):
    Rf, Rc = load(cf), load(f"{D11}/EW_800gev_L2-4-7-10_FG4mb01.jsonl"); C = []
    for lam in (4.0, 10.0):
        keys = sorted(k for k in Rf if k[1] == lam and k in Rc)
        p = compare(Rf, Rc, keys, "mb001", "mb01")
        for sct in ("Z1160", "Z580"):
            C.append(dict(lambda_keV=lam, sct=sct, n=len(keys), k_mb01=sum(bool(Rc[k][f"{sct}_final"]) for k in keys), k_mb001=sum(bool(Rf[k][f"{sct}_final"]) for k in keys),
                          flips=sum(bool(Rc[k][f"{sct}_final"]) != bool(Rf[k][f"{sct}_final"]) for k in keys), fidflips=sum(bool(Rc[k]["fid"]) != bool(Rf[k]["fid"]) for k in keys), **p))
    C = pd.DataFrame(C); C.to_csv(f"{HERE}/out_G01/G11_convergence.csv", index=False)
    print("\nGeant4 convergence, maxBoost 0.001 vs 0.01 (EW 800 GeV, first 40 events)"); print(C.round(2).to_string(index=False))
print("G11_TABLE_EXIT=0")
