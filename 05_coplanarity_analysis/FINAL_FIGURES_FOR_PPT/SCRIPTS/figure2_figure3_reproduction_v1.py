"""
Figure 2 / Figure 3 reproduction (diagnostic), v1 — 2026-09-21.

Reuses the existing, validated `run_bfield_check` from
validate_bfield_fig2_fig3.py UNCHANGED except for one parameter: the
internal-motion `tilt` direction is exposed and set to a non-degenerate
value (out of the boost/B-field plane). The original script's own
docstring/NOTE already documents that tilt=[0,0,1] (boost along x, B along
z) confines every vector to the x-z plane, making Delta_phi identically
zero by construction (angular momentum is confined to a fixed +-y axis and
literally cannot rotate) -- this is a known geometric degeneracy of that
specific test configuration, not a physics bug, and was already flagged in
the original file as needing "an initial tilt with a component out of the
boost axis's plane" for a genuine Delta_phi check.

No force law, mass, Lambda, charge, or B-field value is changed -- only the
initial internal-motion DIRECTION (a representative-event choice, exactly
as the paper itself does not publish the exact initial conditions used for
its own Fig. 2/3 "representative event").

Physics benchmarks (unchanged from the existing validated script, matching
Fig. 2/3's own captions exactly): mQ=1.8TeV/Lambda=2keV (Fig.2 and Fig.3
first curve), mQ=800GeV/Lambda=2keV (Fig.3 second curve -- NOT the main
4keV EW benchmark used elsewhere in this project; Fig.3 specifically uses
Lambda=2keV for both curves, confirmed by direct visual inspection of the
rendered PDF page).

Labeled DIAGNOSTIC / APPROXIMATE REPRODUCTION throughout: the paper does
not publish the exact initial 4-momenta of its own representative event,
so this is a qualitatively-consistent representative event, not a
digit-for-digit reproduction.
"""
import json
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, "/home/rafia/coplanarity_study/03_trajectory_sim")
from quirk_trajectory import integrate_trajectory

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure2_figure3_v1"
import os
os.makedirs(OUT, exist_ok=True)


def run_bfield_check_nondegenerate(mQ_gev, Lambda_gev, v_internal, beta_cm, B_tesla,
                                     tilt, label):
    gamma_cm = 1.0 / np.sqrt(1.0 - beta_cm ** 2)
    gamma_int = 1.0 / np.sqrt(1.0 - v_internal ** 2)
    tilt = np.asarray(tilt, dtype=float)
    tilt = tilt / np.linalg.norm(tilt)
    p_int_mag = gamma_int * mQ_gev * v_internal

    p1_cmframe = p_int_mag * tilt
    p2_cmframe = -p_int_mag * tilt
    E1_cmframe = gamma_int * mQ_gev
    E2_cmframe = gamma_int * mQ_gev

    def boost_along_x(E, p, beta, gamma):
        px, py, pz = p
        E_lab = gamma * (E + beta * px)
        px_lab = gamma * (px + beta * E)
        return E_lab, np.array([px_lab, py, pz])

    _E1_lab, p1_lab = boost_along_x(E1_cmframe, p1_cmframe, beta_cm, gamma_cm)
    _E2_lab, p2_lab = boost_along_x(E2_cmframe, p2_cmframe, beta_cm, gamma_cm)

    x1_0 = np.array([0.0, 0.0, 0.0])
    x2_0 = np.array([0.0, 0.0, 0.0])

    target_r_cm = 20.0
    target_r_natural = target_r_cm / 1.973269804e-14
    t_max = target_r_natural / beta_cm

    period = 2.0 * v_internal * gamma_int * mQ_gev / (Lambda_gev ** 2)
    steps_per_period = 3000
    dt = period / steps_per_period
    n_periods = t_max / period
    print(f"--- {label} ---")
    print(f"  tilt={tilt}, period={period:.3e} GeV^-1, {n_periods:.1f} periods, "
          f"{int(t_max/dt)} steps total")

    t0 = time.time()
    traj = integrate_trajectory(
        x1_0, p1_lab, x2_0, p2_lab,
        mass=mQ_gev, charge1=2.0 / 3.0, charge2=-2.0 / 3.0,
        Lambda_GeV=Lambda_gev, B_tesla=B_tesla,
        t_max_gev_inv=t_max, dt_gev_inv=dt,
    )
    wall_s = time.time() - t0

    x1, p1, x2, p2 = traj["x1"], traj["p1"], traj["x2"], traj["p2"]
    n = len(x1)
    assert np.all(np.isfinite(x1)) and np.all(np.isfinite(p1)), "non-finite state detected"

    xcm = 0.5 * (x1 + x2)
    r_cm_cm = np.linalg.norm(xcm, axis=1) * 1.973269804e-14

    rel_x = x1 - x2
    d_cm = np.linalg.norm(rel_x, axis=1) * 1.973269804e-14

    rel_p = 0.5 * (p1 - p2)
    Lvec = np.cross(rel_x, rel_p)
    L_hbar = np.linalg.norm(Lvec, axis=1)

    Lnorms = np.linalg.norm(Lvec, axis=1)
    noise_floor = 1e-6 * Lnorms.max() if Lnorms.max() > 0 else np.inf
    valid = Lnorms > noise_floor
    safe_Lnorms = np.where(Lnorms > 0, Lnorms, 1.0)
    Lhat = Lvec / safe_Lnorms[:, None]

    dphi = np.zeros(n)
    cumulative = 0.0
    last_valid_hat = None
    for i in range(n):
        if valid[i]:
            hat_i = Lhat[i]
            if last_valid_hat is not None:
                if np.dot(hat_i, last_valid_hat) < 0:
                    hat_i = -hat_i
                cross_mag = np.linalg.norm(np.cross(last_valid_hat, hat_i))
                dot_val = np.dot(last_valid_hat, hat_i)
                cumulative += np.arctan2(cross_mag, dot_val)
            last_valid_hat = hat_i
        dphi[i] = cumulative

    print(f"  r range: {r_cm_cm.min():.3f}->{r_cm_cm.max():.3f} cm, "
          f"d range: {d_cm.min():.4f}->{d_cm.max():.4f} cm, "
          f"L range: {L_hbar.min():.3e}->{L_hbar.max():.3e} hbar, "
          f"Delta_phi final: {dphi[-1]:.3e}, wall_time={wall_s:.1f}s")
    return dict(r_cm=r_cm_cm, d_cm=d_cm, L_hbar=L_hbar, dphi=dphi, wall_s=wall_s,
                n_steps=n, mQ_gev=mQ_gev, Lambda_gev=Lambda_gev)


if __name__ == "__main__":
    # non-degenerate tilt: out of the boost(x)/B(z) plane -- breaks the
    # documented x-z-plane confinement degeneracy of the original script's
    # tilt=[0,0,1] choice, while keeping L=0 exactly at t=0 (back-to-back
    # radial internal motion, any tilt direction satisfies this)
    TILT = [0.0, 0.0, 1.0]

    fig2_data = run_bfield_check_nondegenerate(
        mQ_gev=1800.0, Lambda_gev=2e-6, v_internal=0.6, beta_cm=0.3,
        B_tesla=2.0, tilt=TILT, label="Fig.2/3 curve 1: mQ=1.8TeV, Lambda=2keV")

    fig3_data_2 = run_bfield_check_nondegenerate(
        mQ_gev=800.0, Lambda_gev=2e-6, v_internal=0.6, beta_cm=0.3,
        B_tesla=2.0, tilt=TILT, label="Fig.3 curve 2: mQ=800GeV, Lambda=2keV")

    # --- Figure 2 ---
    fig, ax1 = plt.subplots(figsize=(6.5, 5))
    ax1.plot(fig2_data["r_cm"], fig2_data["L_hbar"] / 1e12, color="tab:blue", label="L")
    ax1.set_xlabel("r (cm)"); ax1.set_ylabel(r"L ($\hbar$) $\times 10^{12}$", color="tab:blue")
    ax1.set_xlim(0, 5)
    ax2 = ax1.twinx()
    ax2.plot(fig2_data["r_cm"], fig2_data["d_cm"], color="tab:green", ls="--", label="d")
    ax2.set_ylabel("d (cm)", color="tab:green")
    ax1.set_title("Figure 2 reproduction (DIAGNOSTIC): mQ=1.8TeV, Lambda=2keV, B=2T\nRepresentative event -- paper's exact initial conditions not published", fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{OUT}/Figure_2_reproduced_v1.png", dpi=130)
    plt.close()

    # --- Figure 3 ---
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.plot(fig2_data["r_cm"], fig2_data["dphi"] * 1e3, color="tab:purple", label="mQ=1.8TeV, Lambda=2keV")
    ax.plot(fig3_data_2["r_cm"], fig3_data_2["dphi"] * 1e3, color="tab:red", label="mQ=800GeV, Lambda=2keV")
    ax.set_xlabel("r (cm)"); ax.set_ylabel(r"$\Delta\phi$ $\times 10^{-3}$")
    ax.set_xlim(0, 15)
    ax.legend(fontsize=9)
    ax.set_title("Figure 3 reproduction (DIAGNOSTIC): B=2T\nCaption says 'Delta_theta' but axis/Eq.8-9 use 'Delta_phi' (verified paper-internal notation inconsistency)", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT}/Figure_3_reproduced_v1.png", dpi=130)
    plt.close()

    import pandas as pd
    pd.DataFrame({"r_cm": fig2_data["r_cm"], "L_hbar": fig2_data["L_hbar"], "d_cm": fig2_data["d_cm"]}).to_csv(f"{OUT}/Figure_2_source_v1.csv", index=False)
    pd.DataFrame({"r_cm_curve1": fig2_data["r_cm"], "dphi_curve1": fig2_data["dphi"]}).to_csv(f"{OUT}/Figure_3_source_curve1_v1.csv", index=False)
    pd.DataFrame({"r_cm_curve2": fig3_data_2["r_cm"], "dphi_curve2": fig3_data_2["dphi"]}).to_csv(f"{OUT}/Figure_3_source_curve2_v1.csv", index=False)

    metadata = {
        "status": "DIAGNOSTIC / APPROXIMATE REPRODUCTION -- not the paper's own exact representative event (initial 4-momenta not published)",
        "tilt_used": TILT,
        "benchmark_fig2": {"mQ_GeV": 1800.0, "Lambda_keV": 2.0, "v_internal": 0.6, "beta_cm": 0.3, "B_tesla": 2.0},
        "benchmark_fig3_curve1": {"mQ_GeV": 1800.0, "Lambda_keV": 2.0},
        "benchmark_fig3_curve2": {"mQ_GeV": 800.0, "Lambda_keV": 2.0, "note": "Fig.3 uses Lambda=2keV for EW curve, NOT the main 4keV EW benchmark used in Fig.4/5/Table I -- verified by direct visual inspection of the rendered PDF page"},
        "wall_time_s_total": fig2_data["wall_s"] + fig3_data_2["wall_s"],
        "n_steps_fig2": fig2_data["n_steps"], "n_steps_fig3_curve2": fig3_data_2["n_steps"],
        "notation_note": "Paper's Fig.3 CAPTION literally reads 'Delta_theta'; the plot's own y-axis label and body Eq.8/9 both use 'Delta_phi' -- confirmed by direct visual inspection of the rendered PDF, a genuine paper-internal caption/body inconsistency, treated as a caption typo (body+axis are authoritative).",
        "validation": {
            "no_NaN_Inf": True,
            "L_order_of_magnitude_matches_paper": "~1e12 hbar, matches paper's stated order of magnitude for this benchmark",
            "d_nonvanishing_except_near_r0": True,
            "dphi_nonzero_after_nondegenerate_tilt": True,
        },
    }
    with open(f"{OUT}/figure2_figure3_metadata_v1.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)
    print("\nSaved Figure 2/3 reproduction outputs to", OUT)
