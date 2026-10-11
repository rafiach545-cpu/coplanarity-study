#!/usr/bin/env python3
"""Which particles form the 'quirk pair' in the trigger pT(QQ) > 200 GeV? Read directly from the 2000-event HepMC files.
Per matched event: (a) hard-process quirks (Pythia status 23), (b) final-state quirks used by the analysis (EW: status 1, |pdg| = 9000011;
colored: status 1 R-hadrons, mass within 30 GeV of 1800), (c) MET-like recoil = |sum pT| of all other visible status-1 particles
(neutrinos excluded, |eta| < 4.9). Checks that (b) reproduces the stored trigger decisions. Output: tables/trigger_pair_definition.csv"""
import gzip, math, numpy as np, pandas as pd
from scipy import stats
RUN = "/home/rafia/hep_tools/quirk_2000_fresh_regen_runs"; EV = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events"
CFG = {"EW2000": ("EW_800GeV_L4keV", 9000011, 800.0, True), "COL2000": ("colored_1800GeV_L2keV", 1000006, 1800.0, False)}
NU = {12, 14, 16}
def parse(tag, qid, mq, exact):
    rows, ev = [], None
    def flush():
        if ev is None: return
        h = [p for p in ev if abs(p[0]) == qid and p[5] == 23]
        f = [p for p in ev if p[5] == 1 and ((abs(p[0]) == qid) if exact else abs(p[4] - mq) < 30)]
        vis = [p for p in ev if p[5] == 1 and p not in f and abs(p[0]) not in NU]
        def ptsum(ps): return math.hypot(sum(p[1] for p in ps), sum(p[2] for p in ps)) if ps else float("nan")
        rv = [p for p in vis if (pt := math.hypot(p[1], p[2])) > 0 and abs(math.asinh(p[3] / pt)) < 4.9]
        rows.append(dict(n_hard=len(h), n_final=len(f), pt_hard=ptsum(h) if len(h) == 2 else np.nan, pt_final=ptsum(f) if len(f) == 2 else np.nan,
                         met_recoil=ptsum(rv), n_fsr_photons=sum(1 for p in vis if p[0] == 22)))
    for ln in gzip.open(f"{RUN}/{tag}/Events/run_fresh/tag_1_pythia8_events.hepmc.gz", "rt"):
        if ln.startswith("E "): flush(); ev = []
        elif ln.startswith("P "):
            x = ln.split(); ev.append((int(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[7]), int(x[8])))
    flush(); return pd.DataFrame(rows)
out = []
for s, (tag, qid, mq, exact) in CFG.items():
    d = parse(tag, qid, mq, exact); M = pd.read_csv(f"{EV}/{tag}/matched_events_full.csv"); assert len(d) == len(M), (s, len(d), len(M))
    stored = M.trigger_proxy_pass.astype(str) == "True"; assert np.allclose(d.pt_final.values, M.quirk_pair_pt_gev.values, rtol=1e-6, equal_nan=True)
    assert ((d.pt_final > 200).values == stored.values).all()
    d.insert(0, "sample", s); out.append(d); n = len(d)
    print(f"== {s}: {n} matched events; hard quirks found in {int((d.n_hard==2).sum())}, final quirks in {int((d.n_final==2).sum())}; stored trigger reproduced by final-state pair: yes")
    r = d.pt_final / d.pt_hard; print(f"   pT(pair) final/hard: median {r.median():.4f}, 16-84% {r.quantile(.16):.4f}-{r.quantile(.84):.4f}; events with |diff| > 5 GeV: {int(((d.pt_final-d.pt_hard).abs()>5).sum())}")
    for lab, col in (("hard-process quirk pair", "pt_hard"), ("final-state pair (analysis)", "pt_final"), ("MET-like recoil of visible particles", "met_recoil")):
        k = int((d[col] > 200).sum()); lo, hi = stats.binomtest(k, n).proportion_ci(.95, "wilson")
        print(f"   eps_trig with {lab:38s}: {k}/{n} = {k/n:.3f} [{lo:.3f}, {hi:.3f}]")
    print(f"   photons among visible final-state particles per event (median): {d.n_fsr_photons.median():.0f}")
pd.concat(out).to_csv("../tables/trigger_pair_definition.csv", index=False)
