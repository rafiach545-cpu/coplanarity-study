Data of the final Figures 2-7 of TABLE_I_REPRODUCTION_REPORT_2026-10-19.pdf (arXiv:1708.02243 reproduction), for ROOT. Written 2026-10-21 by scripts/R_export_figures_csv.py.
Every file: one header line, comma separated, numeric only (text replaced by *_id columns, explained below), booleans 0/1, missing = -999.
ROOT: TTree t; t.ReadFile("Fig6/fig6_kfactor_lines.csv", "", ',');  (branches are Float_t)   or   auto df = ROOT::RDF::FromCSV("Fig6/fig6_grid.csv");
Lines (Fig. 2, Fig. 6): draw one TGraph per group of the id columns listed in the file description, ordered by the point column.
Table I and background data: ROOT_CSV_2026-10-19/.

Fig2/fig2_report_figure.csv  (18444 rows)
  Report Fig. 2 (3 events x |L| and d vs r): draw each (panel_id, curve_id) as a TGraph of y vs r_cm
  source: FINAL_FIGURES/F39_fig2_combined
  columns: r_cm, y, panel_id, curve_id
    panel_id: 1 = paper; 2 = constructed; 3 = key8
    curve_id: 1 = L; 2 = d
    y: curve L: |L| (hbar); curve d: quirk separation in the CM frame (cm)
    r_cm: transverse radius of the CM (cm)

Fig2/fig2_log_scale_four_step_sizes.csv  (616811 rows)
  Report Fig. 2 on a log scale at 4 integration step sizes (Section 3.1)
  source: FINAL_FIGURES/F42_fig2_log_scale
  columns: steps_per_period, r_cm, d_cm, L_signed_hbar, curve_id
    curve_id: 1 = this work; 2 = paper
    steps_per_period: integration steps per oscillation period (-999 for the paper curve)
    L_signed_hbar: signed L (hbar)

Fig2/appendixA_d_L_vs_g.csv  (12938 rows)
  Appendix-A diagram: d and |L| along the trajectory parameter g
  source: FINAL_FIGURES/F41_appendixA_diagram
  columns: g, d_cm, L_1e12_hbar

Fig2/fig2_initial_values_numeric.csv  (2 rows)
  Fig. 2 events: initial values / every meeting (event_id: 0 = paper, 1 = ours with the paper's kinematics, 2 = ours event no. 8)
  source: ROOT_CSV_2026-10-19/Fig2/fig2_initial_values_numeric.csv
  columns: event_id, m_GeV, Lambda_keV, B_T, q1, q2, p1_lab_GeV_x, p1_lab_GeV_y, p1_lab_GeV_z, p2_lab_GeV_x, p2_lab_GeV_y, p2_lab_GeV_z, E1_GeV, E2_GeV, beta_cm_x, beta_cm_y, beta_cm_z, beta_cm_T, v_star, gamma_star, p_star_GeV, dmax_pred_cm

Fig2/fig2_meetings_numeric.csv  (12 rows)
  Fig. 2 events: initial values / every meeting (event_id: 0 = paper, 1 = ours with the paper's kinematics, 2 = ours event no. 8)
  source: ROOT_CSV_2026-10-19/Fig2/fig2_meetings_numeric.csv
  columns: meeting, r_meeting_cm, d_at_meeting_cm, L_abs_at_meeting, L_signed_at_meeting, dL_this_half, d_max_this_half_cm, r_L_zero_between_cm, b_cm, b_over_inv_m, event_id

Fig3/fig3_ours_per_event.csv  (12575 rows)
  Report Fig. 3: Δφ of the quirk pair vs r, every event (our samples)
  source: FINAL_FIGURES/F30_fig3
  columns: r_cm, dphi_rad, key, sample_id
    sample_id: 1 = COL2000; 2 = EW2000
    dphi_rad: Δφ (rad)

Fig3/fig3_paper.csv  (397 rows)
  Paper Fig. 3 curves (vector extraction)
  source: ROOT_CSV_2026-10-19/Fig3/fig3_paper.csv
  columns: r_cm, dphi_1e-3, curve_id

Fig4/fig4_hits_Z0.csv  (3231 rows)
  Report Fig. 4 (no SCT z smearing): hits of the displayed events in the plane frame (n2, n3), with Δs, Δw
  source: FINAL_FIGURES/F29_fig4_Z0
  columns: key, event_id, layer, n2_cm, n3_cm, ds_cm, dw_cm, n_sr_events, rank, ellipse, sample_id, sctz_um
    sample_id: 1 = COL2000; 2 = EW2000
    sctz_um: 0 = Z0
    rank: event shown (median events)
    ellipse: 1 if the hit is inside the signal-region ellipse

Fig4/fig4_hits_Z1160.csv  (3232 rows)
  Report Fig. 4 (SCT z 1.16 mm): hits of the displayed events in the plane frame (n2, n3), with Δs, Δw
  source: FINAL_FIGURES/F29_fig4_Z1160
  columns: key, event_id, layer, n2_cm, n3_cm, ds_cm, dw_cm, n_sr_events, rank, ellipse, sample_id, sctz_um
    sample_id: 1 = COL2000; 2 = EW2000
    sctz_um: 1160 = Z1160
    rank: event shown (median events)
    ellipse: 1 if the hit is inside the signal-region ellipse

Fig5/fig5_Z0.csv  (451 rows)
  Report Fig. 5 (no SCT z smearing): our Δs, Δw per event (ds, dw in cm) and the paper's histograms (lo, hi, paper_frac)
  source: FINAL_FIGURES/F40_fig5_Z0
  columns: ds, dw, lo, hi, paper_frac, population_id, paper_var_id
    population_id: 1 = colored; 2 = EW; 3 = converted γ + pile-up
    paper_var_id: 1 = ds; 2 = dw
    ds: Δs (cm), our events
    dw: Δw (cm), our events
    lo: paper bin low edge (cm)
    hi: paper bin high edge (cm)
    paper_frac: paper fraction in the bin

Fig5/fig5_Z1160.csv  (315 rows)
  Report Fig. 5 (SCT z 1.16 mm): our Δs, Δw per event (ds, dw in cm) and the paper's histograms (lo, hi, paper_frac)
  source: FINAL_FIGURES/F40_fig5_Z1160
  columns: ds, dw, lo, hi, paper_frac, population_id, paper_var_id
    population_id: 1 = colored; 2 = EW; 3 = converted γ + pile-up; 4 = pile-up
    paper_var_id: 1 = ds; 2 = dw
    ds: Δs (cm), our events
    dw: Δw (cm), our events
    lo: paper bin low edge (cm)
    hi: paper bin high edge (cm)
    paper_frac: paper fraction in the bin

Fig6/fig6_grid.csv  (390 rows)
  Report Fig. 6 grid: N at 300 fb-1 for every (mass, Lambda, SCT z); status: computed / bound / missing
  source: FINAL_FIGURES/F6_fig6
  columns: mass_gev, lambda_keV, sigma_fb, eps_trig, eps_trig_LO, f_ch, n_prop, L_sigma_eps_trig, n_fid, k, n_integration_fail, eps_fid, eps_reco, N_with_f, N_without_f, N_with_f_lo, N_with_f_hi, N_without_f_lo, N_without_f_hi, N_with_f_UL95_if_k0, N_without_f_UL95_if_k0, channel_id, sctz_um, status_id, status_with_f_id, status_without_f_id
    channel_id: 1 = colored; 2 = EW
    sctz_um: 0 = Z0; 1160 = Z1160
    status_id: 1 = computed; 2 = not run
    status_with_f_id: 1 = computed; 2 = bound
    status_without_f_id: 1 = computed; 2 = bound
    eps_trig: matched + shower count (both channels)
    eps_trig_LO: EW: LO ratio (alternative)
    N_with_f: 300 fb-1 x sigma x eps_trig x f_ch x k/n

Fig6/fig6_our_contours.csv  (4518 rows)
  Our Fig. 6 contour lines: draw each (channel_id, sctz_um, charge_factor, n_events, segment) as a TGraph of lambda_eV vs mass_GeV
  source: ROOT_CSV_2026-10-19/Fig6/fig6_our_contours.csv
  columns: channel_id, sctz_um, charge_factor, n_events, segment, point, mass_GeV, lambda_eV

Fig6/fig6_paper_curves.csv  (573 rows)
  Paper Fig. 6 curves (vector extraction); curve ids in ROOT_CSV_2026-10-19/README.txt (5 = discovery, 6 = exclusion)
  source: ROOT_CSV_2026-10-19/Fig6/fig6_paper_curves.csv
  columns: channel_id, curve_id, point, m_GeV, lambda_eV

Fig6/F6_reach_numeric.csv  (12 rows)
  Maximum mass reach (main contours)
  source: ROOT_CSV_2026-10-19/Fig6/F6_reach_numeric.csv
  columns: channel_id, sctz_um, charge_factor, n_events, m_max_GeV, at_lambda_keV, m_max_lo, m_max_hi, paper_m_max_GeV, paper_at_lambda_keV

Fig6/F6_reach_sensitivity_numeric.csv  (54 rows)
  Maximum mass reach of the sensitivity variants
  source: ROOT_CSV_2026-10-19/Fig6/F6_reach_sensitivity_numeric.csv
  columns: channel_id, sctz_um, variant_id, K, n_events, m_max_GeV, not_determined, at_lambda_keV, m_max_lo, m_max_hi, paper_m_max_GeV

Fig6/fig6_kfactor_lines.csv  (9857 rows)
  Report F6_kfactor: contour lines with sigma x K and the EW LO-ratio trigger (no SCT z smearing, charge factor included); draw each (channel_id, variant_id, n_events, segment) as a TGraph of lambda_eV vs mass_GeV
  source: fig6/F6_kfactor_lines.csv (F6_05_sensitivity.py)
  columns: channel_id, K, n_events, segment, point, mass_GeV, lambda_eV, variant_id
    variant_id: 1 = K1; 2 = K1.5; 3 = K1.8; 4 = K2; 5 = K0.9; 6 = K1.4; 7 = EW LO-ratio trigger
    n_events: 3 exclusion, 5 discovery

Fig7/fig7_report_histograms.csv  (966 rows)
  Report Fig. 7 histograms: our three selections and the paper (selection_id), dE/dx (MeV cm2/g) and betagamma (var_id); one row per bin (lo, hi, frac)
  source: FINAL_FIGURES/F7_fig7
  columns: lo, hi, frac, n_hits, x, y, sample_id, selection_id, var_id
    sample_id: 1 = colored_1800GeV_2keV; 2 = EW_800GeV_2keV
    selection_id: 1 = main: fiducial events, first crossing; 2 = all triggered events, all crossings; 3 = all matched events (no trigger), all crossings; 4 = paper
    var_id: 1 = dEdx; 2 = betagamma
    frac: fraction of hits in the bin
    n_hits: hits in the selection
    x: paper step-path vertex x
    y: paper step-path vertex y

Fig7/fig7_pixel_hits.csv  (12487 rows)
  every quirk hit on the 4 pixel layers (unbinned; for your own histograms)
  source: ROOT_CSV_2026-10-19/Fig7/fig7_pixel_hits.csv
  columns: event, triggered, fiducial_event, in_25ns, quirk, layer, order, t_ns, betagamma, dEdx_MPV_MeVcm2g, channel_id

Fig7/fig7_paper_curves.csv  (366 rows)
  paper Fig. 7 step histograms (vector extraction)
  source: ROOT_CSV_2026-10-19/Fig7/fig7_paper_curves.csv
  columns: var_id, channel_id, point, x, y

Fig7/fig7_dedx_definition_test.csv  (16 rows)
  report Section 9.1: the paper's betagamma histogram converted with four dE/dx definitions
  source: ROOT_CSV_2026-10-19/Fig7/fig7_dedx_definition_test.csv
  columns: channel_id, bg_min, definition_id, frac_hits_left_out, q10, median, q90, frac_below_paper_min, paper_min, paper_q10, paper_median, paper_q90, median_ratio, sample_pass, definition_pass
