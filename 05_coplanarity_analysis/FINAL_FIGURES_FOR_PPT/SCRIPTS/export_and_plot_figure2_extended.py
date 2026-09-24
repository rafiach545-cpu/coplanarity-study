"""
Figure 2 extension to r=0-20cm -- READ-ONLY export + plot, no new
trajectory propagation. Source: figure2_figure3_v1/Figure_2_source_v1.csv,
already integrated to a target r=20cm by figure2_figure3_reproduction_v1.py
(commit b72fe825c19e15cb8eb5e560e1294ee02414a911) -- the original Figure 2
PNG simply displayed only xlim(0,5) of this same underlying data.
Does not modify the existing paper-range (0-5cm) Figure 2 in any way.
"""
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/rafia/coplanarity_study"
SRC = f"{BASE}/05_coplanarity_analysis/figure2_figure3_v1/Figure_2_source_v1.csv"
OUT_CSV = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SOURCE_DATA/FIGURE_2_EXTENDED_0_TO_20CM_VALUES.csv"
OUT_PNG = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/PNG/FIGURE_2_FINAL_EXTENDED_0_TO_20CM_DIAGNOSTIC.png"
OUT_PDF = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/PDF/FIGURE_2_FINAL_EXTENDED_0_TO_20CM_DIAGNOSTIC.pdf"

# benchmark parameters, from figure2_figure3_reproduction_v1.py's __main__ call for fig2_data
MQ_GEV, LAMBDA_KEV, V_INTERNAL, BETA_CM, B_TESLA = 1800.0, 2.0, 0.6, 0.3, 2.0


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_turning_points(y):
    """Local extrema (sign changes in the discrete derivative)."""
    dy = np.diff(y)
    sign = np.sign(dy)
    sign[sign == 0] = 1
    turns = np.where(np.diff(sign) != 0)[0] + 1
    return turns


def main():
    df = pd.read_csv(SRC)
    df["L_times_1e12_hbar"] = df["L_hbar"] / 1e12
    out = df[["r_cm", "L_hbar", "L_times_1e12_hbar", "d_cm"]].copy()
    out.to_csv(OUT_CSV, index=False)
    print(f"Exported {len(out)} rows to {OUT_CSV}")
    print("r_cm range:", out.r_cm.min(), out.r_cm.max())

    # verify plotted-vs-source agreement (trivial here since same array, but
    # done explicitly per the audit requirement, reading the CSV back fresh)
    check = pd.read_csv(OUT_CSV)
    assert np.allclose(check["r_cm"].values, df["r_cm"].values)
    assert np.allclose(check["L_hbar"].values, df["L_hbar"].values)
    assert np.allclose(check["d_cm"].values, df["d_cm"].values)
    print("Verification: exported CSV values match in-memory source exactly.")

    r = out["r_cm"].values
    L = out["L_times_1e12_hbar"].values
    d = out["d_cm"].values

    L_turns = find_turning_points(L)
    d_turns = find_turning_points(d)
    d_closest_idx = np.argmin(d[r > 0.01]) if np.any(r > 0.01) else np.argmin(d)
    d_closest_idx = np.where(r == r[r > 0.01][np.argmin(d[r > 0.01])])[0][0]

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7.5, 8), sharex=True)

    ax_top.plot(r, L, color="tab:blue", lw=1.0)
    ax_top.scatter(r[L_turns], L[L_turns], color="black", s=14, zorder=5, label="turning points")
    ax_top.set_ylabel(r"L ($\hbar$) $\times 10^{12}$")
    ax_top.set_xlim(0, 20)
    ax_top.grid(alpha=0.3)
    ax_top.legend(fontsize=8, loc="upper right")

    ax_bot.plot(r, d, color="tab:green", lw=1.0)
    ax_bot.scatter(r[d_turns], d[d_turns], color="black", s=14, zorder=5, label="turning points")
    ax_bot.scatter([r[d_closest_idx]], [d[d_closest_idx]], color="red", s=30, zorder=6,
                    marker="*", label=f"closest approach (r={r[d_closest_idx]:.2f}cm, d={d[d_closest_idx]:.4f}cm)")
    ax_bot.set_ylabel("d (cm)")
    ax_bot.set_xlabel("r (cm)")
    ax_bot.set_xlim(0, 20)
    ax_bot.grid(alpha=0.3)
    ax_bot.legend(fontsize=8, loc="upper right")

    fig.suptitle("Extended Quirk Dynamics: Angular Momentum and Separation", fontsize=12, y=0.98)
    ax_top.set_title("Project diagnostic — extended beyond the paper's 0–5 cm display", fontsize=9, style="italic")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_PNG, dpi=150)
    fig.savefig(OUT_PDF)
    plt.close(fig)
    print(f"Wrote {OUT_PNG}")
    print(f"Wrote {OUT_PDF}")
    print(f"L turning points (r_cm): {r[L_turns].tolist()}")
    print(f"d turning points (r_cm): {r[d_turns].tolist()}")
    print(f"d closest approach: r={r[d_closest_idx]:.4f}cm, d={d[d_closest_idx]:.6f}cm")

    for f in [SRC, OUT_CSV, OUT_PNG, OUT_PDF,
              f"{BASE}/03_trajectory_sim/figure2_figure3_reproduction_v1.py"]:
        print(f"SHA256 {sha256_of(f)}  {f}")


if __name__ == "__main__":
    main()
