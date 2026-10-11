#!/usr/bin/env python3
"""P22a (2026-10-08, D11): minimum-bias pools for the pile-up generator variants. Same code as
02_backgrounds/pileup/generate_ancestry_pool.py (same 20 000 events, seed 20260916, 13 TeV, ancestry classification), only the
Pythia process/tune lines differ. Variants: MB_INEL_MONASH = SoftQCD:inelastic (default tune = Monash);
MB_ND_A2 = SoftQCD:nonDiffractive + Tune:pp = 5 (A2-CTEQ6L1). Baseline pool (unchanged): SoftQCD:nonDiffractive, Monash.
Writes 02_backgrounds/pileup/minbias_pool_20000_<VARIANT>_v1.csv (refuses to overwrite)."""
import os, sys, time
os.environ.setdefault("PYTHIA8DATA", "/home/rafia/miniconda3/envs/hep/share/Pythia8/xmldoc")
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/pileup")
import pythia8, generate_ancestry_pool as gap
VAR = {"MB_INEL_MONASH": ["SoftQCD:inelastic = on"], "MB_ND_A2": ["SoftQCD:nonDiffractive = on", "Tune:pp = 5"]}
def make_pythia_variant(lines):
    def mk(seed, ecm_gev=13000.0):
        p = pythia8.Pythia("", False)
        for s in ["Beams:idA = 2212", "Beams:idB = 2212", f"Beams:eCM = {ecm_gev}"] + lines + ["Beams:allowVertexSpread = off", "Random:setSeed = on", f"Random:seed = {seed}", "Print:quiet = on"]:
            p.readString(s)
        assert p.init(); return p, p.settings.parm("Pythia:versionNumber")
    return mk
if __name__ == "__main__":
    v = sys.argv[1]; out = f"/home/rafia/coplanarity_study/02_backgrounds/pileup/minbias_pool_20000_{v}_v1.csv"
    if os.path.exists(out): raise FileExistsError(out)
    gap.make_pythia = make_pythia_variant(VAR[v]); t0 = time.time()
    st = gap.generate_ancestry_pool_streaming(20000, 20260916, out)
    print(v, "Pythia", st["actual_version"], "n_ok", st["n_ok"], "particles", st["n_particles_total"], "labels", st["label_counts"], f"{time.time()-t0:.0f}s", flush=True)
