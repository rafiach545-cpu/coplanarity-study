// Example ROOT macro for the CSV files in this folder (2026-10-18). Run:  root -l -b -q plot_examples.C
// Draws (1) Figure 6: our contours (no SCT z smearing, charge factor included) vs the paper's, colored panel; (2) Table I eps_reco vs Lambda.
#include "TTree.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TMultiGraph.h"
#include "TLegend.h"
#include "TAxis.h"
#include <map>
#include <utility>
void plot_examples() {
  // ---------- Figure 6, colored
  TTree ours; ours.ReadFile("Fig6/fig6_our_contours.csv", "", ',');
  TTree paper; paper.ReadFile("Fig6/fig6_paper_curves.csv", "", ',');
  TCanvas c1("c1", "Fig 6 colored", 800, 600); TMultiGraph mg;
  // our lines: channel 1, no SCT z smearing, charge factor 1; one TGraph per (n_events, segment)
  Float_t ch, sz, cf, ne, seg, m, lam;  /* TTree::ReadFile makes float (F) branches */ ours.SetBranchAddress("channel_id", &ch); ours.SetBranchAddress("sctz_um", &sz); ours.SetBranchAddress("charge_factor", &cf);
  ours.SetBranchAddress("n_events", &ne); ours.SetBranchAddress("segment", &seg); ours.SetBranchAddress("mass_GeV", &m); ours.SetBranchAddress("lambda_eV", &lam);
  std::map<std::pair<int,int>, TGraph*> g;
  for (Long64_t i = 0; i < ours.GetEntries(); ++i) { ours.GetEntry(i); if (ch != 1 || sz != 0 || cf != 1) continue;
    auto k = std::make_pair((int)ne, (int)seg); if (!g.count(k)) { g[k] = new TGraph(); g[k]->SetLineColor(ne == 3 ? kBlue : kAzure + 7); g[k]->SetLineWidth(3); g[k]->SetLineStyle(ne == 3 ? 2 : 1); mg.Add(g[k], "L"); }
    g[k]->SetPoint(g[k]->GetN(), m, lam); }
  // paper curves: curve_id 5 = discovery, 6 = exclusion (full list in README.txt)
  Float_t pch, cid, pm, pl; paper.SetBranchAddress("channel_id", &pch); paper.SetBranchAddress("curve_id", &cid); paper.SetBranchAddress("m_GeV", &pm); paper.SetBranchAddress("lambda_eV", &pl);
  TGraph *pd = new TGraph(), *pe = new TGraph(); pd->SetLineColor(kBlack); pd->SetLineWidth(2); pe->SetLineColor(kBlack); pe->SetLineWidth(2); pe->SetLineStyle(2);
  for (Long64_t i = 0; i < paper.GetEntries(); ++i) { paper.GetEntry(i); if (pch != 1) continue; if (cid == 5) pd->SetPoint(pd->GetN(), pm, pl); if (cid == 6) pe->SetPoint(pe->GetN(), pm, pl); }
  mg.Add(pd, "L"); mg.Add(pe, "L"); mg.SetTitle("Fig. 6 colored, no SCT z smearing;m_{Q} (GeV);#Lambda (eV)"); mg.Draw("A");
  mg.GetXaxis()->SetLimits(500, 2500); mg.SetMinimum(100); mg.SetMaximum(35000); c1.SetLogy(); c1.SaveAs("example_fig6_colored.png");
  // ---------- Table I eps_reco vs Lambda, EW, both SCT z settings
  TTree t; t.ReadFile("TableI/tableI_eps_reco.csv", "", ',');
  TCanvas c2("c2", "Table I", 800, 600); c2.DrawFrame(0.5, 0, 5.5, 1, "EW 800 GeV: #varepsilon_{reco} (red: no SCT z smearing, blue: 1.16 mm, open: paper);#Lambda (keV);#varepsilon_{reco}");
  t.SetMarkerStyle(20); t.SetMarkerColor(kRed); t.Draw("eps_reco:lambda_keV", "channel==2 && sctz_um==0", "P same");
  t.SetMarkerColor(kBlue); t.Draw("eps_reco:lambda_keV", "channel==2 && sctz_um==1160", "P same");
  t.SetMarkerColor(kBlack); t.SetMarkerStyle(25); t.Draw("paper_eps_reco:lambda_keV", "channel==2 && sctz_um==0", "P same");
  c2.SaveAs("example_tableI_EW.png");
}
