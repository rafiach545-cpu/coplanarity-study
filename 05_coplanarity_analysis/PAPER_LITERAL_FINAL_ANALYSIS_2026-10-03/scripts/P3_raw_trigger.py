#!/usr/bin/env python3
"""
Phase 3: independent raw recount of generated / matched / trigger counts for the four frozen samples,
directly from the frozen LHE and HepMC files (read-only; stdlib + numpy only; no project code).

Quirk-pair pT is evaluated at three levels:
  hard      : the two hard-process (status 23) quirks (EW |id|=9000011; colored |id|=1000006)
  shower    : the LAST copy in the record of each hard-process quirk species before hadronisation
              (EW: the final quirk; colored: last |id|=1000006 entry, i.e. post-shower pre-hadronisation)
  final     : status-1 objects (EW: quirks; colored: stop R-hadrons, 1000000 <= |id| < 1100000)
Trigger (paper): pT of the quirk/anti-quirk centre-of-mass system > 200 GeV (strict), at the final level;
denominator = matched events (= events written to the HepMC after the MLM veto, each with 2 final objects).
"""
import gzip, json, math, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
H = "/home/rafia/hep_tools"
SAMPLES = {"EW1000": (f"{H}/quirk_ew_800gev_4kev/Events/run_01", "EW"),
           "EW2000": (f"{H}/quirk_2000_fresh_regen_runs/EW_800GeV_L4keV/Events/run_fresh", "EW"),
           "COL1000": (f"{H}/quirk_signal_1800gev_2kev/Events/run_01", "COL"),
           "COL2000": (f"{H}/quirk_2000_fresh_regen_runs/colored_1800GeV_L2keV/Events/run_fresh", "COL")}


def sha(p):
    h = hashlib.sha256(); f = open(p, "rb")
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)
    return h.hexdigest()


def pairpt(objs):
    return math.hypot(objs[0][1] + objs[1][1], objs[0][2] + objs[1][2]) if len(objs) == 2 else None


out, per = {}, []
for s, (d, b) in SAMPLES.items():
    lhe = f"{d}/unweighted_events.lhe.gz"; hep = f"{d}/tag_1_pythia8_events.hepmc.gz"
    n_lhe = sum(1 for l in gzip.open(lhe, "rt") if l.lstrip().startswith("<event"))
    hard_id = 9000011 if b == "EW" else 1000006
    events, cur = [], None
    for line in gzip.open(hep, "rt"):
        if line.startswith("E "):
            if cur is not None:
                events.append(cur)
            cur = dict(hard=[], last={}, final=[], units=None)
        elif line.startswith("P ") and cur is not None:
            t = line.split(); pid, st = int(t[2]), int(t[8]); px, py = float(t[3]), float(t[4])
            a = abs(pid)
            if a == hard_id:
                if st == 23:
                    cur["hard"].append((pid, px, py))
                cur["last"][pid] = (pid, px, py)
            if st == 1 and ((b == "EW" and a == 9000011) or (b == "COL" and 1000000 <= a < 1100000)):
                cur["final"].append((pid, px, py))
    events.append(cur)
    n_two = sum(len(e["final"]) == 2 for e in events)
    lv = {"hard": [pairpt(e["hard"]) for e in events], "shower": [pairpt(list(e["last"].values())) for e in events],
          "final": [pairpt(e["final"]) for e in events]}
    trig = {k: sum(1 for v in vals if v is not None and v > 200.0) for k, vals in lv.items()}
    near = [v for v in lv["final"] if v is not None and abs(v - 200) < 1.0]
    out[s] = dict(lhe=lhe, lhe_sha256=sha(lhe), hepmc=hep, hepmc_sha256=sha(hep), generated=n_lhe, matched=len(events),
                  matched_with_2_final_objects=n_two, trigger_final=trig["final"], trigger_hard_status23=trig["hard"],
                  trigger_post_shower_pre_hadronisation=trig["shower"], trigger_final_ge200=sum(1 for v in lv["final"] if v is not None and v >= 200),
                  events_within_1GeV_of_threshold=near)
    for i, (h, sh, f) in enumerate(zip(lv["hard"], lv["shower"], lv["final"])):
        per.append(dict(sample=s, hepmc_seq=i, pair_pt_hard=h, pair_pt_post_shower=sh, pair_pt_final=f))
json.dump(out, open(f"{T}/P3_raw_trigger_recount.json", "w"), indent=1)
import csv
with open(f"{T}/P3_raw_pair_pt_levels_per_event.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(per[0])); w.writeheader(); w.writerows(per)
for s, v in out.items():
    print(s, {k: v[k] for k in ("generated", "matched", "matched_with_2_final_objects", "trigger_final", "trigger_final_ge200",
                                "trigger_post_shower_pre_hadronisation", "trigger_hard_status23", "events_within_1GeV_of_threshold")})
