#!/usr/bin/env python3
"""
Trigger-side sensitivity checks on EXISTING events only (read-only).

EW (from 01_raw_event_recount.py tables):
  T0  paper definition: final (status-1) quirk-pair pT > 200 GeV, denominator = matched
  T1  same numerator, denominator = generated LHE events (undocumented-denominator hypothesis)
  T2  hard-process (status-23, pre-shower) pair pT > 200, denominator = matched
  T3  T0 split by LHE parton multiplicity (0-jet / 1-jet ME origin)
  T4  visible-recoil proxy: |sum pT of visible status-1 particles with |eta|<4.9| > 200
      (quirks and neutrinos treated as invisible) -- an "MET-like" variant

Colored cross-check (independent raw parse of the colored 1800 GeV samples):
  final-state stop-R-hadron pair pT > 200 with the same two denominators, to
  test whether one denominator convention reproduces BOTH paper values
  (EW 0.10 and QCD 0.24) simultaneously.
"""
import gzip
import json
import math
import os
import pandas as pd

AUD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T = f"{AUD}/tables"
NU = {12, 14, 16}

COLORED = {
    "COL1000": "/home/rafia/hep_tools/quirk_signal_1800gev_2kev/Events/run_01",
    "COL2000": "/home/rafia/hep_tools/quirk_2000_fresh_regen_runs/colored_1800GeV_L2keV/Events/run_fresh",
}
EW = {
    "EW1000": "/home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01",
    "EW2000": "/home/rafia/hep_tools/quirk_2000_fresh_regen_runs/EW_800GeV_L4keV/Events/run_fresh",
}


def n_lhe(path):
    with gzip.open(path, "rt") as f:
        return sum(1 for l in f if l.lstrip().startswith("<event"))


def scan_hepmc(path, is_quirk):
    """Per event: pair pT of final-state 'quirk' objects, visible-recoil pT."""
    out, cur = [], None
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("E "):
                if cur:
                    out.append(cur)
                cur = {"q": [], "vx": 0.0, "vy": 0.0}
            elif line.startswith("P ") and cur is not None:
                t = line.split()
                if int(t[8]) != 1:
                    continue
                pdg = int(t[2])
                px, py, pz = float(t[3]), float(t[4]), float(t[5])
                if is_quirk(abs(pdg)):
                    cur["q"].append((pdg, px, py))
                elif abs(pdg) not in NU:
                    p = math.sqrt(px * px + py * py + pz * pz)
                    pt = math.hypot(px, py)
                    if pt > 0 and p > abs(pz):
                        eta = 0.5 * math.log((p + pz) / (p - pz))
                        if abs(eta) < 4.9:
                            cur["vx"] += px
                            cur["vy"] += py
    if cur:
        out.append(cur)
    return out


def main():
    res = {}
    for name, d in EW.items():
        hep = pd.read_csv(f"{T}/{name}_hepmc_events.csv")
        lhe = pd.read_csv(f"{T}/{name}_lhe_events.csv")
        n_gen, n_m = len(lhe), len(hep)
        n_t = int(hep["trigger_strict_gt200_final"].sum())
        mult = lhe[lhe["hepmc_seq"].notna()].set_index("hepmc_seq")["n_partons_final"]
        hep["lhe_mult"] = hep["hepmc_seq"].map({int(k): int(v) for k, v in mult.items()})
        ev = scan_hepmc(f"{d}/tag_1_pythia8_events.hepmc.gz", lambda a: a == 9000011)
        vis = [math.hypot(e["vx"], e["vy"]) for e in ev]
        r = {
            "N_generated": n_gen, "N_matched": n_m, "N_trigger_T0": n_t,
            "T0_trigger_over_matched": n_t / n_m,
            "T1_trigger_over_generated": n_t / n_gen,
            "T2_hard_status23_over_matched": int((hep["pair_pt_hard_status23"] > 200).sum()) / n_m,
            "N_T2": int((hep["pair_pt_hard_status23"] > 200).sum()),
            "T4_visible_recoil_gt200_over_matched": sum(v > 200 for v in vis) / n_m,
            "N_T4": sum(v > 200 for v in vis),
            "N_hepmc_unmapped_to_LHE_multiplicity": int(hep["lhe_mult"].isna().sum()),
        }
        for m in (0, 1):
            s = hep[hep["lhe_mult"] == m]
            r[f"T3_{m}jet_matched"] = len(s)
            r[f"T3_{m}jet_trigger"] = int(s["trigger_strict_gt200_final"].sum())
        res[name] = r

    for name, d in COLORED.items():
        lhe_n = n_lhe(f"{d}/unweighted_events.lhe.gz")
        ev = scan_hepmc(f"{d}/tag_1_pythia8_events.hepmc.gz", lambda a: 1000000 <= a < 1100000)
        two = [e for e in ev if len(e["q"]) == 2]
        ptp = [math.hypot(e["q"][0][1] + e["q"][1][1], e["q"][0][2] + e["q"][1][2]) for e in two]
        n_t = sum(p > 200 for p in ptp)
        res[name] = {
            "N_generated": lhe_n, "N_hepmc_events": len(ev),
            "N_with_exactly_2_final_Rhadrons": len(two),
            "N_trigger_pair_pt_gt200": n_t,
            "trigger_over_matched": n_t / len(ev),
            "trigger_over_generated": n_t / lhe_n,
            "note": "trigger counted before any R-hadron charge requirement",
        }
    json.dump(res, open(f"{T}/trigger_variants_summary.json", "w"), indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
