#!/usr/bin/env python3
"""Config checks (2026-10-12, D36): config/detector.yaml, reconstruction.yaml, benchmarks.yaml read through analysis_config.
  1 the three files load and validate (strict: unknown / missing keys, options, Table I Lambda list, layer order)
  2 the loader rejects: an unknown key, a missing key, a production Lambda outside the Table I list, a primary SCT z outside its options
  3 the values installed in the code (P4 globals, trajectory_to_hits layers, step floor, beam spot, cuts) equal the values used for the
    stored results before the config existed (literals of P4 / P18 / coplanarity_fit, kept here as the reference)
  4 the signal-scope inputs agree with the production runs (generator seeds, processes, trigger) and every signal-scope key is read
Prints the config sha256. Exit code 1 on any failure."""
import os, sys, copy, shutil, tempfile, importlib.util, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analysis_config as AC
ok = []
def check(name, cond, info=""):
    ok.append(bool(cond)); print(f"{'PASS' if cond else 'FAIL'}  {name} {info}", flush=True)
cfg = AC.load(); check("1 config loads and validates", True, f"(sha256 {cfg.sha256[:16]}...)")
def broken(edit, expect):
    d = tempfile.mkdtemp()
    for f in AC.FILES: shutil.copy(os.path.join(AC.CDIR, f), d)
    y = {f: yaml.safe_load(open(os.path.join(d, f))) for f in AC.FILES}; edit(y)
    for f in AC.FILES: yaml.safe_dump(y[f], open(os.path.join(d, f), "w"))
    try: AC.load(d); return False
    except AC.ConfigError as e: return expect in str(e)
    finally: shutil.rmtree(d)
check("2a unknown key rejected", broken(lambda y: y["detector.yaml"]["beamspot"].update(sigma_z_cm=4.5), "unknown key"))
check("2b missing key rejected", broken(lambda y: y["reconstruction.yaml"]["cuts"].pop("seed_delta_z_mm"), "missing key"))
check("2c Lambda outside Table I rejected", broken(lambda y: y["benchmarks.yaml"]["colored"].update(lambda_ev_production=4000), "Table I"))
check("2d SCT z primary outside options rejected", broken(lambda y: y["detector.yaml"]["sct"].update(z_sigma_mm=0.3), "z_sigma_options"))
sys.path.insert(0, "/home/rafia/coplanarity_study/04_detector_sim"); import trajectory_to_hits as t0
ref_layers = copy.deepcopy(t0.LAYERS); ref_min, ref_bs = t0.MIN_STEPS_PER_PERIOD, t0.BEAMSPOT_SIGMA_Z_CM
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4); p4._init()
R = p4.R
check("3a P4.HALF", p4.HALF == {1: 33.015, 2: 40.05, 3: 40.05, 4: 40.05, 5: 74.9, 6: 74.9, 7: 74.9, 8: 74.9})
check("3b P4.SZ", p4.SZ == {"Z1160": 0.1160, "Z580": 0.0580, "Z34": 0.0034, "Z0": 0.0})
check("3c P4.PAR", p4.PAR == {"EW": (800.0, 4e-6), "COL": (1800.0, 2e-6)})
check("3d beam spot (fp.SIG_Z0, tth)", p4.fp.SIG_Z0 == 4.5 and p4.tth.BEAMSPOT_SIGMA_Z_CM == ref_bs == 4.5)
check("3e detector layers (radius, pitch, effective resolution)", p4.tth.LAYERS == ref_layers)
check("3f steps per period", p4.tth.MIN_STEPS_PER_PERIOD == ref_min == 300)
check("3g seeding / iterative cuts", R["seed"] == dict(dphi_seed_max=0.1, dz_seed_max_cm=2.0, ds_seed_max_cm=0.05, dw_seed_max_cm=1.0, ds_iter_max_cm=0.05, dw_iter_max_cm=1.0, growth_factor_max=3.0))
check("3h final cuts, timing, SCT r-phi, B, max radius", (R["final_dw_cm"], R["signal_ds_cm"], R["timing_ns"], R["sct_rphi_cm"], R["B_tesla"], R["max_layer_r_cm"]) == (1.0, 0.01, 25.0, 34e-4, 2.0, 60.0))
check("3i primary settings", (R["sct_primary"], R["hit_mode"], R["mult_rule"]) == ("Z0", "first_crossing", "at_least_2"))
try: p4.CFG.validate_signal_inputs(); p4.CFG.assert_used("signal"); check("4 production inputs and signal-scope keys", True)
except AC.ConfigError as e: check("4 production inputs and signal-scope keys", False, str(e))
print("config sha256", cfg.sha256); print("RESULT:", "all checks passed" if all(ok) else f"{ok.count(False)} check(s) failed"); sys.exit(0 if all(ok) else 1)
