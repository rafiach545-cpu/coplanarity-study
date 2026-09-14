"""
Same extraction logic as extract_quirk_momenta.py, adapted for the EW quirk
(1,1)_1 benchmark: mQ=800 GeV, PDG 9000011. Unlike the colored quirk, this is
a color singlet, so it needs no R-hadron treatment -- it appears directly as
a stable final-state particle at exactly 800.0 GeV.
"""

import gzip
import numpy as np
import pandas as pd

QUIRK_MASS_GEV = 800.0
MASS_TOLERANCE_GEV = 5.0


def extract_events(hepmc_path, max_events=None):
    opener = gzip.open if hepmc_path.endswith(".gz") else open
    events = []
    current_weight = None
    current_particles = []
    n_events_seen = 0

    with opener(hepmc_path, "rt") as f:
        for line in f:
            if line.startswith("E "):
                if current_particles or current_weight is not None:
                    events.append({"weight": current_weight, "quirks": current_particles})
                    n_events_seen += 1
                    if max_events is not None and n_events_seen >= max_events:
                        break
                parts = line.split()
                try:
                    current_weight = float(parts[-1])
                except (ValueError, IndexError):
                    current_weight = 1.0
                current_particles = []
            elif line.startswith("P "):
                parts = line.split()
                pdg = int(parts[2])
                px, py, pz, E, m = (float(parts[3]), float(parts[4]),
                                     float(parts[5]), float(parts[6]), float(parts[7]))
                status = int(parts[8])
                if status == 1 and abs(m - QUIRK_MASS_GEV) < MASS_TOLERANCE_GEV:
                    current_particles.append((px, py, pz, E, pdg, m))
        if current_particles or current_weight is not None:
            events.append({"weight": current_weight, "quirks": current_particles})
    return events


def build_dataframe(hepmc_path, max_events=None):
    events = extract_events(hepmc_path, max_events=max_events)
    rows = []
    for i, ev in enumerate(events):
        if ev["weight"] is None or ev["weight"] <= 0:
            continue
        quirks = ev["quirks"]
        if len(quirks) != 2:
            continue
        (px1, py1, pz1, E1, pdg1, m1), (px2, py2, pz2, E2, pdg2, m2) = quirks
        rows.append({
            "event": i, "weight": ev["weight"],
            "px1": px1, "py1": py1, "pz1": pz1, "E1": E1, "pdg1": pdg1, "m1": m1,
            "px2": px2, "py2": py2, "pz2": pz2, "E2": E2, "pdg2": pdg2, "m2": m2,
            "pT_pair": np.hypot(px1 + px2, py1 + py2),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    hepmc_path = ("/home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01/"
                   "tag_1_pythia8_events.hepmc.gz")
    df = build_dataframe(hepmc_path)
    print(f"Extracted {len(df)} valid quirk-pair events (weight>0, exactly 2 quirks found)")
    print(f"(cross-section for this matched sample: 0.0002337 pb, reported separately, "
          f"NOT folded into any per-event weight column here)")
    print(df[["event", "weight", "m1", "m2", "pT_pair"]].describe())
    out_csv = ("/home/rafia/coplanarity_study/01_signal_generation/"
               "ew_quirk_pair_momenta_800gev_4kev.csv")
    df.to_csv(out_csv, index=False)
    print(f"Saved to {out_csv}")
    n_trig = (df["pT_pair"] > 200).sum()
    print(f"\nEvents passing trigger cut pT_pair > 200 GeV: {n_trig} / {len(df)}")
