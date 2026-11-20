"""09 step B04 (2026-11-19): ordinary-track cleaning for the ideal 8-layer tracker. No truth information is used.
Model: prompt helices in a uniform Bz from the primary vertex (hits are PV-relative, so the PV is the origin):
  - transverse plane: a circle through the origin, centre c (|c| = R); a point at radius r lies at azimuth alpha + sgn * acos(r / 2R),
    alpha = atan2(c), with the sign fixed by the seed hits;
  - longitudinal: z = tan(lambda) * s, with the transverse arc length s(r) = 2R asin(r / 2R) from the PV.
Algorithm (road search: pass 1 pixel seeds outward, pass 2 SCT seeds inward (v2), greedy, highest-|pT| first is not needed because hits are removed only after all tracks are found):
  1. Seeds: every pair (hit a on layer i, hit b on layer j) with (i, j) in SEED_LAYERS, |dphi| < DPHI_SEED, and |z_a / s_a - z_b / s_b|
     < DTANL_SEED (both hits compatible with one straight line in s-z from the PV).
  2. Circle through (0, 0), a, b; tan(lambda) from a least-squares line through the origin in (s, z).
  3. Every other layer: predicted point at the layer radius; the nearest unused hit with |r dphi| < W_RPHI[layer] and |dz| < W_Z[layer]
     is added; after each added hit the circle (algebraic least-squares fit through the origin) and tan(lambda) are refitted.
  4. A track is accepted with >= MIN_LAYERS layers (of 8) and >= MIN_SCT SCT layers and RMS transverse residual < MAX_RMS_RPHI_CM.
     Its hits are marked used (they cannot seed or join another track).
Displaced tracks (K_S, Lambda, conversions, if any) are NOT found by this PV-constrained search; their hits stay, as for the
"orphan" input of the ATLAS low-mu study (where the standard tracking also misses most of them). Quirk hits can be absorbed when a quirk
pair looks like a prompt helix (large Lambda: the two quirks move together); this is the signal loss that cleaning costs and is measured.
Returns the set of (layer, index) of hits to remove, and the found tracks."""
import numpy as np

SEED_LAYERS = [(2, 4), (1, 3), (3, 4), (1, 2)]        # pixel pairs; several so that one missing pixel hit does not lose the track
DPHI_SEED = 0.25                                     # rad between the two pixel hits (pT >~ 0.15 GeV between r = 3.3 and 12.3 cm)
DTANL_SEED = 0.05                                    # |z/s| difference (pixel z pitch 250-400 um over a few cm)
# v2 (2026-11-19): second pass with SCT seeds and an inward road. Reason: for stiff tracks (pT >~ 50 GeV) the pixel-only seed has a
# 9 cm lever arm, and the 50 um pixel pitch gives a curvature that is wrong by a large factor (a 100 GeV track fitted as 4-12 GeV), so the
# prediction at L5 misses by 1-5 mm and no SCT hit is found. With the PV constraint, two SCT hits at r = 30-51 cm fix the curvature well.
SCT_SEED_LAYERS = [(6, 8), (5, 7), (5, 8), (7, 8), (6, 7), (5, 6)]
DPHI_SEED_SCT = 0.10                                 # rad between the two SCT hits (pT >~ 0.5 GeV)
DTANL_SEED_SCT = 0.10                                # |z/r| difference (SCT z sigma 1.16 mm over 30-51 cm)
W_RPHI = {1: 0.03, 2: 0.03, 3: 0.03, 4: 0.03, 5: 0.10, 6: 0.08, 7: 0.06, 8: 0.06}   # cm, road half-width in r-phi
W_Z = {1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.6, 6: 0.6, 7: 0.6, 8: 0.6}               # cm (SCT z sigma 1.16 mm -> about 5 sigma)
MIN_LAYERS, MIN_SCT, MAX_RMS_RPHI_CM = 6, 2, 0.01
LAYER_ORDER = range(1, 9)


def _circle_fit(P):
    """Least-squares circle through the origin: x^2 + y^2 = 2 c.x  ->  linear in c. Returns centre c (2,)."""
    A = 2.0 * P[:, :2]; b = (P[:, :2] ** 2).sum(1)
    c, *_ = np.linalg.lstsq(A, b, rcond=None); return c


def _arc(r, R):
    return 2.0 * R * np.arcsin(np.clip(r / (2.0 * R), -1.0, 1.0))


def _predict(c, sgn, tanl, r):
    R = np.hypot(*c)
    if r > 2.0 * R: return None
    th = np.arctan2(c[1], c[0]) + sgn * np.arccos(np.clip(r / (2.0 * R), -1, 1))
    return np.array([r * np.cos(th), r * np.sin(th), tanl * _arc(r, R)])


def _sign(c, p):
    a = np.arctan2(c[1], c[0]); d = np.angle(np.exp(1j * (np.arctan2(p[1], p[0]) - a))); return 1.0 if d >= 0 else -1.0


def _fit(P):
    c = _circle_fit(P); R = np.hypot(*c); r = np.hypot(P[:, 0], P[:, 1]); s = _arc(r, R)
    tanl = float((s * P[:, 2]).sum() / max((s * s).sum(), 1e-12)); return c, tanl


def find_tracks(hbl):
    """hbl: {layer: list of (x, y, z)} PV-relative (cm). Returns (removed: set of (layer, idx), tracks: list of dict)."""
    H = {k: np.asarray(hbl.get(k, []), float).reshape(-1, 3) for k in LAYER_ORDER}
    RL = {k: (float(np.median(np.hypot(H[k][:, 0], H[k][:, 1]))) if len(H[k]) else None) for k in LAYER_ORDER}
    PHI = {k: np.arctan2(H[k][:, 1], H[k][:, 0]) for k in LAYER_ORDER}
    used = {k: np.zeros(len(H[k]), bool) for k in LAYER_ORDER}; tracks = []
    passes = [(i, j, DPHI_SEED, DTANL_SEED, list(LAYER_ORDER)) for i, j in SEED_LAYERS] + \
             [(i, j, DPHI_SEED_SCT, DTANL_SEED_SCT, list(LAYER_ORDER)[::-1]) for i, j in SCT_SEED_LAYERS]
    for (i, j, dphi_cut, dt_cut, order) in passes:
        if not len(H[i]) or not len(H[j]): continue
        ri, rj = np.hypot(H[i][:, 0], H[i][:, 1]), np.hypot(H[j][:, 0], H[j][:, 1])
        dphi = np.abs(np.angle(np.exp(1j * (PHI[i][:, None] - PHI[j][None, :]))))
        dt = np.abs(H[i][:, 2][:, None] / ri[:, None] - H[j][:, 2][None, :] / rj[None, :])
        for a, b in zip(*np.nonzero((dphi < dphi_cut) & (dt < dt_cut))):
            if used[i][a] or used[j][b]: continue
            pts = {i: a, j: b}; P = np.array([H[i][a], H[j][b]])
            c, tanl = _fit(P); sgn = _sign(c, H[j][b])
            for k in order:
                if k in pts or not len(H[k]): continue
                q = _predict(c, sgn, tanl, RL[k])
                if q is None: break
                d_rphi = RL[k] * np.abs(np.angle(np.exp(1j * (PHI[k] - np.arctan2(q[1], q[0])))))
                ok = (~used[k]) & (d_rphi < W_RPHI[k]) & (np.abs(H[k][:, 2] - q[2]) < W_Z[k])
                if not ok.any(): continue
                m = int(np.argmin(np.where(ok, d_rphi / W_RPHI[k] + np.abs(H[k][:, 2] - q[2]) / W_Z[k], np.inf)))
                pts[k] = m; P = np.array([H[l][pts[l]] for l in sorted(pts)]); c, tanl = _fit(P); sgn = _sign(c, P[-1])
            n_sct = sum(1 for l in pts if l >= 5)
            if len(pts) < MIN_LAYERS or n_sct < MIN_SCT: continue
            P = np.array([H[l][pts[l]] for l in sorted(pts)]); R = np.hypot(*c)
            res = [np.hypot(*P[n, :2]) * np.angle(np.exp(1j * (np.arctan2(P[n, 1], P[n, 0]) - np.arctan2(*_predict(c, sgn, tanl, np.hypot(*P[n, :2]))[1::-1]))))
                   for n in range(len(P))]
            if np.sqrt(np.mean(np.square(res))) > MAX_RMS_RPHI_CM: continue
            for l, n in pts.items(): used[l][n] = True
            tracks.append(dict(hits={l: int(n) for l, n in pts.items()}, pt_gev=0.3 * 2.0 * R / 100.0, tanl=tanl))
    removed = {(k, n) for k in LAYER_ORDER for n in np.nonzero(used[k])[0]}
    return removed, tracks
