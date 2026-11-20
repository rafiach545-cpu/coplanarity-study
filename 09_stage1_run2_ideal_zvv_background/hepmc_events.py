"""09 step B02 (2026-11-19): streaming reader for the HepMC2 (IO_GenEvent) files written by MG5 + Pythia8.
iter_events(path) yields one dict per event:
  event (index in the file), weight (nominal = first weight of the E line), met_x / met_y / met (GeV, vector sum of the status-1
  neutrinos 12/14/16), and the status-1 CHARGED particles as numpy arrays: pdg, q (e), px, py, pz, m (GeV) and the production vertex
  vx, vy, vz (cm; the HepMC file is in MM, converted here) relative to Pythia's origin (the hard interaction).
Format (HepMC 2.06 IO_GenEvent): 'V barcode id x y z ctau n_orphan n_out ...' is followed by its n_orphan incoming orphan particles and then
its n_out outgoing particles; an outgoing particle's production vertex is that V. 'P barcode pdg px py pz E m status ...'.
Status-1 quirks (QUIRKS) are listed in ev['quirks'] as (pdg, px, py, pz, E, m) and are not in the charged arrays (added 2026-11-19 for B05).
Charge from Pythia8's own particle table (same Pythia 8.312 as the generation)."""
import gzip, os, numpy as np

import sys as _sys
os.environ.setdefault("PYTHIA8DATA", f"{_sys.prefix}/share/Pythia8/xmldoc")   # the running conda env (hep or g4: both Pythia 8.312)
NEUTRINOS = {12, 14, 16}
QUIRKS = {9000011}          # EW quirk (Stage 1 signal model): returned separately in ev["quirks"], never as an ordinary charged particle
_Q = {}


def charge(pdg):
    if pdg not in _Q:
        global _PD
        if "_PD" not in globals():
            import pythia8
            _PD = pythia8.Pythia("", False).particleData
        _Q[pdg] = float(_PD.charge(pdg))
    return _Q[pdg]


def _finish(ev, rows):
    a = np.array(rows, dtype=float).reshape(-1, 10)
    ev.update(pdg=a[:, 0].astype(int), q=a[:, 1], px=a[:, 2], py=a[:, 3], pz=a[:, 4], m=a[:, 5], vx=a[:, 6], vy=a[:, 7], vz=a[:, 8])
    ev["met"] = float(np.hypot(ev["met_x"], ev["met_y"]))
    return ev


def iter_events(path, max_events=None):
    op = gzip.open if path.endswith(".gz") else open
    ev, rows, n, unit_mm = None, [], 0, None
    vxyz, n_orphan_left = (0.0, 0.0, 0.0), 0
    with op(path, "rt") as f:
        for line in f:
            t = line[0]
            if t == "E":
                if ev is not None:
                    yield _finish(ev, rows); n += 1
                    if max_events is not None and n >= max_events: return
                p = line.split(); nrand = int(p[11]); nw = int(p[12 + nrand])
                ev = dict(event=n, weight=float(p[13 + nrand]) if nw > 0 else 1.0, met_x=0.0, met_y=0.0, quirks=[]); rows = []
            elif t == "U":
                unit_mm = line.split()[2] == "MM"; assert unit_mm, f"length unit is not MM: {line}"
            elif t == "V":
                p = line.split(); s = 0.1                                   # mm -> cm
                vxyz = (float(p[3]) * s, float(p[4]) * s, float(p[5]) * s); n_orphan_left = int(p[7])
            elif t == "P":
                if n_orphan_left > 0: n_orphan_left -= 1; continue            # incoming orphan: not produced at this vertex
                p = line.split()
                if int(p[8]) != 1: continue
                pdg = int(p[2]); px, py, pz = float(p[3]), float(p[4]), float(p[5])
                if abs(pdg) in NEUTRINOS: ev["met_x"] += px; ev["met_y"] += py; continue
                if abs(pdg) in QUIRKS: ev["quirks"].append((pdg, px, py, pz, float(p[6]), float(p[7]))); continue   # (pdg, px, py, pz, E, m)
                q = charge(pdg)
                if q == 0: continue
                rows.append((pdg, q, px, py, pz, float(p[7]), *vxyz, 0.0))
    if ev is not None and (max_events is None or n < max_events):
        yield _finish(ev, rows)
