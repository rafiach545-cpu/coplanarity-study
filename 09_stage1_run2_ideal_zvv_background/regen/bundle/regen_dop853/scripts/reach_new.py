#!/usr/bin/env python3
"""regen_dop853: 13.6 TeV reach (332 fb^-1) from the new DOP853 runs (step C) with the unchanged 07 method, next to the old one.
Method = the KF6 / X08 'central b' computation (07 REPORT_KNAPEN_FIGURES_2026-11-18/K02_prepare.py): R01_reach_07.grid (strict for the old runs;
non-strict for the new runs: an incomplete band = 'not run'), R01.reach_rows with s95(N_bkg) / s5(N_bkg), the backgrounds of
07 tables/X08_background_used.csv (read only: the converted-photon background has no quirk and does not depend on the quirk integrator),
contours with zgrid / lines / scaled of 07 FIGURES_ROOT_2026-11-17/prepare_data_07.py.
Check: the old reach recomputed here must equal 07 REPORT_KNAPEN_FIGURES_2026-11-18/data/fig6_reach.csv (C2 of K02).
Usage: reach_new.py <regen_dop853 dir>. Writes <dir>/out/reach/*.csv and <dir>/out/reach/REACH_NOTES.txt."""
import os, sys, importlib.util, numpy as np, pandas as pd, contourpy
from scipy.interpolate import RegularGridInterpolator
RD = os.path.abspath(sys.argv[1]); B = f"{RD}/base"; R7 = f"{B}/07_atlas_real_geometry"; OUT = f"{RD}/out/reach"; os.makedirs(OUT, exist_ok=True)
spec = importlib.util.spec_from_file_location("R01", f"{R7}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
src = open(f"{R7}/FIGURES_ROOT_2026-11-17/prepare_data_07.py").read(); exec(src[src.index("def zgrid"):src.index("BK = rd(")])
L = 332.0; SET = ("Z0", "A580", "Z1160"); INP = f"{R7}/signal/inputs_large"
GEO = {"S1_Run3_Ideal": ("stage2", "large_ideal"), "S2_Run3_ATLAS": ("atlas", "large_atlas")}
TOL = {("colored", "S2_Run3_ATLAS"): 22, ("colored", "S1_Run3_Ideal"): 27, ("EW", "S2_Run3_ATLAS"): 14, ("EW", "S1_Run3_Ideal"): 24}
BENCH = {"colored": (1800, 2.0), "EW": (800, 4.0)}
notes = []; BU = pd.read_csv(f"{R7}/tables/X08_background_used.csv")
C0 = pd.read_csv(f"{INP}/counts.csv"); grids = {}
for setup, (geom, old) in GEO.items():
    for ver, d, strict in (("old", f"{R7}/signal/runs/{old}", True), ("new", f"{RD}/out/C_13p6TeV_{geom}", False)):
        C, nr = R01.with_runs(C0, d); notes += [f"{setup} {ver}: {n}" for n in nr]
        if not len(C): notes.append(f"{setup} {ver}: no complete mass point"); continue
        g, nn = R01.grid(C, INP, lambda tag, d=d: R01.load_07(tag, d), SET, strict=strict); notes += [f"{setup} {ver}: {n}" for n in nn]
        g.to_csv(f"{OUT}/N_grid_{setup}_{ver}_300fb.csv", index=False); grids[(setup, ver)] = g
rows, cl = [], []
for (setup, ver), g0 in grids.items():
    g1 = scaled(g0, L)
    for sct in SET:
        for mu in (0, 20, 50):
            b = BU[(BU.setup == setup) & (BU.sct == sct) & (BU.mu == mu)]
            if not len(b): continue
            b = b.iloc[0]; se, sd = R01.s95(b.N_bkg), R01.s5(b.N_bkg)
            for ch in ("colored", "EW"):
                if not len(g0[g0.channel == ch]): continue
                for r in R01.reach_rows(g0, ch, sct, L, se, sd, {}):
                    rows.append(dict(version=ver, setup=setup, channel=ch, sct=sct, mu=mu, N_bkg=b.N_bkg, n_bkg_mc=int(b.n_final), contour=r["contour"],
                                     s_required=r["s_required"], m_max_GeV=r["m_max_GeV"], m_max_lo=r.get("m_max_lo"), m_max_hi=r.get("m_max_hi"),
                                     at_lambda_keV=r.get("at_lambda_keV"), reach_beyond_grid=r.get("reach_beyond_grid")))
                if ver != "new" or sct != "A580" or mu not in (0, 50): continue
                gg = g1[(g1.channel == ch) & (g1.sct == sct)]
                for cn, t in (("exclusion", se), ("discovery", sd)):
                    for band, col in (("central", "N_with_f"), ("lo", "N_with_f_lo"), ("hi", "N_with_f_hi")):
                        try:
                            for s, seg in enumerate(lines(gg, col, t)):
                                cl += [dict(setup=setup, channel=ch, sct=sct, mu=mu, contour=cn, threshold=t, band=band, segment=s, mass_gev=x, lambda_eV=10 ** y) for x, y in seg]
                        except Exception as e: notes.append(f"contour {setup} {ch} {cn} {band}: {str(e)[:80]}")
RR = pd.DataFrame(rows); RR.to_csv(f"{OUT}/reach_old_and_new_332fb.csv", index=False); pd.DataFrame(cl).to_csv(f"{OUT}/fig6_contours_new.csv", index=False)
# check: old recomputed == fig6_reach.csv (KF6)
F6 = pd.read_csv(f"{R7}/REPORT_KNAPEN_FIGURES_2026-11-18/data/fig6_reach.csv"); bad = 0; n = 0
for r in F6.itertuples():
    x = RR[(RR.version == "old") & (RR.setup == r.setup) & (RR.channel == r.channel) & (RR.sct == r.sct) & (RR.mu == r.mu) & (RR.contour == r.contour)]
    n += 1; bad += int(not (len(x) == 1 and x.m_max_GeV.iloc[0] == r.m_max_GeV))
notes.insert(0, f"CHECK old reach recomputed vs KF6 fig6_reach.csv: {n - bad}/{n} rows identical -> {'PASS' if bad == 0 else 'FLAG'}")
# headline: A580, mu = 50
H = []
for setup in GEO:
    for ch in ("colored", "EW"):
        row = dict(channel=ch, geometry="ATLAS" if "ATLAS" in setup else "Ideal", setup=setup); same = True; have = True
        for cn in ("exclusion", "discovery"):
            o = RR[(RR.version == "old") & (RR.setup == setup) & (RR.channel == ch) & (RR.sct == "A580") & (RR.mu == 50) & (RR.contour == cn)]
            nw = RR[(RR.version == "new") & (RR.setup == setup) & (RR.channel == ch) & (RR.sct == "A580") & (RR.mu == 50) & (RR.contour == cn)]
            ov = o.m_max_GeV.iloc[0] if len(o) else np.nan; nv = nw.m_max_GeV.iloc[0] if len(nw) else np.nan
            row[f"old_{cn}"] = ov; row[f"new_{cn}"] = nv; row[f"new_{cn}_lo"] = nw.m_max_lo.iloc[0] if len(nw) else np.nan; row[f"new_{cn}_hi"] = nw.m_max_hi.iloc[0] if len(nw) else np.nan
            row[f"change_{cn}"] = nv - ov if np.isfinite(ov) and np.isfinite(nv) else np.nan
            if not np.isfinite(row[f"change_{cn}"]): have = False
            elif abs(row[f"change_{cn}"]) > TOL[(ch, setup)]: same = False
        row["tolerance_GeV"] = TOL[(ch, setup)]; row["verdict"] = ("SAME" if same else "CHANGED") if have else "n/a (new result missing)"; H.append(row)
pd.DataFrame(H).to_csv(f"{OUT}/headline_A580_mu50.csv", index=False)
# benchmarks
BM = []
for (setup, ver), g in grids.items():
    for ch, (m, lam) in BENCH.items():
        x = g[(g.channel == ch) & (g.mass_gev == m) & np.isclose(g.lambda_keV, lam) & (g.sct == "A580")]
        if len(x) and x.status.iloc[0] == "computed":
            BM.append(dict(setup=setup, version=ver, channel=ch, mass_gev=m, lambda_keV=lam, n_prop=int(x.n_prop.iloc[0]), n_fid=int(x.n_fid.iloc[0]), k=int(x.k.iloc[0]),
                           eps_reco=x.eps_reco.iloc[0]))
pd.DataFrame(BM).to_csv(f"{OUT}/benchmarks.csv", index=False)
open(f"{OUT}/REACH_NOTES.txt", "w").write("\n".join(notes) + "\n"); print("\n".join(notes[:20])); print(pd.DataFrame(H).to_string(index=False)); print("REACH_NEW_EXIT=0")
