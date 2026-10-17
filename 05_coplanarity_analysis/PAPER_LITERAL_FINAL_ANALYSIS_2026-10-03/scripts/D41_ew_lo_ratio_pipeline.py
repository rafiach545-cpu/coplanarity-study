#!/usr/bin/env python3
"""D41 (pre-registered: notes/D41_prereg.md, sha256 70d7d29e...): EW signal as parton-level QQ + 1 jet (pT(j) > 200 GeV), 2026-10-15.
Input: argv[1] = LHE(.gz) of p p > qe+ qe- j, ptj = 200, ickkw = 0, xqcut = 0 (MG5 3.7.3, 3000 events); argv[2] = output tag.
Per event i: quirk four-momenta from the LHE (qe- charge -1, qe+ +1; pT(QQ) = pT(j) > 200 GeV, checked); z0 ~ N(0, 4.5 cm) and the SCT r-phi draws
from SeedSequence([41, i]); for Lambda = 1..5 keV: production integrator (config: 300 steps/period, B = 2 T), first crossings, fiducial (P20
definition: all 16 first crossings inside the Ref. [27] lengths, t < 25 ns), reconstruction p18.reco, SCT z none, first crossing.
eps_trig = 1 for this sample by construction (the LO ratio is computed separately from sigma(B)/sigma(A)); eps_fid = fiducial / events.
Statistics: Wilson 95%, exact two-sided binomial p vs the paper; combined chi2 of the Lambda column with the event-level bootstrap correlation
(10 000 resamples, as D3b). Output: tables/D41_<tag>_per_event.csv, tables/D41_<tag>_summary.txt"""
import os, sys, gzip, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18); p4 = p18.p4
LAMS = (1, 2, 3, 4, 5); PAPER = {1: .11, 2: .41, 3: .65, 4: .72, 5: .74}; PAPER_FID = 0.28; MQ = p4.PAR["EW"][0]
def read_lhe(path):
    op = gzip.open if path.endswith(".gz") else open; ev, cur, inside = [], None, False
    for line in op(path, "rt"):
        if line.startswith("<event"): cur, inside, first = [], True, True; continue
        if line.startswith("</event"):
            q = {int(round(float(r[0]))): r for r in cur if abs(int(round(float(r[0])))) == 9000011}
            ev.append((np.array(q[9000011][6:9], float), np.array(q[-9000011][6:9], float))); inside = False; continue
        if inside:
            if first: first = False; continue                                  # event header line
            if line.strip().startswith("<"): continue
            cur.append(line.split())
    return ev
def fid_of(cr):
    f = {(c["quirk"], c["layer"]): c for c in cr if c["order"] == 0}
    return all((q, L) in f and abs(f[(q, L)]["z_lab"]) < p4.HALF[L] and f[(q, L)]["t_ns"] < p4.R["timing_ns"] for q in (1, 2) for L in range(1, 9))
def job(a):
    i, pm, pp = a                                                           # quirk 1 = qe- (charge -1), quirk 2 = qe+ (+1)
    rng = np.random.default_rng(np.random.SeedSequence([41, i])); z0 = rng.normal(0.0, p4.R["beamspot_cm"])
    g = {(q, L): rng.standard_normal(2) for q in (1, 2) for L in range(1, 9)}; out = []
    for lam in LAMS:
        try:
            _, tr = p4.tth.simulate_quirk_hits((*pm, np.sqrt(pm @ pm + MQ * MQ)), (*pp, np.sqrt(pp @ pp + MQ * MQ)), mass_gev=MQ, Lambda_gev=lam * 1e-6,
                                               B_tesla=p4.R["B_tesla"], charge1=-1.0, charge2=1.0, rng=np.random.default_rng(0), z0_cm=z0,
                                               max_layer_r_cm=p4.R["max_layer_r_cm"])
        except Exception as e:
            out.append(dict(event=i, lambda_keV=lam, fid=False, final=False, error=str(e)[:80])); continue
        cr = p18.all_crossings(tr); f = fid_of(cr); r = p18.reco(cr, z0, g, "Z0", i, "EW2000", True) if f else dict(final=False, ds=np.nan, dw=np.nan, plane=False)
        out.append(dict(event=i, lambda_keV=lam, fid=f, plane=r["plane"], final=r["final"], ds=r["ds"], dw=r["dw"], error=""))
    return out
def combined(fid, pas, L, rng):
    n = fid.sum(0); k = pas.sum(0); e = k / n; p0 = np.array([PAPER[l] for l in L]); N = len(fid); bs = np.empty((10000, len(L)))
    for b in range(10000):
        j = rng.integers(0, N, N); bs[b] = pas[j].sum(0) / fid[j].sum(0)
    C = np.cov(bs.T); r = e - p0; chi2 = float(r @ np.linalg.solve(C, r)); return chi2, float(stats.chi2.sf(chi2, len(L)))
if __name__ == "__main__":
    lhe, tag = sys.argv[1], sys.argv[2]
    if lhe.endswith(".csv"):                                                # sensitivity: showered sample B (shower driver CSV); trigger pT(QQ) > 200 GeV after the shower
        c = pd.read_csv(lhe); c = c[c.n_final_quirks == 2]; ev = []
        for r in c.itertuples():
            a1, a2 = np.array([r.px1, r.py1, r.pz1]), np.array([r.px2, r.py2, r.pz2]); ev.append((a1, a2) if r.pdg1 == 9000011 else (a2, a1))
        n_all = len(ev); ev = [e for e in ev if np.hypot(*(e[0] + e[1])[:2]) > 200.0]; print(f"showered: {n_all} events, {len(ev)} with pT(QQ) > 200 GeV after the shower", flush=True)
    else:
        ev = read_lhe(lhe)
    n = len(ev)
    ptqq = np.array([np.hypot(*(a + b)[:2]) for a, b in ev]); print(f"events {n}; pT(QQ) min {ptqq.min():.1f} GeV (all > 200: {bool((ptqq > 200).all())})", flush=True)
    import json; LOG = f"{HERE}/../logs/D41_{tag}_events.jsonl"; done = set()          # append-only checkpoint (one line per event); a rerun resumes
    if os.path.exists(LOG): done = {json.loads(l)[0]["event"] for l in open(LOG)}
    todo = [(i, a, b) for i, (a, b) in enumerate(ev) if i not in done]; print(f"done {len(done)}, to run {len(todo)}", flush=True)
    if os.environ.get("SUMMARY_ONLY"): todo = []                             # summary from the checkpoint only (does not touch a running job)
    with mp.Pool(int(os.environ.get("NWORKERS", 3)) if todo else 1, initializer=p4._init) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap(job, todo), 1):                         # events in order: the first N are usable at any time
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else str(v)) + "\n"); fh.flush()
            if k % 50 == 0: print(f"{k}/{len(todo)}", flush=True)
    d = pd.DataFrame([r for l in open(LOG) for r in json.loads(l)])
    if os.environ.get("NMAX"):                                               # summary on the first NMAX events (all must be finished)
        n = int(os.environ["NMAX"]); d = d[d.event < n]; assert d.event.nunique() == n, f"only {d.event.nunique()} of the first {n} events finished"
        tag = f"{tag}_first{n}"
    d = d.sort_values(["event", "lambda_keV"]); d.to_csv(f"{T}/D41_{tag}_per_event.csv", index=False); p4.CFG.write_provenance(f"{T}/D41_{tag}_per_event.csv", dict(lhe=lhe, prereg="notes/D41_prereg.md"))
    W = lambda k, n: stats.binomtest(int(k), int(n)).proportion_ci(0.95, "wilson"); out = [f"D41 {tag}: {n} events (LHE {lhe}); errors {int((d.error.astype(str) != '').sum())}"]
    piv = lambda c: d.pivot(index="event", columns="lambda_keV", values=c)[list(LAMS)].astype(bool).values
    fid, pas = piv("fid"), piv("final") & piv("fid")
    for j, lam in enumerate(LAMS):
        kf = int(fid[:, j].sum()); lo, hi = W(kf, n); pf = stats.binomtest(kf, n, PAPER_FID).pvalue
        kr = int(pas[:, j].sum()); lo2, hi2 = W(kr, kf); pr = stats.binomtest(kr, kf, PAPER[lam]).pvalue
        out.append(f"Lambda {lam} keV: eps_fid {kf}/{n} = {kf / n:.3f} [{lo:.3f}, {hi:.3f}] p(paper 0.28) = {pf:.2g} | eps_reco {kr}/{kf} = {kr / kf:.3f} [{lo2:.3f}, {hi2:.3f}] "
                   f"paper {PAPER[lam]} p = {pr:.2g} | Delta_s median {np.nanmedian(d[(d.lambda_keV == lam) & d.final.astype(bool)].ds) * 1e4:.1f} um")
    chi2, pc = combined(fid, pas, list(LAMS), np.random.default_rng(20261015)); out.append(f"combined chi2 (bootstrap correlation) = {chi2:.2f}, dof 5, p = {pc:.2g}  (production: 23.81, p = 2.4e-4)")
    kf4 = int(fid[:, 3].sum()); pf4 = stats.binomtest(kf4, n, PAPER_FID).pvalue; prod_fid_p = stats.binomtest(kf4, n, 62 / 186).pvalue
    e2 = pas[:, 1].sum() / fid[:, 1].sum()
    c1, c2, c3 = pf4 >= 0.05, pc >= 0.05, e2 <= 0.545
    rej = (prod_fid_p >= 0.05) and (abs(e2 - 0.645) < 0.10) and not c2
    verdict = "SUPPORT" if (c1 and c2 and c3) else ("REJECT" if rej else ("PARTIAL" if (c1 or c2 or c3) else "neither SUPPORT nor PARTIAL nor REJECT (no criterion met)"))
    out.append(f"criteria: (i) eps_fid (4 keV) vs 0.28 p = {pf4:.2g} -> {c1}; (ii) combined p = {pc:.2g} -> {c2}; (iii) eps_reco(2 keV) = {e2:.3f} <= 0.545 -> {c3}; "
               f"REJECT test: eps_fid vs production 0.333 p = {prod_fid_p:.2g}, |eps_reco(2) - 0.645| = {abs(e2 - 0.645):.3f} -> {rej}")
    out.append(f"VERDICT: {verdict}")
    # interim rule (notes/D41_prereg_addendum.md, sha256 e79f29e1...): a criterion is decided if its outcome is unchanged for the estimate +-2 sigma
    sg = lambda e, n: np.sqrt(e * (1 - e) / n); ef = kf4 / n; sf = sg(ef, n); nf2 = int(fid[:, 1].sum()); s2 = sg(e2, nf2)
    def cons(e, p0):
        return [stats.binomtest(int(round(min(max(x, 0), 1) * n)), n, p0).pvalue >= 0.05 for x in (e - 2 * sf, e, e + 2 * sf)]
    ci = cons(ef, PAPER_FID); d_i = len(set(ci)) == 1
    d_ii = (pc < 0.0027) or (pc > 0.32); d_iii = abs(e2 - 0.545) > 2 * s2
    cr = cons(ef, 62 / 186); d_rfid = len(set(cr)) == 1; d_r2 = abs(e2 - 0.545) > 2 * s2 and abs(e2 - 0.745) > 2 * s2
    out.append(f"interim rule: eps_fid {ef:.3f} +- {sf:.3f}; eps_reco(2 keV) {e2:.3f} +- {s2:.3f} (n_fid {nf2}); combined p {pc:.2g}")
    out.append(f"   decided: (i) {d_i} {ci} | (ii) {d_ii} | (iii) {d_iii} | REJECT parts: fid vs 0.333 {d_rfid} {cr}, 2 keV vs 0.645 +- 0.10 {d_r2}")
    all_dec = d_i and d_ii and d_iii and (d_rfid and d_r2 if verdict == "REJECT" or not (c1 or c2 or c3) else True)
    out.append(f"   INTERIM: {'verdict final at this N: ' + verdict if all_dec else 'not all criteria decided -> verdict waits for 3000 events'}")
    print("\n".join(out)); open(f"{T}/D41_{tag}_summary.txt", "w").write("\n".join(out) + "\n")
