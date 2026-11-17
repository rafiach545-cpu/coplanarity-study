#!/usr/bin/env python3
"""07 X02 (2026-11-17): ideal (G01 stage2 geometry = 8 barrel layers of Stage 2) vs ATLAS (G01 atlas geometry) on the same 10k-generated events
(signal/inputs_large), server runs signal/runs/large_ideal and signal/runs/large_atlas (13 points x low/mid/high_a, all complete).

1. Grid N(m, Lambda) for both with the Stage 2 method unchanged (reach/R01_reach_07.py grid(), strict: every band complete; T09 PASS):
   N = L sigma eps_trig f_ch k/n_prop, i.e. L sigma (n_prop / n_matched) (k / n_prop); n_prop = n_trigger (EW) or n_trigger and both charged (colored);
   sigma, n_matched from signal/inputs_large/counts.csv and the event files; Wilson 68% interval on k/n; k = 0 -> status bound/computed as Stage 2.
   -> tables/X02_N_grid_{S1_Run3_Ideal,S2_Run3_ATLAS}_300fb.csv (300 fb^-1 as R01; scaled to 332 fb^-1 below).
2. Reach at 332 fb^-1 (N = 3 / 5, Stage 2 reach() unchanged) for ideal, ATLAS and Stage 2 (2k) -> tables/X02_reach_332fb.csv.
3. Contour lines (06 method, T10) -> tables/X02_contours_332fb.csv.
4. Paired event-by-event comparison per (channel, mass, Lambda, SCT) and summed over masses per (channel, Lambda, SCT): McNemar exact test on the discordant pairs
   b = ideal pass & ATLAS fail, c = ideal fail & ATLAS pass (two-sided binomial p, b ~ Bin(b + c, 1/2)); for the selection (<sct>_final) and for fid.
   Holm correction over all tests of the same table. -> tables/X02_mcnemar_per_point.csv, tables/X02_mcnemar_per_lambda.csv.
5. Where the N = 3 / 5 lines cross between grid points: for every Lambda the mass interval [m_i, m_i+1] with N(m_i) >= thr > N(m_i+1) (log-linear crossing, as reach()),
   the crossing of the Wilson band ends, and a 3-point check: the crossing from a quadratic in log N through m_i-1 (or m_i+2), m_i, m_i+1; and for every mass the
   Lambda interval where N crosses thr. -> tables/X02_crossings_mass.csv, tables/X02_crossings_lambda.csv."""
import os, sys, json, importlib.util, numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
import contourpy
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); BASE = os.path.abspath(f"{R}/.."); T = f"{R}/tables"; INP = f"{R}/signal/inputs_large"
S2 = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop"; L = 332.0; SET = ("Z0", "A580", "Z1160"); RUNS = {"S1_Run3_Ideal": f"{R}/signal/runs/large_ideal", "S2_Run3_ATLAS": f"{R}/signal/runs/large_atlas"}
spec = importlib.util.spec_from_file_location("R01", f"{R}/reach/R01_reach_07.py"); R01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(R01)
src = open(f"{R}/FIGURES_ROOT_2026-11-17/prepare_data_07.py").read(); exec(src[src.index("def zgrid"):src.index("BK = rd(")])   # zgrid, lines, scaled (T10)
C, NOTES = R01.with_runs(pd.read_csv(f"{INP}/counts.csv"), RUNS["S2_Run3_ATLAS"]); assert len(R01.with_runs(C, RUNS["S1_Run3_Ideal"])[0]) == len(C); print("\n".join(NOTES))

# 1. grids
G = {}
for nm, d in RUNS.items():
    g, notes = R01.grid(C, INP, lambda tag, d=d: R01.load_07(tag, d), SET, strict=True); assert not notes, notes
    g.to_csv(f"{T}/X02_N_grid_{nm}_300fb.csv", index=False); G[nm] = g
G["S1_Run3_Ideal_2k"] = pd.read_csv(f"{S2}/S2_N_grid_300fb.csv")
for nm in ("S1_Run3_Ideal", "S2_Run3_ATLAS"): print(nm, G[nm].status_with_f.value_counts().to_dict())

# 2. reach
rows = []
for nm, g in G.items():
    for ch in ("colored", "EW"):
        for sct in SET:
            if not (g.sct == sct).any(): continue
            for r in R01.reach_rows(g, ch, sct, L, 3.0, 5.0, {}): rows.append(dict(setup=nm, **r))
RE = pd.DataFrame(rows); RE.to_csv(f"{T}/X02_reach_332fb.csv", index=False)

# 3. contours
cl = []
for nm, g0 in G.items():
    g1 = scaled(g0, L)
    for ch in ("colored", "EW"):
        for sct in SET:
            g = g1[(g1.channel == ch) & (g1.sct == sct)]
            if not len(g): continue
            for cn, t in (("exclusion", 3.0), ("discovery", 5.0)):
                for band, col in (("central", "N_with_f"), ("lo", "N_with_f_lo"), ("hi", "N_with_f_hi")):
                    for s, seg in enumerate(lines(g, col, t)):
                        cl += [dict(setup=nm, channel=ch, sct=sct, contour=cn, band=band, segment=s, mass_gev=x, lambda_eV=10 ** y) for x, y in seg]
pd.DataFrame(cl).to_csv(f"{T}/X02_contours_332fb.csv", index=False)

# 4. McNemar
def load(nm, tag, band):
    out = {}
    for l in open(f"{RUNS[nm]}/G01_{tag}_{band}.jsonl"):
        for r in json.loads(l): out[(r["event"], round(r["lambda_keV"], 6))] = r
    return out
def mcn(b, c): return float(stats.binomtest(b, b + c, 0.5).pvalue) if b + c else 1.0
def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for i, j in enumerate(o): run = max(run, min(1.0, (m - i) * p[j])); adj[j] = run
    return adj
pp = []
for r in C.itertuples():
    tag = f"{r.channel}_{r.mass_gev}gev"
    for band in ("low", "mid", "high_a"):
        a, s = load("S1_Run3_Ideal", tag, band), load("S2_Run3_ATLAS", tag, band); assert set(a) == set(s), f"{tag} {band}: different (event, Lambda) sets"
        for lam in sorted({k[1] for k in a}):
            ks = [k for k in a if k[1] == lam]
            for q in ("fid",) + tuple(f"{x}_final" for x in SET):
                i = np.array([bool(a[k].get(q)) for k in ks]); t = np.array([bool(s[k].get(q)) for k in ks])
                pp.append(dict(channel=r.channel, mass_gev=r.mass_gev, lambda_keV=lam, quantity=q, n=len(ks), k_S1_Run3_Ideal=int(i.sum()), k_S2_Run3_ATLAS=int(t.sum()),
                               both=int((i & t).sum()), b_S1_only=int((i & ~t).sum()), c_S2_only=int((~i & t).sum())))
P = pd.DataFrame(pp); P["p_mcnemar"] = [mcn(b, c) for b, c in zip(P.b_S1_only, P.c_S2_only)]
P["p_holm"] = np.nan
for q, x in P.groupby("quantity"): P.loc[x.index, "p_holm"] = holm(x.p_mcnemar.values)
P["diff_k_over_n"] = (P.k_S2_Run3_ATLAS - P.k_S1_Run3_Ideal) / P.n; P.to_csv(f"{T}/X02_mcnemar_per_point.csv", index=False)
A = P.groupby(["channel", "lambda_keV", "quantity"]).agg(n=("n", "sum"), k_S1_Run3_Ideal=("k_S1_Run3_Ideal", "sum"), k_S2_Run3_ATLAS=("k_S2_Run3_ATLAS", "sum"), b_S1_only=("b_S1_only", "sum"),
                                                         c_S2_only=("c_S2_only", "sum")).reset_index()
A["p_mcnemar"] = [mcn(b, c) for b, c in zip(A.b_S1_only, A.c_S2_only)]; A["p_holm"] = np.nan
for q, x in A.groupby("quantity"): A.loc[x.index, "p_holm"] = holm(x.p_mcnemar.values)
A["ratio_k_S2_over_S1"] = A.k_S2_Run3_ATLAS / A.k_S1_Run3_Ideal.replace(0, np.nan); A.to_csv(f"{T}/X02_mcnemar_per_lambda.csv", index=False)

# 5. crossings
cm, clam = [], []
for nm, g0 in G.items():
    g1 = scaled(g0, L)
    for ch in ("colored", "EW"):
        for sct in SET:
            g = g1[(g1.channel == ch) & (g1.sct == sct)]
            if not len(g): continue
            ms = sorted(g.mass_gev.unique()); lams = sorted(g.lambda_keV.unique())
            for thr, cn in ((3.0, "exclusion"), (5.0, "discovery")):
                for lam in lams:
                    x = g[np.isclose(g.lambda_keV, lam)].sort_values("mass_gev")
                    ok = (x.status_with_f == "bound") | ((x.status_with_f == "computed") & (x.k > 0)); v = np.where(ok, x.N_with_f, np.nan); m = x.mass_gev.values
                    vlo, vhi = np.where(ok, x.N_with_f_lo, np.nan), np.where(ok, x.N_with_f_hi, np.nan)
                    for i in range(len(m) - 1):
                        if np.isfinite(v[i]) and np.isfinite(v[i + 1]) and v[i] >= thr > v[i + 1]:
                            ll = lambda a, b: m[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (m[i + 1] - m[i]) if (np.isfinite(a) and np.isfinite(b) and a > 0 and b > 0 and a != b) else np.nan
                            j = [k for k in ((i - 1, i, i + 1), (i, i + 1, i + 2)) if min(k) >= 0 and max(k) < len(m) and all(np.isfinite(v[list(k)]) & (v[list(k)] > 0))]
                            mq = np.nan
                            if j:
                                kk = list(j[0]); cf = np.polyfit(m[kk], np.log10(v[kk]), 2); rts = np.roots(cf - np.array([0, 0, np.log10(thr)]))
                                rts = [z.real for z in rts if abs(z.imag) < 1e-9 and m[i] <= z.real <= m[i + 1]]; mq = rts[0] if rts else np.nan
                            mc = ll(v[i], v[i + 1])
                            cm.append(dict(setup=nm, channel=ch, sct=sct, contour=cn, lambda_keV=lam, m_lo=m[i], m_hi=m[i + 1], gap_GeV=m[i + 1] - m[i],
                                           N_at_m_lo=v[i], N_at_m_hi=v[i + 1], m_cross_loglin=mc, m_cross_quadratic=mq, d_quadratic_minus_loglin=mq - mc,
                                           m_cross_wilson_lo=ll(vlo[i], vlo[i + 1]) if vlo[i] >= thr > vlo[i + 1] else np.nan,
                                           m_cross_wilson_hi=ll(vhi[i], vhi[i + 1]) if vhi[i] >= thr > vhi[i + 1] else np.nan))
                for mm in ms:
                    x = g[g.mass_gev == mm].sort_values("lambda_keV")
                    ok = (x.status_with_f == "bound") | ((x.status_with_f == "computed") & (x.k > 0)); v = np.where(ok, x.N_with_f, 0.0); lv = x.lambda_keV.values
                    for i in range(len(lv) - 1):
                        if (v[i] >= thr) != (v[i + 1] >= thr):
                            clam.append(dict(setup=nm, channel=ch, sct=sct, contour=cn, mass_gev=mm, lambda_lo_keV=lv[i], lambda_hi_keV=lv[i + 1], N_at_lambda_lo=v[i], N_at_lambda_hi=v[i + 1],
                                             direction="rises" if v[i + 1] >= thr else "falls"))
pd.DataFrame(cm).to_csv(f"{T}/X02_crossings_mass.csv", index=False); pd.DataFrame(clam).to_csv(f"{T}/X02_crossings_lambda.csv", index=False)
print("X02: wrote", ", ".join(f"X02_{x}" for x in ("N_grid_ideal_300fb.csv", "N_grid_atlas_300fb.csv", "reach_332fb.csv", "contours_332fb.csv", "mcnemar_per_point.csv",
                                                     "mcnemar_per_lambda.csv", "crossings_mass.csv", "crossings_lambda.csv")))
