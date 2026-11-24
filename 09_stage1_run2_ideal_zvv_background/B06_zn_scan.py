#!/usr/bin/env python3
"""09 step B06 (2026-11-22): Z_N scan of the signal-region cuts, Stage 1 · Run 2 · Ideal (13 TeV, 139 fb^-1).
PIPELINE TEST ONLY until the new 13 TeV signal grid (DOP853) exists: the signal here is the single B05 point (EW, m = 800 GeV,
Lambda = 4 keV, 511 Pythia events of the Stage 1 sample, old RK4 transport); the numbers are not results.

Scanned: input (all = no cleaning, orp = full cleaning; c100 / cinf / iso / iso20 for the background, signal only where it exists),
Delta_s cut (um), multiplicity required or not, monojet selection (B10) on or off. Delta_w < 1 cm is part of the plane selection (B03).
Background: Z(nunu)+jet chunks 1-10 (B03, B09, B10), weight per MC event w_c = sigma_c L / N_total (N_total = all chunks used; B01_chunks.csv).
  B = sum of w over passing events; sigma_stat^2 = sum w^2. Zero MC events: B = 3.0 w (95 % CL upper limit, the rule used in 09) and
  sigma_stat = 0 (the upper limit already covers the MC statistics). sigma_B^2 = sigma_stat^2 + (f B)^2, f = 0.1, 0.2, 0.3.
Signal: s = sigma L k / N_gen, sigma from the Stage 1 grid (06 S1_N_grid_139fb.csv), trigger pT(QQ) > 200 GeV (B05 'trig').
Z_N: Cowan's Asimov significance with background uncertainty (arXiv:1007.1727; e.g. Cowan, 'Discovery sensitivity for a counting
experiment with background uncertainty', 2012):
  Z = sqrt(2 [ (s+b) ln((s+b)(b+s2)/(b^2+(s+b)s2)) - (b^2/s2) ln(1 + s2 s/(b(b+s2))) ]),  s2 = sigma_B^2.
Output: data/B06_scan_pipeline_test.csv."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = f"{HERE}/data"
L_PB = 139000.0; CHUNKS = range(1, 11)
DS_CUTS_UM = (50, 75, 100, 125, 150, 200, 300); FS = (0.1, 0.2, 0.3)
SIG_FB = 0.2341                    # EW 800 GeV, 13 TeV, Stage 1 grid (06 S1_N_grid_139fb.csv, sigma_fb)


def zn(s, b, sb):
    if s <= 0: return 0.0
    s2 = sb * sb
    if s2 <= 0: return float(np.sqrt(2 * ((s + b) * np.log(1 + s / b) - s)))
    t1 = (s + b) * np.log((s + b) * (b + s2) / (b * b + (s + b) * s2)); t2 = b * b / s2 * np.log(1 + s2 * s / (b * (b + s2)))
    return float(np.sqrt(max(2 * (t1 - t2), 0.0)))


def background():
    C = pd.read_csv(f"{D}/B01_chunks.csv").set_index("chunk"); out = []; NTOT = float(C.loc[list(CHUNKS), "n_generated"].sum())
    for c in CHUNKS:
        b3 = pd.read_csv(f"{D}/B03_events_c{c:02d}.csv"); b9 = pd.read_csv(f"{D}/B09_events_c{c:02d}.csv"); b10 = pd.read_csv(f"{D}/B10_monojet_c{c:02d}.csv")
        assert len(b3) == len(b9) == len(b10) and (b3.event.values == b9.event.values).all()
        m = b3[["chunk", "event", "met"]].copy(); m["w"] = C.loc[c, "sigma_pb"] * L_PB / NTOT
        for inp, src in (("all", b3), ("orp", b3), ("c100", b9), ("cinf", b9), ("iso", b9), ("iso20", b9)):
            m[f"{inp}_plane"] = src[f"{inp}_has_plane"].astype(bool).values; m[f"{inp}_mult"] = src[f"{inp}_sel_mult_ok"].fillna(False).astype(bool).values
            m[f"{inp}_ds"] = src[f"{inp}_sel_ds_cm"].values
        m["trig"] = m.met > 200; m["monojet"] = b10.pass_monojet.astype(bool).values; out.append(m)
    return pd.concat(out, ignore_index=True)


def signal():
    s = pd.read_csv(f"{D}/B05_signal_m800_L4keV.csv"); mj = pd.read_csv(f"{D}/B10_signal_EW800_L4keV_13TeV.csv")
    assert len(s) == len(mj)
    m = pd.DataFrame(dict(event=s.event, trig=s.trig.astype(bool), monojet=mj.pass_monojet.astype(bool).values))
    m["w"] = SIG_FB * L_PB / 1000.0 / len(s)                                # fb -> events at 139 fb^-1 per generated event
    for inp in ("qrk", "all", "orp"):
        m[f"{inp}_plane"] = s[f"{inp}_has_plane"].astype(bool); m[f"{inp}_mult"] = s[f"{inp}_sel_mult_ok"].fillna(False).astype(bool)
        m[f"{inp}_ds"] = s[f"{inp}_sel_ds_cm"]
    return m


def passing(T, inp, ds_um, mult, mono):
    p = T.trig & T[f"{inp}_plane"] & (T[f"{inp}_ds"] < ds_um * 1e-4)
    if mult: p &= T[f"{inp}_mult"]
    if mono: p &= T.monojet
    return p


if __name__ == "__main__":
    Bk, Sg = background(), signal(); rows = []
    # check: the B06 selection must reproduce the README SR counts (Delta_s < 100 um, multiplicity, no monojet)
    for inp, ref in (("all", 42), ("orp", 0), ("c100", 24), ("cinf", 0), ("iso", 0), ("iso20", 0)):
        n = int(passing(Bk, inp, 100, True, False).sum()); assert n == ref, (inp, n, ref)
    for inp in ("all", "orp"):
        for ds in DS_CUTS_UM:
            for mult in (True, False):
                for mono in (False, True):
                    pb = passing(Bk, inp, ds, mult, mono); n = int(pb.sum()); w = Bk.w[pb]
                    B = float(w.sum()) if n else 3.0 * float(Bk.w.mean()); sst = float(np.sqrt((w ** 2).sum())) if n else 0.0
                    ps = passing(Sg, inp, ds, mult, mono); k = int(ps.sum()); S = float(Sg.w[ps].sum())
                    r = dict(input=inp, ds_cut_um=ds, mult=mult, monojet=mono, n_bkg_mc=n, B=B, sigma_stat=sst, k_sig=k, S=S)
                    for f in FS: r[f"ZN_f{int(f * 100)}"] = zn(S, B, np.hypot(sst, f * B))
                    rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(f"{D}/B06_scan_pipeline_test.csv", index=False)
    pd.set_option("display.width", 200); print("PIPELINE TEST (single B05 point, old transport) - not a result"); print(T.round(3).to_string(index=False))
    for f in FS:
        b = T.loc[T[f"ZN_f{int(f * 100)}"].idxmax()]
        print(f"best at f = {f}: input {b.input}, ds < {b.ds_cut_um} um, mult {b.mult}, monojet {b.monojet}: S = {b.S:.3f}, B = {b.B:.1f} (MC {b.n_bkg_mc}), Z_N = {b[f'ZN_f{int(f * 100)}']:.4f}")
