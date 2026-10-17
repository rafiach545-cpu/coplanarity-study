#!/usr/bin/env python3
"""D39 pre-registered test (notes/D39_prereg.md, sha256 eb59c8f7...): string direction at equal CM time vs equal lab time, effect on Delta_s and
eps_reco (mode FIRST), 2026-10-14.
Per event (COL2000 at 2 keV; EW2000 at 4, 1, 2 keV): z0 and SCT draws as P18. (a) lab-time string: production integrator (300 steps per period),
first crossings via p18.all_crossings; (b) CM-time string: PreFASER step (driver argv[1], divStep 30000, uniform 2 T, no energy loss, start at
the origin, until the CM radius reaches 60 cm), first crossings with lab times, z shifted by z0. Both through p18.reco (SCT z none and 580 um).
Denominator: (a)'s fiducial set at each Lambda (P20 definition); (b)'s own fiducial flag is recorded.
Output: tables/D32_cm_time_string_reco.csv, printed summary with Wilson 95% intervals."""
import os, sys, subprocess, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
DRV = sys.argv[1]; RAD = [L["r_cm"] for L in p4.tth.LAYERS] if hasattr(p4, "tth") else None
RUNS = [("COL2000", 2), ("EW2000", 4), ("EW2000", 1), ("EW2000", 2)]
def fid_of(cr, c1, c2):
    if c1 == 0 or c2 == 0: return False
    f = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}
    return all((q, L) in f and abs(f[(q, L)]["z_lab"]) < p4.HALF[L] and f[(q, L)]["t_ns"] < p4.R["timing_ns"] for q in (1, 2) for L in range(1, 9))
def thick(cr, z0):
    X = np.array([(c["x"], c["y"], c["z_lab"] - z0) for c in cr if c["order"] == 0]); return np.sqrt(max(np.linalg.eigvalsh(X.T @ X / (len(X) - 1))[0], 0)) * 1e4
def job(a):
    s, lamk, key, P1, P2, c1, c2, z0, g = a; m = p4.PAR["EW" if s.startswith("EW") else "COL"][0]; lam = lamk * 1e-6
    E1, E2 = np.sqrt(P1 @ P1 + m * m), np.sqrt(P2 @ P2 + m * m)
    _, tr = p4.tth.simulate_quirk_hits((*P1, E1), (*P2, E2), mass_gev=m, Lambda_gev=lam, B_tesla=p4.R["B_tesla"], charge1=c1, charge2=c2,
                                       rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=p4.R["max_layer_r_cm"])
    A = p18.all_crossings(tr); fa = fid_of(A, c1, c2)
    row = dict(sample=s, lambda_keV=lamk, key=key, fid_lab=fa)
    if not fa: return row
    o = subprocess.run([DRV, str(m), str(lamk * 1000), str(p4.R["B_tesla"]), *map(str, P1), *map(str, P2), "600000", "30000", str(int(c1)), str(int(c2))],
                       capture_output=True, text=True).stdout
    B = []
    for line in o.splitlines():
        q, L, x, y, z, t = line.split(); B.append(dict(quirk=int(q), layer=int(L), order=0, x=float(x) * 1e-4, y=float(y) * 1e-4, z_lab=float(z) * 1e-4 + z0,
                                                      t_ns=float(t), r=p4.tth.LAYERS[int(L) - 1]["r_cm"]))
    row.update(fid_cm=fid_of(B, c1, c2), ds_truth_lab_um=thick(A, z0), ds_truth_cm_um=thick(B, z0) if len(B) >= 3 else np.nan)
    for tag, cr in (("lab", A), ("cm", B)):
        for sct in ("Z0", "Z580"):
            r = p18.reco(cr, z0, g, sct, key, s, True)
            row.update({f"{tag}_{sct}_plane": r["plane"], f"{tag}_{sct}_final": r["final"], f"{tag}_{sct}_ds_um": r["ds"] * 1e4, f"{tag}_{sct}_dw_cm": r["dw"]})
    return row
if __name__ == "__main__":
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv"); jobs = []
    for s in ("COL2000", "EW2000"):
        ev = p4.fp.load_sample(s).sort_values("key"); cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv"); M = p4.momenta(s)
        for e in ev.itertuples():
            c = cr0[cr0.key == e.key].sort_values(["quirk", "layer"])
            if len(c) == 0 or ("technical_error" in c.columns and c.technical_error.notna().any()): continue
            exk = ex[(ex["sample"] == s) & (ex.key == e.key)].sort_values(["quirk", "layer"])
            if len(exk) == 0: continue
            z0, g = p4.fp.stream_draws(np.random.default_rng(int(e.seed)), c, exk.copy()); r = M.iloc[int(e.key)]
            for ss, lamk in RUNS:
                if ss == s: jobs.append((s, lamk, int(e.key), np.array([r.px1, r.py1, r.pz1]), np.array([r.px2, r.py2, r.pz2]), float(r.charge1), float(r.charge2), z0, g))
    print("jobs", len(jobs), flush=True)
    with mp.Pool(int(os.environ.get("NWORKERS", 3)), initializer=p4._init) as pool: d = pd.DataFrame(list(pool.imap_unordered(job, jobs, chunksize=2)))
    d = d.sort_values(["sample", "lambda_keV", "key"]); d.to_csv(f"{T}/D32_cm_time_string_reco.csv", index=False)
    p4.CFG.write_provenance(f"{T}/D32_cm_time_string_reco.csv", dict(prereg="notes/D39_prereg.md", driver_divStep=30000))
    W = lambda k, n: stats.binomtest(int(k), int(n)).proportion_ci(0.95, "wilson") if n else (np.nan, np.nan)
    for (s, lamk), x in d.groupby(["sample", "lambda_keV"]):
        f = x[x.fid_lab == True]; n = len(f)
        print(f"\n== {s} {lamk} keV: lab fiducial {n}; CM-time fiducial among them {int(f.fid_cm.sum())}; truth thickness median lab {f.ds_truth_lab_um.median():.2f} um, CM {f.ds_truth_cm_um.median():.2f} um")
        for sct in ("Z0", "Z580"):
            kl, kc = int(f[f"lab_{sct}_final"].sum()), int(f[f"cm_{sct}_final"].sum()); lo1, hi1 = W(kl, n); lo2, hi2 = W(kc, n)
            sw = int((f[f"lab_{sct}_final"] != f[f"cm_{sct}_final"]).sum())
            pl = f[f[f"lab_{sct}_plane"] == True]; pc = f[f[f"cm_{sct}_plane"] == True]
            print(f"   SCT z {sct}: eps_reco lab {kl}/{n} = {kl / n:.3f} [{lo1:.3f}, {hi1:.3f}] | CM {kc}/{n} = {kc / n:.3f} [{lo2:.3f}, {hi2:.3f}] | events changed {sw} | "
                  f"Delta_s median lab {pl[f'lab_{sct}_ds_um'].median():.1f} um, CM {pc[f'cm_{sct}_ds_um'].median():.1f} um | Delta_w median lab {pl[f'lab_{sct}_dw_cm'].median():.3f}, CM {pc[f'cm_{sct}_dw_cm'].median():.3f} cm")
