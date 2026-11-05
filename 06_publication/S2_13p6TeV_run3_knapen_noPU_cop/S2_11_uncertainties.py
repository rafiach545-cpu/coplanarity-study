#!/usr/bin/env python3
"""Stage 2, step 11: statistical uncertainties of every factor, of the expected events and of the reach, and a test of the 13 vs 13.6 TeV selection efficiency.
Samples as S2_10_compare_13_vs_13p6.py (same reading code, same F6_04 reach algorithm). Statistical only (no PDF / scale / detector systematics).
(1) Budget: for every mass point at its best Lambda (largest N), relative 68% uncertainty of sigma (MG5 integration error), eps_trig and f_ch (Wilson),
    k/n (Wilson) and their sum in quadrature; 13 TeV at 139 fb^-1, 13.6 TeV at 332 fb^-1.
(2) Reach toys (NT per mode): "kn" = events resampled with replacement per mass point (all Lambda of an event together), as the S2_10 bootstrap;
    "gen" = sigma ~ Gauss(sigma, err), n_trig ~ Binomial(n_matched, eps_trig), n_prop ~ Binomial(n_trig, f_ch); "all" = both; with background
    (sigma_z = 0, 13.6 TeV, mu = 0 / 20 / 50 / 60) also the signal-region count ~ Binomial(n, k/n) of the S2_09 background, thresholds as S2_09 (s95, s5).
    Output: 16 / 50 / 84 percentiles of the maximum reach. Bootstrap cannot move a k = 0 point up (limitation, stated in the report).
(3) Consistency of the selection efficiency (13 vs 13.6 TeV, propagated events): per event the fraction of the 15 Lambda values passing; per mass point
    D = mean(13.6) - mean(13); z = D / sd of D under NP label permutations (events of both energies pooled per mass point). Per channel and SCT:
    chi2 = sum z^2 (two-sided) and S = sum z / sqrt(M) (signed), p-values from the same permutations; global p for the 4 channel x SCT tests.
    eps_trig, f_ch: two-proportion z per mass point (independent across masses) and chi2.
Output: S2_unc_budget.csv, S2_unc_reach.csv, S2_unc_consistency_mass.csv, S2_unc_consistency.csv. Run with /home/rafia/venvs/f6fast/bin/python."""
import os, json, numpy as np, pandas as pd
from scipy import stats, optimize
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03"
SRC = {"13": (f"{REP}/fig6/inputs", f"{REP}/logs"), "13.6": (f"{HERE}/inputs", f"{HERE}/logs")}
LAMS = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25]); TR = lambda s: s.astype(str) == "True"; NT = 1000; NP = 5000; RNG = np.random.default_rng(20261105)
LUM = {"13": 139.0, "13.6": 332.0}

def sample(E, ch):                                                           # as S2_10, plus the sigma error
    ind, logd = SRC[E]; C = pd.read_csv(f"{ind}/counts.csv"); C = C[C.channel == ch]; out = {}
    for r in C.itertuples():
        tag = f"{ch}_{r.mass_gev}gev"; ev = pd.read_csv(f"{ind}/{tag}_events.csv"); tr = TR(ev.trigger_proxy_pass)
        sel = tr & (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5) if ch == "colored" else tr
        rows = []
        for band in ("low", "mid", "high_a"):
            f = f"{logd}/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl"
            if os.path.exists(f): rows += [x for l in open(f) if l.strip() for x in json.loads(l)]
        d = dict(sigma=r.sigma_matched_fb, sigma_err=r.sigma_matched_err_fb, n_matched=len(ev), n_trig=int(tr.sum()), n_prop=int(sel.sum()), prop=False)
        if rows:
            D = pd.DataFrame(rows).drop_duplicates(["event", "lambda_keV"]); D["lam"] = D.lambda_keV.astype(float)
            assert all(len(D[np.isclose(D.lam, l)]) == d["n_prop"] for l in LAMS), (E, tag)
            D = D.sort_values(["event", "lam"]); n = d["n_prop"]
            for c in ("Z0_final", "Z1160_final"): d[c] = TR(D[c]).values.reshape(n, len(LAMS))
            d["prop"] = True
        out[int(r.mass_gev)] = d
    return out
def reach(ms, N, ok, thr):                                                   # F6_04 algorithm (as S2_10)
    best = np.nan
    for j in range(N.shape[1]):
        v = np.where(ok[:, j], N[:, j], np.nan)
        for i in range(len(ms) - 1):
            a, b = v[i], v[i + 1]
            if np.isfinite(a) and np.isfinite(b) and a >= thr > b:
                mm = ms[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (ms[i + 1] - ms[i])
                best = mm if not np.isfinite(best) or mm > best else best
    return best
def grid(S, sct, L, toy=None):
    """N (mass x Lambda); toy: None (central) or dict(kn=bool, gen=bool)"""
    ms = np.array(sorted(S)); N = np.full((len(ms), len(LAMS)), np.nan); ok = np.zeros_like(N, bool)
    for i, m in enumerate(ms):
        d = S[m]; sg, nt, npr = d["sigma"], d["n_trig"], d["n_prop"]
        if toy and toy["gen"]:
            sg = max(RNG.normal(d["sigma"], d["sigma_err"]), 0); nt = RNG.binomial(d["n_matched"], d["n_trig"] / d["n_matched"]); npr = RNG.binomial(nt, d["n_prop"] / d["n_trig"])
        p = L * sg * nt / d["n_matched"] * (npr / nt if nt else 0)
        if not d["prop"]: N[i] = p; ok[i] = p < 3; continue                     # not propagated: bound (as S2_10)
        X = d[f"{sct}_final"]
        if toy and toy["kn"]: X = X[RNG.integers(0, len(X), len(X))]
        e = X.mean(0); N[i] = p * e; ok[i] = e > 0
    return ms, N, ok
X = dict(l.split() for l in open(f"{HERE}/inputs/zgamma_xsec_13p6TeV.txt")); SG = float(X["sigma_after_MET_pb"]) * 1e3 * 0.01
def s95(b):
    n = int(round(b)); return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-3, 300)
def s5(b):
    za = lambda s: np.sqrt(2 * ((s + b) * np.log(1 + s / b) - s)) - 5
    return max(5.0, optimize.brentq(za, 1e-3, 1e3)) if b > 0 else 5.0
BK = pd.read_csv(f"{HERE}/S2_background_13p6TeV.csv"); BK = BK[(BK.process == "conversion + pile-up") & (BK.sct == "Z0")].set_index("mu")
def thresholds(mu, toy):                                                     # sigma_z = 0 background of S2_09 at 332 fb^-1
    r = BK.loc[mu]; n, k = int(r.n), int(r.sr)
    if toy: k = RNG.binomial(n, k / n)
    b = 332.0 * SG * k / n; bu = b if k else 332.0 * SG * (1 - 0.05 ** (1 / n)); return s95(bu), s5(b)
wil = lambda k, n: stats.binomtest(int(k), int(n)).proportion_ci(0.6827, "wilson")
pct = lambda v: np.nanpercentile(v, [16, 50, 84]) if np.isfinite(v).sum() else [np.nan] * 3

S = {(E, ch): sample(E, ch) for E in ("13", "13.6") for ch in ("colored", "EW")}
# ---- (1) budget
bud = []
for (E, ch), A in S.items():
    for m, d in sorted(A.items()):
        L = LUM[E]; et, fc = d["n_trig"] / d["n_matched"], d["n_prop"] / d["n_trig"]; elo, ehi = wil(d["n_trig"], d["n_matched"]); flo, fhi = wil(d["n_prop"], d["n_trig"])
        pre = L * d["sigma"] * et * fc
        for sct in ("Z1160", "Z0"):
            r = dict(sqrt_s_TeV=E, lumi_fb=L, channel=ch, sct=sct, mass_gev=m, sigma_fb=d["sigma"], rel_sigma=d["sigma_err"] / d["sigma"], eps_trig=et, rel_eps_trig=(ehi - elo) / 2 / et,
                     f_ch=fc, rel_f_ch=(fhi - flo) / 2 / fc if ch == "colored" else 0.0, pre_N=pre, status="computed" if d["prop"] else "bound")
            if d["prop"]:
                e = d[f"{sct}_final"].mean(0); j = int(np.argmax(e)); k = int(d[f"{sct}_final"][:, j].sum()); n = d["n_prop"]; lo, hi = wil(k, n)
                r.update(best_lambda_keV=LAMS[j], k=k, n=n, kn=k / n, rel_kn_lo=(k / n - lo) / (k / n), rel_kn_hi=(hi - k / n) / (k / n), N=pre * k / n)
                q = np.sqrt(r["rel_sigma"] ** 2 + r["rel_eps_trig"] ** 2 + r["rel_f_ch"] ** 2)
                r.update(rel_gen=q, rel_tot_lo=np.hypot(q, r["rel_kn_lo"]), rel_tot_hi=np.hypot(q, r["rel_kn_hi"]))
            bud.append(r)
BU = pd.DataFrame(bud); BU.to_csv(f"{HERE}/S2_unc_budget.csv", index=False)

# ---- (2) reach toys
rr = []
for ch in ("colored", "EW"):
    for sct in ("Z1160", "Z0"):
        for E in ("13", "13.6"):
            A = S[(E, ch)]; L = LUM[E]
            mus = [None] + ([0, 20, 50, 60] if (E == "13.6" and sct == "Z0") else [])
            for mu in mus:
                for ci, cn in enumerate(("exclusion", "discovery")):
                    thr0 = (3.0, 5.0)[ci] if mu is None else thresholds(mu, False)[ci]
                    row = dict(sqrt_s_TeV=E, lumi_fb=L, channel=ch, sct=sct, mu=-1 if mu is None else mu, contour=cn, threshold=thr0, central=reach(*grid(A, sct, L), thr0))
                    for mode, tk in (("kn", dict(kn=True, gen=False)), ("gen", dict(kn=False, gen=True)), ("all", dict(kn=True, gen=True))):
                        v = np.array([reach(*grid(A, sct, L, tk), thr0 if mu is None else thresholds(mu, True)[ci]) for _ in range(NT)])
                        row.update({f"{mode}_16": pct(v)[0], f"{mode}_50": pct(v)[1], f"{mode}_84": pct(v)[2], f"{mode}_nfail": int((~np.isfinite(v)).sum())})
                    if mu is not None:                                       # background count alone
                        v = np.array([reach(*grid(A, sct, L), thresholds(mu, True)[ci]) for _ in range(NT)])
                        row.update(bkg_16=pct(v)[0], bkg_50=pct(v)[1], bkg_84=pct(v)[2])
                    rr.append(row); print(ch, sct, E, mu, cn, {k: round(v, 0) for k, v in row.items() if k.endswith(("central", "_16", "_84"))}, flush=True)
RR = pd.DataFrame(rr); RR.to_csv(f"{HERE}/S2_unc_reach.csv", index=False)

# ---- (3) consistency 13 vs 13.6 TeV
cm, cs = [], []
for ch in ("colored", "EW"):
    A, B = S[("13", ch)], S[("13.6", ch)]; ms = [m for m in sorted(B) if m in A and A[m]["prop"] and B[m]["prop"]]
    for sct in ("Z1160", "Z0"):
        Z, Zp = [], []
        for m in ms:
            a, b = A[m][f"{sct}_final"].mean(1), B[m][f"{sct}_final"].mean(1); pool = np.r_[a, b]; na = len(a)
            D = b.mean() - a.mean(); Dp = np.empty(NP)
            for t in range(NP):
                q = RNG.permutation(pool); Dp[t] = q[na:].mean() - q[:na].mean()
            sd = Dp.std(); z = D / sd; Z.append(z); Zp.append(Dp / sd)
            cm.append(dict(channel=ch, sct=sct, mass_gev=m, eff13=a.mean(), eff13p6=b.mean(), n13=na, n13p6=len(b), k13_sum=int(A[m][f"{sct}_final"].sum()), k13p6_sum=int(B[m][f"{sct}_final"].sum()),
                           ratio=b.mean() / a.mean() if a.mean() else np.nan, z=z, p_two_sided=(np.abs(Dp) >= abs(D) - 1e-12).mean()))
        Z, Zp = np.array(Z), np.array(Zp)                                    # Zp: masses x permutations (independent across masses)
        chi, chip = (Z ** 2).sum(), (Zp ** 2).sum(0); Sg, Sgp = Z.sum() / np.sqrt(len(Z)), Zp.sum(0) / np.sqrt(len(Z))
        cs.append(dict(test=f"selection k/n, {sct}", channel=ch, sct=sct, n_points=len(Z), chi2=chi, p_chi2=(chip >= chi).mean(), signed_z=Sg, p_signed_low=(Sgp <= Sg).mean(),
                       p_signed_two=(np.abs(Sgp) >= abs(Sg)).mean()))
    for nm, kk, nn in (("eps_trig", "n_trig", "n_matched"), ("f_ch", "n_prop", "n_trig")):
        if nm == "f_ch" and ch == "EW": continue
        z = []
        for m in sorted(B):
            if m not in A: continue
            ka, na, kb, nb = A[m][kk], A[m][nn], B[m][kk], B[m][nn]; pp = (ka + kb) / (na + nb)
            z.append((kb / nb - ka / na) / np.sqrt(pp * (1 - pp) * (1 / na + 1 / nb)))
        z = np.array(z); Sg = z.sum() / np.sqrt(len(z))
        cs.append(dict(test=nm, channel=ch, sct="", n_points=len(z), chi2=(z ** 2).sum(), p_chi2=stats.chi2.sf((z ** 2).sum(), len(z)), signed_z=Sg, p_signed_low=stats.norm.cdf(Sg),
                       p_signed_two=2 * stats.norm.sf(abs(Sg))))
CM, CS = pd.DataFrame(cm), pd.DataFrame(cs)
sel = CS.test.str.startswith("selection"); CS["p_global_4tests"] = np.where(sel, 1 - (1 - np.minimum(CS.p_chi2, CS.p_signed_two)) ** 4, np.nan)
CM.to_csv(f"{HERE}/S2_unc_consistency_mass.csv", index=False); CS.to_csv(f"{HERE}/S2_unc_consistency.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
print(BU.round(3).to_string(index=False)); print(RR.round(0).to_string(index=False)); print(CM.round(3).to_string(index=False)); print(CS.round(4).to_string(index=False))
