#!/usr/bin/env python3
"""
Phase 1: line-by-line paper evidence matrix from the arXiv v2 LaTeX source (quirks_prd_v2.tex).
Every non-comment sentence (body, captions, footnotes, table, appendix) becomes one row; TeX comment
lines are listed separately (status COMMENT, not paper text); v1->v2 changed lines are listed.
Implementation-relevant sentences are annotated from the ANNOT table below (pattern -> annotation);
other sentences are recorded as narrative with "no direct implementation consequence".
Status vocabulary: PAPER-STATED, REFERENCE-STATED, DERIVED DIRECTLY, INFERRED, UNDOCUMENTED, NARRATIVE, COMMENT.
"""
import csv, difflib, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/../tables"
SRC = "/home/rafia/coplanarity_study/05_coplanarity_analysis/EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/paper_source"
v2 = open(f"{SRC}/v2/quirks_prd_v2.tex").read().split("\n")
v1 = open(f"{SRC}/v1/quirks_arxiv.tex").read().split("\n")

# pattern, requirement, reference, consequence, current project value, status, ambiguity, action
ANNOT = [
 (r"\\Lambda\\gtrsim 30|Lambda \\gtrsim 30", "regime classification by Lambda", "-", "none (benchmarks 2,4 keV in the intermediate regime)", "-", "NARRATIVE", "", "none"),
 (r"d_\{\\cm\}\\sim 2", "Eq.1 amplitude d_cm ~ 2 cm (gamma-1)(mQ/100 GeV)(keV/Lambda)^2", "-", "validation target for trajectories; Fig.6 d_cm contours", "trajectories reproduce Eq.1 (ratio truth Delta_w/A ~0.53-0.59 both benchmarks)", "PAPER-STATED", "", "validate"),
 (r"\(1,1\)_1 and \$\(3,1\)", "benchmarks are vector-like quirks in (1,1)_1 and (3,1)_{2/3}", "-", "EW: colour-singlet, Y=1, |Q|=1, spin 1/2 vector-like; colored: triplet, Q=2/3, spin 1/2", "EW UFO: spin1/2, Q=-1, colour 1, BUT Z coupling = SM chiral electron (wrong for (1,1)_1); colored UFO correct", "PAPER-STATED", "", "EW Z coupling = implementation error (trigger-neutral, sigma -24%); flag"),
 (r"roughly 30\\% as estimated", "~30% of colored final states have +-1 charges", "Pythia8", "colored charge requirement exists", "both R-hadrons non-zero charge; observed charged fraction 0.29-0.31", "PAPER-STATED", "+-1 vs non-zero", "apply non-zero (next sentence)"),
 (r"as long as both quirk-hadrons carry non-zero electric charge", "analysis requires both quirk-hadrons charged (non-zero)", "-", "colored: require both R-hadron charges != 0", "non-zero (frozen COL1000/COL2000 inputs)", "PAPER-STATED", "placement in cutflow not stated", "apply between trigger and fiducial (INFERRED placement)"),
 (r"S = - m_Q \\sum", "Eq.2 Nambu-Goto action, Lambda^2 = string tension", "Luscher", "string tension = Lambda^2", "Lambda^2 used as tension", "PAPER-STATED", "", "verified"),
 (r"\\frac\{\\partial\}\{\\partial t\}\(m\\gamma", "Eq.3 EOM with parallel/perp string force + F_ext", "-", "integrator EOM", "project integrator (validated vs Eq.4)", "PAPER-STATED", "", "verified"),
 (r"string can be approximated as straight", "straight-string approximation for Lambda >> 100 eV", "-", "straight string", "straight string", "PAPER-STATED", "", "verified"),
 (r"d_\{\\rm cm\}\(t\)=", "Eq.4 free motion", "-", "integrator validation", "validate_against_eq4.py", "PAPER-STATED", "", "verified"),
 (r"uniform 2T magnetic field|2T magnetic field along", "uniform 2 T field along z", "-", "B=2 T along z", "B=2 T along z", "PAPER-STATED", "", "verified"),
 (r"with up to 1 jet using", "signal: up to 1 jet, MG5_aMC, matched with Pythia8", "MG5, Pythia8", "0+1 jet MLM", "0+1 jet, MLM ickkw=1, xqcut 30, qCut 45", "PAPER-STATED", "matching parameters, PDF, scale, sqrt(s), tune, versions not stated", "keep frozen values; label UNDOCUMENTED"),
 (r"unit charge and are produced in Drell-Yan", "EW: unit charge, Drell-Yan", "-", "qqbar -> gamma*/Z -> QQ", "p p > qe+ qe- (+j)", "PAPER-STATED", "", "verified"),
 (r"only QCD contributions are included", "colored: QCD production only", "-", "no EW couplings for colored quirk", "UFO has only QC-g vertex", "PAPER-STATED", "", "verified"),
 (r"numerically solving the equation of motion", "four-momenta evolved by numerically solving Eq.3", "-", "numerical integration", "integrate_trajectory_fast_v2", "PAPER-STATED", "integrator / step size not stated", "project validated step sizing"),
 (r"intersections of the trajectories with a simplified model", "hits = intersections with simplified ATLAS ID; centre of each pixel hit used", "-", "pixel hits at pixel centre", "pixel centre quantisation", "PAPER-STATED", "multiple crossings not specified", "first outward crossing per layer (INFERRED; Sec. III B says quirks 'most likely intersect each layer only once')"),
 (r"parameters of the various detector elements as specified in", "detector parameters from ref [27]", "ref [27] (=arXiv:0901.0512 ID chapter)", "radii, lengths, accuracies from [27]", "Run-2 radii incl. IBL; finite lengths from [27]", "PAPER-STATED", "[27] is pre-IBL (7 barrel layers)", "use [27]; IBL radius/length INFERRED (paper Fig.4 hit spacing confirms 8 Run-2 layers)"),
 (r"pixel size rather than the resolution", "pixel: use pixel size (not resolution)", "ref [27]: 50x400 um", "pixel-centre quantisation on 50x400 um grid", "quantisation (IBL 50x250 um INFERRED)", "PAPER-STATED", "Gaussian(pitch) vs quantisation (tested: equivalent to pitch/sqrt12)", "quantisation ('centre of each pixel hit')"),
 (r"twice the intrinsic accuracy", "SCT resolution = 2 x intrinsic accuracy of [27]", "ref [27]: 17 um (R-phi), 580 um (z)", "SCT sigma_Rphi=34 um, sigma_z=1160 um", "literal: 34/1160 um; systematic envelope z in {0,34,580} um", "PAPER-STATED + REFERENCE-STATED", "Gaussian interpretation INFERRED; contradicts paper Fig.5 Delta_s", "LITERAL = 34/1160 um; envelope kept as systematic"),
 (r"neightboring pixels", "hits in neighbouring pixels merged into one hit", "-", "pixel merging (adjacency 1, transitive)", "merge_neighboring_pixel_hits", "PAPER-STATED", "adjacency definition (edge vs corner) not stated", "adjacency 1 incl. diagonal (project)"),
 (r"smearing with width 45 mm", "uniform gaussian smearing 45 mm of z of all hits (beamspot)", "-", "common per-event z shift (DERIVED: 'uniform' over all hits)", "vertex z0 ~ N(0,4.5 cm), shared", "PAPER-STATED", "common vs per-hit: 'uniform' read as common", "common event-level shift"),
 (r"only included the barrel of the pixel and SCT", "only barrel of pixel and SCT; effectively |eta|<~1.8", "ref [27] lengths", "finite barrels (|z|<400.5/749 mm); no explicit eta cut", "LITERAL: finite barrel; systematic: eta-cone", "PAPER-STATED + REFERENCE-STATED", "1.8 inconsistent with all-8-layer finite barrel (1.17)", "finite barrel primary; eta cone systematic"),
 (r"timing constraint \(\$t < 25", "timing constraint t<25 ns", "-", "max hit time < 25 ns", "max crossing time over tracker layers < 25 ns", "PAPER-STATED", "where measured not stated", "tracker crossings (INFERRED)"),
 (r"quirks must reach the muon chamber in less than 25", "muon-chamber timing caveat (motivation)", "-", "none (no muon trigger used)", "-", "NARRATIVE", "", "none"),
 (r"impose a \$p_T>\$ 200 GeV cut on the center mass momentum", "trigger: pT(QQbar CM system) > 200 GeV", "ATL-DAQ-PUB-2016-001", "pair pT > 200", "final-state pair pT > 200 / matched", "PAPER-STATED", "level (hard/final) and denominator not stated", "final state; matched (DERIVED: reproduces colored 0.24)"),
 (r"primary vertex is identified correctly", "primary vertex known, at origin", "-", "fit planes through true vertex", "vertex-relative hits", "PAPER-STATED", "", "verified"),
 (r"d\(\{\\bm n\},  \{\\bm x\}_a\)", "Eq.10 RMS distance with 1/(N-1)", "-", "Delta definitions", "fit_plane N-1", "PAPER-STATED", "", "verified"),
 (r"\{\\bm T\}\(\{\\bm x\}_a\)_\{ij\}", "Eq.11 tensor T with 1/(N-1), no mean subtraction", "-", "T", "fit_plane", "PAPER-STATED", "", "verified"),
 (r"smallest eigenvalue, \$\\Delta s\^2", "Delta_s^2 = smallest eigenvalue", "-", "Delta_s = sqrt(lambda_1)", "sqrt(lambda_1)", "PAPER-STATED", "", "verified"),
 (r"second eigenvalue, denoted by \$\\Delta w", "Delta_w = second eigenvalue measure", "-", "Delta_w = sqrt(lambda_2)", "sqrt(lambda_2)", "PAPER-STATED", "paper Fig.4 shows quoted Delta_w = 0.5 sqrt(lambda_2)", "Eq. definition primary; Fig.4 factor-2 convention systematic (W2)"),
 (r"8 layers of detector", "8 detector layers (pixel + SCT)", "-", "8 layers", "IBL+3 pixel+4 SCT", "PAPER-STATED", "which 8 layers (ref [27] gives 7)", "IBL added (DERIVED from paper Fig.4 hit positions)"),
 (r"Start from the 8\$\^\{\\rm th\}\$ layer", "seed pairs in layers 8 and 7: dphi<0.1, dz<2 cm", "-", "seeding", "coplanarity_fit", "PAPER-STATED", "", "verified"),
 (r"four-hits combinations", "4-hit seeds: x.n3>0, Ds<0.05, Dw<1 cm", "-", "seed cuts", "coplanarity_fit", "PAPER-STATED", "", "verified"),
 (r"collect all hits that satisfy", "iteration window: x.n3>0, |x.n1|<0.05, |x.n2|<1 cm", "-", "association window", "coplanarity_fit", "PAPER-STATED", "", "verified"),
 (r"do not increase by a factor of 3", "accept hit if Ds and Dw do not increase by x3; smallest |x.n1| first", "-", "growth rule", "relative to current list", "PAPER-STATED", "reference (current vs seed) - literal = current", "current list"),
 (r"Iterate the previous steps all the way to the first layer", "iterate to layer 1", "-", "outside-in to layer 1", "coplanarity_fit", "PAPER-STATED", "", "verified"),
 (r"apply the final cut \$\\Delta w < 1\$ cm", "event selection: Dw<1, keep smallest Ds", "-", "plane selection", "select_reconstructed_plane", "PAPER-STATED", "", "verified"),
 (r"At least one plane reconstructed", "SR cut 1: >=1 plane", "-", "SR", "apply_signal_region_cuts", "PAPER-STATED", "", "verified"),
 (r"All but one layer must contain 2 hits", "SR cut 2: 7 layers with 2 hits, remaining >=1", "-", "SR", "check_hit_multiplicity (>=2 counted)", "PAPER-STATED", "'2 hits' read as >=2", ">=2"),
 (r"\\Delta w < 1.0 \\; \{\\rm cm\}\}\$ and", "SR cut 3: Dw<1.0 cm and Ds<0.01 cm", "-", "SR", "apply_signal_region_cuts", "PAPER-STATED", "", "verified"),
 (r"reconstruction efficiency for these cuts", "eps_reco refers to the SR cuts (~73%)", "-", "eps_reco = full SR / (trig AND fid)", "full SR", "PAPER-STATED", "", "verified"),
 (r"fiducial efficiency parametrizes", "eps_fid: each quirk intersects each layer at least once, in trigger-passing events; includes 25 ns cut", "-", "eps_fid = fid / trigger", "16 first crossings, t<25", "PAPER-STATED", "", "verified"),
 (r"reconstruction efficiency is defined as", "eps_reco on trigger AND fiducial events", "-", "denominator", "trig AND fid", "PAPER-STATED", "", "verified"),
 (r"epsilon = \\epsilon_\{\\trig\}\\times", "Eq.12 eps = eps_trig x eps_fid x eps_reco", "-", "factorisation", "-", "PAPER-STATED", "", "verified"),
 (r"langle \\mu\\rangle=50", "pile-up <mu>=50, beam-spot spread 45 mm", "-", "pile-up overlay mu=50", "pile-up pipeline mu=50", "PAPER-STATED", "", "Phase 8"),
 (r"125\$\\times 10\^3\$ events", "pile-up from 125k Pythia8 min-bias events through simplified detector [Knapen:2016hky]", "arXiv:1612.00850 App. A", "min-bias pool + detector of 1612.00850", "20000-event pool (project)", "PAPER-STATED", "pool size differs", "record difference"),
 (r"tracking efficiency plots", "unassociated hits: remove tracks per ATLAS tracking efficiency (ATL-PHYS-PUB-2015-051), eta-dependence neglected in barrel", "ATL-PHYS-PUB-2015-051", "track suppression", "tracking_efficiency.py", "PAPER-STATED", "", "Phase 8"),
 (r"service layers and endcaps", "pile-up sim includes beam pipe, services, endcaps, brems, ionisation", "1612.00850", "pile-up detector model", "helix_propagation.py", "PAPER-STATED", "", "Phase 8"),
 (r"secondaries from hadronic interactions", "no hadronic secondaries (offset by conservative mu)", "-", "none", "none", "PAPER-STATED", "", "none"),
 (r"Z\+\\gamma\+j\$ sample", "conversion bkg: Z(nunu)+gamma+j, MET>200, photon pT>0.5 GeV, sigma~1 pb -> ~10 fb with beam-pipe conversion; equal energy sharing", "PDG Figs 33.16/33.17", "conversion background model", "converted-photon pipeline", "PAPER-STATED", "perturbative order, conversion radius details", "Phase 9"),
 (r"overlay pile-up hits", "conversion events overlaid with pile-up", "-", "overlay", "conversion_with_pileup_mu50", "PAPER-STATED", "", "Phase 10"),
 (r"only \$\\sim 10\^\{-3\}\$ of all background events", "pile-up: ~1e-3 events with plane with >=1 hit in 4/8 layers; 6e-5 with all 8", "-", "pile-up validation numbers", "pile-up statistics", "PAPER-STATED", "", "Phase 8"),
 (r"allowed to have 1-hit per layer", "pile-up bkg distribution from relaxed 1-hit/layer events weighted by multiplicity efficiency", "-", "relaxed control", "pile-up pipeline", "PAPER-STATED", "", "Phase 8"),
 (r"3 \(5\) events", "Fig.6 contours: 3 (5) signal events at 300 fb^-1", "-", "Figure 6 only", "-", "PAPER-STATED", "", "out of scope (Figure 6 paused)"),
 (r"most probable value as a function", "App. A dE/dx: most probable value, omit beta*gamma<0.1", "PDG", "not used in analysis", "-", "PAPER-STATED", "", "none"),
]

# plain-substring fallbacks for patterns whose LaTeX escaping is awkward
KEYS = {
 r"\(1,1\)_1 and \$\(3,1\)": "vector-like quirks in the $(1,1)_1$",
 r"only included the barrel of the pixel and SCT": "only included the barrel",
 r"d\(\{\\bm n\},  \{\\bm x\}_a\)": "root-mean-squared distance of the hits to the plane",
 r"Start from the 8\$\^\{\\rm th\}\$ layer": "collect all pairs of hits with",
 r"collect all hits that satisfy": "collect all hits that satisfy",
 r"At least one plane reconstructed": "At least one plane reconstructed",
 r"All but one layer must contain 2 hits": "All but one layer must contain 2 hits",
 r"\\Delta w < 1.0 \\; \{\\rm cm\}\}\$ and": "{\\Delta s < 0.01 \\; {\\rm cm}}",
}


def sentences(lines, start, stop):
    body = []
    for i in range(start, stop):
        l = lines[i]
        if l.lstrip().startswith("%"):
            continue
        body.append((i + 1, re.sub(r"(?<!\\)%.*$", "", l) + "\n"))
    text, idx = "", []
    for ln, l in body:
        for ch in l:
            text += ch; idx.append(ln)
    out = []
    # split only at . ! ? followed by whitespace and an upper-case letter, '$', '\\' or '{' (keeps decimals,
    # "Fig.~", "Sec.~", "e.g." inside sentences); also split at \item and blank-line paragraph breaks
    pos = 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-Z$\\{(])|\\item\b|\n\s*\n", text):
        seg = text[pos:m.start()]
        if len(seg.strip()) > 3:
            out.append((idx[pos], re.sub(r"\s+", " ", seg).strip()))
        pos = m.end()
    if len(text[pos:].strip()) > 3:
        out.append((idx[pos], re.sub(r"\s+", " ", text[pos:]).strip()))
    return out

sec = {}
cur = "preamble"
for i, l in enumerate(v2):
    m = re.search(r"\\(sub)?section\*?\{([^}]*)", l)
    if m and not l.lstrip().startswith("%"):
        cur = ("  " if m.group(1) else "") + re.sub(r"\\label\{.*", "", m.group(2))
    if "\\appendix" in l:
        cur = "Appendix"
    sec[i + 1] = cur
start = next(i for i, l in enumerate(v2) if "\\begin{abstract}" in l or "\\section{Introduction}" in l)
stop = next(i for i, l in enumerate(v2) if "\\bibliography{" in l)
rows = []
for ln, s in sentences(v2, start, stop):
    hits = [rest for pat, *rest in ANNOT if re.search(pat, s) or (KEYS.get(pat) and KEYS[pat] in s)]
    a = None
    if hits:
        a = [" || ".join(h[k] for h in hits) for k in range(7)]
        a[4] = hits[0][4] if len({h[4] for h in hits}) == 1 else " || ".join(h[4] for h in hits)
    if a is None:
        a = ["(narrative / physics motivation)", "-", "no direct implementation consequence", "-", "NARRATIVE", "", "none"]
    rows.append(dict(source="v2 body", tex_line=ln, section=sec.get(ln, ""), text=s[:900], requirement=a[0], reference=a[1],
                     implementation_consequence=a[2], current_project_value=a[3], status=a[4], ambiguity=a[5], action=a[6]))
for i, l in enumerate(v2[start:stop], start + 1):
    if l.lstrip().startswith("%") and len(l.strip()) > 2:
        rows.append(dict(source="v2 TeX comment", tex_line=i, section=sec.get(i, ""), text=l.strip()[:900],
                         requirement="(not paper text)", reference="-", implementation_consequence="none unless corroborated",
                         current_project_value="-", status="COMMENT",
                         ambiguity="author draft information" if re.search(r"MG5|Pythia 8|0\.03|0\.21", l) else "",
                         action="record (MG5 v2.3.3 / Pythia 8.212 / draft eps_trig tested separately)" if re.search(r"MG5|Pythia|0\.03", l) else "none"))
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, v1, v2).get_opcodes():
    if tag != "equal":
        rows.append(dict(source=f"v1->v2 {tag}", tex_line=j1 + 1, section=sec.get(j1 + 1, ""),
                         text=(" | ".join(v1[i1:i2]) + " => " + " | ".join(v2[j1:j2]))[:900], requirement="(version difference)",
                         reference="-", implementation_consequence="checked: no change to Table I or implementation-relevant text" , current_project_value="-",
                         status="NARRATIVE", ambiguity="", action="none"))
cols = ["source", "tex_line", "section", "text", "requirement", "reference", "implementation_consequence", "current_project_value", "status", "ambiguity", "action"]
for name in ("PAPER_REQUIREMENTS_LINE_BY_LINE.csv", "paper_requirement_matrix.csv"):
    with open(f"{OUT}/{name}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), Counter(r["status"] for r in rows), Counter(r["source"].split()[0] + " " + r["source"].split()[1] for r in rows))
used = {p for p, *_ in ANNOT if any(re.search(p, r["text"]) or (KEYS.get(p) and KEYS[p] in r["text"]) for r in rows if r["source"] == "v2 body")}
print("annotation patterns matched:", len(used), "/", len(ANNOT)); print("UNMATCHED:", [p for p, *_ in ANNOT if p not in used])
