#!/usr/bin/env python3
"""09 step B07 (2026-11-20): pT-threshold ordinary-track cleaning on the Z(nunu)+jets background (Stage 1 · Run 2 · Ideal).
The same events, hits and tracks as B03 (track_cleaning v2), but only the hits of found tracks with fitted pT < PT_CUT are removed, for
PT_CUT = 20, 50, 100 GeV and infinity (= B03 'orp', all found tracks). Reason: straight quirk tracks fit a helix well, so a chi2 cut cannot keep
them, while the cleaning loss of the signal (B05) comes from quirks that look like stiff prompt tracks.
Per input tag: c20 / c50 / c100 / cinf columns, as B03 (reconstruct() of B03, unchanged). Hits, seeds and RNG are exactly B03's (B03.analyse
is not rerun; the hit building below is the same code path with the same SeedSequence).
Output data/B07_events_c<cc>.csv. Usage (env hep): B07_cleaning_pt_threshold_bkg.py <chunk> [--workers 8]"""
import os, sys, time, argparse, numpy as np, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import B03_hits_and_planes as B                                                   # noqa: E402
PT_CUTS = [20.0, 50.0, 100.0, np.inf]


def tag(c):
    return "cinf" if np.isinf(c) else f"c{int(c)}"


def hits(chunk, ev):
    rng = np.random.default_rng(np.random.SeedSequence([B.SEED, chunk, ev["event"]]))
    z0 = rng.normal(0.0, B.BEAMSPOT_SIGMA_Z_CM); pv = np.array([0.0, 0.0, z0]); raw = []
    for j in range(len(ev["q"])):
        v = np.array([ev["vx"][j], ev["vy"][j], ev["vz"][j] + z0])
        raw += B.pileup_particle_hits(ev["px"][j], ev["py"][j], ev["pz"][j], ev["m"][j], ev["q"][j], v, f"p{j}", rng, B_tesla=2.0)
    merged, _ = B.overlay_and_merge(raw, [])
    hbl = {k: [] for k in range(1, 9)}; owner = {}
    for h in merged:
        x = B.vertex_relative_hits([(h["x"], h["y"], h["z"])], pv)[0]; hbl[B.LAYER_IDX[h["layer"]]].append(x)
        src = h.get("source_quirk_indices") or [h.get("quirk_index")]; owner[B.key(x)] = [int(str(s)[1:]) for s in src if s is not None]
    return hbl, owner


def analyse(job):
    chunk, ev = job; t0 = time.time(); hbl, owner = hits(chunk, ev)
    _, tracks = B.TC.find_tracks(hbl)
    row = dict(chunk=chunk, event=ev["event"], weight=ev["weight"], met=ev["met"], n_tracks=len(tracks),
               **{f"n_tracks_pt_lt_{tag(c)}": sum(1 for t in tracks if t["pt_gev"] < c) for c in PT_CUTS})
    for c in PT_CUTS:
        rem = {(l, n) for t in tracks if t["pt_gev"] < c for l, n in t["hits"].items()}
        h = {k: [x for n, x in enumerate(hbl[k]) if (k, n) not in rem] for k in range(1, 9)}
        r, _ = B.reconstruct(h, owner, ev, tag(c), chunk); row.update(r)
    row["t_s"] = time.time() - t0
    return row


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("chunk", type=int); a.add_argument("--workers", type=int, default=8)
    a.add_argument("--nmax", type=int, default=None); A = a.parse_args()
    C = pd.read_csv(f"{HERE}/data/B01_chunks.csv").set_index("chunk"); t0 = time.time()
    with Pool(A.workers) as P:
        R = list(P.imap(analyse, ((A.chunk, e) for e in B.H.iter_events(C.loc[A.chunk, "hepmc"], A.nmax)), chunksize=4))
    E = pd.DataFrame(R); E.to_csv(f"{HERE}/data/B07_events_c{A.chunk:02d}{'' if A.nmax is None else '_test'}.csv", index=False); m = E.met > 200
    print(f"B07 chunk {A.chunk}: {len(E)} events, MET > 200: {int(m.sum())}; " + "; ".join(
        f"{tag(c)}: SR {int((E[f'{tag(c)}_sr_pass'] & m).sum())}, mean hits {E[f'{tag(c)}_n_hits'].mean():.0f}" for c in PT_CUTS) + f"; wall {time.time() - t0:.0f} s")
    print("B07_EXIT=0")


# ---- 2026-11-20: cleaning variants shared by B08 (signal) and B09 (background) -------------------------------------------------------
# c100 / cinf: pT threshold (B07). iso: remove the hits of found tracks that have >= ISO_N other found tracks within Delta R < ISO_DR
# (jet-like), keep isolated tracks. iso20: iso, and also remove tracks with pT < 20 GeV. Track direction: the PV-relative innermost hit
# (eta from atan2(r, z), phi from atan2(y, x)); all found tracks (any pT) count as neighbours.
ISO_DR, ISO_N = 0.4, 2
VARIANTS = ["c100", "cinf", "iso", "iso20"]


def removal_sets(hbl, tracks):
    eta, phi = [], []
    for t in tracks:
        l0 = min(t["hits"]); x = hbl[l0][t["hits"][l0]]
        eta.append(-np.log(np.tan(0.5 * np.arctan2(np.hypot(x[0], x[1]), x[2])))); phi.append(np.arctan2(x[1], x[0]))
    eta, phi = np.array(eta), np.array(phi)
    nnb = ((np.hypot(eta[:, None] - eta[None, :], np.angle(np.exp(1j * (phi[:, None] - phi[None, :])))) < ISO_DR).sum(1) - 1) if len(tracks) else np.array([])
    pt = np.array([t["pt_gev"] for t in tracks])
    sel = {"c100": pt < 100.0, "cinf": np.ones(len(tracks), bool), "iso": nnb >= ISO_N, "iso20": (nnb >= ISO_N) | (pt < 20.0)}
    return {v: {(l, n) for t, s in zip(tracks, sel[v]) if s for l, n in t["hits"].items()} for v in VARIANTS}
