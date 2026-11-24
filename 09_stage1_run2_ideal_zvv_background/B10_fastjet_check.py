#!/usr/bin/env python3
"""09 / B10 check (2026-11-22): our numba anti-kT (monojet_selection.antikt) vs fastjet 3.5.2 (pip), anti-kT R = 0.4, E-scheme, same inputs
(status-1 particles without neutrinos, muons and quirks), on 100 Z(nunu)+jet events (chunk 01) and 100 signal events (B05 EW 800 GeV).
Compared per event: every jet with pT > 5 GeV (pT, matched in order) and the number of jets with pT > 30 GeV, |eta| < 2.8. Env g4."""
import math, numpy as np, fastjet, paths09 as P, monojet_selection as M
def inputs(ev, quirk=9000011):
    V = [(px, py, pz, E) for (pdg, px, py, pz, E, st, pv, endv) in ev["parts"].values()
         if st == 1 and abs(pdg) not in M.NEUTRINOS and abs(pdg) != quirk and abs(pdg) != 13]
    return np.array(V, float).reshape(-1, 4)
jd = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
for name, path in (("Zvv", f"{P.SAMPLES['zvv']['runs']}/chunk_01/Events/run_b01/tag_1_pythia8_events.hepmc.gz"), ("signal", P.B05_HEPMC)):
    dpt, nmis, nev, nj = [], 0, 0, 0
    for ev in M.iter_full(path, 100):
        V = inputs(ev); J = M.antikt(V[:, 0].copy(), V[:, 1].copy(), V[:, 2].copy(), V[:, 3].copy(), 0.4)
        ours = np.hypot(J[:, 0], J[:, 1]); oe = np.array([math.asinh(j[2] / max(math.hypot(j[0], j[1]), 1e-12)) for j in J])
        cs = fastjet.ClusterSequence([fastjet.PseudoJet(*v) for v in V], jd); F = fastjet.sorted_by_pt(cs.inclusive_jets(5.0))
        fpt = np.array([j.pt() for j in F]); fe = np.array([j.eta() for j in F])
        a = ours[ours > 5.0]
        if len(a) != len(fpt): nmis += 1
        else: dpt += list(np.abs(a - fpt) / fpt)
        n30o = int(((ours > 30) & (np.abs(oe) < 2.8)).sum()); n30f = int(((fpt > 30) & (np.abs(fe) < 2.8)).sum())
        nj += int(n30o != n30f); nev += 1
    print(f"{name}: {nev} events; events with a different number of jets (pT > 5): {nmis}; max |dpT|/pT of matched jets {max(dpt) if dpt else float('nan'):.2e}; "
          f"events with different N(jets pT>30, |eta|<2.8): {nj}")
