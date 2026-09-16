"""
Stage 3 REAL pile-up: minimum-bias event generator using Pythia8 directly
(no MadGraph needed -- minimum-bias QCD is a native Pythia8 process).

VERSION AND SETTINGS RECORD (per Part B's audit table):
  - Pythia8 version: 8.312 (confirmed via pythia8.Pythia().settings.parm(
    'Pythia:versionNumber'); paper cites the "8.2" series, ref [21] =
    arXiv:1410.3012 -- exact sub-version not reproducible, documented gap).
  - Collision energy: 13 TeV (sqrt(s)) -- NOT explicitly restated for
    pileup in Sec III-D; inferred from the paper's general Run-2 context
    (documented ASSUMPTION, not a literal paper statement for this specific
    number).
  - Process: SoftQCD:nonDiffractive = on -- the standard "minimum bias"
    recipe used across ATLAS/CMS pileup Monte Carlo. The paper does NOT
    specify this switch (Sec III-D just says "minimum bias events... by
    Pythia8") -- documented ASSUMPTION, not a paper requirement.
  - Beams:allowVertexSpread = off (explicitly disabled) -- we apply the
    paper's OWN 45mm beamspot prescription ourselves, per-interaction, at
    overlay time (Part D), not inside the generator, to avoid double-
    smearing and to keep the vertex-assignment step auditable/documented
    separately.
  - Random seed: recorded explicitly per run (see __main__), for
    reproducibility.

Output: one row per (event, charged final-state particle), preserving
event ID, PDG ID, status, charge, and four-momentum. Production vertex is
NOT stored from Pythia8's own internal frame (vertex spread is disabled);
the actual pileup-vertex position is assigned during overlay (Part D),
which is the documented, correct place for it per the paper's own
beamspot description.
"""
import sys
import time
import numpy as np
import pandas as pd
import pythia8

PYTHIA_VERSION_EXPECTED = "8.312"


def make_pythia(seed, ecm_gev=13000.0):
    pythia = pythia8.Pythia("", False)
    actual_version = pythia.settings.parm("Pythia:versionNumber")
    pythia.readString("Beams:idA = 2212")
    pythia.readString("Beams:idB = 2212")
    pythia.readString(f"Beams:eCM = {ecm_gev}")
    pythia.readString("SoftQCD:nonDiffractive = on")
    pythia.readString("Beams:allowVertexSpread = off")
    pythia.readString("Random:setSeed = on")
    pythia.readString(f"Random:seed = {seed}")
    pythia.readString("Print:quiet = on")
    pythia.init()
    return pythia, actual_version


COLUMNS = ["event", "pdgid", "status", "charge", "px", "py", "pz", "E", "m"]


def generate_events_streaming(n_events, seed, out_path, ecm_gev=13000.0,
                               chunk_events=2000):
    """
    Streams output to `out_path` in chunks of `chunk_events` events, instead
    of accumulating all rows in memory: the naive all-in-memory version
    OOM-killed at 125,000 events (13.5M+ particle dicts on a 7.6GB-RAM
    machine, confirmed via dmesg: RSS reached 7.4GB before SIGKILL). Peak
    memory here is bounded by one chunk's rows, independent of n_events.

    Returns (n_ok, n_particles_total, actual_version, mult_per_event dict,
    any_nan, any_inf, unique_event_ids_count) -- same summary statistics the
    old all-in-memory version printed, computed incrementally instead.
    """
    pythia, actual_version = make_pythia(seed, ecm_gev)
    n_ok = 0
    n_particles_total = 0
    mult_by_event = {}
    any_nan = False
    any_inf = False
    seen_event_ids = set()
    first_chunk = True
    rows = []

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
        n_this = 0
        for prt in pythia.event:
            if not prt.isFinal():
                continue
            if prt.charge() == 0:
                continue
            px, py, pz, E, m = prt.px(), prt.py(), prt.pz(), prt.e(), prt.m()
            if not (np.isfinite(px) and np.isfinite(py) and np.isfinite(pz)
                    and np.isfinite(E) and np.isfinite(m)):
                any_nan = any_nan or any(v != v for v in (px, py, pz, E, m))  # NaN check
                any_inf = any_inf or any(np.isinf(v) for v in (px, py, pz, E, m))
            rows.append({
                "event": iev, "pdgid": prt.id(), "status": prt.status(),
                "charge": prt.charge(), "px": px, "py": py, "pz": pz, "E": E, "m": m,
            })
            n_this += 1
        n_particles_total += n_this
        mult_by_event[iev] = n_this
        seen_event_ids.add(iev)
        if len(rows) >= chunk_events * 100:  # ~100 particles/event average
            flush()
    flush()
    if first_chunk:
        # zero events generated OK -- still write an empty file with header
        pd.DataFrame(columns=COLUMNS).to_csv(out_path, index=False)

    return {
        "n_ok": n_ok, "n_particles_total": n_particles_total,
        "actual_version": actual_version, "mult_by_event": mult_by_event,
        "any_nan": any_nan, "any_inf": any_inf,
        "n_unique_event_ids": len(seen_event_ids),
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    seed = 20260916
    ecm = 13000.0

    if mode == "smoke":
        n = 100
        out = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_smoke_100.csv"
    elif mode == "benchmark":
        n = 1000
        out = "/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_benchmark_1000.csv"
    elif mode == "pool":
        n = int(sys.argv[2])
        out = f"/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_{n}.csv"
    else:
        raise ValueError("mode must be smoke, benchmark, or pool <N>")

    print(f"Generating {n} minimum-bias events, seed={seed}, ecm={ecm} GeV (streaming to {out})")
    t0 = time.time()
    stats = generate_events_streaming(n, seed, out, ecm)
    dt = time.time() - t0
    n_ok = stats["n_ok"]

    print(f"Pythia8 version actually used: {stats['actual_version']}")
    print(f"Events generated OK: {n_ok} / {n}")
    print(f"Wall time: {dt:.2f}s ({dt/max(n_ok,1)*1000:.2f} ms/event)")
    print(f"Total charged final-state particles: {stats['n_particles_total']}")
    if n_ok > 0:
        mult = np.array(list(stats["mult_by_event"].values()))
        print(f"Charged multiplicity per event: mean={mult.mean():.2f}, "
              f"min={mult.min()}, max={mult.max()}")
    print(f"NaN detected: {stats['any_nan']}")
    print(f"Inf detected: {stats['any_inf']}")
    print(f"Unique event IDs: {stats['n_unique_event_ids']} (expect <= {n_ok})")

    file_size_mb = __import__("os").path.getsize(out) / 1e6
    print(f"Saved to {out} ({file_size_mb:.2f} MB)")

    # Projection to 125,000 events
    if n_ok > 0:
        proj_time_s = dt / n_ok * 125000
        proj_size_mb = file_size_mb / n_ok * 125000
        print(f"\nProjected for 125,000 events: time={proj_time_s/60:.1f} min, "
              f"size={proj_size_mb:.1f} MB")
