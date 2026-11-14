#!/usr/bin/env python3
"""Stage 2, step 10: is the lower 13.6 TeV reach of the colored channel at sigma_z = 1.16 mm a fluctuation or a setup difference?
(1) Factor by factor, 13 vs 13.6 TeV, every mass point and the benchmark (1800 GeV, 2 keV): sigma, eps_trig = n_trigger / n_matched, f_ch = both charged /
    triggered, eps_fid = n_fid / n_prop, eps_reco = k / n_fid; two-proportion z for each efficiency.
(2) Kinematics of the propagated events (KS tests: quirk pT, |eta|, beta, pT(QQ)).
(3) Reach (F6_04 algorithm, as S2_05_reach.py) at 300 and 332 fb^-1 for: 13 TeV as is; 13 TeV efficiencies x 13.6 TeV sigma, eps_trig, f_ch ("expected");
    13.6 TeV as is; pooled eps_fid x eps_reco of both samples with the 13.6 TeV sigma, eps_trig, f_ch.
(4) Bootstrap (events resampled with replacement per mass point, all Lambda values of an event kept together, both samples): distribution of
    Delta = reach(13.6 TeV) - reach(expected); fraction of replicas with Delta >= 0.
Output: S2_compare_factors.csv, S2_compare_kinematics.csv, S2_compare_reach.csv, S2_compare_bootstrap.csv (printed)."""
import os, json, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03"
SRC = {"13": (f"{REP}/fig6/inputs", f"{REP}/logs"), "13.6": (f"{HERE}/inputs", f"{HERE}/logs")}
LAMS = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25]); TR = lambda s: s.astype(str) == "True"; NB = 500; RNG = np.random.default_rng(20261104)

def sample(E, ch):
    ind, logd = SRC[E]; C = pd.read_csv(f"{ind}/counts.csv"); C = C[C.channel == ch]; out = {}
    for r in C.itertuples():
        tag = f"{ch}_{r.mass_gev}gev"; ev = pd.read_csv(f"{ind}/{tag}_events.csv"); tr = TR(ev.trigger_proxy_pass)
        sel = tr & (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5) if ch == "colored" else tr; P = ev[sel].reset_index(drop=True)
        rows = []
        for band in ("low", "mid", "high_a"):
            f = f"{logd}/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl"
            if os.path.exists(f): rows += [x for l in open(f) if l.strip() for x in json.loads(l)]
        d = dict(sigma=r.sigma_matched_fb, n_matched=len(ev), n_trig=int(tr.sum()), n_prop=int(sel.sum()), ev=P, prop=False)
        if rows:
            D = pd.DataFrame(rows).drop_duplicates(["event", "lambda_keV"]); D["lam"] = D.lambda_keV.astype(float)
            assert all(len(D[np.isclose(D.lam, l)]) == d["n_prop"] for l in LAMS), (E, tag)
            D = D.sort_values(["event", "lam"]); n = d["n_prop"]
            for c in ("fid", "Z0_final", "Z1160_final"): d[c] = TR(D[c]).values.reshape(n, len(LAMS))   # event x Lambda
            d["prop"] = True
        out[int(r.mass_gev)] = d
    return out

def pre(d, L): return L * d["sigma"] * d["n_trig"] / d["n_matched"] * d["n_prop"] / d["n_trig"]   # L sigma eps_trig f_ch (EW: f_ch = 1)
def reach(ms, N, ok, thr):                                                   # F6_04 algorithm on a mass x Lambda matrix
    best = np.nan
    for j in range(N.shape[1]):
        v = np.where(ok[:, j], N[:, j], np.nan)
        for i in range(len(ms) - 1):
            a, b = v[i], v[i + 1]
            if np.isfinite(a) and np.isfinite(b) and a >= thr > b:
                mm = ms[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (ms[i + 1] - ms[i])
                best = mm if not np.isfinite(best) or mm > best else best
    return best
def grid(S, sct, L, eff=None, idx=None):
    """N (mass x Lambda) and ok mask. eff: dict mass -> k/n per Lambda used instead of S's own (for 'expected' / pooled); idx: bootstrap indices."""
    ms = np.array(sorted(S)); N = np.full((len(ms), len(LAMS)), np.nan); ok = np.zeros_like(N, bool)
    for i, m in enumerate(ms):
        d = S[m]; p = pre(d, L)
        if eff is not None and m in eff: e = eff[m]
        elif d["prop"]: X = d[f"{sct}_final"] if idx is None else d[f"{sct}_final"][idx[m]]; e = X.mean(0)
        else: N[i] = p; ok[i] = p < 3; continue                                  # not propagated: N <= L sigma eps_trig f_ch ("bound")
        N[i] = p * e; ok[i] = e > 0
    return ms, N, ok

rows_f, rows_k, rows_r, rows_b = [], [], [], []
for ch in ("colored", "EW"):
    A, B = sample("13", ch), sample("13.6", ch)
    for m in sorted(B):
        a, b = A.get(m), B[m]
        for nm, ka, na, kb, nb in (("eps_trig", a["n_trig"], a["n_matched"], b["n_trig"], b["n_matched"]), ("f_ch", a["n_prop"], a["n_trig"], b["n_prop"], b["n_trig"])):
            pa, pb = ka / na, kb / nb; pp = (ka + kb) / (na + nb); z = (pb - pa) / np.sqrt(pp * (1 - pp) * (1 / na + 1 / nb)) if 0 < pp < 1 else 0
            rows_f.append(dict(channel=ch, mass_gev=m, lambda_keV=np.nan, sct="", factor=nm, v13=pa, v13p6=pb, ratio=pb / pa, z=z, counts13=f"{ka}/{na}", counts13p6=f"{kb}/{nb}"))
        rows_f.append(dict(channel=ch, mass_gev=m, lambda_keV=np.nan, sct="", factor="sigma_fb", v13=a["sigma"], v13p6=b["sigma"], ratio=b["sigma"] / a["sigma"], z=np.nan, counts13="", counts13p6=""))
        if not (a["prop"] and b["prop"]): continue
        for j, lam in enumerate(LAMS):
            if lam not in (1, 2, 4, 5, 10): continue
            for sct in ("Z1160", "Z0"):
                fa, fb = a["fid"][:, j], b["fid"][:, j]; ra, rb = a[f"{sct}_final"][:, j], b[f"{sct}_final"][:, j]
                for nm, ka, na, kb, nb in (("eps_fid", fa.sum(), len(fa), fb.sum(), len(fb)), ("eps_reco", ra.sum(), fa.sum(), rb.sum(), fb.sum()), ("k/n", ra.sum(), len(ra), rb.sum(), len(rb))):
                    if nm == "eps_fid" and sct == "Z0": continue
                    pa, pb = ka / na, kb / nb; pp = (ka + kb) / (na + nb); z = (pb - pa) / np.sqrt(pp * (1 - pp) * (1 / na + 1 / nb)) if 0 < pp < 1 else 0
                    rows_f.append(dict(channel=ch, mass_gev=m, lambda_keV=lam, sct="" if nm == "eps_fid" else sct, factor=nm, v13=pa, v13p6=pb, ratio=pb / pa if pa else np.nan, z=z,
                                       counts13=f"{ka}/{na}", counts13p6=f"{kb}/{nb}"))
        kin = lambda P: dict(pT=np.r_[np.hypot(P.px1, P.py1), np.hypot(P.px2, P.py2)], abseta=np.abs(np.r_[np.arcsinh(P.pz1 / np.hypot(P.px1, P.py1)), np.arcsinh(P.pz2 / np.hypot(P.px2, P.py2))]),
                             beta=np.r_[np.sqrt(P.px1**2 + P.py1**2 + P.pz1**2) / P.E1, np.sqrt(P.px2**2 + P.py2**2 + P.pz2**2) / P.E2], pTQQ=np.hypot(P.px1 + P.px2, P.py1 + P.py2))
        ka_, kb_ = kin(a["ev"]), kin(b["ev"])
        for v in ka_: rows_k.append(dict(channel=ch, mass_gev=m, variable=v, median13=np.median(ka_[v]), median13p6=np.median(kb_[v]), KS_p=stats.ks_2samp(ka_[v], kb_[v]).pvalue))
    # reach variants and bootstrap
    for sct in ("Z1160", "Z0"):
        effA = {m: A[m][f"{sct}_final"].mean(0) for m in A if A[m]["prop"]}
        pool = {m: np.r_[A[m][f"{sct}_final"], B[m][f"{sct}_final"]].mean(0) for m in B if B[m]["prop"] and m in A and A[m]["prop"]}
        for L in (300.0, 332.0):
            for cn, thr in (("exclusion", 3), ("discovery", 5)):
                v = dict(r13=reach(*grid(A, sct, 300.0), thr), expected=reach(*grid(B, sct, L, eff=effA), thr), r13p6=reach(*grid(B, sct, L), thr), pooled=reach(*grid(B, sct, L, eff=pool), thr))
                rows_r.append(dict(channel=ch, sct=sct, lumi_fb=L, contour=cn, reach_13TeV_300fb=v["r13"], expected_13TeVeff_x_13p6sigma=v["expected"], reach_13p6TeV=v["r13p6"], pooled_eff_13p6sigma=v["pooled"]))
                if L != 332.0: continue
                D = []
                for _ in range(NB):
                    ia = {m: RNG.integers(0, A[m]["n_prop"], A[m]["n_prop"]) for m in A if A[m]["prop"]}; ib = {m: RNG.integers(0, B[m]["n_prop"], B[m]["n_prop"]) for m in B if B[m]["prop"]}
                    ea = {m: A[m][f"{sct}_final"][ia[m]].mean(0) for m in ia}
                    D.append(reach(*grid(B, sct, L, idx=ib), thr) - reach(*grid(B, sct, L, eff=ea), thr))
                D = np.array(D); D = D[np.isfinite(D)]; obs = v["r13p6"] - v["expected"]
                rows_b.append(dict(channel=ch, sct=sct, lumi_fb=L, contour=cn, delta_observed=obs, delta_boot_median=np.median(D), delta_boot_16=np.percentile(D, 16), delta_boot_84=np.percentile(D, 84),
                                   sigma_boot=(np.percentile(D, 84) - np.percentile(D, 16)) / 2, frac_delta_ge_0=(D >= 0).mean(), n_replicas=len(D)))
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
F = pd.DataFrame(rows_f); F.to_csv(f"{HERE}/S2_compare_factors.csv", index=False)
K = pd.DataFrame(rows_k); K.to_csv(f"{HERE}/S2_compare_kinematics.csv", index=False)
R = pd.DataFrame(rows_r).round(0); R.to_csv(f"{HERE}/S2_compare_reach.csv", index=False)
Bt = pd.DataFrame(rows_b).round(3); Bt.to_csv(f"{HERE}/S2_compare_bootstrap.csv", index=False)
print("== benchmark colored 1800 GeV, 2 keV"); print(F[(F.channel == "colored") & (F.mass_gev == 1800) & (F.lambda_keV.isna() | (F.lambda_keV == 2))].round(4).to_string(index=False))
print("== eps_trig, f_ch, all points"); print(F[F.factor.isin(["eps_trig", "f_ch"])].round(4).to_string(index=False))
print("== colored Z1160 k/n, Lambda 1-10 keV"); print(F[(F.channel == "colored") & (F.factor == "k/n") & (F.sct == "Z1160")].round(4).to_string(index=False))
print("== kinematics"); print(K.round(4).to_string(index=False))
print("== reach"); print(R.to_string(index=False)); print("== bootstrap (332 fb^-1)"); print(Bt.to_string(index=False))
