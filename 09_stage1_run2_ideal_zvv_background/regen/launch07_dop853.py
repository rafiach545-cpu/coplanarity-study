#!/usr/bin/env python3
"""09 regen (2026-11-22): run 07_atlas_real_geometry/signal/G01_signal_07.py unchanged, with the DOP853 integrator.
Sets QUIRK_INTEGRATOR=dop853 (read inside trajectory_to_hits.simulate_quirk_hits) and gives DOP853 the crossing surfaces of the chosen 07
geometry (barrel radii and, for atlas, the disk planes z = z_d), so that every element crossing is refined by the dense output.
The worker pool of G01 forks after this, so the settings reach the workers (Linux fork start method; checked below).
Usage: launch07_dop853.py <G01 arguments: geom tag band --input CSV --out DIR --workers K>"""
import os, sys, runpy, multiprocessing as mp
BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path[:0] = [f"{BASE}/03_trajectory_sim", f"{BASE}/07_atlas_real_geometry/sim", f"{BASE}/04_detector_sim"]
assert mp.get_start_method(allow_none=False) == "fork", "G01 workers must inherit the DOP853 settings (fork start method)"
os.environ["QUIRK_INTEGRATOR"] = "dop853"
import quirk_trajectory_dop853 as Q                     # noqa: E402
import detsim07                                         # noqa: E402
geom = sys.argv[1]; els = detsim07.build(geom)
Q.RTOL = float(os.environ.get("DOP853_RTOL", "1e-10")); Q.ATOL_X = 1e-7 / Q.CM * Q.RTOL / 1e-10; Q.ATOL_P = 1e-10 * Q.RTOL / 1e-10
Q.RADII_CM = sorted({e["r_cm"] for e in els if e["kind"] == "barrel"}); Q.ZPLANES_CM = sorted({e["z_cm"] for e in els if e["kind"] == "disk"})
Q.T_STOP_NS = None
print(f"launch07_dop853: geom {geom}, rtol {Q.RTOL:g}, {len(Q.RADII_CM)} barrel radii, {len(Q.ZPLANES_CM)} disk planes", flush=True)
sys.argv = [f"{BASE}/07_atlas_real_geometry/signal/G01_signal_07.py"] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
