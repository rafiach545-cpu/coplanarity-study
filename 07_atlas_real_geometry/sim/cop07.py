#!/usr/bin/env python3
"""07 coplanarity reconstruction with stations (decision D1, 2026-11-15).

The algorithm of arXiv:1708.02243 Sec. III C (implemented in 05_coplanarity_analysis/coplanarity_fit.py: seeding on the two outermost layers,
iterative outside-in fit, event selection by smallest Delta_s with Delta_w < 1 cm, Sec. IV multiplicity cut) is kept. Only the meaning of
"layer k" changes: layer k = station k of the plane's direction.

Stations (detector-level, no truth; D1, refined 2026-11-15): every hit gets a station from the straight line PV -> hit: the number of pixel
(SCT) elements this line crosses before reaching the hit, + 1, is the hit's pixel station 1-4 (SCT station 5-8); later elements get no station.
This is "the k-th measurement along the track" (ATLAS counts measurements on barrel layers and disks alike, R14 Table 1). A per-hit definition
is needed because in the barrel / end-cap transition the two tracks of one pair cross different elements as their k-th measurement (first
version with one element list per plane: no plane found at |eta| = 1.4 and 1.9 in T03 (e)).
The paper's algorithm (coplanarity_fit.seeding_and_iterative_fit, copied with only the seed-pair longitudinal cut generalised) then runs on
stations 1-8 as on layers 1-8. With the barrel only every hit's station is its layer, so the result must equal Stage 2 (test T05).
Limitation: straight line from the PV; strongly curved (low-pT) tracks can have other elements before the hit than the line."""
import math, numpy as np
import coplanarity_fit as cf


def station_list(d, pv, els):
    """Element names of stations 1-8 along PV + s d (d unit 3-vector, cm), or None."""
    hits = []
    for e in els:
        if e["kind"] == "barrel":
            a = d[0] ** 2 + d[1] ** 2
            if a < 1e-15: continue
            b = 2 * (pv[0] * d[0] + pv[1] * d[1]); c = pv[0] ** 2 + pv[1] ** 2 - e["r_cm"] ** 2; disc = b * b - 4 * a * c
            if disc < 0: continue
            s = (-b + math.sqrt(disc)) / (2 * a)
            if s > 0 and abs(pv[2] + s * d[2]) < e["half_cm"]: hits.append((s, e))
        else:
            if d[2] == 0: continue
            s = (e["z_cm"] - pv[2]) / d[2]
            if s <= 0: continue
            r = math.hypot(pv[0] + s * d[0], pv[1] + s * d[1])
            if e["rmin_cm"] <= r <= e["rmax_cm"]: hits.append((s, e))
    hits.sort(key=lambda t: t[0])
    pix = [e["name"] for s, e in hits if e["is_pixel"]][:4]; sct = [e["name"] for s, e in hits if not e["is_pixel"]][:4]
    return pix + sct if len(pix) == 4 and len(sct) == 4 else None


def _dphi(h1, h2):
    d = abs(math.atan2(h1[1], h1[0]) - math.atan2(h2[1], h2[0])); return min(d, 2 * math.pi - d)


def _mu_small(P, Q):
    """Smaller non-zero eigenvalue of p p^T + q q^T for rows of P (n,3) against rows of Q (m,3): (|p|^2+|q|^2 - sqrt((|p|^2-|q|^2)^2 + 4 (p.q)^2)) / 2."""
    pp = (P * P).sum(1)[:, None]; qq = (Q * Q).sum(1)[None, :]; pq = P @ Q.T
    return 0.5 * (pp + qq - np.sqrt(np.maximum((pp - qq) ** 2 + 4 * pq * pq, 0.0)))


def _pairs(hs, dlv, dphi_max, dlong_max):
    """All (hs[i], hs[j]), i < j, with Delta_phi < dphi_max and dlv(i, j) < dlong_max, in the order of the original double loop."""
    n = len(hs)
    if n < 2: return []
    X = np.array(hs, float); ph = np.arctan2(X[:, 1], X[:, 0]); d = np.abs(ph[:, None] - ph[None, :]); d = np.minimum(d, 2 * np.pi - d)
    m = np.triu((d < dphi_max), 1)
    I, J = np.nonzero(m)
    if len(I) == 0: return []
    ok = dlv(I, J) < dlong_max
    return [(hs[i], hs[j]) for i, j in zip(I[ok], J[ok])]


def _seed_combos(p8, p7, ds_seed, dw_seed, margin=1e-6):
    """(i8, i7) index combinations, in the original row-major order, that can pass the 4-hit seed cuts; every other combination provably fails.
    Step 1 (Weyl): for the first hits a (station 8) and c (station 7), Delta_w^2 >= mu_small(a, c) / 3 (lambda_2(A + B) >= lambda_2(A) for B PSD,
      A = (a a^T + c c^T) / 3), and mu_small >= |a|^2 |c|^2 sin^2(alpha) / (|a|^2 + |c|^2) >= (m^2 / 2) sin^2(alpha), m = min(|a|, |c|). So a passing
      combination has sin(alpha) < sqrt(6) dw_seed / m, i.e. alpha < asin(...) or alpha > pi - asin(...). Candidates: unit vectors u_a within the
      chord 2 sin(alpha_max / 2) of u_c or of -u_c (KD-tree ball query, alpha_max from the smallest |a|, |c| in the event: a superset), then the
      exact condition mu_small < 3 dw_seed^2.
    Step 2: the seed fit (T = X^T X / 3, eigenvalues) for all remaining combinations at once; combinations with Delta_s or Delta_w above the cut
      by more than a relative `margin` (1e-6, far above rounding differences of ~1e-15) are dropped. The survivors are refit exactly (cf.fit_plane)
      by the caller with the original cuts."""
    A8 = np.array([q[0] for q in p8], float); A7 = np.array([q[0] for q in p7], float)
    n8 = np.linalg.norm(A8, axis=1); n7 = np.linalg.norm(A7, axis=1)
    t8 = np.arccos(np.clip(A8[:, 2] / n8, -1, 1)); t7 = np.arccos(np.clip(A7[:, 2] / n7, -1, 1))
    from scipy.spatial import cKDTree
    U8, U7 = A8 / n8[:, None], A7 / n7[:, None]
    amax = math.asin(min(1.0, math.sqrt(6.0) * dw_seed / min(n7.min(), n8.min()))) + 1e-9   # largest allowed angle over all combinations
    rad = 2.0 * math.sin(min(amax, math.pi / 2) / 2.0) * (1 + 1e-9)                             # chord length of that angle on the unit sphere
    tree = cKDTree(U8); II, JJ = [], []
    for sgn in (1.0, -1.0):                                                    # parallel and anti-parallel neighbours
        for j, lst in enumerate(tree.query_ball_point(sgn * U7, rad)):
            if lst: II.append(np.asarray(lst, np.int64)); JJ.append(np.full(len(lst), j, np.int64))
    if not II: return []
    I = np.concatenate(II); J = np.concatenate(JJ)
    a, c = A8[I], A7[J]; aa = (a * a).sum(1); cc = (c * c).sum(1); ac = (a * c).sum(1)
    mu = 0.5 * (aa + cc - np.sqrt(np.maximum((aa - cc) ** 2 + 4 * ac * ac, 0.0)))
    sel = mu < 3.0 * dw_seed ** 2; I, J = I[sel], J[sel]
    if len(I) == 0: return []
    # no duplicates: alpha_max < pi/2 here, so no u_a lies within alpha_max of both u_c and -u_c; restore the original row-major order
    assert amax < math.pi / 2
    o = np.argsort(I * len(A7) + J, kind="stable"); I, J = I[o], J[o]
    P8 = np.array([[q[0], q[1]] for q in p8], float); P7 = np.array([[q[0], q[1]] for q in p7], float)
    X = np.concatenate([P8[I], P7[J]], axis=1)                                 # (M, 4, 3): the 4 seed hits in the original order
    T = np.einsum("mai,maj->mij", X, X) / 3.0; ev = np.linalg.eigvalsh(T)
    ds = np.sqrt(np.maximum(ev[:, 0], 0)); dw = np.sqrt(np.maximum(ev[:, 1], 0))
    keep = (ds < ds_seed * (1 + margin)) & (dw < dw_seed * (1 + margin))
    return list(zip(I[keep], J[keep]))


def seeding_and_iterative_fit(hbl, dlong, ds_seed=0.05, dw_seed=1.0, ds_iter=0.05, dw_iter=1.0, growth=3.0, dphi_max=0.1, dlong_max=2.0):
    """Copy of coplanarity_fit.seeding_and_iterative_fit with one change: the seed-pair longitudinal difference is dlong[k](a, b) for station k
    (barrel: |dz|, the original; disk: |dr|). Same thresholds, same loop order, same results. Two speed-ups that cannot change any result:
    (1) seed pre-filter _seed_combos (Weyl bound + angular window + batched seed fit with a 1e-6 margin): it removes only combinations that
        the original seed cuts reject; the survivors go through the original fit and cuts.
    (2) the iterative-fit eligibility cuts are evaluated with numpy for all hits of a station at once; the eligible hits are then processed in
        the original order (stable sort by |x.n1|, ties in input order)."""
    def pairs(k):
        hs = hbl.get(k, [])
        if hasattr(dlong[k], "vec"): return _pairs(hs, dlong[k].vec, dphi_max, dlong_max)   # vectorised: same conditions, same order
        return [(a, b) for i, a in enumerate(hs) for b in hs[i + 1:] if _dphi(a, b) < dphi_max and dlong[k](a, b) < dlong_max]
    p8, p7 = pairs(8), pairs(7)
    cands = []
    if p8 and p7:
        for i8, i7 in _seed_combos(p8, p7, ds_seed, dw_seed):
            sh = list(p8[i8]) + list(p7[i7]); fit = cf.fit_plane(np.array(sh))
            if fit["delta_s"] >= ds_seed or fit["delta_w"] >= dw_seed: continue
            if not np.all(np.array(sh) @ fit["n3"] > 0): continue
            cands.append({"hits": sh, "layers": [8, 8, 7, 7], "fit": fit})
    H = {k: np.array(hbl.get(k, []), float).reshape(-1, 3) for k in range(1, 7)}
    final = []
    for c in cands:
        cur, curl = list(c["hits"]), list(c["layers"])
        for k in range(6, 0, -1):
            fit = cf.fit_plane(np.array(cur)); X = H[k]
            if len(X) == 0: continue
            a3, a1, a2 = X @ fit["n3"], np.abs(X @ fit["n1"]), np.abs(X @ fit["n2"])
            idx = np.nonzero((a3 > 0) & (a1 < ds_iter) & (a2 < dw_iter))[0]
            idx = idx[np.argsort(a1[idx], kind="stable")]
            hk = hbl[k]
            for j in idx:
                h = hk[j]; tf = cf.fit_plane(np.array(cur + [h]))
                if tf["delta_s"] <= growth * fit["delta_s"] and tf["delta_w"] <= growth * fit["delta_w"]:
                    cur = cur + [h]; curl.append(k); fit = tf
        final.append({"hits": cur, "layers": curl, "fit": cf.fit_plane(np.array(cur))})
    return final


def _stations(hits, origin, els):
    """Per hit: station index from the straight line PV -> hit. Returns list of ints (0 = beyond station 8)."""
    if not hits: return []
    X = np.array([[h["x"] - origin[0], h["y"] - origin[1], h["z"] - origin[2]] for h in hits]); L = np.linalg.norm(X, axis=1); U = X / L[:, None]
    npix = np.zeros(len(hits), int); nsct = np.zeros(len(hits), int); pv = origin
    for e in els:                                                    # count elements crossed strictly before the hit (path < L - 1e-6 cm)
        if e["kind"] == "barrel":
            a = U[:, 0] ** 2 + U[:, 1] ** 2; b = 2 * (pv[0] * U[:, 0] + pv[1] * U[:, 1]); c = pv[0] ** 2 + pv[1] ** 2 - e["r_cm"] ** 2
            disc = b * b - 4 * a * c; ok = (a > 1e-15) & (disc >= 0)
            sl = np.where(ok, (-b + np.sqrt(np.where(disc >= 0, disc, 0))) / np.where(a > 1e-15, 2 * a, 1), -1.0)
            hit = ok & (sl > 0) & (sl < L - 1e-6) & (np.abs(pv[2] + sl * U[:, 2]) < e["half_cm"])
        else:
            with np.errstate(divide="ignore", invalid="ignore"):
                sl = np.where(U[:, 2] != 0, (e["z_cm"] - pv[2]) / U[:, 2], -1.0)
            r = np.hypot(pv[0] + sl * U[:, 0], pv[1] + sl * U[:, 1])
            hit = (sl > 0) & (sl < L - 1e-6) & (r >= e["rmin_cm"]) & (r <= e["rmax_cm"])
        if e["is_pixel"]: npix += hit
        else: nsct += hit
    out = []
    for k, h in enumerate(hits):
        if h["is_pixel"]: st = npix[k] + 1; out.append(st if st <= 4 else 0)
        else: st = nsct[k] + 1; out.append(4 + st if st <= 4 else 0)
    return out


def reconstruct(hits, origin, els, kind_of):
    """hits: merged hit dicts (lab frame, cm). origin: PV (lab). Hits are grouped by station (per hit, D1) and the paper's algorithm runs
    on stations 1-8 exactly as on layers 1-8. Seed-pair longitudinal cut: |dz| < 2 cm for two barrel hits (the paper), |dr| < 2 cm for two disk
    hits, both for a barrel-disk pair. Returns (candidates, hits_by_station, element of every hit tuple)."""
    st = _stations(hits, origin, els); hbl = {k: [] for k in range(1, 9)}; kind, elem = {}, {}
    for h, k in zip(hits, st):
        if k == 0: continue
        t = (h["x"] - origin[0], h["y"] - origin[1], h["z"] - origin[2]); hbl[k].append(t); kind[t] = kind_of[h["layer"]]; elem[t] = h["layer"]
    def make(k):
        hs = hbl[k]
        def dl(a, b):
            ka, kb = kind[a], kind[b]; dz = abs(a[2] - b[2])
            dr = abs(math.hypot(a[0] + origin[0], a[1] + origin[1]) - math.hypot(b[0] + origin[0], b[1] + origin[1]))
            return dz if ka == kb == "barrel" else (dr if ka == kb == "disk" else max(dz, dr))
        if hs:
            X = np.array(hs, float); Z = X[:, 2]; R = np.hypot(X[:, 0] + origin[0], X[:, 1] + origin[1]); B = np.array([kind[t] == "barrel" for t in hs])
            def vec(I, J):
                dz = np.abs(Z[I] - Z[J]); dr = np.abs(R[I] - R[J]); bb = B[I] & B[J]; dd = ~B[I] & ~B[J]
                return np.where(bb, dz, np.where(dd, dr, np.maximum(dz, dr)))
            dl.vec = vec
        return dl
    cands = seeding_and_iterative_fit(hbl, {k: make(k) for k in range(1, 9)})
    for c in cands: c["stations"] = [sorted({elem[t] for t, l in zip(c["hits"], c["layers"]) if l == k}) for k in range(1, 9)]
    return cands, hbl


def analyse(hits, origin, els):
    kind_of = {e["name"]: e["kind"] for e in els}
    cands, by = reconstruct(hits, origin, els, kind_of)
    w = cf.select_reconstructed_plane(cands)
    mult = cf.check_hit_multiplicity(w["layers"]) if w else False
    ds = w["fit"]["delta_s"] if w else np.nan; dw = w["fit"]["delta_w"] if w else np.nan
    best = max((len(set(c["layers"])) for c in cands), default=0)
    return dict(n_hits=len(hits), n_candidates=len(cands), best_layers=best, plane=w is not None, ds=ds, dw=dw, mult=bool(mult),
                dw_pass=bool(w is not None and dw < 1.0), ds_pass=bool(w is not None and ds < 0.01),
                final=bool(w is not None and mult and ds < 0.01), winner_layers=str(sorted(w["layers"])) if w else "",
                winner_stations="|".join("+".join(x) for x in w["stations"]) if w else ""), w
