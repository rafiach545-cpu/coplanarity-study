#!/usr/bin/env python3
"""Stage 2, step 13: why does eps_trig depend on mass differently for colored and EW? Two checks on the existing samples (13 and 13.6 TeV, every mass point).
(1) Production channel. (a) MG5 cross section of every subprocess directory (HTML/<run>/results.html, before MLM matching): gg, qqbar, qg initial states
    (P0 = 0 extra jet, P1 = 1 extra jet). (b) The same on the matched events that the analysis uses: the two incoming hard partons of every HepMC event
    (Pythia8 status 21) and the number of extra hard partons (status 23, not quirks).
(2) pT of the quirk pair (the trigger variable, eps_trig = fraction with pT(QQbar) > 200 GeV, checked equal to trigger_proxy_pass) from the extracted event
    CSVs (same events, hepmc_event_idx = position in the HepMC file): median, quartiles, mean, eps_trig, per mass point and per production channel.
Output: S2_production_channels.csv, S2_pair_pt.csv, S2_pair_pt_hist.csv (20 GeV bins, 0-1000 GeV, unit-normalised). Run with /home/rafia/venvs/f6fast/bin/python."""
import os, re, glob, gzip, multiprocessing as mp, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); REP = f"{HERE}/../../05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03"
RUNS = {"13": ("/home/rafia/hep_tools/figure6_full_v1_runs", "run_fig6", f"{REP}/fig6/inputs"), "13.6": ("/home/rafia/hep_tools/S2_13p6TeV_runs", "run_s2", f"{HERE}/inputs")}
TAGS = [f"colored_{m}gev" for m in (600, 900, 1200, 1500, 1800, 2100, 2400)] + [f"EW_{m}gev" for m in (100, 200, 400, 600, 800, 1000)]
QUIRK = lambda pid: abs(pid) > 1000000
def cls(a, b):
    g = (a == 21) + (b == 21); return {2: "gg", 1: "qg", 0: "qqbar"}[g]
def mg5_xsec(E, tag):
    base, run, _ = RUNS[E]; ban = glob.glob(f"{base}/{tag}/Events/{run}/*_banner.txt"); name = os.path.basename(ban[0]).split("_tag_")[0]
    h = re.sub(r"<[^>]*>", " ", open(f"{base}/{tag}/HTML/{name}/results.html").read()); out = {}
    for d, x, e in re.findall(r"SubProcesses/(P\d_\w+)\s+([0-9.e+-]+)\s+([0-9.e+-]+)", h): out.setdefault(d, (float(x), float(e)))   # first table: per directory
    return name, out
def hepmc(args):
    E, tag = args; base, run, _ = RUNS[E]; rows = []; inc = []; n23 = 0; ev = -1
    with gzip.open(f"{base}/{tag}/Events/{run}/tag_1_pythia8_events.hepmc.gz", "rt") as f:
        for l in f:
            if l[0] == "E":
                if ev >= 0: rows.append((ev, *inc[:2], len(inc), n23))
                ev += 1; inc = []; n23 = 0
            elif l[0] == "P":
                s = l.split(); pid, stt = int(s[2]), int(s[8])
                if stt == 21: inc.append(pid)
                elif stt == 23 and not QUIRK(pid): n23 += 1
    rows.append((ev, *inc[:2], len(inc), n23))
    return E, tag, pd.DataFrame(rows, columns=["hepmc_event_idx", "in1", "in2", "n_in", "n_extra"])
wil = lambda k, n: stats.binomtest(int(k), int(n)).proportion_ci(0.6827, "wilson")

if __name__ == "__main__":
    jobs = [(E, t) for E in RUNS for t in TAGS if os.path.exists(f"{RUNS[E][0]}/{t}/Events/{RUNS[E][1]}/tag_1_pythia8_events.hepmc.gz")]
    with mp.Pool(10) as pool: HM = {(E, t): d for E, t, d in pool.imap_unordered(hepmc, jobs)}
    pc, pt, hist = [], [], []; bins = np.arange(0, 1001, 20)
    for E, t in jobs:
        ch, m = t.split("_")[0], int(t.split("_")[1][:-3]); d = HM[(E, t)]; assert (d.n_in == 2).all(), (E, t)
        ev = pd.read_csv(f"{RUNS[E][2]}/{t}_events.csv"); assert len(ev) == len(d) and (ev.hepmc_event_idx.values == d.hepmc_event_idx.values).all(), (E, t)
        ev = ev.merge(d, on="hepmc_event_idx"); ev["prod"] = [cls(a, b) for a, b in zip(ev.in1, ev.in2)]; x = ev.quirk_pair_pt_gev.values
        assert ((ev.trigger_proxy_pass.astype(str) == "True") == (x > 200)).all()
        run, xs = mg5_xsec(E, t); tot = sum(v[0] for v in xs.values())
        r = dict(sqrt_s_TeV=E, channel=ch, mass_gev=m, mg5_run=run, xsec_total_pb_prematch=tot, n_matched=len(ev))
        for k in ("gg", "qqbar", "qg"):
            ds = [dd for dd in xs if cls(*(21 if c == "g" else 1 for c in dd.split("_")[1][:2])) == k]
            r[f"prematch_frac_{k}"] = sum(xs[dd][0] for dd in ds) / tot
            n = int((ev["prod"] == k).sum()); lo, hi = wil(n, len(ev)); r.update({f"matched_n_{k}": n, f"matched_frac_{k}": n / len(ev), f"matched_frac_{k}_lo": lo, f"matched_frac_{k}_hi": hi})
        for d_ in sorted(xs): r[f"xsec_pb_{d_}"] = xs[d_][0]
        r["matched_frac_1extra"] = (ev.n_extra > 0).mean(); pc.append(r)
        for k in ("all", "gg", "qqbar", "qg"):
            v = x if k == "all" else x[ev["prod"].values == k]
            if len(v) == 0: continue
            q = np.percentile(v, [25, 50, 75]); kk = int((v > 200).sum()); lo, hi = wil(kk, len(v))
            se = 1.2533 * v.std(ddof=1) / np.sqrt(len(v))                       # standard error of the median (normal approximation)
            pt.append(dict(sqrt_s_TeV=E, channel=ch, mass_gev=m, production=k, n=len(v), pt_q25=q[0], pt_median=q[1], pt_median_err=se, pt_q75=q[2], pt_mean=v.mean(),
                           eps_trig=kk / len(v), eps_trig_lo=lo, eps_trig_hi=hi, pt_over_m_median=q[1] / m))
        h, _ = np.histogram(np.clip(x, 0, 999.9), bins); hist += [dict(sqrt_s_TeV=E, channel=ch, mass_gev=m, pt_lo=a, pt_hi=a + 20, frac=c / len(x)) for a, c in zip(bins[:-1], h)]
        print(E, t, f"matched gg/qq/qg = {r['matched_frac_gg']:.2f}/{r['matched_frac_qqbar']:.2f}/{r['matched_frac_qg']:.2f}", f"prematch {r['prematch_frac_gg']:.2f}/{r['prematch_frac_qqbar']:.2f}/{r['prematch_frac_qg']:.2f}",
              f"median pT {np.median(x):.0f}, eps_trig {np.mean(x > 200):.3f}", flush=True)
    srt = lambda D: D.sort_values(["channel", "sqrt_s_TeV", "mass_gev"])
    srt(pd.DataFrame(pc)).to_csv(f"{HERE}/S2_production_channels.csv", index=False); srt(pd.DataFrame(pt)).to_csv(f"{HERE}/S2_pair_pt.csv", index=False)
    srt(pd.DataFrame(hist)).to_csv(f"{HERE}/S2_pair_pt_hist.csv", index=False); print("S2_13_EXIT=0")
