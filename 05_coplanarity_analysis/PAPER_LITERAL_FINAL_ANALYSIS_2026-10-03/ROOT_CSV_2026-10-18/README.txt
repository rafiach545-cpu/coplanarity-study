CSV files to redraw the Table I reproduction of arXiv:1708.02243 with ROOT (2026-10-18). One header line, comma separated, missing values = -999, booleans 0/1.
ROOT: auto df = ROOT::RDF::FromCSV("Fig6/fig6_grid.csv");  or  TTree t; t.ReadFile("file.csv", "", ',');  (the header line gives the branch names)
TGraph from two columns: TGraph g("file.csv", "%*lg,%lg,%lg", ",")  -- skip columns with %*lg.

TableI/tableI_eps_reco.csv  (20 rows)
  Table I reconstruction efficiency per Lambda (production samples, 2000 events, first crossing)
  source: tables/lambda_scan_summary.csv, tables/lambda_scan_z1160_summary.csv
    channel: 1 = colored (m = 1800 GeV), 2 = EW (m = 800 GeV)
    mass_GeV: quirk mass
    lambda_keV: string tension
    sctz_um: SCT z smearing (0 = none, 1160 = 1.16 mm)
    n_fid: fiducial events (denominator)
    k_signal_region: events in the signal region
    eps_reco: k / n_fid
    sigma_eps: sqrt(eps(1-eps)/n)
    paper_eps_reco: paper Table I

TableI/tableI_trigger_fiducial.csv  (2 rows)
  Trigger and fiducial efficiency, production samples (fiducial at the benchmark Lambda: colored 2 keV, EW 4 keV)
  source: report Table I (R_data_2026_10_15.production)
    channel: 
    mass_GeV: 
    n_matched: 
    n_trigger: pT(QQ) > 200 GeV
    n_trigger_both_charged: colored: both quirk-hadrons charged (EW: = n_trigger)
    n_fid_2keV: fiducial events at the benchmark Lambda
    eps_trig: n_trigger / n_matched
    eps_fid: n_fid / n_trigger_both_charged
    paper_eps_trig: 
    paper_eps_fid: 

TableI/tableI_cutflow.csv  (20 rows)
  Cut-flow after the fiducial requirement, per Lambda (production samples)
  source: tables/lambda_scan_*per_event.csv
    channel: 
    lambda_keV: 
    sctz_um: 
    n_fid: 
    n_plane: plane found (Dw < 1 cm)
    n_hits: + hit multiplicity
    n_signal_region: + Ds < 0.01 cm

TableI/EW_LO_samples.csv  (15 rows)
  EW 800 GeV: production vs leading-order samples (no SCT z smearing, first crossing)
  source: logs/D41_*_events.jsonl, Table I
    sample: 0 = production (matched + shower), 1 = LO no shower (3000 events), 2 = LO + Pythia shower (2792 events with pT(QQ) > 200 GeV)
    lambda_keV: 
    n_events: events in the sample (production: triggered)
    n_fid: 
    k_signal_region: 
    eps_reco: 
    eps_fid: 

Fig2/fig2_meetings_numeric.csv  (12 rows)
  Figure 2 per meeting, numeric (event_id 0 = paper, 1 = ours with the paper's kinematics, 2 = ours event no. 8)
  source: tables/fig2_final/fig2_meetings_detail.csv
    meeting: 
    r_meeting_cm: 
    d_at_meeting_cm: 
    L_abs_at_meeting: 
    L_signed_at_meeting: 
    dL_this_half: 
    d_max_this_half_cm: 
    r_L_zero_between_cm: r where |L| = 0 between the meetings (-999 = none)
    b_cm: impact parameter |L|/p* (cm)
    b_over_inv_m: 
    event_id: 

Fig2/fig2_paper_L.csv  (129 rows)
  Figure 2 (see tables/fig2_final/README.txt)
  source: tables/fig2_final/fig2_paper_L.csv
    r_cm: transverse radius of the CM (cm)
    L_1e12_hbar: |L| (1e12 hbar)

Fig2/fig2_paper_d.csv  (153 rows)
  Figure 2 (see tables/fig2_final/README.txt)
  source: tables/fig2_final/fig2_paper_d.csv
    r_cm: transverse radius of the CM (cm)
    d_cm: quirk separation in the CM frame (cm)

Fig2/fig2_ours_constructed.csv  (12938 rows)
  Figure 2 (see tables/fig2_final/README.txt)
  source: tables/fig2_final/fig2_ours_constructed.csv
    r_cm: transverse radius of the CM (cm)
    d_cm: quirk separation in the CM frame (cm)
    L_1e12_hbar: |L| (1e12 hbar)

Fig2/fig2_ours_key8.csv  (14304 rows)
  Figure 2 (see tables/fig2_final/README.txt)
  source: tables/fig2_final/fig2_ours_key8.csv
    r_cm: transverse radius of the CM (cm)
    d_cm: quirk separation in the CM frame (cm)
    L_1e12_hbar: |L| (1e12 hbar)

Fig2/fig2_initial_values.csv  (2 rows)
  Figure 2 (see tables/fig2_final/README.txt)
  source: tables/fig2_final/fig2_initial_values.csv
    event: 
    m_GeV: 
    Lambda_keV: 
    B_T: 
    charges: 
    p1_lab_GeV: 
    p2_lab_GeV: 
    E1_GeV: 
    E2_GeV: 
    beta_cm: 
    beta_cm_T: 
    v_star: 
    gamma_star: 
    p_star_GeV: 
    dmax_pred_cm: 
    source: 

Fig2/fig2_meetings_detail.csv  (12 rows)
  Figure 2 (see tables/fig2_final/README.txt)
  source: tables/fig2_final/fig2_meetings_detail.csv
    event: 
    meeting: 
    r_meeting_cm: 
    d_at_meeting_cm: 
    L_abs_at_meeting: 
    L_signed_at_meeting: 
    dL_this_half: 
    d_max_this_half_cm: 
    r_L_zero_between_cm: 
    b_cm: 
    b_over_inv_m: 

Fig2/fig2_logscale_four_step_sizes.csv  (616682 rows)
  Figure 2 on a log scale: event with the paper's kinematics at 4 integration step sizes
  source: tables/fig2_final/fig2_ours_constructed_steps.csv
    steps_per_period: RK4 steps per oscillation
    r_cm: 
    d_cm: 
    L_signed_hbar: L projected on its maximum direction (hbar); plot |L|

Fig2/appendixA_d_L_vs_g.csv  (12938 rows)
  d and |L| vs g (half-oscillations) for the Appendix A diagram
  source: FINAL_FIGURES/F41_appendixA_diagram
    g: time in half-oscillations (= r / meeting spacing)
    d_cm: 
    L_1e12_hbar: 

Fig3/fig3_ours_per_event.csv  (12575 rows)
  Figure 3: rotation Dphi of the plane of the two velocity vectors vs r, every fiducial event, Lambda = 2 keV
  source: FINAL_FIGURES/F30_fig3
    channel: 1 = colored 1800 GeV, 2 = EW 800 GeV
    key: event id
    r_cm: 
    dphi_rad: 

Fig3/fig3_paper.csv  (397 rows)
  Figure 3 paper curves (vector extraction): curve_id 0 = m_Q = 1.8 TeV, Lambda = 2 keV, curve_id 1 = m_Q = 800 GeV, Lambda = 2 keV
  source: tables/paper_fig3_curves.csv
    r_cm: 
    dphi_1e-3: 
    curve_id: see description

Fig4/fig4_hits_Z0.csv  (3231 rows)
  Figure 4: hits of the median-Ds signal event projected on (n3, n2); SCT z none
  source: FINAL_FIGURES/F29_fig4_Z0
    key: 
    event_id: 
    layer: 
    n2_cm: coordinate along n2 (cm)
    n3_cm: coordinate along n3 (cm)
    ds_cm: 
    dw_cm: 
    n_sr_events: 
    rank: 
    channel: 
    is_layer_ellipse: 1 = point of a detector-layer ellipse, 0 = hit

Fig4/fig4_hits_Z1160.csv  (3232 rows)
  Figure 4: hits of the median-Ds signal event projected on (n3, n2); SCT z 1.16 mm
  source: FINAL_FIGURES/F29_fig4_Z1160
    key: 
    event_id: 
    layer: 
    n2_cm: coordinate along n2 (cm)
    n3_cm: coordinate along n3 (cm)
    ds_cm: 
    dw_cm: 
    n_sr_events: 
    rank: 
    channel: 
    is_layer_ellipse: 1 = point of a detector-layer ellipse, 0 = hit

Fig5/fig5_ours_Z0.csv  (343 rows)
  Figure 5: Ds and Dw of every plane after the plane and hit cuts (before the Ds cut); signal and background SCT z none
  source: FINAL_FIGURES/F40_fig5_Z0
    population_id: 1 colored signal, 2 EW signal, 3 converted photon + pile-up, 4 pile-up only
    ds_cm: 
    dw_cm: 

Fig5/fig5_paper_histograms.csv  (108 rows)
  Figure 5 paper histograms (unit area)
  source: tables/paper_fig5_vector.json
    population_id: 
    lo: bin low edge (cm)
    hi: bin high edge (cm)
    paper_frac: fraction per bin
    var_id: 1 = Ds, 2 = Dw

Fig5/fig5_ours_Z1160.csv  (185 rows)
  Figure 5: Ds and Dw of every plane after the plane and hit cuts (before the Ds cut); signal and background SCT z 1.16 mm
  source: FINAL_FIGURES/F40_fig5_Z1160
    population_id: 1 colored signal, 2 EW signal, 3 converted photon + pile-up, 4 pile-up only
    ds_cm: 
    dw_cm: 

Fig6/fig6_grid.csv  (390 rows)
  Figure 6 grid: expected signal events at 300 fb-1 for every (mass, Lambda, SCT z)
  source: fig6/F6_N_grid.csv
    channel_id: 1 colored, 2 EW
    mass_gev: 
    lambda_keV: 
    sctz_um: 
    sigma_fb: matched cross section (fb)
    eps_trig: colored: count; EW: LO ratio
    f_ch: colored: fraction with both quirk-hadrons charged (EW 1)
    n_prop: propagated events
    n_fid: 
    k: events in the signal region
    n_integration_fail: 
    eps_fid: 
    eps_reco: 
    N_with_f: 300 fb-1 x sigma x eps_trig x f_ch x k/n
    N_with_f_lo: N at the Wilson 68% lower bound of k/n
    N_with_f_hi: 
    N_without_f: colored without f_ch
    N_without_f_lo: 
    N_without_f_hi: 
    N_with_f_UL95_if_k0: 95% upper limit on N when k = 0
    N_without_f_UL95_if_k0: 
    status_with_f: 1 computed, 2 bound (max possible N < 3, not propagated), 0 not available
    status_without_f: 

Fig6/fig6_our_contours.csv  (4387 rows)
  Our Figure 6 contour lines (3 = exclusion, 5 = discovery); draw each (channel, sctz, charge_factor, n_events, segment) as a TGraph
  source: traced from fig6/F6_N_grid.csv
    channel_id: 
    sctz_um: 
    charge_factor: colored: 1 with the both-charged factor, 0 without (EW: 1)
    n_events: 3 or 5
    segment: separate line pieces
    point: 
    mass_GeV: 
    lambda_eV: string tension (eV)

Fig6/fig6_paper_curves.csv  (573 rows)
  Paper Figure 6 curves (vector extraction): 0 = dcm_100m, 1 = dcm_100um, 2 = dcm_1cm, 3 = dcm_1m, 4 = dcm_1mm, 5 = discovery, 6 = exclusion, 7 = hscp_12.9_boundary, 8 = hscp_300, 9 = monojet_12.9_boundary, 10 = monojet_300
  source: tables/paper_fig6_curves.csv
    channel_id: 
    curve_id: see description
    point: 
    m_GeV: 
    lambda_eV: 

Fig6/F6_reach.csv  (12 rows)
  maximum mass reach (main variants)
  source: fig6/F6_reach.csv
    channel: 
    sct: 
    variant: 
    contour: 
    m_max_GeV: 
    at_lambda_keV: 
    m_max_lo: 
    m_max_hi: 
    paper_m_max_GeV: 
    paper_at_lambda_keV: 

Fig6/F6_reach_sensitivity.csv  (46 rows)
  maximum mass reach for the normalisation-sensitivity variants
  source: fig6/F6_reach_sensitivity.csv
    channel: 
    sct: 
    variant: 
    contour: 
    m_max: 
    lam_keV: 
    lo: 
    hi: 
    paper: 

Fig6/F6_ew_lo_ratio.csv  (6 rows)
  EW LO cross sections and trigger ratio
  source: fig6/F6_ew_lo_ratio.csv
    mass_gev: 
    sigma_A_fb: 
    sigma_A_err_fb: 
    sigma_B_fb: 
    sigma_B_err_fb: 
    ratio: 
    ratio_err: 

Fig7/fig7_pixel_hits.csv  (12487 rows)
  Figure 7: every quirk hit on the 4 pixel layers, Lambda = 2 keV (EW 800 GeV, colored 1800 GeV)
  source: tables/F7_pixel_hits.csv (main selection of the figure: triggered, fiducial_event, order 0, in_25ns)
    event: 
    triggered: 1 = pT(QQ) > 200 GeV event
    fiducial_event: 1 = fiducial at 2 keV
    in_25ns: 1 = hit time < 25 ns
    quirk: 
    layer: 
    order: 0 = first crossing of that layer
    t_ns: 
    betagamma: |p|/m at the crossing
    dEdx_MPV_MeVcm2g: PDG most probable value (MeV cm2/g), only for betagamma >= 0.1
    channel_id: 1 colored 1800 GeV, 2 EW 800 GeV

Fig7/fig7_paper_curves.csv  (366 rows)
  Paper Figure 7 step histograms (vector extraction)
  source: tables/paper_fig7_curves.csv
    var_id: 1 = dE/dx (MeV cm2/g), 2 = betagamma
    channel_id: 
    point: 
    x: 
    y: 

Backgrounds/backgrounds_signal_region.csv  (3 rows)
  Backgrounds in the signal region
  source: report Section 7
    sample: 1 = converted photon + pile-up (mu = 50), 2 = pile-up only
    sctz_um: 
    n_events: 
    n_signal_region: 
