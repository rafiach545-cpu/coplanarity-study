# Figure 5 event-weight denominator audit (v1) — 2026-09-21

Read-only. No event generation, detector simulation, or reconstruction run.

## 1. Exact meaning of N=125 (colored) — **CORRECTED**
**N=125 is NOT the full matched sample.** It is a **charge-filtered
subset** of the true matched sample. Verified directly:
- `zcat .../quirk_signal_1800gev_2kev/.../tag_1_pythia8_events.hepmc.gz | grep -c "^E "` = **419** E-records (the full matched+showered sample).
- `extract_quirk_momenta.py`'s own docstring/code confirms: of 419 mass-matched candidate pairs, only 125 (29.8%) have both R-hadrons electrically non-zero-charge (required per paper Sec II: a neutral R-hadron leaves no tracker hit). The other 294 are correctly excluded from the *analysis*, but they are **not absent from the matched sample the cross-section refers to.**
- Every one of the 419 raw HepMC events carries the identical weight **7.5035995×10⁻⁴** (verified: `E` line's last field, first event shown = `7.5035995e-04`). Sum over all 419 = **0.314400819** = exactly the banner's "Matched Integrated weight (pb)" × 1000 (fb conversion) = 0.00031440081900×1000. This confirms the raw per-event weight field already equals `σ_matched(fb)/419`, and is **already stored correctly in the analysis CSV's own `weight` column** (`quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv`, confirmed value 0.00075036 for all 125 rows).

## 2. Exact meaning of N=511 (EW) — unchanged, already correct
`zcat .../quirk_ew_800gev_4kev/.../tag_1_pythia8_events.hepmc.gz | grep -c "^E "` = **511** — this **is** the full matched sample (EW quirk is a color-singlet with fixed unit charge; no charge filter is needed or applied, confirmed by `extract_ew_quirk_momenta.py`'s docstring: "511 each"). Every event carries weight **4.5738381×10⁻⁴**; sum over 511 = 0.233723127 = the banner's matched xsec (pb)×1000 exactly. **No correction needed.**

## 3. Exact meaning of N=9139 and N=10000 — unchanged, already correct
N=10000 = raw generated Z+γ+j events (denominator of `PER_EVENT_XSEC_PB = TOTAL_XSEC_PB/10000`). N=9139 = the post-shower MET>200GeV & pT_γ>0.5GeV survivors — a **downstream filter**, correctly **not** used as the weight denominator (the code already divides by the full 10000, letting the 861 discarded events reduce yield, exactly the correct general-formula behavior). Verified `weight_pb` is identical (2.310512×10⁻⁷ pb) in both the μ=0 (v4) and μ=50 overlay CSVs — pile-up does not alter it, and the 1% conversion probability is applied exactly once (`PER_EVENT_XSEC_PB × 0.01`).

## 4. Correct denominator for every component

| Component | Old denominator | **Correct denominator** | Changed? |
|---|---|---|---|
| Colored | 125 (charge-filtered subset) | **419** (full matched HepMC sample) | **YES — corrected** |
| EW | 511 | 511 | No |
| Converted-γ(+PU) | 10000 | 10000 | No |

## 5. Correct event-weight formula
For equal-weight unweighted MC samples: **w = σ_matched / N_full_matched_sample**, using every event this cross-section was integrated over — **never** a denominator reduced by a downstream physics/analysis filter (charge, trigger, fiducial, etc.); discarded events instead simply contribute zero to the weighted histogram. All three samples here have constant, positive weights (verified directly from the raw files) — no LHE-style variable-weight renormalization (`w_i = σ×w_i/Σw_i`) was needed.

## 6. Old vs corrected event weights

| Component | OLD weight (fb/event) | **CORRECTED weight (fb/event)** | Ratio |
|---|---|---|---|
| Colored | 2.515207×10⁻³ | **7.503600×10⁻⁴** | 3.352× too large before |
| EW | 4.573838×10⁻⁴ | 4.573838×10⁻⁴ (unchanged) | 1.000 |
| Converted-γ+PU | 2.310512×10⁻⁴ | 2.310512×10⁻⁴ (unchanged) | 1.000 |

## 7. Old vs corrected histogram integrals (sum of weights over the plotted Sec IIIC population, fb)

| Component | OLD integral | **CORRECTED integral** |
|---|---|---|
| Colored (N=5) | 1.257603×10⁻² | **3.751800×10⁻³** |
| EW (N=32) | 1.463628×10⁻² | 1.463628×10⁻² (unchanged) |
| Converted-γ+PU (N=3276) | 0.756924 | 0.756924 (unchanged) |

## 8. Did Figure 5 change? **Yes — the colored-quirk curve moved down by a factor of 3.352×.** EW and converted-γ+pileup curves are unchanged.

## 9. Corrected Figure 5 path and source CSV
`05_coplanarity_analysis/fig5_absnorm_audit_v1/figure5_left_panel_ABSOLUTE_3curves_v2_CORRECTED.png` and
`figure5_left_panel_ABSOLUTE_source_v2_CORRECTED.csv`. The prior (v1,
now known incorrect for the colored curve) files are **preserved,
not overwritten**: `figure5_left_panel_ABSOLUTE_3curves.png` /
`figure5_left_panel_ABSOLUTE_source.csv`.

## 10. Files inspected, with paths and hashes
- `/home/rafia/hep_tools/quirk_signal_1800gev_2kev/Events/run_01/tag_1_pythia8_events.hepmc.gz` — sha256=`c983da0977f670b034ee935fa28c9b404ac4676a22809077b5b7d2339ea8ff01`
- `/home/rafia/hep_tools/quirk_ew_800gev_4kev/Events/run_01/tag_1_pythia8_events.hepmc.gz` — sha256=`d94c83d61e2126299d5f898e6cadf7e47fd3835e794373427bd54f7ccf6b769a`
- `01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv` — sha256=`8f46a31c7a05cf4aeffa0a8b068e22bbc158dda4a4e63100a8bbf02efced918f`
- `01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv` — sha256=`8e169e7901a7c0e231e7de7f8b8a15c14131fc256d2bb312a3cec931f2d7568d`
- `01_signal_generation/extract_quirk_momenta.py`, `extract_ew_quirk_momenta.py` (docstrings/code re-read in full)
- Both banner files (hashes recorded in the prior audit turn, unchanged)

## 11. Tests and exit codes
`tests/test_wilson_interval_regression.py` — exit 0 (rerun, unaffected by this task).

## 12–13. Commit hash / git status
See final response.

## 14. Confirmation
No simulation, event generation, or reconstruction was run. No process
remains active (verified via `ps aux`).
