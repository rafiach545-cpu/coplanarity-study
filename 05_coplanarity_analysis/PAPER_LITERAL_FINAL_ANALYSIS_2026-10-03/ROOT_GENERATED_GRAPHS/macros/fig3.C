// Figure 3: rotation Delta_phi of the plane of the two quirks' velocity vectors vs the transverse radius r of the centre of mass (B = 2 T, Lambda = 2 keV).
// Data: Fig3/fig3_ours_per_event.csv (every fiducial event: r_cm on 0.1 cm bin centres, dphi_rad in rad, key = event, sample_id 1 = colored 1.8 TeV, 2 = EW 800 GeV)
//       Fig3/fig3_paper.csv (the paper's one event per benchmark from its vector figure steps.pdf; y axis label "Delta_phi x10^-3", so dphi_1e-3 is in 1e-3 rad;
//                            curve_id 0 = m_Q 1.8 TeV, 1 = m_Q 800 GeV, both Lambda = 2 keV)
// Ours: median over events at each r and the 16-84% band (quantiles, linear interpolation = TMath::Quantiles type 7). Ours is converted to 1e-3 rad for panels 1-2.
// Panel 3: per event, the median Delta_phi over r > 14.5 cm, histogram (rad, log bins), with the paper's value at r = 15 cm.
#include "common.h"
#include "TGraph.h"
#include "TGraphAsymmErrors.h"
#include "TH1D.h"
#include "TLegend.h"
#include "TLine.h"
#include "TMath.h"
#include "TLatex.h"
#include <set>
#include <cmath>

void fig3() {
  SetStyle();
  Table d = ReadCSV("Fig3/fig3_ours_per_event.csv"), p = ReadCSV("Fig3/fig3_paper.csv");
  const char* LAB[3] = {"", "colored 1.8 TeV, #Lambda = 2 keV", "EW 800 GeV, #Lambda = 2 keV"}; int COL[3] = {0, C_COL, C_EW};
  TCanvas* c = new TCanvas("fig3", "fig3", 1500, 470); c->Divide(3, 1, 0.004, 0.004);
  TH1D* hst[3]; double paper15[3];
  for (int s = 1; s <= 2; ++s) {
    std::map<long, std::vector<double>> byr; std::set<double> keys; std::map<double, std::vector<std::pair<double, double>>> ev;   // r bin -> values; event -> (r, dphi)
    for (size_t i = 0; i < d.n; ++i) if (d["sample_id"][i] == s) {
      byr[std::lround(d["r_cm"][i] * 1000)].push_back(d["dphi_rad"][i] * 1e3); keys.insert(d["key"][i]); ev[d["key"][i]].push_back({d["r_cm"][i], d["dphi_rad"][i]}); }
    std::vector<double> r, med, lo, hi; double ymax = 0;
    for (auto& kv : byr) {
      std::vector<double>& x = kv.second; double pr[3] = {0.16, 0.5, 0.84}, q[3]; TMath::Quantiles(x.size(), 3, x.data(), q, pr, false, nullptr, 7);
      r.push_back(kv.first / 1000.); med.push_back(q[1]); lo.push_back(q[1] - q[0]); hi.push_back(q[2] - q[1]); ymax = std::max(ymax, q[2]); }
    std::vector<double> z(r.size(), 0.);
    TGraphAsymmErrors* band = new TGraphAsymmErrors(r.size(), r.data(), med.data(), z.data(), z.data(), lo.data(), hi.data());
    band->SetFillColorAlpha(COL[s], 0.25); band->SetLineColor(COL[s]);
    TGraph* gm = new TGraph(r.size(), r.data(), med.data()); gm->SetLineColor(COL[s]); gm->SetLineWidth(3);
    std::vector<double> px, py; double best = 1e9; paper15[s] = NAN;
    for (size_t i = 0; i < p.n; ++i) if (p["curve_id"][i] == s - 1) {
      if (p["r_cm"][i] <= 15.0) { px.push_back(p["r_cm"][i]); py.push_back(p["dphi_1e-3"][i]); ymax = std::max(ymax, p["dphi_1e-3"][i]); }
      if (std::fabs(p["r_cm"][i] - 15.0) < best) { best = std::fabs(p["r_cm"][i] - 15.0); paper15[s] = p["dphi_1e-3"][i] * 1e-3; } }
    TGraph* gp = new TGraph(px.size(), px.data(), py.data()); gp->SetLineColor(C_PAPER); gp->SetLineStyle(2); gp->SetLineWidth(2);
    c->cd(s); gPad->SetLeftMargin(0.14);
    TH1D* fr = new TH1D(Form("fr3_%d", s), Form("%s;r (cm);#Delta#phi (#times10^{-3} rad)", LAB[s]), 10, 0, 15); fr->SetMaximum(ymax * 1.3); fr->SetMinimum(0); fr->Draw("AXIS");
    TLatex tt; tt.SetNDC(); tt.SetTextFont(42); tt.SetTextSize(0.048); tt.DrawLatex(0.14, 0.94, LAB[s]);
    band->Draw("3 same"); gm->Draw("L same"); gp->Draw("L same");
    TLegend* lg = new TLegend(0.16, 0.70, 0.75, 0.90);
    lg->AddEntry(gm, Form("this work, median (%zu events)", keys.size()), "l"); lg->AddEntry(band, "this work, 16-84% of events", "f"); lg->AddEntry(gp, "paper (one event)", "l"); lg->Draw();
    // per-event median over r > 14.5 cm (rad), log bins 10^-5 ... 10^-1.5 in steps of 0.25 decade (as the report)
    std::vector<double> e; for (int k = 0; k <= 14; ++k) e.push_back(std::pow(10., -5 + 0.25 * k));
    hst[s] = new TH1D(Form("h3_%d", s), "", e.size() - 1, e.data()); hst[s]->SetLineColor(COL[s]); hst[s]->SetLineWidth(3);
    std::vector<double> evmed;
    for (auto& kv : ev) { std::vector<double> x; for (auto& q : kv.second) if (q.first > 14.5) x.push_back(q.second);
      if (x.empty()) continue; double m = TMath::Median(x.size(), x.data()); evmed.push_back(m); hst[s]->Fill(std::min(std::max(m, e.front() * 1.0001), e.back() * 0.9999)); }
    printf("Fig3 %s: %zu events, median over events at r = 15 cm %.3g rad (per-event medians: median %.3g rad); paper's event at r = 15 cm: %.3g rad\n", LAB[s], keys.size(),
           med.back() * 1e-3, TMath::Median(evmed.size(), evmed.data()), paper15[s]);
  }
  c->cd(3); gPad->SetLogx(); gPad->SetLeftMargin(0.14);
  double hm = std::max(hst[1]->GetMaximum(), hst[2]->GetMaximum());
  hst[1]->SetTitle("#Delta#phi at r > 14.5 cm, per event;#Delta#phi (rad);events"); hst[1]->SetMaximum(hm * 2.0); hst[1]->Draw("HIST"); hst[2]->Draw("HIST same");
  TLegend* lg = new TLegend(0.16, 0.68, 0.93, 0.90); lg->SetFillStyle(0);
  for (int s = 1; s <= 2; ++s) {
    TLine* l = new TLine(paper15[s], 0, paper15[s], hm * 1.3); l->SetLineColor(COL[s]); l->SetLineStyle(2); l->SetLineWidth(2); l->Draw();
    lg->AddEntry(hst[s], Form("this work, %s", s == 1 ? "colored" : "EW"), "l"); lg->AddEntry(l, Form("paper's event at r = 15 cm, %s", s == 1 ? "colored" : "EW"), "l"); }
  lg->Draw();
  Save(c, "Fig3", "fig3_dphi_vs_r");
}
