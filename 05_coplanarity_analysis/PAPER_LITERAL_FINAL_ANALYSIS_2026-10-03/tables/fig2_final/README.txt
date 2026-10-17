Fig. 2 of arXiv:1708.02243: paper curves and this work (colored quirk, m_Q = 1800 GeV, Lambda = 2 keV, B = 2 T along z).
Units: r_cm = transverse radius of the centre of mass (cm); d_cm = quirk separation |x1* - x2*| in the CM frame (cm); L_1e12_hbar = |L| in 1e12 hbar.
Files (comma separated, one header line, sorted in r, no missing values):
  fig2_paper_L.csv        paper |L| curve (129 points)  - vector extraction of the paper's figures/angular_momentum.pdf
  fig2_paper_d.csv        paper d curve (153 points)    - same source (L and d have different r points in the paper's figure)
  fig2_ours_constructed.csv  this work, event with the paper's kinematics: v* = 0.556, CM transverse speed 0.0975, charges +-2/3,
                             RK4 3000 steps per period; L = d* x (p1* - p2*)/2 in the initial CM frame at equal CM time
  fig2_ours_key8.csv         this work, simulated event COL2000 key 8 (MadGraph + Pythia, charges +-1), same method
Sources: tables/paper_fig2_curves.csv, FINAL_FIGURES/F34_fig2_v4/F34_fig2_v4_source.csv (scripts S2, S3, D8, F33, F34).
ROOT example:
  TTree t; t.ReadFile("fig2_ours_constructed.csv", "r_cm/D:d_cm/D:L/D", ',');   // header line is skipped when the descriptor is given
  t.Draw("L:r_cm", "", "L");
  TGraph gp("fig2_paper_L.csv", "%lg,%lg");                                      // first line (header) is ignored by TGraph
  gp.SetLineStyle(2); gp.Draw("L same");
