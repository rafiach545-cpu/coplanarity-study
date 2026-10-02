"""
Efficiency figures: Colored/EW 1000 vs 2000 vs paper, cutflows for all
four samples, plane-finding vs full Sec.IV comparison, Wilson 95%
comparison. Uses ONLY already-verified numbers from this session's
master table (PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv).
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
master = pd.read_csv("/home/rafia/coplanarity_study/05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv")

COLORED = "#1f3d7a"
EW = "#0e8a7d"
PAPER = "#4d4d4d"
C2000 = "#3a5ba0"
C1000 = "#7d97c9"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "legend.fontsize": 10, "xtick.labelsize": 11, "ytick.labelsize": 11,
})


def save_all(fig, name):
    fig.savefig(f"{OUT}/PNG/{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUT}/PDF/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/SVG/{name}.svg", bbox_inches="tight")
    plt.close(fig)


def wilson95(k, n):
    z = 1.96
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = (z / d) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return max(0, c - h), min(1, c + h)


def get(qname):
    return master[master["quantity"] == qname].iloc[0]


# =========================================================
# 1&2: Colored 1000 vs 2000 vs paper; EW 1000 vs 2000 vs paper
# =========================================================
def make_1000_2000_panel(prefix, ax):
    quantities = [
        ("trigger_only" if "Colored" in prefix else "trigger", "eps_trig"),
        ("fiducial", "eps_fid"),
        ("eps_plane_conditional", "eps_reco (plane)"),
        ("eps_secIV_conditional", "eps_reco (SecIV)"),
    ]
    labels = []
    x = np.arange(len(quantities))
    width = 0.25
    for i, (suffix, label) in enumerate(quantities):
        labels.append(label)
        # 1000
        qname1000 = [q for q in master["quantity"] if q.startswith(f"{prefix}1000") and suffix in q]
        r1000 = get(qname1000[0])
        p1000, lo1000, hi1000 = r1000["efficiency"], *wilson95(int(r1000["numerator"]), int(r1000["denominator"]))
        # 2000
        qname2000 = [q for q in master["quantity"] if q.startswith(f"{prefix}2000") and suffix in q]
        r2000 = get(qname2000[0])
        p2000, lo2000, hi2000 = r2000["efficiency"], *wilson95(int(r2000["numerator"]), int(r2000["denominator"]))
        paper_v = r2000["paper_value"]
        ax.bar(i - width, p1000 * 100, width=width, color=C1000,
               yerr=[[p1000 * 100 - lo1000 * 100], [hi1000 * 100 - p1000 * 100]], capsize=3,
               label="1000-event" if i == 0 else None)
        ax.bar(i, p2000 * 100, width=width, color=C2000,
               yerr=[[p2000 * 100 - lo2000 * 100], [hi2000 * 100 - p2000 * 100]], capsize=3,
               label="2000-event" if i == 0 else None)
        if not np.isnan(paper_v):
            ax.scatter(i + width, paper_v * 100, color=PAPER, marker="D", s=60, zorder=5,
                       label="Paper" if i == 0 else None)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 100); ax.set_ylabel("Efficiency (%)")
    ax.legend(loc="upper left", frameon=False, fontsize=9)


fig, axes = plt.subplots(1, 2, figsize=(12, 5))
make_1000_2000_panel("Colored", axes[0])
axes[0].set_title("Colored: 1000 vs 2000 vs paper")
make_1000_2000_panel("EW", axes[1])
axes[1].set_title("EW: 1000 vs 2000 vs paper")
fig.suptitle("Efficiency stability across sample sizes", y=1.03)
save_all(fig, "EFF_1000_vs_2000_vs_paper")

rows_1 = []
for prefix in ["Colored", "EW"]:
    for suffix, label in [("trigger_only" if prefix == "Colored" else "trigger", "eps_trig"),
                          ("fiducial", "eps_fid"), ("eps_plane_conditional", "eps_reco_plane"),
                          ("eps_secIV_conditional", "eps_reco_secIV")]:
        for n in ["1000", "2000"]:
            qn = [q for q in master["quantity"] if q.startswith(f"{prefix}{n}") and suffix in q][0]
            r = get(qn)
            rows_1.append({"benchmark": prefix, "sample_size": n, "quantity": label,
                            "numerator": r["numerator"], "denominator": r["denominator"],
                            "efficiency": r["efficiency"], "std_err": r["std_binom_err"],
                            "wilson95_lo": r["wilson95_lo"], "wilson95_hi": r["wilson95_hi"],
                            "paper_value": r["paper_value"], "exact_p_value": r["exact_p_value"]})
pd.DataFrame(rows_1).to_csv(f"{OUT}/SOURCE_DATA/EFF_1000_vs_2000_source.csv", index=False)

# =========================================================
# 3: Corrected cutflows for all four samples
# =========================================================
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
cutflow_data = {
    "Colored 1000": (["Matched", "Trig-only", "Trig&Charged", "Fiducial", "Fid&Plane", "Fid&Plane&Mult", "Final"],
                      [419, 101, 27, 7, 5, 3, 1]),
    "Colored 2000": (["Matched", "Trig-only", "Trig&Charged", "Fiducial", "Fid&Plane", "Fid&Plane&Mult", "Final"],
                      [873, 207, 68, 25, 12, 7, 3]),
    "EW 1000": (["Matched", "Trigger", "Fiducial", "Fid&Plane", "Hit-mult", "Final"],
                [511, 89, 40, 32, 16, 6]),
    "EW 2000": (["Matched", "Trigger", "Fiducial", "Fid&Plane", "Hit-mult", "Final"],
                [1045, 186, 94, 75, 48, 21]),
}
cutflow_rows = []
for ax, (name, (stages, counts)) in zip(axes.flat, cutflow_data.items()):
    color = COLORED if "Colored" in name else EW
    x = np.arange(len(stages))
    ax.bar(x, counts, color=color, alpha=0.85)
    for i, c in enumerate(counts):
        ax.text(i, c + max(counts) * 0.02, str(c), ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(stages, rotation=30, ha="right", fontsize=9)
    ax.set_title(name); ax.set_ylabel("Events")
    for s, c in zip(stages, counts):
        cutflow_rows.append({"sample": name, "stage": s, "count": c})
fig.suptitle("Corrected cutflows, all four samples", y=1.01)
save_all(fig, "CUTFLOWS_all_four_samples")
pd.DataFrame(cutflow_rows).to_csv(f"{OUT}/SOURCE_DATA/CUTFLOWS_all_four_samples_source.csv", index=False)

# =========================================================
# 4: Plane-finding vs complete Sec.IV comparison
# =========================================================
fig, ax = plt.subplots(figsize=(8, 5))
comparisons = [("Colored1000", "Colored 1000"), ("Colored2000", "Colored 2000"),
               ("EW1000", "EW 1000"), ("EW2000", "EW 2000")]
x = np.arange(len(comparisons))
width = 0.35
plane_vals, plane_err, secIV_vals, secIV_err, paper_vals = [], [], [], [], []
for prefix, _ in comparisons:
    rp = get([q for q in master["quantity"] if q.startswith(prefix) and "eps_plane_conditional" in q][0])
    rs = get([q for q in master["quantity"] if q.startswith(prefix) and "eps_secIV_conditional" in q][0])
    lo_p, hi_p = wilson95(int(rp["numerator"]), int(rp["denominator"]))
    lo_s, hi_s = wilson95(int(rs["numerator"]), int(rs["denominator"]))
    plane_vals.append(rp["efficiency"] * 100); plane_err.append([(rp["efficiency"] - lo_p) * 100, (hi_p - rp["efficiency"]) * 100])
    secIV_vals.append(rs["efficiency"] * 100); secIV_err.append([(rs["efficiency"] - lo_s) * 100, (hi_s - rs["efficiency"]) * 100])
    paper_vals.append(rp["paper_value"] * 100)
plane_err = np.array(plane_err).T; secIV_err = np.array(secIV_err).T
ax.bar(x - width / 2, plane_vals, width, yerr=plane_err, capsize=4, color="#4a90d9", label="Plane-finding ($\\epsilon_{reco}$, Sec IIIC)")
ax.bar(x + width / 2, secIV_vals, width, yerr=secIV_err, capsize=4, color="#c0504d", label="Complete Sec.IV final rate")
ax.scatter(x, paper_vals, color=PAPER, marker="D", s=60, zorder=5, label="Paper $\\epsilon_{reco}$")
ax.set_xticks(x); ax.set_xticklabels([c[1] for c in comparisons])
ax.set_ylim(0, 100); ax.set_ylabel("Efficiency (%)")
ax.set_title("Plane-finding vs complete Sec.IV rate (kept separate)")
ax.legend(loc="upper right", frameon=False, fontsize=9)
save_all(fig, "PLANE_vs_SECIV_comparison")

pd.DataFrame([{"sample": c[1], "plane_eff": pv, "secIV_eff": sv, "paper": pap}
              for c, pv, sv, pap in zip(comparisons, plane_vals, secIV_vals, paper_vals)]
             ).to_csv(f"{OUT}/SOURCE_DATA/PLANE_vs_SECIV_source.csv", index=False)

# =========================================================
# 5: Wilson 95% interval comparison (all quantities, one figure)
# =========================================================
fig, ax = plt.subplots(figsize=(9, 10))
plot_rows = master[master["paper_value"].notna()].reset_index(drop=True)
y = np.arange(len(plot_rows))
for i, r in plot_rows.iterrows():
    lo, hi = wilson95(int(r["numerator"]), int(r["denominator"]))
    color = COLORED if "Colored" in r["quantity"] else EW
    ax.plot([lo * 100, hi * 100], [i, i], color=color, linewidth=3)
    ax.scatter(r["efficiency"] * 100, i, color=color, zorder=5, s=30)
    ax.scatter(r["paper_value"] * 100, i, color=PAPER, marker="D", s=50, zorder=6)
ax.set_yticks(y); ax.set_yticklabels(plot_rows["quantity"], fontsize=8)
ax.set_xlabel("Efficiency (%)"); ax.set_xlim(0, 100)
ax.set_title("Wilson 95% intervals, project vs paper — all quantities")
save_all(fig, "WILSON95_all_quantities_comparison")
plot_rows.to_csv(f"{OUT}/SOURCE_DATA/WILSON95_all_quantities_source.csv", index=False)

print("Efficiency figures 1-5 generated.")
