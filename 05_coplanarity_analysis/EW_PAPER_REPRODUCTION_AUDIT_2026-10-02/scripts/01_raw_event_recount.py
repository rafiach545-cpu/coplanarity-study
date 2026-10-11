#!/usr/bin/env python3
"""
Independent raw-file recount for the EW quirk benchmark (mQ=800 GeV).

Reads ONLY the frozen raw generator files (read-only):
  - unweighted_events.lhe.gz          (MadGraph parton level, "generated")
  - tag_1_pythia8_events.hepmc.gz     (Pythia8 after MLM matching, "matched")

Does NOT import any project analysis code and does NOT use cached summaries.

For every LHE event:   parton multiplicity, quirk-pair pT at parton level.
For every HepMC event: quirk momenta for every status code present, pair pT
                       built from (a) final status-1 quirks, (b) status-23
                       hard-process quirks, (c) status-44 last recoiled copy.
HepMC events are matched back to LHE events through the status-23 quirk
four-momenta (identical to LHE momenta up to print precision), so the MLM
veto can be studied per LHE event.

Outputs (one row per LHE event and one per HepMC event) go to ../tables/.
"""
import gzip
import sys
import json
import math
import hashlib
import os

QPDG = 9000011
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")

SAMPLES = {
    "EW1000": "/home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01",
    "EW2000": "/home/rafia/hep_tools/quirk_2000_fresh_regen_runs/EW_800GeV_L4keV/Events/run_fresh",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pt(px, py):
    return math.hypot(px, py)


def read_lhe(path):
    events = []
    with gzip.open(path, "rt") as f:
        in_ev = False
        lines = []
        for line in f:
            s = line.strip()
            if s.startswith("<event"):
                in_ev, lines = True, []
                continue
            if s.startswith("</event>"):
                in_ev = False
                hdr = lines[0].split()
                nup = int(hdr[0])
                parts = [l.split() for l in lines[1:1 + nup]]
                quirks = [p for p in parts if abs(int(p[0])) == QPDG and int(p[1]) == 1]
                partons = [p for p in parts if int(p[1]) == 1 and abs(int(p[0])) != QPDG]
                assert len(quirks) == 2, "LHE event without exactly 2 quirks"
                px = sum(float(q[6]) for q in quirks)
                py = sum(float(q[7]) for q in quirks)
                events.append({
                    "lhe_idx": len(events),
                    "nup": nup,
                    "n_partons_final": len(partons),
                    "parton_pdgs": "|".join(p[0] for p in partons),
                    "parton_pt_max": max([pt(float(p[6]), float(p[7])) for p in partons], default=0.0),
                    "lhe_pair_pt": pt(px, py),
                    "lhe_scalup": float(hdr[3]),
                    "key": tuple(round(float(q[6]), 3) for q in quirks) + tuple(round(float(q[8]), 3) for q in quirks),
                    "q1_px": float(quirks[0][6]), "q1_py": float(quirks[0][7]), "q1_pz": float(quirks[0][8]),
                    "q2_px": float(quirks[1][6]), "q2_py": float(quirks[1][7]), "q2_pz": float(quirks[1][8]),
                })
                continue
            if in_ev:
                if s and not s.startswith("<"):
                    lines.append(s)
                elif s.startswith("<"):
                    # stop collecting particle lines at first tag
                    pass
    return events


def read_hepmc(path):
    events, cur = [], None
    units = set()

    def flush():
        if cur is not None:
            events.append(cur)

    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("E "):
                flush()
                t = line.split()
                cur = {"hepmc_seq": len(events), "hepmc_evnum": int(t[1]),
                       "n_vtx": int(t[8]), "weight": float(t[-1]), "q": {}, "n_final": 0}
            elif line.startswith("U "):
                units.add(line.strip())
            elif line.startswith("P ") and cur is not None:
                t = line.split()
                pdg, st = int(t[2]), int(t[8])
                if st == 1:
                    cur["n_final"] += 1
                if abs(pdg) == QPDG:
                    cur["q"].setdefault(st, []).append(
                        (pdg, float(t[3]), float(t[4]), float(t[5]), float(t[6]), float(t[7])))
    flush()
    return events, units


def pair_pt(qs):
    if qs is None or len(qs) != 2:
        return None
    return pt(qs[0][1] + qs[1][1], qs[0][2] + qs[1][2])


def eta(px, py, pz):
    p = math.sqrt(px * px + py * py + pz * pz)
    return 0.5 * math.log((p + pz) / (p - pz)) if p != abs(pz) else math.copysign(1e9, pz)


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = {}
    for name, d in SAMPLES.items():
        lhe_path = f"{d}/unweighted_events.lhe.gz"
        hep_path = f"{d}/tag_1_pythia8_events.hepmc.gz"
        lhe = read_lhe(lhe_path)
        hep, units = read_hepmc(hep_path)

        key_to_lhe = {}
        for e in lhe:
            key_to_lhe.setdefault(e["key"], []).append(e["lhe_idx"])

        hep_rows = []
        lhe_matched = {}
        status_census = {}
        for e in hep:
            for st, qs in e["q"].items():
                status_census[st] = status_census.get(st, 0) + len(qs)
            fin = e["q"].get(1, [])
            hard = e["q"].get(23, [])
            rec = e["q"].get(44, [])
            # last status-44 copies: one per quirk (the last two listed)
            last44 = None
            if rec:
                byp = {}
                for q in rec:
                    byp[q[0]] = q
                last44 = list(byp.values()) if len(byp) == 2 else None
            key = None
            if len(hard) == 2:
                key = tuple(round(q[1], 3) for q in hard) + tuple(round(q[3], 3) for q in hard)
            li = key_to_lhe.get(key, [None])
            lhe_idx = li[0] if len(li) == 1 else (None if li == [None] else "AMBIGUOUS")
            if lhe_idx is None and len(hard) == 2:
                # rounding-boundary fallback: nearest LHE event within 1e-3 GeV
                best, bd = None, 1e9
                for le in lhe:
                    dd = max(abs(hard[0][1] - le["q1_px"]), abs(hard[0][3] - le["q1_pz"]),
                             abs(hard[1][1] - le["q2_px"]), abs(hard[1][3] - le["q2_pz"]))
                    if dd < bd:
                        best, bd = le["lhe_idx"], dd
                if bd < 1e-3:
                    lhe_idx = best
            if isinstance(lhe_idx, int):
                lhe_matched[lhe_idx] = e["hepmc_seq"]
            ptf = pair_pt(fin)
            row = {
                "sample": name, "hepmc_seq": e["hepmc_seq"], "hepmc_evnum": e["hepmc_evnum"],
                "lhe_idx": lhe_idx, "n_final_quirks": len(fin), "n_final_state": e["n_final"],
                "pair_pt_final_status1": ptf,
                "pair_pt_hard_status23": pair_pt(hard),
                "pair_pt_last_status44": pair_pt(last44),
                "trigger_strict_gt200_final": (ptf is not None and ptf > 200.0),
                "trigger_ge200_final": (ptf is not None and ptf >= 200.0),
            }
            if len(fin) == 2:
                for i, q in enumerate(fin, 1):
                    row[f"pdg{i}"] = q[0]
                    row[f"px{i}"], row[f"py{i}"], row[f"pz{i}"], row[f"E{i}"], row[f"m{i}"] = q[1:]
                    row[f"pt{i}"] = pt(q[1], q[2])
                    row[f"eta{i}"] = eta(q[1], q[2], q[3])
            hep_rows.append(row)

        for e in lhe:
            e["passed_mlm"] = e["lhe_idx"] in lhe_matched
            e["hepmc_seq"] = lhe_matched.get(e["lhe_idx"])
            e["key"] = None

        import csv
        with open(f"{OUT}/{name}_lhe_events.csv", "w", newline="") as f:
            cols = [k for k in lhe[0] if k != "key"]
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(lhe)
        cols = sorted({k for r in hep_rows for k in r}, key=lambda k: list(hep_rows[0]).index(k) if k in hep_rows[0] else 999)
        with open(f"{OUT}/{name}_hepmc_events.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(hep_rows)

        n_two = sum(r["n_final_quirks"] == 2 for r in hep_rows)
        boundary = [r["pair_pt_final_status1"] for r in hep_rows
                    if r["pair_pt_final_status1"] is not None and abs(r["pair_pt_final_status1"] - 200) < 1.0]
        by_mult = {}
        for e in lhe:
            m = e["n_partons_final"]
            b = by_mult.setdefault(m, {"lhe": 0, "matched": 0})
            b["lhe"] += 1
            b["matched"] += e["passed_mlm"]
        summary[name] = {
            "lhe_path": lhe_path, "lhe_sha256": sha256(lhe_path),
            "hepmc_path": hep_path, "hepmc_sha256": sha256(hep_path),
            "hepmc_units": sorted(units),
            "N_generated_LHE": len(lhe),
            "N_hepmc_events": len(hep),
            "N_hepmc_with_2_final_quirks": n_two,
            "N_hepmc_mapped_to_unique_LHE": sum(isinstance(r["lhe_idx"], int) for r in hep_rows),
            "quirk_status_census": {str(k): v for k, v in sorted(status_census.items())},
            "N_trigger_strict_gt200_final": sum(r["trigger_strict_gt200_final"] for r in hep_rows),
            "N_trigger_ge200_final": sum(r["trigger_ge200_final"] for r in hep_rows),
            "N_trigger_gt200_hard_status23": sum((r["pair_pt_hard_status23"] or 0) > 200 for r in hep_rows),
            "N_trigger_gt200_last_status44": sum((r["pair_pt_last_status44"] or 0) > 200 for r in hep_rows),
            "pair_pt_within_1GeV_of_200": boundary,
            "LHE_events_with_pair_pt_gt200_parton_level": sum(e["lhe_pair_pt"] > 200 for e in lhe),
            "matching_by_LHE_parton_multiplicity": {str(k): v for k, v in sorted(by_mult.items())},
            "max_abs_final_minus_status44_pairpt": max(
                (abs(r["pair_pt_final_status1"] - r["pair_pt_last_status44"]) for r in hep_rows
                 if r["pair_pt_final_status1"] is not None and r["pair_pt_last_status44"] is not None), default=None),
        }
    with open(f"{OUT}/raw_recount_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
