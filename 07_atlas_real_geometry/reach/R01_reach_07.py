#!/usr/bin/env python3
"""07 reach step R01 (2026-11-17): expected signal events and reach for the ATLAS Run 2 ID geometry (07), large samples (G02: 10 000 generated events
per mass point, 13.6 TeV), SCT settings Z0 / A580 / Z1160 (D4), with and without the C01 converted-photon background.
Method copied without change from Stage 2 (06_publication/S2_.../S2_05_reach.py, S2_09_background_summary.py; checked by test T09, which runs the functions
below on the Stage 2 inputs and must reproduce S2_N_grid_300fb.csv, S2_reach.csv and S2_reach_with_background.csv):
  N = L sigma eps_trig [f_ch] k / n; colored: n = triggered events with both quirk-hadrons charged, f_ch included; EW: n = triggered events;
  Wilson 68% band on k/n; k = 0: 95% upper limit 1 - 0.05^(1/n); reach: F6_04_summary.py algorithm (log-linear interpolation in m_Q of N at fixed Lambda,
  highest crossing over Lambda); thresholds with background b: exclusion = 95% CLs with n_obs = round(b_used), discovery = max(5, Asimov Z = 5) at the central b.
07 inputs:
  signal - signal/inputs_large/counts.csv (sigma, n_matched, n_trigger, n_trigger_both_charged) and signal/runs/large_atlas/G01_<tag>_<band>.jsonl (server runs; env R01_RUNS)
           (fid = 07 station rule, <sct>_final = plane + multiplicity + Delta_s + Delta_w; fid_stage2 also stored). A band file is used only when it holds
           every propagated event (n); otherwise its Lambda values are "not run" (as S2_05: "bound" if L sigma eps_trig f_ch < 3, else "missing").
  background - tables/S01_C01_atlas[_A580]_mu<mu>.csv (C01 + S01, 332 fb^-1, summed over the conversion regions); scaled linearly to L.
           b_used (exclusion) = central N if any event passed, else the 95% upper limit with 0 events in every region: P(0) = exp(-sum b_i / w_i) >= 0.05
           with w_i the weight of one simulated photon in region i gives b <= 3 max_i w_i = the largest per-region S01 limit (S2_09: one region, the same formula).
           Also given: the reach with b_used = central N (variant 'central b'), because the limit is set by the background MC statistics (9130 photons).
Output: tables/R01_N_grid_300fb.csv, tables/R01_reach.csv (zero background), tables/R01_background.csv, tables/R01_reach_with_background.csv."""
import os, glob, json, numpy as np, pandas as pd
from scipy import stats, optimize
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/.."); T = f"{ROOT}/tables"
BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study"); S2 = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop"
LUMI = 300.0; LUMIS = (300.0, 332.0, 355.0)
LAMS = (0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25)
BANDS = ("low", "mid", "high_a"); TR = lambda s: s.astype(str) == "True"


def load_s2(tag):                                                             # Stage 2 F6 logs (as S2_05 load)
    rows, nev = [], {}
    for band in BANDS:
        f = f"{S2}/logs/F6_{tag}{'' if band == 'mid' else '_' + band}_events.jsonl"
        if os.path.exists(f):
            new = [r for l in open(f) if l.strip() for r in json.loads(l)]; nev[band] = len({r["event"] for r in new}); rows += new
    return pd.DataFrame(rows), nev


def load_07(tag, d=os.environ.get("R01_RUNS", f"{ROOT}/signal/runs/large_atlas")):
    rows, nev = [], {}
    for band in BANDS:
        f = f"{d}/G01_{tag}_{band}.jsonl"
        if os.path.exists(f):
            new = [r for l in open(f) if l.strip() for r in json.loads(l)]; nev[band] = len({r["event"] for r in new}); rows += [dict(r, band=band) for r in new]
    return pd.DataFrame(rows), nev


def with_runs(C, d=None):
    """2026-11-17: keep only the mass points whose three band files exist in the run directory (a new point, e.g. EW 1200 GeV, is in counts.csv
    before it is propagated); returns (C, notes)."""
    d = d or os.environ.get("R01_RUNS", f"{ROOT}/signal/runs/large_atlas")
    has = C.apply(lambda r: all(os.path.exists(f"{d}/G01_{r.channel}_{r.mass_gev}gev_{b}.jsonl") for b in BANDS), axis=1)
    return C[has].reset_index(drop=True), [f"{r.channel}_{r.mass_gev}gev: no runs in {d} -> not in the grid" for r in C[~has].itertuples()]


def grid(C, inputs_dir, loader, settings, strict):
    """S2_05 grid. strict=True: every present band must be complete (S2_05 assert); False: incomplete bands are dropped (their Lambda = not run)."""
    recs, notes = [], []
    for r in C.itertuples():
        tag = f"{r.channel}_{r.mass_gev}gev"; ev = pd.read_csv(f"{inputs_dir}/{tag}_events.csv"); tr = TR(ev.trigger_proxy_pass)
        if r.channel == "colored":
            nch = int((tr & (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)).sum()); et = tr.sum() / len(ev); fch = nch / tr.sum(); n_prop = nch
        else:
            et = tr.sum() / len(ev); fch = 1.0; n_prop = int(tr.sum())
        D, nev = loader(tag); pre = LUMI * r.sigma_matched_fb * et
        if strict:
            assert all(v == n_prop for v in nev.values()), f"{tag}: incomplete band(s) {nev}, expected {n_prop}"
        else:
            bad = [b for b, v in nev.items() if v != n_prop]
            if bad: notes.append(f"{tag}: bands {bad} incomplete ({ {b: nev[b] for b in bad} } of {n_prop}) -> not used"); D = D[~D.band.isin(bad)] if len(D) else D
        for lam in LAMS:
            x = D[np.isclose(D.lambda_keV.astype(float), lam)] if len(D) else D; done = len(x) == n_prop and len(x) > 0
            for sct in settings:
                base = dict(sqrt_s_TeV=13.6, lumi_fb=LUMI, channel=r.channel, mass_gev=r.mass_gev, lambda_keV=lam, sct=sct, sigma_fb=r.sigma_matched_fb, eps_trig=et, f_ch=fch,
                            n_prop=n_prop, L_sigma_eps_trig=pre)
                if done:
                    n_fid = int(TR(x.fid).sum()); k = int(TR(x[f"{sct}_final"]).sum()); lo, hi = stats.binomtest(k, n_prop).proportion_ci(0.6827, "wilson"); ul = 1 - 0.05 ** (1 / n_prop)
                    base.update(status="computed", status_with_f="computed", status_without_f="computed", n_fid=n_fid, k=k, n_integration_fail=int((x.error.astype(str) != "").sum()),
                                eps_fid=n_fid / n_prop, eps_reco=k / n_fid if n_fid else np.nan, N_with_f=pre * fch * k / n_prop, N_with_f_lo=pre * fch * lo, N_with_f_hi=pre * fch * hi,
                                N_with_f_UL95_if_k0=pre * fch * ul if k == 0 else np.nan)
                    if "fid_stage2" in x:                                      # 07 only: barrel rule on the same trajectories, end-cap use of the winner plane
                        base.update(n_fid_barrel_rule=int(TR(x.fid_stage2).sum()), k_endcap=int((TR(x[f"{sct}_final"]) & TR(x[f"{sct}_endcap"])).sum()))
                else:
                    base.update(status="not run", status_with_f="bound" if pre * fch < 3 else "missing", status_without_f="bound" if pre < 3 else "missing", N_with_f=pre * fch)
                recs.append(base)
    return pd.DataFrame(recs), notes


def reach(g, col, thr):                                                      # F6_04_summary.py, unchanged (as S2_05_reach.py)
    best = (np.nan, np.nan)
    for lam, x in g.groupby("lambda_keV"):
        x = x.sort_values("mass_gev"); ok = (x[f"status_{'with_f' if 'with_f' in col else 'without_f'}"] == "bound") | ((x.status_with_f == "computed") & (x.k > 0))
        m, v = x.mass_gev.values, np.where(ok, x[col].values, np.nan)
        for i in range(len(m) - 1):
            a, b = v[i], v[i + 1]
            if np.isfinite(a) and np.isfinite(b) and a >= thr > b:
                mm = m[i] + (np.log10(thr) - np.log10(a)) / (np.log10(b) - np.log10(a)) * (m[i + 1] - m[i])
                if not np.isfinite(best[0]) or mm > best[0]: best = (mm, lam)
    return best


def s95(b):                                                                  # S2_09, unchanged
    n = int(round(b)); return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-3, 300)


def s5(b):                                                                   # S2_09, unchanged
    za = lambda s: np.sqrt(2 * ((s + b) * np.log(1 + s / b) - s)) - 5
    return max(5.0, optimize.brentq(za, 1e-3, 1e3)) if b > 0 else 5.0


rd = lambda v: round(v) if np.isfinite(v) else np.nan


def reach_rows(G, ch, sct, L, thr_e, thr_d, extra):
    g = G[(G.channel == ch) & (G.sct == sct)].copy(); g[["N_with_f", "N_with_f_lo", "N_with_f_hi"]] *= L / LUMI; out = []
    for nm, thr in (("exclusion", thr_e), ("discovery", thr_d)):
        c, lo, hi = (reach(g, f"N_with_f{s}", thr) for s in ("", "_lo", "_hi"))
        top = g[g.mass_gev == g.mass_gev.max()]
        topc = top[(top.status_with_f == "bound") | ((top.status_with_f == "computed") & (top.k > 0))]   # 07 addition: only rows the reach method uses
        nc = float(topc.N_with_f.max()) if len(topc) else np.nan
        out.append(dict(channel=ch, sct=sct, lumi_fb=L, contour=nm, **extra, s_required=round(thr, 2), m_max_GeV=rd(c[0]), at_lambda_keV=c[1], m_max_lo=rd(lo[0]),
                        m_max_hi=rd(hi[0]), N_max_at_highest_mass=round(float(top.N_with_f.max()), 2),
                        N_max_at_highest_mass_used=round(nc, 2) if np.isfinite(nc) else np.nan,
                        reach_beyond_grid=bool(np.isfinite(nc) and nc >= thr)))   # 07 addition: True -> true reach >= highest grid mass (method gives a lower bound)
    return out


if __name__ == "__main__":
    SET = ("Z0", "A580", "Z1160"); INP = f"{ROOT}/signal/inputs_large"
    C = pd.read_csv(f"{INP}/counts.csv"); C, nr = with_runs(C)
    G, notes = grid(C, INP, load_07, SET, strict=True); notes = nr + notes
    for n in notes: print("NOTE", n)
    G.to_csv(f"{T}/R01_N_grid_300fb.csv", index=False)
    S2R = pd.read_csv(f"{S2}/S2_reach.csv"); rows = []
    for ch in ("colored", "EW"):
        for sct in SET:
            for L in LUMIS:
                for r in reach_rows(G, ch, sct, L, 3.0, 5.0, {}):
                    s = S2R[(S2R.channel == ch) & (S2R.sct == sct) & (S2R.lumi_fb == L) & (S2R.contour == r["contour"])]
                    r["m_max_S1_Run3_Ideal_2k_GeV"] = s.m_max_GeV.iloc[0] if len(s) else np.nan; rows.append(r)
    R = pd.DataFrame(rows); R.to_csv(f"{T}/R01_reach.csv", index=False); pd.set_option("display.width", 250); print(R[R.lumi_fb == 332].to_string(index=False))
    # background (C01 + S01, 332 fb^-1)
    B = []
    for sct, pre in (("Z0", "C01_atlas_mu"), ("Z1160", "C01_atlas_mu"), ("A580", "C01_atlas_A580_mu")):
        for mu in (0, 20, 50, 60):
            f = f"{T}/S01_{pre}{mu}.csv"
            if not os.path.exists(f): continue
            s = pd.read_csv(f); s = s[s.sct == sct]
            if not len(s): continue
            N = float(s.N_bkg_332fb.sum()); nf = int(s.final.sum()); ul = float(s.N_UL95_332fb_if_zero.max()) if nf == 0 else np.nan
            B.append(dict(sct=sct, mu=mu, n_final=nf, N_bkg_332fb=N, N_UL95_332fb_if_zero=ul, source=os.path.basename(f)))
    B = pd.DataFrame(B); rows = []
    for b in B.itertuples():
        for L in LUMIS:
            # 2026-11-17 (user): the background value is the central MC estimate (b = 0 when no MC photon passes); the MC 95% upper limit is used only
            # for the systematic variant "UL if 0 passed (systematic)". Columns b_used / s_excl / s_disc are the central ones; *_UL the variant.
            Nb = b.N_bkg_332fb * L / 332.0; bul = Nb if b.n_final else b.N_UL95_332fb_if_zero * L / 332.0
            B.loc[b.Index, f"N_bkg_{L:g}fb"] = Nb; B.loc[b.Index, f"b_used_{L:g}fb"] = Nb; B.loc[b.Index, f"s_excl_{L:g}fb"] = s95(Nb); B.loc[b.Index, f"s_disc_{L:g}fb"] = s5(Nb)
            B.loc[b.Index, f"b_UL_{L:g}fb"] = bul; B.loc[b.Index, f"s_excl_UL_{L:g}fb"] = s95(bul)
            for ch in ("colored", "EW"):
                rows += reach_rows(G, ch, b.sct, L, s95(Nb), s5(Nb), dict(variant="central b", mu=b.mu, N_bkg=round(Nb, 3), b_used=round(Nb, 3)))
                rows += reach_rows(G, ch, b.sct, L, s95(bul), s5(Nb), dict(variant="UL if 0 passed (systematic)", mu=b.mu, N_bkg=round(Nb, 3), b_used=round(bul, 3)))
    B.to_csv(f"{T}/R01_background.csv", index=False); print(B.round(3).to_string(index=False))
    RB = pd.DataFrame(rows).sort_values(["variant", "channel", "sct", "lumi_fb", "contour", "mu"]); RB.to_csv(f"{T}/R01_reach_with_background.csv", index=False)
    print(RB[RB.lumi_fb == 332].to_string(index=False)); print("R01_EXIT=0")
