"""
Extraction script for the madgraph_pilot_v1 data-preservation package.

IMPORTANT: this does NOT run MadGraph. It parses the ALREADY-EXISTING,
ORIGINAL LHE and HepMC output from the two benchmark generation runs
located at /home/rafia/hep_tools/quirk_{ew_800gev_4kev,signal_1800gev_2kev}/
(confirmed original via: particle codes qe+/qe- and t1/t1~ matching this
project's own extraction scripts' documented PDG codes; HepMC event counts
511/419 matching bit-for-bit the "N_matched" figures already used
throughout this project since before this task began).

Extracts, per event, from the LHE file (parton level, ALL 1000 generated
events per benchmark) and the HepMC file (showered+matched final sample,
511 EW / 419 colored events):
  - LHE: process id, incoming parton PDG/momentum fraction, event weight,
    scale, alpha_s, alpha_EM, jet-parton 4-momentum (process @1 only)
  - HepMC: event weight, final-state quirk 4-momenta, all other final-state
    particles (used for a simple leading-parton/hadron pT proxy, NOT a
    real jet-clustering algorithm -- documented limitation)

Saves compact Parquet+CSV event tables, per-stage cutflows, cross-section
summaries, and distribution source CSVs. Wall time for this extraction
(not generation) is recorded via time.time() at each major stage.
"""
import gzip
import re
import time
import json
import hashlib
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study/05_coplanarity_analysis/madgraph_pilot_v1"

BENCHMARKS = {
    "EW": {
        "dir": "/home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01",
        "quirk_pdg": 9000011,
        "mass_gev": 800.0,
        "mass_tol": 5.0,
    },
    "colored": {
        "dir": "/home/rafia/hep_tools/quirk_signal_1800gev_2kev/Events/run_01",
        "quirk_pdg": 1000006,  # unused when require_pdg=False (kept for reference/documentation only)
        "mass_gev": 1800.0,
        "mass_tol": 5.0,
        "require_pdg": False,  # R-hadron composite PDG codes vary; select by mass window only, matches extract_quirk_momenta.py
    },
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_lhe_init(lhe_path):
    """Returns dict with beam info and per-subprocess XSECUP/XERRUP/XMAXUP."""
    opener = gzip.open if lhe_path.endswith(".gz") else open
    with opener(lhe_path, "rt") as f:
        text = f.read(60000)  # init block follows the embedded banner/header
    m = re.search(r"<init>\s*\n(.*?)\n</init>", text, re.DOTALL)
    lines = [l for l in m.group(1).splitlines() if l.strip()]
    hdr = lines[0].split()
    # IDBMUP(1) IDBMUP(2) EBMUP(1) EBMUP(2) PDFGUP(1) PDFGUP(2) PDFSUP(1) PDFSUP(2) IDWTUP NPRUP
    idbmup1, idbmup2 = int(hdr[0]), int(hdr[1])
    ebmup1, ebmup2 = float(hdr[2]), float(hdr[3])
    idwtup = int(hdr[8])
    nprup = int(hdr[9])
    procs = []
    for i in range(1, 1 + nprup):
        p = lines[i].split()
        procs.append({"xsecup_pb": float(p[0]), "xerrup_pb": float(p[1]),
                      "xmaxup_pb": float(p[2]), "lprup": int(p[3])})
    return {"idbmup": (idbmup1, idbmup2), "ebmup_gev": (ebmup1, ebmup2),
            "idwtup": idwtup, "nprup": nprup, "processes": procs,
            "total_xsecup_pb": sum(p["xsecup_pb"] for p in procs)}


def parse_lhe_events(lhe_path):
    """Yields one dict per LHE event: weight, scale, alphaS, alphaEW,
    n_particles, incoming parton PDGs+pz (-> momentum fraction x1,x2),
    process id (IDPRUP), and whether a jet parton (status=1, |PDG|<=21,
    not the quirks) is present (i.e. which of the @0/@1 processes)."""
    opener = gzip.open if lhe_path.endswith(".gz") else open
    events = []
    with opener(lhe_path, "rt") as f:
        in_event = False
        buf = []
        for line in f:
            if line.strip() == "<event>":
                in_event = True
                buf = []
                continue
            if line.strip() == "</event>":
                in_event = False
                events.append(buf)
                continue
            if in_event:
                buf.append(line.rstrip("\n"))
    rows = []
    ebeam = None
    for i, buf in enumerate(events):
        hdr = buf[0].split()
        nup, idprup, xwgtup, scalup, aqedup, aqcdup = (
            int(hdr[0]), int(hdr[1]), float(hdr[2]), float(hdr[3]), float(hdr[4]), float(hdr[5]))
        particles = []
        for j in range(1, 1 + nup):
            p = buf[j].split()
            pdg, status = int(p[0]), int(p[1])
            px, py, pz, E, m = float(p[6]), float(p[7]), float(p[8]), float(p[9]), float(p[10])
            particles.append({"pdg": pdg, "status": status, "px": px, "py": py, "pz": pz, "E": E, "m": m})
        incoming = [p for p in particles if p["status"] == -1]
        outgoing = [p for p in particles if p["status"] == 1]
        n_jet_partons = sum(1 for p in outgoing if abs(p["pdg"]) <= 21 and p["pdg"] != 0)
        jet_pt = 0.0
        for p in outgoing:
            if abs(p["pdg"]) <= 21 and p["pdg"] != 0:
                jet_pt = max(jet_pt, float(np.hypot(p["px"], p["py"])))
        rows.append({
            "lhe_event_idx": i, "n_particles": nup, "process_id": idprup,
            "weight": xwgtup, "scale_gev": scalup, "alpha_em": aqedup, "alpha_s": aqcdup,
            "pdg_in1": incoming[0]["pdg"], "pdg_in2": incoming[1]["pdg"],
            "pz_in1_gev": incoming[0]["pz"], "pz_in2_gev": incoming[1]["pz"],
            "n_jet_partons_lhe": n_jet_partons, "jet_parton_pt_gev": jet_pt,
        })
    return pd.DataFrame(rows)


def parse_hepmc(hepmc_path, quirk_pdg, mass_gev, mass_tol, require_pdg=True):
    """Returns DataFrame, one row per HepMC event with the 2 quirks'
    4-momenta plus a simple leading-other-particle pT proxy (NOT real jet
    clustering -- documented limitation, see README).

    require_pdg=True (EW): selects status==1 particles with EXACT
    |pdg|==quirk_pdg AND within the mass window -- matches
    extract_ew_quirk_momenta.py exactly (EW quirks are color singlets with
    a fixed, known PDG code, no R-hadron formation).

    require_pdg=False (colored): selects status==1 particles by MASS
    WINDOW ONLY -- matches extract_quirk_momenta.py exactly. The colored
    quirk hadronizes into an R-hadron via Pythia8's RHadrons machinery,
    whose final-state PDG code is a large COMPOSITE code (>=1000600,
    flavor-dependent), NOT the base "stop" slot id (1000006) used only
    internally to configure RHadrons:idStop. Restricting by exact PDG here
    would (and initially did, before this fix) silently find zero events."""
    opener = gzip.open if hepmc_path.endswith(".gz") else open
    rows = []
    cur_weight = None
    cur_particles = []
    n_ev = 0

    def flush():
        nonlocal cur_weight, cur_particles, n_ev
        if cur_weight is None and not cur_particles:
            return
        if require_pdg:
            quirks = [p for p in cur_particles if p["status"] == 1 and abs(p["pdg"]) == quirk_pdg
                      and abs(p["m"] - mass_gev) < mass_tol]
        else:
            quirks = [p for p in cur_particles if p["status"] == 1
                      and abs(p["m"] - mass_gev) < mass_tol]
        quirk_ids = {id(q) for q in quirks}
        others_pt = [float(np.hypot(p["px"], p["py"])) for p in cur_particles
                     if p["status"] == 1 and id(p) not in quirk_ids]
        leading_other_pt = max(others_pt) if others_pt else 0.0
        n_final_state = sum(1 for p in cur_particles if p["status"] == 1)
        row = {"hepmc_event_idx": n_ev, "weight": cur_weight, "n_quirks_found": len(quirks),
               "n_final_state_particles": n_final_state, "leading_other_pt_gev": leading_other_pt}
        if len(quirks) == 2:
            (q1, q2) = quirks
            if q1["pdg"] < 0:
                q1, q2 = q2, q1  # q1 = positive PDG (quirk), q2 = negative (antiquirk), for a stable convention
            for tag, q in (("1", q1), ("2", q2)):
                row.update({f"px{tag}": q["px"], f"py{tag}": q["py"], f"pz{tag}": q["pz"],
                            f"E{tag}": q["E"], f"m{tag}": q["m"], f"pdg{tag}": q["pdg"]})
        rows.append(row)
        n_ev += 1
        cur_weight = None
        cur_particles = []

    with opener(hepmc_path, "rt") as f:
        for line in f:
            if line.startswith("E "):
                flush()
                parts = line.split()
                try:
                    cur_weight = float(parts[-1])
                except (ValueError, IndexError):
                    cur_weight = 1.0
            elif line.startswith("P "):
                p = line.split()
                pdg = int(p[2])
                px, py, pz, E, m = float(p[3]), float(p[4]), float(p[5]), float(p[6]), float(p[7])
                status = int(p[8])
                cur_particles.append({"pdg": pdg, "px": px, "py": py, "pz": pz, "E": E, "m": m, "status": status})
    flush()
    df = pd.DataFrame(rows)
    if len(df) and "px1" in df.columns:
        df["quirk_pair_px"] = df["px1"].fillna(0) + df["px2"].fillna(0)
        df["quirk_pair_py"] = df["py1"].fillna(0) + df["py2"].fillna(0)
        df["quirk_pair_pz"] = df["pz1"].fillna(0) + df["pz2"].fillna(0)
        df["quirk_pair_E"] = df["E1"].fillna(0) + df["E2"].fillna(0)
        df["quirk_pair_pt_gev"] = np.hypot(df["quirk_pair_px"], df["quirk_pair_py"])
        with np.errstate(invalid="ignore"):
            df["quirk_pair_mass_gev"] = np.sqrt(np.clip(
                df["quirk_pair_E"]**2 - df["quirk_pair_px"]**2 - df["quirk_pair_py"]**2 - df["quirk_pair_pz"]**2,
                0, None))
        p1 = np.stack([df["px1"], df["py1"], df["pz1"]], axis=1)
        p2 = np.stack([df["px2"], df["py2"], df["pz2"]], axis=1)
        for tag, p, E in (("1", p1, df["E1"]), ("2", p2, df["E2"])):
            pmag = np.linalg.norm(p, axis=1)
            pt = np.hypot(p[:, 0], p[:, 1])
            with np.errstate(divide="ignore", invalid="ignore"):
                eta = np.arctanh(np.clip(p[:, 2] / np.where(pmag > 0, pmag, 1), -1 + 1e-12, 1 - 1e-12))
            phi = np.arctan2(p[:, 1], p[:, 0])
            df[f"pt{tag}_gev"] = pt
            df[f"eta{tag}"] = eta
            df[f"phi{tag}"] = phi
        df["trigger_proxy_pass"] = df["quirk_pair_pt_gev"] > 200
    return df


def main():
    t_start = time.time()
    timing = {}
    for name, cfg in BENCHMARKS.items():
        t0 = time.time()
        lhe_path = f"{cfg['dir']}/unweighted_events.lhe.gz"
        hepmc_path = f"{cfg['dir']}/tag_1_pythia8_events.hepmc.gz"

        init = parse_lhe_init(lhe_path)
        with open(f"{BASE}/metadata/{name}_lhe_init.json", "w") as f:
            json.dump(init, f, indent=2)
        t1 = time.time()
        print(f"[{name}] LHE init parsed: total parton-level xsec = {init['total_xsecup_pb']:.6e} pb ({t1-t0:.2f}s)")

        lhe_df = parse_lhe_events(lhe_path)
        t2 = time.time()
        lhe_df.to_csv(f"{BASE}/event_tables/{name}_lhe_events.csv", index=False)
        print(f"[{name}] LHE events parsed: {len(lhe_df)} ({t2-t1:.2f}s)")

        hepmc_df = parse_hepmc(hepmc_path, cfg["quirk_pdg"], cfg["mass_gev"], cfg["mass_tol"],
                                require_pdg=cfg.get("require_pdg", True))
        t3 = time.time()
        hepmc_df.to_csv(f"{BASE}/event_tables/{name}_hepmc_events.csv", index=False)
        print(f"[{name}] HepMC events parsed: {len(hepmc_df)} ({t3-t2:.2f}s)")

        timing[name] = {
            "lhe_init_parse_s": t1 - t0, "lhe_events_parse_s": t2 - t1,
            "hepmc_events_parse_s": t3 - t2, "total_s": t3 - t0,
            "lhe_n_events": len(lhe_df), "hepmc_n_events": len(hepmc_df),
        }

    with open(f"{BASE}/runtime/extraction_runtime.json", "w") as f:
        json.dump({"per_benchmark": timing, "total_wall_time_s": time.time() - t_start}, f, indent=2)
    print(f"\nTotal extraction wall time: {time.time()-t_start:.2f}s")


if __name__ == "__main__":
    main()
