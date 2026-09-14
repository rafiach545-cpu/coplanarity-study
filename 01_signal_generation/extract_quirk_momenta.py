"""
Parse the showered+matched HepMC2 output from MadGraph5_aMC@NLO+Pythia8 and
extract, per event, the final-state quirk R-hadron pair's 4-momenta and
electric charges.

Our colored quirk (3,1)_2/3, mQ=1800 GeV, was implemented by reusing
Pythia8's RHadrons:idStop slot (PDG 1000006), so it appears in the final
state as an R-hadron with PDG code in Pythia8's stop-R-hadron numbering
scheme, at a mass ~1800.5 GeV -- 0.03% above the pure quirk mass, i.e. the
light-quark constituent's contribution to the MASS is negligible. The
R-hadron's own 4-momentum is used as an APPROXIMATION for "the quirk's
four-momentum" (Sec. II: "the quirks will quickly hadronize into
quirk-hadrons... we will loosely refer to the quirk-hadrons as quirks") --
this is a reasonable approximation given the paper's own stated looseness of
language, NOT a claim that Sec. III A's "the resulting four-momenta of the
quirks are then evolved" specifically endorses using the raw R-hadron
four-momentum unmodified; that sentence describes the trajectory-evolution
step, not this extraction/identification choice.

ELECTRIC CHARGE (Sec. II): "the probability for those final states to have
+-1 charges is roughly 30%... Our analysis is largely independent on the
charges of the quirk-hadrons, AS LONG AS BOTH QUIRK-HADRONS CARRY NON-ZERO
ELECTRIC CHARGE, such that they leave a signal in the inner trackers." A
neutral quirk-hadron does not ionize silicon and leaves NO tracker hits, so
an event where either quirk-hadron is neutral is not usable by this
analysis at all -- this must be checked, not assumed. Verified directly
against Pythia8's own authoritative RHadrons particle database (not
memory/guessed PDG-digit conventions): of the 419 mass-matched candidate
pairs in the actual quirk_signal_1800gev_2kev sample, only 125 (29.8%) have
BOTH quirk-hadrons non-zero charge -- strikingly close to the paper's own
quoted ~30% figure, which is strong independent confirmation this physics is
being modelled correctly by Pythia8 and was previously being silently
ignored (all 419 were being kept and fed downstream as if uniformly
charged). This module now requires the `pythia8` Python bindings (used
read-only, purely to query particleData.chargeType() -- no event generation
happens here) and filters out events where either quirk-hadron is neutral.

Ordering: HepMC does not guarantee particle-1/particle-2 ordering matches
quirk/antiquirk. What IS guaranteed (verified: 419/419 events in the real
sample) is that exactly one of the two candidates has a POSITIVE PDG code
(built from the quirk itself, idStop=+1000006) and the other NEGATIVE (built
from the antiquirk, -1000006) -- R-hadrons built from the quirk and from the
antiquirk can combine with DIFFERENT light quarks (e.g. quirk+dbar vs.
antiquirk+s), so pdg1 == -pdg2 need NOT hold and is not asserted; only the
opposite-sign condition is, since it is what is actually guaranteed by the
particle/antiparticle PDG-sign convention. Per-hadron charge is recorded
explicitly (charge1, charge2) so downstream code never needs to assume a
fixed charge or a fixed particle/antiparticle column order.

Weight field: verified directly (not assumed) that in the actual
quirk_signal_1800gev_2kev/.../tag_1_pythia8_events.hepmc.gz file, ALL 419 'E'
records carry the exact same positive weight (7.5036e-4) -- there are ZERO
weight<=0 events anywhere in the file for the `weight>0` check to filter.
MadGraph's HepMC writer evidently omits MLM-matching-vetoed events from the
file entirely rather than including them with a non-positive weight marker,
so the "419 events after matching/merging" count is simply the total number
of E-records in this run's own output file -- a fact about THIS run, not a
number the paper reports. The `weight>0` check is kept as a defensive guard
for a differently-configured sample, but is empirically a no-op here, and
should not be described as "the mechanism that performs MLM-matching
selection" for this specific file.
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


def _make_rhadron_charge_lookup():
    """
    Build a PDG-code -> electric charge (in units of e) lookup using
    Pythia8's own particle database, configured exactly as the actual
    generation run configured RHadrons (RHadrons:allow=on, allowDecay=off,
    default idStop=1000006 -- matches
    quirk_signal_1800gev_2kev/Cards/pythia8_card.dat). This is a read-only
    query of Pythia8's static particle-content logic; no events are
    generated. Charge assignment for a given quark content is mass- and
    width-independent, so the exact 1800 GeV mass is not needed here for
    correctness, only for realism.

    Returns a callable pdg -> float charge, or None if Pythia8 does not
    recognize the code (which would itself indicate the mass-window
    selection above picked up something that is not a real R-hadron --
    treated as a hard error rather than silently guessed).
    """
    import pythia8
    pythia = pythia8.Pythia("", False)
    pythia.readString("RHadrons:allow = on")
    pythia.readString("RHadrons:allowDecay = off")
    pythia.init()
    pdt = pythia.particleData

    def charge_of(pdg):
        if not pdt.isParticle(pdg):
            raise ValueError(
                f"PDG {pdg} (mass-window-selected as a candidate quirk R-hadron) "
                "is not recognized by Pythia8's own RHadrons particle database -- "
                "this is a real inconsistency, not something to silently skip or "
                "guess a charge for. Check MASS_TOLERANCE_GEV and the actual "
                "RHadrons configuration used for this sample.")
        return pdt.chargeType(pdg) / 3.0

    return charge_of


def extract_events(hepmc_path, max_events=None):
    """
    Returns a list of dicts, one per event, each with:
      'weight': event weight (float)
      'quirks': list of (px,py,pz,E,pdg,m) tuples for the R-hadron(s) found
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
                # Grab the last field, which is where MG5's writer places the
                # single event weight for this sample (verified: exactly one
                # weight value appears, consistently, across the real file).
                try:
                    current_weight = float(parts[-1])
                except (ValueError, IndexError):
                    current_weight = 1.0
                current_particles = []
            elif line.startswith("P ") and current_weight is not None:
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
    charge_of = _make_rhadron_charge_lookup()
    events = extract_events(hepmc_path, max_events=max_events)
    rows = []
    n_weight_fail = 0
    n_not_pair = 0
    n_same_sign = 0
    n_neutral_excluded = 0
    for i, ev in enumerate(events):
        if ev["weight"] is None or ev["weight"] <= 0:
            n_weight_fail += 1
            continue  # defensive guard; empirically a no-op for this sample (see module docstring)
        quirks = ev["quirks"]
        if len(quirks) != 2:
            n_not_pair += 1
            continue  # skip malformed/edge events (should be exactly q + qbar)
        (px1, py1, pz1, E1, pdg1, m1), (px2, py2, pz2, E2, pdg2, m2) = quirks

        # Quirk/antiquirk pairing check (Sec. II defines the system as a
        # quirk/ANTIQUIRK pair): verified guarantee is opposite PDG SIGN (one
        # built from the quirk, one from the antiquirk), NOT pdg1==-pdg2,
        # since the two can hadronize with different light quarks.
        if (pdg1 > 0) == (pdg2 > 0):
            n_same_sign += 1
            continue

        charge1 = charge_of(pdg1)
        charge2 = charge_of(pdg2)
        if charge1 == 0.0 or charge2 == 0.0:
            # Sec. II: analysis only applies "as long as both quirk-hadrons
            # carry non-zero electric charge" -- a neutral quirk-hadron
            # leaves no tracker signal at all, so this event is not usable.
            n_neutral_excluded += 1
            continue

        rows.append({
            "event": i, "weight": ev["weight"],
            "px1": px1, "py1": py1, "pz1": pz1, "E1": E1,
            "pdg1": pdg1, "m1": m1, "charge1": charge1,
            "px2": px2, "py2": py2, "pz2": pz2, "E2": E2,
            "pdg2": pdg2, "m2": m2, "charge2": charge2,
            "pT_pair": np.hypot(px1 + px2, py1 + py2),
        })

    df = pd.DataFrame(rows)
    print(f"Events skipped, weight<=0 (defensive guard, expect 0 for this sample): {n_weight_fail}")
    print(f"Events skipped, not exactly 2 mass-matched R-hadrons: {n_not_pair}")
    print(f"Events skipped, same-PDG-sign anomaly (not a quirk/antiquirk pair): {n_same_sign}")
    print(f"Events EXCLUDED, at least one quirk-hadron is electrically neutral "
          f"(paper Sec. II applicability condition): {n_neutral_excluded}")
    print(f"Events KEPT (both quirk-hadrons non-zero charge): {len(df)}")
    return df


if __name__ == "__main__":
    import sys
    hepmc_path = sys.argv[1] if len(sys.argv) > 1 else (
        "/home/rafia/hep_tools/quirk_signal_1800gev_2kev/Events/run_01/"
        "tag_1_pythia8_events.hepmc.gz")
    df = build_dataframe(hepmc_path)
    print(f"\nExtracted {len(df)} valid, charged quirk-pair events")
    print(df[["event", "weight", "m1", "charge1", "m2", "charge2", "pT_pair"]].describe())
    out_csv = ("/home/rafia/coplanarity_study/01_signal_generation/"
               "quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv")
    df.to_csv(out_csv, index=False)
    print(f"Saved to {out_csv}")
    print(f"\nEvents passing trigger cut pT_pair > 200 GeV: {(df['pT_pair'] > 200).sum()} / {len(df)}")
