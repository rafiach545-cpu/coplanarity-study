"""09 step B10 (2026-11-22): truth-level lepton veto and monojet selection, after ATLAS PRD 103 (2021) 112006 (arXiv:2102.10874), Sec. 4-5.
Applied to the MG5 + Pythia8 HepMC2 files (background chunks and signal), one row per event. Nominal selection:
  MET > 200 GeV (truth: vector sum of status-1 neutrinos, plus the status-1 quirks for the signal: they reach no calorimeter)
  electron veto: prompt e, pT > 7 GeV, |eta| < 2.47
  muon veto:     prompt mu, pT > 7 GeV, |eta| < 2.5
  tau veto:      prompt hadronic tau, visible pT > 20 GeV, |eta_vis| < 2.5 excluding 1.37 < |eta_vis| < 1.52
  leading jet pT > 150 GeV, |eta| < 2.4;  at most 4 jets with pT > 30 GeV, |eta| < 2.8
  dphi(jet, MET) > 0.4 for every such jet (> 0.6 if 200 < MET <= 250 GeV)
Variation (not nominal): photon veto, prompt photon pT > 10 GeV, |eta| < 2.37.
Definitions (truth level, our choices, written before any result):
  prompt = no hadron (|pdg| >= 100, i.e. meson or baryon) among the ancestors;  the tau is the last tau copy before its decay;
  hadronic tau = no e or mu among its decay products; visible = its stable descendants without neutrinos;
  jets = anti-kT R = 0.4 (E-scheme, rapidity-phi), inputs all status-1 particles except neutrinos, muons and quirks (ATLAS truth-jet inputs).
The anti-kT here is our own numba code (fastjet is not in the envs); it is the exact N^2 algorithm, to be cross-checked with fastjet.
Usage: python monojet_selection.py <hepmc> <out.csv> [--max N] [--quirk-pdg 9000011]"""
import gzip, sys, math, argparse, numpy as np
from numba import njit

NEUTRINOS = {12, 14, 16}


@njit(cache=True)
def antikt(px, py, pz, E, R):
    """Exact anti-kT (E-scheme). Returns jets as (n, 4) array px, py, pz, E, sorted by pT (descending)."""
    n = len(px); P = np.empty((n, 4)); alive = np.ones(n, dtype=np.bool_)
    y = np.empty(n); phi = np.empty(n); ipt2 = np.empty(n)
    for i in range(n):
        P[i, 0], P[i, 1], P[i, 2], P[i, 3] = px[i], py[i], pz[i], E[i]
    def kin(i):
        pt2 = P[i, 0] ** 2 + P[i, 1] ** 2
        ipt2[i] = 1.0 / max(pt2, 1e-300); phi[i] = math.atan2(P[i, 1], P[i, 0])
        ee, zz = P[i, 3], P[i, 2]
        y[i] = 0.5 * math.log(max(ee + zz, 1e-300) / max(ee - zz, 1e-300)) if ee > abs(zz) else (1e9 if zz > 0 else -1e9)
    for i in range(n): kin(i)
    R2 = R * R; nn = np.full(n, -1); dnn = np.full(n, 1e300)
    def dij(i, j):
        dp = abs(phi[i] - phi[j])
        if dp > math.pi: dp = 2 * math.pi - dp
        return min(ipt2[i], ipt2[j]) * ((y[i] - y[j]) ** 2 + dp * dp) / R2
    def find_nn(i):
        best = 1e300; bj = -1
        for j in range(n):
            if j != i and alive[j]:
                d = dij(i, j)
                if d < best: best = d; bj = j
        nn[i] = bj; dnn[i] = best
    for i in range(n): find_nn(i)
    jets = np.zeros((n, 4)); nj = 0; left = n
    while left > 0:
        bi = -1; bd = 1e300; beam = True
        for i in range(n):
            if alive[i]:
                if ipt2[i] < bd: bd = ipt2[i]; bi = i; beam = True
                if nn[i] >= 0 and dnn[i] < bd: bd = dnn[i]; bi = i; beam = False
        if beam:
            jets[nj] = P[bi]; nj += 1; alive[bi] = False; left -= 1; gone = bi; merged = -1
        else:
            j = nn[bi]
            for c in range(4): P[bi, c] += P[j, c]
            alive[j] = False; left -= 1; kin(bi); gone = j; merged = bi
        for k in range(n):
            if not alive[k]: continue
            if k == merged or nn[k] == gone or nn[k] == merged: find_nn(k)
            elif merged >= 0:
                d = dij(k, merged)
                if d < dnn[k]: dnn[k] = d; nn[k] = merged
    jets = jets[:nj]; pt = np.sqrt(jets[:, 0] ** 2 + jets[:, 1] ** 2)
    return jets[np.argsort(-pt)]


def _eta(px, py, pz):
    pt = math.hypot(px, py); return math.asinh(pz / pt) if pt > 0 else math.copysign(1e9, pz)


def iter_full(path, max_events=None):
    """HepMC2 IO_GenEvent with the graph: per event, particles {barcode: (pdg, px, py, pz, E, status, prod_vtx, end_vtx)}, vertex -> incoming."""
    op = gzip.open if path.endswith(".gz") else open; ev = None; n = 0; cur_v = None; orph = 0
    with op(path, "rt") as f:
        for line in f:
            t = line[0]
            if t == "E":
                if ev is not None:
                    yield ev; n += 1
                    if max_events and n >= max_events: return
                p = line.split(); ev = dict(number=int(p[1]), parts={}, vin={})
            elif t == "V":
                p = line.split(); cur_v = int(p[1]); orph = int(p[7])
            elif t == "P":
                p = line.split(); bc = int(p[1]); endv = int(p[11])
                prod = None if orph > 0 else cur_v
                if orph > 0: orph -= 1
                ev["parts"][bc] = (int(p[2]), float(p[3]), float(p[4]), float(p[5]), float(p[6]), int(p[8]), prod, endv)
                if endv != 0: ev["vin"].setdefault(endv, []).append(bc)
    if ev is not None: yield ev


def select(ev, quirk_pdg=9000011, photon_veto=False):
    parts, vin = ev["parts"], ev["vin"]
    vout = {}
    for bc, q in parts.items():
        if q[6] is not None: vout.setdefault(q[6], []).append(bc)
    memo = {}
    def from_hadron(bc):
        stack, seen = [bc], set()
        while stack:
            b = stack.pop(); v = parts[b][6]
            if v is None or v in seen: continue
            seen.add(v)
            for a in vin.get(v, []):
                if a in memo:
                    if memo[a]: return True
                    continue
                pa = abs(parts[a][0])
                if pa >= 100 and pa not in (2212,) and not (1000000 <= pa): return True   # meson/baryon (beam protons have no production vertex)
                stack.append(a)
        return False
    def stable_desc(bc):
        out, stack = [], [bc]
        while stack:
            b = stack.pop(); q = parts[b]
            if q[5] == 1: out.append(b); continue
            stack += vout.get(q[7], [])
        return out
    mx = my = 0.0; vis = []; mu = []; el = []; ph = []
    for bc, (pdg, px, py, pz, E, st, pv, endv) in parts.items():
        a = abs(pdg)
        if st != 1:
            continue
        if a in NEUTRINOS or a == quirk_pdg:
            mx += px; my += py; continue
        if a == 13: mu.append(bc)
        else: vis.append((px, py, pz, E))
        if a == 11: el.append(bc)
        if a == 22: ph.append(bc)
    met = math.hypot(mx, my); metphi = math.atan2(my, mx)
    pt = lambda q: math.hypot(q[1], q[2])
    r = dict(event=ev["number"], met=met)
    r["n_e"] = sum(1 for b in el if pt(parts[b]) > 7 and abs(_eta(*parts[b][1:4])) < 2.47 and not from_hadron(b))
    r["n_mu"] = sum(1 for b in mu if pt(parts[b]) > 7 and abs(_eta(*parts[b][1:4])) < 2.5 and not from_hadron(b))
    ntau = 0
    for bc, q in parts.items():
        if abs(q[0]) != 15 or q[5] == 1: continue
        if any(abs(parts[d][0]) == 15 for d in vout.get(q[7], [])): continue          # not the last copy
        if from_hadron(bc): continue
        desc = stable_desc(bc)
        if any(abs(parts[d][0]) in (11, 13) for d in desc): continue                    # leptonic tau
        v = np.sum([parts[d][1:5] for d in desc if abs(parts[d][0]) not in NEUTRINOS], axis=0) if desc else np.zeros(4)
        if np.ndim(v) == 0: continue
        ptv = math.hypot(v[0], v[1]); etv = abs(_eta(v[0], v[1], v[2])) if ptv > 0 else 99
        if ptv > 20 and etv < 2.5 and not (1.37 < etv < 1.52): ntau += 1
    r["n_tau"] = ntau
    r["n_gamma"] = sum(1 for b in ph if pt(parts[b]) > 10 and abs(_eta(*parts[b][1:4])) < 2.37 and not from_hadron(b))
    V = np.array(vis, dtype=float).reshape(-1, 4)
    J = antikt(V[:, 0].copy(), V[:, 1].copy(), V[:, 2].copy(), V[:, 3].copy(), 0.4) if len(V) else np.zeros((0, 4))
    jpt = np.hypot(J[:, 0], J[:, 1]); jeta = np.array([_eta(*j[:3]) for j in J]); jphi = np.arctan2(J[:, 1], J[:, 0])
    sel = (jpt > 30) & (np.abs(jeta) < 2.8)
    r["n_jet30"] = int(sel.sum()); r["j1_pt"] = float(jpt[0]) if len(jpt) else 0.0; r["j1_eta"] = float(jeta[0]) if len(jpt) else 0.0
    dphi = np.abs(np.angle(np.exp(1j * (jphi[sel] - metphi)))); r["min_dphi"] = float(dphi.min()) if len(dphi) else 9.0
    cut_dphi = 0.6 if met <= 250 else 0.4
    r["pass_met"] = met > 200; r["pass_lepveto"] = r["n_e"] == 0 and r["n_mu"] == 0 and r["n_tau"] == 0
    r["pass_jets"] = r["j1_pt"] > 150 and abs(r["j1_eta"]) < 2.4 and r["n_jet30"] <= 4
    r["pass_dphi"] = r["min_dphi"] > cut_dphi
    r["pass_monojet"] = r["pass_met"] and r["pass_lepveto"] and r["pass_jets"] and r["pass_dphi"]
    r["pass_monojet_gveto"] = r["pass_monojet"] and r["n_gamma"] == 0
    return r


if __name__ == "__main__":
    import pandas as pd
    a = argparse.ArgumentParser(); a.add_argument("hepmc"); a.add_argument("out"); a.add_argument("--max", type=int); a.add_argument("--quirk-pdg", type=int, default=9000011)
    A = a.parse_args()
    rows = [select(ev, A.quirk_pdg) for ev in iter_full(A.hepmc, A.max)]
    D = pd.DataFrame(rows); D.to_csv(A.out, index=False)
    print(f"{len(D)} events; " + ", ".join(f"{c} {D[c].mean():.3f}" for c in ["pass_met", "pass_lepveto", "pass_jets", "pass_dphi", "pass_monojet", "pass_monojet_gveto"]))
