"""
Parse the showered Z(->nunu)+gamma+jet HepMC2 output and extract, per event:
  - the hardest final-state photon's 4-momentum
  - the true MET (vector sum of final-state neutrino pT)

Generation config verified directly (Stage 2 audit, 2026-09-15): run_card.dat
gives ebeam1=ebeam2=6500 GeV (sqrt(s)=13 TeV); proc_card_mg5.dat's
`generate p p > z a j, z > vl vl~` with `vl = ve vm vt` sums over all THREE
neutrino flavors at generation, matching NEUTRINO_PDGS={12,14,16} below.

"Hardest final-state photon" is a PRACTICAL PROXY for "the photon from the Z
decay," not a verified match -- this script does not trace HepMC mother/
daughter ancestry to confirm the selected photon actually descends from the
hard-process vertex (as opposed to e.g. a hard FSR photon radiated
elsewhere). For this LO Z+gamma+jet sample the hardest photon is generally
expected to be the hard-process one, but that expectation is NOT verified
here and should not be read as confirmed ancestry.

MET: neutrinos are neutral and colorless, so they are untouched by Pythia8's
parton shower -- their momenta are fixed at the matrix-element (LHE) level.
HOWEVER the generation-level `misset > 200 GeV` cut in the run_card is NOT
exact for the POST-SHOWER MET computed here: Pythia8's hadronization adds
secondary neutrinos from semileptonic hadron decays inside the jet, which
the generation-level cut (evaluated on only the primary Z-decay neutrinos)
does not see. Depending on their direction relative to the primary
neutrinos, these secondary neutrinos can shift the vector-sum MET in either
direction -- they do not "necessarily" lower it, and post-shower MET
failures are NOT expected to be ~0. Measured directly (2026-09-14): 861/10000
events (8.6%) have true post-shower MET < 200 GeV despite passing the
generation-level cut. The exact post-shower cut is applied below rather than
trusting the generation-level proxy.
"""

import gzip
import numpy as np
import pandas as pd

NEUTRINO_PDGS = {12, 14, 16}


def extract_events(hepmc_path, max_events=None):
    opener = gzip.open if hepmc_path.endswith(".gz") else open
    events = []
    current = None
    n_seen = 0

    def new_event():
        return {"weight": None, "photons": [], "nu_px": 0.0, "nu_py": 0.0}

    with opener(hepmc_path, "rt") as f:
        for line in f:
            if line.startswith("E "):
                if current is not None:
                    events.append(current)
                    n_seen += 1
                    if max_events is not None and n_seen >= max_events:
                        break
                parts = line.split()
                current = new_event()
                try:
                    current["weight"] = float(parts[-1])
                except (ValueError, IndexError):
                    current["weight"] = 1.0
            elif line.startswith("P ") and current is not None:
                parts = line.split()
                pdg = int(parts[2])
                px, py, pz, E = (float(parts[3]), float(parts[4]),
                                  float(parts[5]), float(parts[6]))
                status = int(parts[8])
                if status != 1:
                    continue
                if pdg == 22:
                    current["photons"].append((px, py, pz, E))
                elif abs(pdg) in NEUTRINO_PDGS:
                    current["nu_px"] += px
                    current["nu_py"] += py
        if current is not None:
            events.append(current)

    return events


def build_dataframe(hepmc_path, max_events=None):
    events = extract_events(hepmc_path, max_events=max_events)
    rows = []
    n_no_photon = 0
    n_met_fail = 0
    n_pt_gamma_fail = 0
    for i, ev in enumerate(events):
        if ev["weight"] is None or ev["weight"] <= 0:
            continue
        if not ev["photons"]:
            n_no_photon += 1
            continue
        # hardest photon by pT
        px, py, pz, E = max(ev["photons"], key=lambda p: np.hypot(p[0], p[1]))
        pT_gamma = np.hypot(px, py)
        if pT_gamma < 0.5:
            # Paper (Sec III D) states pT_gamma > 0.5 GeV as an explicit cut.
            # The run_card's generation-level `ptgmin=0.5` is only a PROXY for
            # this, exactly like `misset` was a proxy for the true post-shower
            # MET cut below -- unlike MET, hadronization does not measurably
            # pull the LEADING photon's pT down (no secondary-photon analog of
            # the secondary-neutrino effect), so this proxy is expected to
            # hold essentially exactly; verified here rather than assumed, per
            # the same rigor already applied to the MET cut.
            n_pt_gamma_fail += 1
            continue
        met = np.hypot(ev["nu_px"], ev["nu_py"])
        if met < 200.0:
            # The generation-level `misset` cut only sees the 2 primary
            # Z->nunu neutrinos; Pythia8's hadronization adds further soft
            # neutrinos from semileptonic hadron decays inside the jet,
            # which a real calorimeter-based MET trigger would also see and
            # which can shift the vector-sum MET in either direction (not
            # necessarily downward). This full post-shower MET is the
            # physically correct quantity to cut on -- apply the genuine
            # >200 GeV requirement here, exactly, rather than trusting the
            # generation-level proxy. Measured: this removes 861/10000
            # (8.6%) events that passed the generation-level cut -- a real,
            # non-negligible effect, not an edge case.
            n_met_fail += 1
            continue
        rows.append({
            "event": i, "weight": ev["weight"],
            "px": px, "py": py, "pz": pz, "E": E,
            "pT_gamma": pT_gamma, "met": met,
        })
    df = pd.DataFrame(rows)
    print(f"Events with no final-state photon found: {n_no_photon}")
    print(f"Events with pT_gamma < 0.5 GeV despite generation-level ptgmin cut "
          f"(expected ~0, confirms the cut holds post-shower): {n_pt_gamma_fail}")
    print(f"Events with MET < 200 GeV despite generation-level misset cut "
          f"(a real, non-negligible effect from secondary neutrinos, NOT "
          f"expected to be ~0 -- measured 861/10000 historically): {n_met_fail}")
    return df


if __name__ == "__main__":
    import sys
    hepmc_path = sys.argv[1] if len(sys.argv) > 1 else (
        "/home/rafia/hep_tools/zgamma_background_test/Events/run_02/"
        "tag_1_pythia8_events.hepmc.gz")
    df = build_dataframe(hepmc_path)
    print(f"\nExtracted {len(df)} valid events")
    print(df[["weight", "pT_gamma", "met"]].describe())
    out_csv = ("/home/rafia/coplanarity_study/02_backgrounds/photon_conversion/"
               "zgamma_photons.csv")
    df.to_csv(out_csv, index=False)
    print(f"Saved to {out_csv}")
