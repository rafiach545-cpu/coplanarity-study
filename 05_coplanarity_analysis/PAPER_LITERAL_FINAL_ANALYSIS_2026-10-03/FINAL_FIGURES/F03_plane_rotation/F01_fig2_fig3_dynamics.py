#!/usr/bin/env python3
"""
Figure 2-style (angular momentum L and quirk separation d vs CM radius) and Figure 3-style (rotation of the
quirk plane vs CM radius) from REAL stored events replayed with the unmodified project propagator (B = 2 T).
Events (one representative event each -- NOT distributions):
  colored : first COL2000 trigger event that is fiducial in the literal configuration (mQ=1800 GeV, Lambda=2 keV)
  EW      : first EW2000 trigger event that is fiducial in the literal configuration, at its Table I Lambda=4 keV,
            and the same stored momenta replayed at Lambda=2 keV (the paper's Fig. 3 EW label is 800 GeV, 2 keV).
Definitions (natural units -> hbar for L):
  CM frame (paper: angular momentum of the quirk system in its centre-of-mass frame):
    beta = (p1+p2)/(E1+E2) per sample; p_i* = Lorentz-boosted momenta; r_rel* = r_rel with its component along
    beta scaled by gamma (equal-lab-time approximation; non-simultaneity correction neglected -- labelled)
    L = |r_rel* x (p1* - p2*)/2|  [GeV * GeV^-1 = hbar];   d = |r_rel*| (cm)
  r_cm  = transverse radius of (x1 + x2)/2 (cm)
  quirk plane (what the hits measure): plane through the vertex containing both quirks, normal n = x1 x x2 (vertex-relative);
  defined only where the two position vectors are well separated, sin(alpha) = |x1 x x2|/(|x1||x2|) > 0.3 * max;
  Delta_phi(r) = angle between n(t) and the first well-defined n (undefined samples are dropped, not interpolated).
"""
import os, sys, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu                                          # noqa: E402
BASE = "/home/rafia/coplanarity_study"
sys.path[:0] = [f"{BASE}/04_detector_sim", f"{BASE}/03_trajectory_sim"]
import trajectory_to_hits as tth                                # noqa: E402
from quirk_trajectory_optimized_v2 import integrate_trajectory_fast_v2   # noqa: E402
tth.integrate_trajectory = integrate_trajectory_fast_v2
HB = 1.973269804e-14
T = f"{HERE}/../tables"


def pick(sample):
    d = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
    x = d[(d["sample"] == sample) & (d.geom == "B") & (d.sct == "Z1160") & (d.wconv == "W1") & (d.fid == True)].sort_values("key")
    k = int(x.key.iloc[0]); z0 = float(x.z0_cm.iloc[0]); eid = int(x.event_id.iloc[0])
    tag = "EW_800GeV_L4keV" if sample == "EW2000" else "colored_1800GeV_L2keV"
    m = pd.read_csv(f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/{tag}/trigger_passing_events.csv").iloc[k]
    return k, eid, z0, m


def run(m, mq, lam, z0):
    _, tr = tth.simulate_quirk_hits((m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2), mass_gev=mq, Lambda_gev=lam,
                                    B_tesla=2.0, charge1=float(m.charge1), charge2=float(m.charge2),
                                    rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    x1, x2, p1, p2 = tr["x1"], tr["x2"], tr["p1"], tr["p2"]
    E1 = np.sqrt((p1 ** 2).sum(1) + mq ** 2); E2 = np.sqrt((p2 ** 2).sum(1) + mq ** 2)
    beta = (p1 + p2) / (E1 + E2)[:, None]; b = np.linalg.norm(beta, axis=1); g = 1.0 / np.sqrt(1.0 - b ** 2)
    bh = beta / np.maximum(b, 1e-300)[:, None]

    def boost(p, E):
        pl = (p * bh).sum(1)
        return p + ((g - 1.0) * pl - g * b * E)[:, None] * bh
    p1s, p2s = boost(p1, E1), boost(p2, E2)
    rr = x1 - x2
    rr = rr + ((g - 1.0) * (rr * bh).sum(1))[:, None] * bh          # longitudinal separation in the CM frame
    pr = (p1s - p2s) / 2.0
    Lv = np.cross(rr, pr); L = np.linalg.norm(Lv, axis=1)
    d = np.linalg.norm(rr, axis=1) * HB
    cm = (x1 + x2) / 2.0 * HB; rcm = np.hypot(cm[:, 0], cm[:, 1])
    v0 = np.array([0.0, 0.0, z0 / HB])
    a1, a2 = x1 - v0, x2 - v0
    nq = np.cross(a1, a2); nn = np.linalg.norm(nq, axis=1)
    sina = nn / np.maximum(np.linalg.norm(a1, axis=1) * np.linalg.norm(a2, axis=1), 1e-300)
    ok = sina > 0.3 * sina.max()
    j0 = int(np.argmax(ok)); nref = nq[j0] / nn[j0]
    dphi = np.where(ok, np.arccos(np.clip(np.abs((nq / np.maximum(nn, 1e-300)[:, None]) @ nref), -1, 1)), np.nan)
    sel = rcm <= 60.0
    step = max(1, int(sel.sum() // 4000))
    idx = np.where(sel)[0][::step]
    return pd.DataFrame(dict(r_cm=rcm[idx], L_hbar=L[idx], d_cm=d[idx], dphi_rad=dphi[idx]))


def main():
    kc, ec, z0c, mc = pick("COL2000"); ke, ee, z0e, me = pick("EW2000")
    parts = [("colored 1800 GeV, 2 keV (COL2000 event %d)" % ec, run(mc, 1800.0, 2e-6, z0c)),
             ("EW 800 GeV, 4 keV (EW2000 event %d)" % ee, run(me, 800.0, 4e-6, z0e)),
             ("EW 800 GeV, 2 keV (EW2000 event %d momenta replayed at 2 keV)" % ee, run(me, 800.0, 2e-6, z0e))]
    src = pd.concat([p.assign(series=s) for s, p in parts])
    import matplotlib.pyplot as plt

    def plot2(df):
        x = df[df.series.str.startswith("colored")]
        x = x[x.r_cm <= 5.0]
        fig, ax = plt.subplots(figsize=(5.6, 4.0))
        ax.plot(x.r_cm, x.L_hbar, color=fu.SERIES[0], ls="-", label="L")
        ax.set_xlabel("r (cm), transverse radius of the pair centre of mass"); ax.set_ylabel("L (ħ)", color=fu.SERIES[0])
        ax2 = ax.twinx(); ax2.plot(x.r_cm, x.d_cm, color=fu.SERIES[1], ls="--", label="d"); ax2.set_ylabel("d (cm)", color=fu.SERIES[1])
        ax2.grid(False); ax.set_title("Fig. 2-style: one real event, colored 1800 GeV, Λ = 2 keV", fontsize=9)
        h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper right")
        return fig

    def plot3(df):
        fig, ax = plt.subplots(figsize=(5.6, 4.0))
        for i, (s, g) in enumerate(df.groupby("series", sort=False)):
            g = g.dropna(subset=["dphi_rad"])
            ax.plot(g.r_cm, g.dphi_rad * 1e3, color=fu.SERIES[i], ls="none", marker=fu.MARKERS[i], ms=2, label=s)
        ax.set_xlabel("r (cm), transverse radius of the pair centre of mass"); ax.set_ylabel("Δφ of quirk plane (10⁻³ rad)")
        ax.set_xlim(0, 15); ax.legend(fontsize=7); ax.set_title("Fig. 3-style: plane rotation, real replayed events", fontsize=9)
        return fig

    srcs = [f"{T}/signal_per_event_all_configs.csv",
            f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv",
            f"{BASE}/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/trigger_passing_events.csv"]
    fu.figure("F02_angular_momentum_and_separation", src, plot2,
              "Centre-of-mass-frame angular momentum L (ħ) and CM-frame quirk separation d (cm) versus the transverse radius of the pair centre of mass for ONE real "
              "colored event (COL2000 event %d, mQ = 1800 GeV, Λ = 2 keV, B = 2 T), replayed with the unmodified project propagator from its "
              "stored four-momenta and stored vertex. Paper Fig. 2 analogue; a single representative event, not a distribution. "
              "(The source CSV also contains the two EW traces used by F03.)" % ec,
              srcs, "first COL2000 trigger event fiducial in the literal configuration", os.path.abspath(__file__))
    fu.figure("F03_plane_rotation", src, plot3,
              "Rotation Δφ of the plane spanned by the quirk pair (normal along r_rel × p_rel) versus centre-of-mass transverse radius, for one "
              "real colored event (1800 GeV, 2 keV) and one real EW event at its Table I Λ = 4 keV and replayed at Λ = 2 keV (the paper's Fig. 3 "
              "EW label). Paper Fig. 3 analogue; single events, not distributions.",
              srcs, "first literal-fiducial events of COL2000 and EW2000", os.path.abspath(__file__))
    print("done", ec, ee)


if __name__ == "__main__":
    main()
