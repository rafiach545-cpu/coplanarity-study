#!/usr/bin/env python3
"""Phase 10 tables: converted photon + mu=50 pile-up overlay, literal.
Inputs : ../logs/P10_chunks_LITERAL/*.csv (configs LITERAL, SYS_CONVPT)
         02_backgrounds/photon_conversion/conversion_with_pileup_mu50_v1.csv (frozen project overlay)
Outputs: ../tables/overlay_cutflow.csv, ../tables/overlay_event_changes.csv, ../tables/overlay_winner_ancestry.csv,
         ../tables/weighted_yields_overlay.csv  (same A/B/C/D factorisation as P9c; never forced)
Partial input is allowed (reported as n events processed); the final tables are rebuilt after P10_EXIT=0."""
import os, sys, glob, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from stats_utils import row, cp_upper
T = f"{HERE}/../tables"; PC = f"{HERE}/../../../02_backgrounds/photon_conversion"
Tr = lambda s: s.astype(str) == "True"
fs = sorted(glob.glob(f"{HERE}/../logs/P10_chunks_LITERAL/chunk_*.csv"))
ov = pd.concat(pd.read_csv(f) for f in fs)
for c in ["plane", "mult", "dw_pass", "ds_pass", "final"]: ov[c] = Tr(ov[c])
assert (ov.status == "ok").all() and not ov.duplicated(["event", "config"]).any()
fro = pd.read_csv(f"{PC}/conversion_with_pileup_mu50_v1.csv")
fz = pd.DataFrame(dict(event=fro.event, plane=Tr(fro.sec3c_plane_found), mult=Tr(fro.hit_multiplicity_pass),
                       dw_pass=fro.sec3c_dw < 1, ds_pass=Tr(fro.delta_s_pass_0p01), final=Tr(fro.final_sec_iv_pass)))
DONE = sorted(set(ov.event)); NTOT = 9139
out = []
def flow(name, d, note):
    d = d.reset_index(drop=True); n = len(d); prev = pd.Series(True, index=d.index)
    out.append(dict(config=name, events_processed=n, of_total=NTOT, note=note, stage="generated photons (MET>200)", **row(n, n)))
    for st, m, seq in [("plane >=1 hit in >=4/8 layers (non-sequential)", d.best_layers >= 4 if "best_layers" in d else None, False),
                       ("plane >=1 hit in 8/8 layers (non-sequential)", d.best_layers >= 8 if "best_layers" in d else None, False),
                       ("Sec. III C plane", d.plane, True), ("hit multiplicity 7x2+1", d.mult, True), ("dw < 1 cm", d.dw_pass, True),
                       ("ds < 0.01 cm = final Sec. IV", d.ds_pass, True)]:
        if m is None: continue
        if seq: m = prev & m; prev = m
        r = dict(config=name, events_processed=n, of_total=NTOT, note=note, stage=st, **row(int(m.sum()), n))
        r["event_ids"] = " ".join(map(str, d.event[m])) if m.sum() <= 60 else f"({int(m.sum())})"; out.append(r)
    assert (prev == d.final).all(), name
flow("FROZEN overlay v1 (all 9139)", fz, "frozen project result")
flow("FROZEN overlay v1 (same events as literal subset)", fz[fz.event.isin(DONE)], "for like-for-like comparison while P10 is partial")
for c, g in ov.groupby("config", sort=False): flow(f"{c} overlay (finite barrel, SCT 34/1160 um, mu=50)", g, "literal" if c == "LITERAL" else "systematic: fit origin = conversion point")
cf = pd.DataFrame(out); cf.to_csv(f"{T}/overlay_cutflow.csv", index=False)
L = ov[ov.config == "LITERAL"].set_index("event"); F = fz.set_index("event").loc[L.index]
ch = []
for stage, fcol, lcol in [("plane", F.plane, L.plane), ("plane+mult", F.plane & F.mult, L.plane & L.mult), ("final", F.final, L.final)]:
    for ev in fcol.index[fcol != lcol]:
        ch.append(dict(event=ev, stage=stage, frozen=bool(fcol[ev]), literal=bool(lcol[ev]),
                       reason="literal detector (finite barrel, SCT z 1160 um, PV origin) + per-event conversion seed SeedSequence([99,1708,i]) "
                              "(frozen used sequential rng); pile-up stream identical in seed convention but hits differ through acceptance/smearing"))
pd.DataFrame(ch).to_csv(f"{T}/overlay_event_changes.csv", index=False)
anc = L[L.plane][["winner_conv_hits", "winner_pileup_hits", "winner_mixed_hits", "mult", "ds", "dw", "final"]].reset_index()
anc["category"] = np.select([anc.winner_conv_hits == 0, anc.winner_pileup_hits == 0], ["pile-up only", "conversion only"], "mixed conversion+pile-up")
anc.to_csv(f"{T}/overlay_winner_ancestry.csv", index=False)
SIG_A = 0.2310512 * 9139 / 10000; C = 0.01; yl = []
for c, g in [("FROZEN overlay v1", fz)] + list(ov.groupby("config", sort=False)):
    k = int(g.final.sum()); n = len(g)
    for sname, sig in [("A project sigma_afterMET = 0.21116 pb", SIG_A), ("B paper sigma ~ 1 pb (alternative, not a correction)", 1.0)]:
        r = dict(background="converted photon + mu=50 pile-up", config=c, events_processed=n, sigma_choice=sname, sigma_pb=sig, conversion_prob_C=C,
                 eff_D_k=k, eff_D_n=n, eff_D=k / n, eff_D_cp95_upper=cp_upper(k, n), yield_fb=sig * C * k / n * 1e3, yield_fb_cp95_upper=sig * C * cp_upper(k, n) * 1e3)
        for lum in (36.1, 139, 300, 3000): r[f"N_{lum:g}fb-1"] = r["yield_fb"] * lum; r[f"N_{lum:g}fb-1_cp95_upper"] = r["yield_fb_cp95_upper"] * lum
        yl.append(r)
pd.DataFrame(yl).to_csv(f"{T}/weighted_yields_overlay.csv", index=False)
print(f"{len(fs)} chunks, {len(DONE)} events"); print(cf[["config", "stage", "k", "n"]].to_string())
print(anc.category.value_counts().to_dict(), anc[anc.mult].category.value_counts().to_dict())
