"""
Parse the showered+matched HepMC2 output from MadGraph5_aMC@NLO+Pythia8 and
extract, per event, the final-state quirk R-hadron pair's 4-momenta.

Our colored quirk (3,1)_2/3, mQ=1800 GeV, was implemented by reusing
Pythia8's RHadrons:idStop slot (PDG 1000006), so it appears in the final
state as an R-hadron with PDG code in Pythia8's stop-R-hadron numbering
scheme (|PDG| in the 1000600-1009999-ish range per RHadrons.xml), at a mass
~1800.5 GeV -- 0.03% above the pure quirk mass, i.e. the light-quark
constituent's contribution is negligible and the R-hadron's own 4-momentum
is used directly as "the quirk's four-momentum" (matches the paper's Sec.
III A: "The resulting four-momenta of the quirks are then evolved...").

Only MLM-matching-surviving events (weight > 0) are kept, matching the
"419 events after matching/merging" reported by MadGraph.
"""

import gzip
import numpy as np
import pandas as pd

QUIRK_MASS_GEV = 1800.0
# R-hadron PDG codes are large (>= 1000600) and come in +/- pairs; the true
# quirk pair is exactly the two R-hadron final-state particles whose mass is
# closest to QUIRK_MASS_GEV (the light-constituent contribution is small but
# non-zero and slightly flavor-dependent, so we don't hardcode exact codes).
MASS_TOLERANCE_GEV = 5.0  # generous window around 1800 GeV


def extract_events(hepmc_path, max_events=None):
    """
    Returns a list of dicts, one per event, each with:
      'weight': event weight (float)
      'quirks': list of (px,py,pz,E,pdg) tuples for the R-hadron(s) found
    """
    opener = gzip.open if hepmc_path.endswith(".gz") else open
    events = []
    current_weight = None
    current_particles = []
    n_events_seen = 0

    with opener(hepmc_path, "rt") as f:
        for line in f:
            if line.startswith("E "):
                if current_particles or current_weight is not None:
                    events.append({"weight": current_weight,
                                    "quirks": current_particles})
                    n_events_seen += 1
                    if max_events is not None and n_events_seen >= max_events:
                        break
                parts = line.split()
                # HepMC2 'E' line: E evtnum ... nrandom ... nweights weight1 ...
                # Weight is typically the last-ish field before vertex count;
                # robustly grab the first weight value (field index 11 in the
                # standard 2.06 layout used by MG5's writer).
                try:
                    current_weight = float(parts[-1])
                except (ValueError, IndexError):
                    current_weight = 1.0
                current_particles = []
            elif line.startswith("P "):
                parts = line.split()
                pdg = int(parts[2])
                px, py, pz, E, m = (float(parts[3]), float(parts[4]),
                                     float(parts[5]), float(parts[6]),
                                     float(parts[7]))
                status = int(parts[8])
                if status == 1 and abs(m - QUIRK_MASS_GEV) < MASS_TOLERANCE_GEV:
                    current_particles.append((px, py, pz, E, pdg, m))
        # flush last event
        if current_particles or current_weight is not None:
            events.append({"weight": current_weight, "quirks": current_particles})

    return events


def build_dataframe(hepmc_path, max_events=None):
    events = extract_events(hepmc_path, max_events=max_events)
    rows = []
    for i, ev in enumerate(events):
        if ev["weight"] is None or ev["weight"] <= 0:
            continue  # MLM-matching-vetoed event
        quirks = ev["quirks"]
        if len(quirks) != 2:
            continue  # skip malformed/edge events (should be exactly q + qbar)
        (px1, py1, pz1, E1, pdg1, m1), (px2, py2, pz2, E2, pdg2, m2) = quirks
        rows.append({
            "event": i, "weight": ev["weight"],
            "px1": px1, "py1": py1, "pz1": pz1, "E1": E1, "pdg1": pdg1, "m1": m1,
            "px2": px2, "py2": py2, "pz2": pz2, "E2": E2, "pdg2": pdg2, "m2": m2,
            "pT_pair": np.hypot(px1 + px2, py1 + py2),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    hepmc_path = sys.argv[1] if len(sys.argv) > 1 else (
        "/home/rafia/hep_tools/quirk_signal_1800gev_2kev/Events/run_01/"
        "tag_1_pythia8_events.hepmc.gz")
    df = build_dataframe(hepmc_path)
    print(f"Extracted {len(df)} valid quirk-pair events (weight>0, exactly 2 quirks found)")
    print(df[["event", "weight", "m1", "m2", "pT_pair"]].describe())
    out_csv = "/home/rafia/coplanarity_study/01_signal_generation/quirk_pair_momenta_1800gev_2kev.csv"
    df.to_csv(out_csv, index=False)
    print(f"Saved to {out_csv}")
    print(f"\nEvents passing trigger cut pT_pair > 200 GeV: {(df['pT_pair'] > 200).sum()} / {len(df)}")
