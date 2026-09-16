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


def generate_events(n_events, seed, ecm_gev=13000.0):
    pythia, actual_version = make_pythia(seed, ecm_gev)
    rows = []
    n_ok = 0
    for iev in range(n_events):
        if not pythia.next():
            continue
        n_ok += 1
        for prt in pythia.event:
            if not prt.isFinal():
                continue
            if prt.charge() == 0:
                continue
            rows.append({
                "event": iev, "pdgid": prt.id(), "status": prt.status(),
                "charge": prt.charge(),
                "px": prt.px(), "py": prt.py(), "pz": prt.pz(), "E": prt.e(),
                "m": prt.m(),
            })
    df = pd.DataFrame(rows)
    return df, n_ok, actual_version


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

    print(f"Generating {n} minimum-bias events, seed={seed}, ecm={ecm} GeV")
    t0 = time.time()
    df, n_ok, actual_version = generate_events(n, seed, ecm)
    dt = time.time() - t0

    print(f"Pythia8 version actually used: {actual_version}")
    print(f"Events generated OK: {n_ok} / {n}")
    print(f"Wall time: {dt:.2f}s ({dt/max(n_ok,1)*1000:.2f} ms/event)")
    print(f"Total charged final-state particles: {len(df)}")
    if n_ok > 0:
        mult = df.groupby("event").size()
        print(f"Charged multiplicity per event: mean={mult.mean():.2f}, "
              f"min={mult.min()}, max={mult.max()}")
    print(f"NaN count: {df.isna().sum().sum()}")
    print(f"Inf count: {np.isinf(df.select_dtypes(include=[np.number])).sum().sum()}")
    print(f"Unique event IDs: {df['event'].nunique()} (expect <= {n_ok})")

    df.to_csv(out, index=False)
    file_size_mb = __import__("os").path.getsize(out) / 1e6
    print(f"Saved to {out} ({file_size_mb:.2f} MB)")

    # Projection to 125,000 events
    if n_ok > 0:
        proj_time_s = dt / n_ok * 125000
        proj_size_mb = file_size_mb / n_ok * 125000
        print(f"\nProjected for 125,000 events: time={proj_time_s/60:.1f} min, "
              f"size={proj_size_mb:.1f} MB")
