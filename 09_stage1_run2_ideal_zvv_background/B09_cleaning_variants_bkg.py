#!/usr/bin/env python3
"""09 step B09 (2026-11-20): the cleaning variants c100 / cinf / iso / iso20 (B07.removal_sets) on the Z(nunu)+jets background.
Same events, hits (B07.hits = B03's hit building and RNG) and tracks (track_cleaning v2) as B03 / B07; only the removal rule differs.
cinf and c100 must reproduce B07 exactly (checked by the caller). Output data/B09_events_c<cc>.csv.
Usage (env hep or g4): B09_cleaning_variants_bkg.py <chunk> [--workers 4] [--sample zvv|wlnu]   (wlnu outputs: data/wlnu_B09_events_c<cc>.csv)"""
import os, sys, time, argparse, pandas as pd
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import B07_cleaning_pt_threshold_bkg as B7                                         # noqa: E402
B = B7.B


def analyse(job):
    chunk, ev = job; t0 = time.time(); hbl, owner = B7.hits(chunk, ev)
    _, tracks = B.TC.find_tracks(hbl)
    row = dict(chunk=chunk, event=ev["event"], weight=ev["weight"], met=ev["met"], n_tracks=len(tracks))
    for v, rem in B7.removal_sets(hbl, tracks).items():
        row[f"{v}_n_removed"] = len(rem)
        r, _ = B.reconstruct({k: [x for n, x in enumerate(hbl[k]) if (k, n) not in rem] for k in range(1, 9)}, owner, ev, v, chunk); row.update(r)
    row["t_s"] = time.time() - t0
    return row


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("chunk", type=int); a.add_argument("--workers", type=int, default=4)
    a.add_argument("--sample", default="zvv", choices=sorted(B.PATHS.SAMPLES)); A = a.parse_args(); SP = B.PATHS.SAMPLES[A.sample]
    C = pd.read_csv(f"{HERE}/data/{SP['chunks']}").set_index("chunk"); t0 = time.time(); hep = B.PATHS.hepmc_of(A.sample, A.chunk, C.loc[A.chunk, "hepmc"])
    with Pool(A.workers) as P:
        R = list(P.imap(analyse, ((A.chunk, e) for e in B.H.iter_events(hep)), chunksize=4))
    E = pd.DataFrame(R); E.to_csv(f"{HERE}/data/{SP['prefix']}B09_events_c{A.chunk:02d}.csv", index=False); m = E.met > 200
    print(f"B09 chunk {A.chunk}: {len(E)} events; " + "; ".join(f"{v}: SR {int((E[f'{v}_sr_pass'] & m).sum())}, mean hits {E[f'{v}_n_hits'].mean():.0f}"
                                                         for v in B7.VARIANTS) + f"; wall {time.time() - t0:.0f} s")
    print("B09_EXIT=0")
