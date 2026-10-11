#!/usr/bin/env python3
"""Phase 9 tables: converted-photon background (conversion only, no pile-up).
Inputs : ../logs/P9_chunks_LITERAL/*.csv (literal + 3 systematic configs, common random numbers per event)
         02_backgrounds/photon_conversion/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv (frozen project result)
Outputs: ../tables/converted_photon_cutflow.csv           (per config incl. FROZEN_v4; k/n, Wilson, CP, one-sided CP95 UL)
         ../tables/converted_photon_event_changes.csv     (every event whose plane / multiplicity / final decision differs
                                                           between FROZEN_v4 and LITERAL, with reason tags)
         ../tables/weighted_yields_conversion.csv          (A/B/C/D factors kept separate; luminosity yields)
Yield factorisation (kept separate, never forced):
  A = project sigma after the shower-level MET cut = 0.2310512 pb x 9139/10000 (MG5, frozen; 02_backgrounds/.../convert_and_analyze.py)
  B = paper's quoted sigma ~ 1 pb (Sec. III D, 'Z(nunu)gamma+j ... ~1 pb'), applied at the same selection stage as A
      (the paper states the generator cuts MET > 200 GeV and pT(gamma) > 0.5 GeV) -- shown as an ALTERNATIVE row, not a correction
  C = conversion probability 0.01 (DERIVED from the paper's own '~1 pb -> ~10 fb')
  D = detector + signal-region efficiency k/9139 (this analysis), with CP95 one-sided UL if k = 0
  yield(L) = sigma x C x D x L."""
import os, sys, glob, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from stats_utils import row, cp_upper
T = f"{HERE}/../tables"; PC = f"{HERE}/../../../02_backgrounds/photon_conversion"
lit = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{HERE}/../logs/P9_chunks_LITERAL/chunk_*.csv")))
assert (lit.groupby("config").event.nunique() == 9139).all() and (lit.status == "ok").all()
fro = pd.read_csv(f"{PC}/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv")
Tr = lambda s: s.astype(str) == "True"
fro_std = pd.DataFrame(dict(event=fro.event, config="FROZEN_v4 (eta-cone |eta|<1.8, SCT 34/1160 um, conv-point origin, sequential rng 99)",
                            plane=Tr(fro.sec3c_plane_found), mult=Tr(fro.hit_multiplicity_pass), dw=fro.sec3c_dw, ds=fro.sec3c_ds))
fro_std["dw_pass"] = fro_std.dw < 1; fro_std["ds_pass"] = fro_std.ds < 0.01
lit = lit.copy()
for c in ["plane", "mult", "dw_pass", "ds_pass", "final"]: lit[c] = Tr(lit[c])
DESC = {"LITERAL": "LITERAL (finite barrel, SCT 34/1160 um, PV origin, pile-up helix)", "SYS_CONVPT": "SYS_CONVPT (fit origin = conversion point)",
        "SYS_Z0": "SYS_Z0 (SCT z not smeared; calibrated, NOT literal)", "SYS_ETA": "SYS_ETA (eta-cone acceptance)"}
out = []
def flow(name, d):
    n = len(d); prev = pd.Series(True, index=d.index)
    out.append(dict(config=name, stage="generated photons (MET>200)", **row(n, n)))
    for st, m in [("plane with >=1 hit in >=4/8 layers (non-sequential)", d.best_layers >= 4 if "best_layers" in d else None),
                  ("plane with >=1 hit in 8/8 layers (non-sequential)", d.best_layers >= 8 if "best_layers" in d else None),
                  ("Sec. III C plane", d.plane), ("hit multiplicity 7x2+1", d.mult), ("dw < 1 cm", d.dw_pass), ("ds < 0.01 cm = final Sec. IV", d.ds_pass)]:
        if m is None: continue
        if "non-sequential" not in st: m = prev & m; prev = m
        r = dict(config=name, stage=st, **row(int(m.sum()), n)); r["event_ids"] = " ".join(map(str, d.event[m])) if m.sum() <= 40 else f"({int(m.sum())})"
        out.append(r)
    if "final" in d: assert (prev == d.final).all(), name
flow(fro_std.config.iloc[0], fro_std.reset_index(drop=True))
for c, g in lit.groupby("config", sort=False): flow(DESC[c], g.reset_index(drop=True))
cf = pd.DataFrame(out); cf.to_csv(f"{T}/converted_photon_cutflow.csv", index=False)
# per-event changes FROZEN_v4 -> LITERAL, reason tags from the single-change systematic configs (common random numbers)
L = {c: g.set_index("event") for c, g in lit.groupby("config")}; F = fro_std.set_index("event")
ch = []
for stage, col in [("plane", "plane"), ("multiplicity", "mult")]:
    fz = F[col] if col == "plane" else F.plane & F.mult; lz = L["LITERAL"][col] if col == "plane" else L["LITERAL"].plane & L["LITERAL"].mult
    for ev in fz.index[fz != lz.reindex(fz.index)]:
        tags = []
        for sc, tag in [("SYS_ETA", "geometry(finite barrel vs eta-cone)"), ("SYS_Z0", "SCT z smearing 1160 um"), ("SYS_CONVPT", "fit origin (PV vs conversion point)")]:
            v = L[sc].loc[ev, col] if col == "plane" else (L[sc].loc[ev, "plane"] and L[sc].loc[ev, "mult"])
            if v == fz.loc[ev]: tags.append(tag)
        if not tags: tags = ["random stream / helix propagation / merging (not isolated by a single-change config)"]
        ch.append(dict(event=ev, stage=stage, frozen=bool(fz.loc[ev]), literal=bool(lz.loc[ev]), reason_tags="; ".join(tags)))
chd = pd.DataFrame(ch); chd.to_csv(f"{T}/converted_photon_event_changes.csv", index=False)
# weighted yields
SIG_A = 0.2310512 * 9139 / 10000; SIG_B = 1.0; C = 0.01
yl = []
for name, d in [(fro_std.config.iloc[0], fro_std)] + [(DESC[c], g) for c, g in lit.groupby("config", sort=False)]:
    k = int((d.plane & d.mult & d.dw_pass & d.ds_pass).sum()); n = len(d); D = k / n; Dul = cp_upper(k, n)
    for sname, sig in [("A project sigma_afterMET = 0.21116 pb", SIG_A), ("B paper sigma ~ 1 pb (alternative, not a correction)", SIG_B)]:
        r = dict(background="converted photon (no pile-up)", config=name, sigma_choice=sname, sigma_pb=sig, conversion_prob_C=C,
                 eff_D_k=k, eff_D_n=n, eff_D=D, eff_D_cp95_upper=Dul, sigma_x_C_fb=sig * C * 1e3,
                 yield_fb=sig * C * D * 1e3, yield_fb_cp95_upper=sig * C * Dul * 1e3)
        for lum in (36.1, 139, 300, 3000): r[f"N_{lum:g}fb-1"] = sig * C * D * 1e3 * lum; r[f"N_{lum:g}fb-1_cp95_upper"] = sig * C * Dul * 1e3 * lum
        yl.append(r)
pd.DataFrame(yl).to_csv(f"{T}/weighted_yields_conversion.csv", index=False)
print(cf[["config", "stage", "k", "n", "cp95_upper_one_sided"]].to_string()); print(chd.groupby(["stage", "frozen", "literal"]).size()); print(chd.reason_tags.value_counts().head(8))
print(pd.DataFrame(yl)[["config", "sigma_choice", "eff_D_k", "yield_fb", "yield_fb_cp95_upper", "N_300fb-1_cp95_upper"]].to_string())
