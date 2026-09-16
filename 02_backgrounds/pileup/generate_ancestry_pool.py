"""
Phase 2: regenerate the minimum-bias pool with an added ref[33] primary/
secondary classification column, using the FIXED Pythia8-aware classifier
(ancestry_classifier.py, Phase 1). Self-contained (not a bare sidecar
requiring a fragile row-order join) so it can be validated standalone by
comparing momenta against the already-committed minbias_pool_20000_FINAL.csv.

NEVER overwrites minbias_pool_20000_FINAL.csv -- always writes to a new,
explicitly versioned filename.

Same memory-safe streaming pattern as generate_minbias.py's fixed
generate_events_streaming() (chunked CSV writes), for the same reason: the
original all-in-memory approach OOM-killed at pool scale.
"""
import sys
import time
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
from generate_minbias import make_pythia
from ancestry_classifier import classify_particle

COLUMNS = ["event", "particle_idx", "pdgid", "status", "charge", "px", "py", "pz", "E", "m", "ancestry_label"]


def generate_ancestry_pool_streaming(n_events, seed, out_path, ecm_gev=13000.0, chunk_events=2000):
    pythia, actual_version = make_pythia(seed, ecm_gev)
    n_ok = 0
    n_particles_total = 0
    label_counts = {"primary": 0, "secondary": 0, "ambiguous": 0}
    rows = []
    first_chunk = True

    def flush():
        nonlocal rows, first_chunk
        if not rows:
            return
        chunk_df = pd.DataFrame(rows, columns=COLUMNS)
        chunk_df.to_csv(out_path, mode="w" if first_chunk else "a",
                         header=first_chunk, index=False)
        first_chunk = False
        rows = []

    for iev in range(n_events):
        if not pythia.next():
            continue
        n_ok += 1
        event = pythia.event
        for prt in event:
            if not prt.isFinal() or prt.charge() == 0:
                continue
            label, _reason = classify_particle(event, prt.index())
            label_counts[label] += 1
            rows.append({
                "event": iev, "particle_idx": prt.index(), "pdgid": prt.id(),
                "status": prt.status(), "charge": prt.charge(),
                "px": prt.px(), "py": prt.py(), "pz": prt.pz(), "E": prt.e(), "m": prt.m(),
                "ancestry_label": label,
            })
            n_particles_total += 1
        if len(rows) >= chunk_events * 100:
            flush()
    flush()
    if first_chunk:
        pd.DataFrame(columns=COLUMNS).to_csv(out_path, index=False)

    return {"n_ok": n_ok, "n_particles_total": n_particles_total,
            "actual_version": actual_version, "label_counts": label_counts}


if __name__ == "__main__":
    n_events = int(sys.argv[1])
    out_path = sys.argv[2]
    seed = 20260916  # SAME seed as minbias_pool_20000_FINAL.csv

    import os
    if os.path.exists(out_path):
        raise FileExistsError(f"Refusing to overwrite existing file: {out_path}")

    print(f"Generating {n_events} ancestry-classified events, seed={seed} -> {out_path}")
    t0 = time.time()
    stats = generate_ancestry_pool_streaming(n_events, seed, out_path)
    dt = time.time() - t0
    print(f"Pythia version: {stats['actual_version']}")
    print(f"n_ok={stats['n_ok']}, n_particles_total={stats['n_particles_total']}")
    print(f"wall time: {dt:.2f}s ({dt/max(stats['n_ok'],1)*1000:.3f} ms/event)")
    print(f"label counts: {stats['label_counts']}")
    total = stats["n_particles_total"]
    for k, v in stats["label_counts"].items():
        print(f"  {k}: {v} ({v/total:.4f})" if total else f"  {k}: {v}")
