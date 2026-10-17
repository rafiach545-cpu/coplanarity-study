#!/usr/bin/env python3
"""Strict loader for config/detector.yaml, config/reconstruction.yaml, config/benchmarks.yaml (2026-10-12).
Rules:
  - every leaf key must be declared in CONSUMERS below (unknown key -> error) and every declared key must be present (missing -> error);
  - every declared key names the code that reads it; a key without a consumer cannot be declared (no "written but unused" values);
  - values are validated (allowed options, primary setting inside its option list, production Lambda inside the Table I list, layer order);
  - `used` records which keys a run actually read; `assert_used(scope)` fails if a key of that scope was not read;
  - `sha256` is the hash of the three files (in that order); `write_provenance(path)` stores it with the resolved values next to an output.
Lengths in the files are in mm; `resolved` gives the values in the units the code uses (cm, GeV)."""
import os, json, hashlib, yaml

HERE = os.path.dirname(os.path.abspath(__file__)); CDIR = os.path.abspath(f"{HERE}/../config")
FILES = ("detector.yaml", "reconstruction.yaml", "benchmarks.yaml")
# leaf key -> (scope, consumer). scope "signal" keys must be read by every signal run.
CONSUMERS = {
    "detector.magnetic_field_t": ("signal", "P4.propagate / P18.job / D26.job: simulate_quirk_hits(B_tesla)"),
    "detector.beam_pipe_radius_mm": ("background", "atlas_geometry.BEAMPIPE_RADIUS_CM (conversion background)"),
    "detector.timing_cut_ns": ("signal", "P18.reco: hit kept if t < cut"),
    "detector.beamspot.sigma_z_mm": ("signal", "02_forensic_pipeline.SIG_Z0 and trajectory_to_hits.BEAMSPOT_SIGMA_Z_CM"),
    "detector.beamspot.mode": ("signal", "validated: only common_shift_fit_true_vertex is implemented (fp.stream_draws, P18.reco)"),
    "detector.sct.rphi_sigma_mm": ("signal", "P18.reco: SCT r-phi smearing"),
    "detector.sct.z_sigma_mm": ("signal", "primary SCT z setting (name of P4.SZ key)"),
    "detector.sct.z_sigma_options_mm": ("signal", "P4.SZ"),
    "detector.merge_hits_in": ("signal", "validated: only [pixel] is implemented (trajectory_to_hits.merge_neighboring_pixel_hits)"),
    "detector.layers": ("signal", "trajectory_to_hits.LAYERS (radius, pitch) and P4.HALF (half-length)"),
    "reconstruction.simulation.integrator": ("signal", "validated: P4._init installs quirk_trajectory_optimized_v2"),
    "reconstruction.simulation.steps_per_period": ("signal", "trajectory_to_hits.MIN_STEPS_PER_PERIOD"),
    "reconstruction.simulation.max_layer_radius_mm": ("signal", "simulate_quirk_hits(max_layer_r_cm)"),
    "reconstruction.hits.mode": ("signal", "primary hit mode (P18.reco first_only)"),
    "reconstruction.hits.mode_options": ("signal", "P18 modes"),
    "reconstruction.hits.multiplicity_rule": ("signal", "P18.reco hit-multiplicity cut"),
    "reconstruction.cuts.seed_delta_phi_rad": ("signal", "seeding_and_iterative_fit(dphi_seed_max)"),
    "reconstruction.cuts.seed_delta_z_mm": ("signal", "seeding_and_iterative_fit(dz_seed_max_cm)"),
    "reconstruction.cuts.seed_delta_s_max_mm": ("signal", "seeding_and_iterative_fit(ds_seed_max_cm)"),
    "reconstruction.cuts.seed_delta_w_max_mm": ("signal", "seeding_and_iterative_fit(dw_seed_max_cm)"),
    "reconstruction.cuts.iter_n1_max_mm": ("signal", "seeding_and_iterative_fit(ds_iter_max_cm)"),
    "reconstruction.cuts.iter_n2_max_mm": ("signal", "seeding_and_iterative_fit(dw_iter_max_cm)"),
    "reconstruction.cuts.iter_growth_factor_max": ("signal", "seeding_and_iterative_fit(growth_factor_max)"),
    "reconstruction.cuts.final_delta_w_max_mm": ("signal", "P18.reco event selection"),
    "reconstruction.cuts.signal_delta_s_max_mm": ("signal", "P18.reco signal region"),
    "reconstruction.cuts.prefilter": ("signal", "validated: none (no prefilter exists in the code)"),
    "benchmarks.colored.model": ("signal", "validated against the production banner process (P4.momenta samples)"),
    "benchmarks.colored.mass_gev": ("signal", "P4.PAR['COL']"),
    "benchmarks.colored.lambda_ev_table": ("signal", "validation of lambda_ev_production"),
    "benchmarks.colored.lambda_ev_production": ("signal", "P4.PAR['COL']"),
    "benchmarks.colored.charged_fraction": ("limits", "cross section x charged fraction (Fig. 6; not run)"),
    "benchmarks.colored.generator_seed": ("signal", "validated against the run banner (tables/generator_settings_2000.csv)"),
    "benchmarks.ew.model": ("signal", "as colored"),
    "benchmarks.ew.mass_gev": ("signal", "P4.PAR['EW']"),
    "benchmarks.ew.lambda_ev_table": ("signal", "validation of lambda_ev_production"),
    "benchmarks.ew.lambda_ev_production": ("signal", "P4.PAR['EW']"),
    "benchmarks.ew.charged_fraction": ("limits", "as colored"),
    "benchmarks.ew.generator_seed": ("signal", "validated against the run banner"),
    "benchmarks.trigger_pt_pair_min_gev": ("signal", "validated against the trigger selection of the momenta files (P3 recount)"),
    "benchmarks.luminosity_fb": ("limits", "Fig. 6 expected events (not run)"),
    "benchmarks.pileup_mu_signal": ("signal", "validated: signal path has no pile-up overlay"),
    "benchmarks.pileup_mu_background": ("background", "pile-up background scripts (P21)"),
}
LAYER_KEYS = {"pixel": {"id", "name", "kind", "radius_mm", "z_half_mm", "pitch_rphi_mm", "pitch_z_mm"}, "sct": {"id", "name", "kind", "radius_mm", "z_half_mm"}}


class ConfigError(Exception):
    pass


def _flatten(d, prefix, out):
    for k, v in d.items():
        p = f"{prefix}.{k}"
        if isinstance(v, dict): _flatten(v, p, out)
        else: out[p] = v
    return out


class Config:
    def __init__(self, cdir=CDIR):
        raw, h = {}, hashlib.sha256()
        for f in FILES:
            b = open(os.path.join(cdir, f), "rb").read(); h.update(b); raw[f.split(".")[0]] = yaml.safe_load(b)
        self.sha256 = h.hexdigest(); self.raw = raw
        flat = {}
        for top, d in raw.items():
            if not isinstance(d, dict): raise ConfigError(f"{top}.yaml: top level must be a mapping")
            _flatten(d, top, flat)
        unknown = sorted(set(flat) - set(CONSUMERS)); missing = sorted(set(CONSUMERS) - set(flat))
        if unknown: raise ConfigError(f"unknown key(s), not read by any code: {unknown}")
        if missing: raise ConfigError(f"missing key(s): {missing}")
        self._v = flat; self.used = set(); self._validate()

    def get(self, key):
        if key not in self._v: raise ConfigError(f"no such key: {key}")
        self.used.add(key); return self._v[key]

    def _validate(self):
        v = self._v; e = []
        if v["detector.beamspot.mode"] != "common_shift_fit_true_vertex": e.append("beamspot.mode: only common_shift_fit_true_vertex is implemented")
        if v["detector.merge_hits_in"] != ["pixel"]: e.append("merge_hits_in: only [pixel] is implemented")
        if v["detector.sct.z_sigma_mm"] not in v["detector.sct.z_sigma_options_mm"]: e.append("sct.z_sigma_mm not in z_sigma_options_mm")
        if v["reconstruction.hits.mode"] not in v["reconstruction.hits.mode_options"]: e.append("hits.mode not in mode_options")
        if not set(v["reconstruction.hits.mode_options"]) <= {"first_crossing", "all_crossings"}: e.append("hits.mode_options: unknown mode")
        if v["reconstruction.hits.multiplicity_rule"] not in ("at_least_2", "exactly_2"): e.append("multiplicity_rule: at_least_2 | exactly_2")
        if v["reconstruction.cuts.prefilter"] != "none": e.append("cuts.prefilter: only 'none' (the code has no prefilter)")
        if v["reconstruction.simulation.integrator"] != "quirk_trajectory_optimized_v2_rk4": e.append("simulation.integrator: only quirk_trajectory_optimized_v2_rk4")
        for b in ("colored", "ew"):
            if v[f"benchmarks.{b}.lambda_ev_production"] not in v[f"benchmarks.{b}.lambda_ev_table"]: e.append(f"{b}: production Lambda not in the Table I list")
            if not 0 < v[f"benchmarks.{b}.charged_fraction"] <= 1: e.append(f"{b}.charged_fraction outside (0, 1]")
        if v["benchmarks.pileup_mu_signal"] != 0: e.append("pileup_mu_signal: the signal path has no pile-up overlay (only 0 is implemented)")
        L = v["detector.layers"]
        if [x.get("id") for x in L] != list(range(1, 9)): e.append("layers: ids must be 1..8 in order")
        for x in L:
            k = x.get("kind")
            if k not in LAYER_KEYS: e.append(f"layer {x.get('id')}: kind must be pixel or sct"); continue
            if set(x) != LAYER_KEYS[k]: e.append(f"layer {x.get('id')}: keys {sorted(x)} != {sorted(LAYER_KEYS[k])}")
        if sorted(x["radius_mm"] for x in L) != [x["radius_mm"] for x in L]: e.append("layers: radii must increase")
        if e: raise ConfigError("; ".join(e))

    # ---- resolved values in code units ----
    def sz_name(self, mm): return f"Z{round(mm * 1000)}"
    def resolved(self):
        g = self.get; cm = lambda mm: round(mm / 10.0, 12)   # mm -> cm, rounded so that e.g. 0.58 mm gives exactly 0.058
        c = g("reconstruction.cuts.seed_delta_phi_rad")
        return dict(
            B_tesla=g("detector.magnetic_field_t"), timing_ns=g("detector.timing_cut_ns"), beamspot_cm=cm(g("detector.beamspot.sigma_z_mm")),
            sct_rphi_cm=cm(g("detector.sct.rphi_sigma_mm")), SZ={self.sz_name(x): cm(x) for x in g("detector.sct.z_sigma_options_mm")},
            sct_primary=self.sz_name(g("detector.sct.z_sigma_mm")), layers=g("detector.layers"),
            HALF={x["id"]: cm(x["z_half_mm"]) for x in g("detector.layers")},
            steps_per_period=g("reconstruction.simulation.steps_per_period"), max_layer_r_cm=cm(g("reconstruction.simulation.max_layer_radius_mm")),
            hit_mode=g("reconstruction.hits.mode"), hit_modes=g("reconstruction.hits.mode_options"), mult_rule=g("reconstruction.hits.multiplicity_rule"),
            seed=dict(dphi_seed_max=c, dz_seed_max_cm=cm(g("reconstruction.cuts.seed_delta_z_mm")), ds_seed_max_cm=cm(g("reconstruction.cuts.seed_delta_s_max_mm")),
                      dw_seed_max_cm=cm(g("reconstruction.cuts.seed_delta_w_max_mm")), ds_iter_max_cm=cm(g("reconstruction.cuts.iter_n1_max_mm")),
                      dw_iter_max_cm=cm(g("reconstruction.cuts.iter_n2_max_mm")), growth_factor_max=g("reconstruction.cuts.iter_growth_factor_max")),
            final_dw_cm=cm(g("reconstruction.cuts.final_delta_w_max_mm")), signal_ds_cm=cm(g("reconstruction.cuts.signal_delta_s_max_mm")),
            PAR={"COL": (g("benchmarks.colored.mass_gev"), g("benchmarks.colored.lambda_ev_production") / 1e9),
                 "EW": (g("benchmarks.ew.mass_gev"), g("benchmarks.ew.lambda_ev_production") / 1e9)})

    def validate_signal_inputs(self):
        """Reads the remaining signal-scope keys and checks them against the production inputs (banners, trigger)."""
        import csv
        for k in ("detector.beamspot.mode", "detector.merge_hits_in", "reconstruction.cuts.prefilter", "reconstruction.simulation.integrator",
                  "benchmarks.pileup_mu_signal", "benchmarks.colored.lambda_ev_table", "benchmarks.ew.lambda_ev_table",
                  "benchmarks.colored.model", "benchmarks.ew.model"): self.get(k)       # validated in _validate
        gs = {r[0]: r[1:] for r in csv.reader(open(f"{HERE}/../tables/generator_settings_2000.csv"))}
        if [int(x) for x in gs["iseed"]] != [self.get("benchmarks.colored.generator_seed"), self.get("benchmarks.ew.generator_seed")]:
            raise ConfigError(f"generator seeds differ from the run banners: {gs['iseed']}")
        if "t1 t1~" not in gs["process"][0] or "qe+ qe-" not in gs["process"][1]: raise ConfigError("production processes differ from the models")
        if self.get("benchmarks.trigger_pt_pair_min_gev") != 200.0: raise ConfigError("trigger threshold differs from the production trigger selection (200 GeV)")

    def assert_used(self, scope="signal"):
        need = {k for k, (s, _) in CONSUMERS.items() if s == scope}; miss = sorted(need - self.used)
        if miss: raise ConfigError(f"{scope}-scope key(s) not read in this run: {miss}")

    def write_provenance(self, out_path, extra=None):
        d = dict(config_sha256=self.sha256, files=list(FILES), used=sorted(self.used), values={k: self._v[k] for k in sorted(self.used)}, **(extra or {}))
        json.dump(d, open(f"{out_path}.config.json", "w"), indent=1, default=str)


def load(cdir=CDIR):
    return Config(cdir)
