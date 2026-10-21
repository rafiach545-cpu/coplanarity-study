// Figure 2 (2026-10-21): angular momentum |L| and quirk separation d of a colored quirk pair, m_Q = 1800 GeV, Lambda = 2 keV, B = 2 T along z.
// Three outputs, one per report figure (no new analysis; every point is read from ../ROOT_CSV_FIGURES_2026-10-21/Fig2/):
//   fig2_L_and_d_vs_r       report F39: |L| (top row) and d (bottom row) vs r for the paper's event, our event with the paper's kinematics and our event no. 8.
//                           Data: fig2_report_figure.csv, panel_id 1 = paper, 2 = ours with the paper's kinematics, 3 = ours event no. 8; curve_id 1 = |L|, 2 = d.
//                           Units: |L| in 1e12 hbar (the CSV README says "hbar"; the values, e.g. paper peak 0.666, are in 1e12 hbar), d in cm, r = CM radius in cm.
//   fig2_log_scale          report F42 (Sec. 3.1): |L| in hbar on a log scale for the event with the paper's kinematics at 3000 / 10000 / 30000 / 100000 RK4 steps
//                           per oscillation (left pad: all four; F42 showed 3000 and 100000 there); right pad: zoom on meeting 2, same colours, one legend (left pad). Data: fig2_log_scale_four_step_sizes.csv, curve_id 1 = this work, 2 = paper
//                           (steps_per_period 0 for the paper, not -999 as the CSV README says; its d_cm is -999). |L| below 1 hbar is drawn at 1 hbar (log axis), as in F42.
//   fig2_appendixA_d_L_vs_g report F41 panels (b) and (c): d and |L| vs g (time in units of half an oscillation) for the event with the paper's kinematics.
//                           Data: appendixA_d_L_vs_g.csv. Panel (a) of F41 is a conceptual sketch (no data) and is not redrawn.
// Separate pads for |L| and d (no second y axis), so both are solid lines: |L| blue, d orange (F39: d dashed); the y-axis title names the curve. Paper dotted black where overlaid.
#include "common.h"
#include "TGraph.h"
#include "TH1D.h"
#include "TLegend.h"
#include "TLine.h"
#include "TLatex.h"
#include "TVirtualPad.h"
#include <cmath>

static TGraph* Graph(const std::vector<double>& x, const std::vector<double>& y) {   // points sorted in x
  std::vector<size_t> o(x.size()); for (size_t i = 0; i < o.size(); ++i) o[i] = i;
  std::stable_sort(o.begin(), o.end(), [&](size_t a, size_t b) { return x[a] < x[b]; });
  TGraph* g = new TGraph(); for (size_t i : o) g->SetPoint(g->GetN(), x[i], y[i]); return g;
}
static TH1D* Frame(const char* name, const char* titles, double x0, double x1, double y0, double y1) {
  TH1D* f = new TH1D(name, titles, 10, x0, x1); f->SetMinimum(y0); f->SetMaximum(y1); f->Draw("AXIS"); return f;
}

void fig2_L_and_d() {
  Table t = ReadCSV("Fig2/fig2_report_figure.csv");
  const char* TIT[4] = {"", "Paper (arXiv:1708.02243, Fig. 2)", "This work: event with the paper's kinematics", "This work: one event of our sample (no. 8)"};
  TCanvas* c = new TCanvas("fig2_L_and_d_vs_r", "", 1650, 840); c->Divide(3, 2, 0.002, 0.002);
  for (int i = 1; i <= 6; ++i) { TVirtualPad* q = c->cd(i); q->SetPad(q->GetXlowNDC(), q->GetYlowNDC() * 0.95, q->GetXlowNDC() + q->GetWNDC(), (q->GetYlowNDC() + q->GetHNDC()) * 0.95); }   // room for the common title
  for (int p = 1; p <= 3; ++p) {
    for (int cv = 1; cv <= 2; ++cv) {
      std::vector<double> x, y; for (size_t i = 0; i < t.n; ++i) if (t["panel_id"][i] == p && t["curve_id"][i] == cv) { x.push_back(t["r_cm"][i]); y.push_back(t["y"][i]); }
      c->cd(p + 3 * (cv - 1)); gPad->SetLeftMargin(0.14); gPad->SetTopMargin(cv == 1 ? 0.11 : 0.06); gPad->SetGrid(1, 0);
      Frame(Form("fr2_%d_%d", p, cv), cv == 1 ? ";r (cm);|L| (10^{12} #hbar)" : ";r (cm);d (cm)", 0, 5, 0, cv == 1 ? 1.0 : 5.0);
      TGraph* g = Graph(x, y); g->SetLineColor(cv == 1 ? C_COL : C_EW); g->SetLineWidth(2); g->Draw("L same");
      if (cv == 1) { TLatex tl; tl.SetNDC(); tl.SetTextFont(42); tl.SetTextSize(0.05); tl.DrawLatex(0.14, 0.92, TIT[p]); }
      double ymax = *std::max_element(y.begin(), y.end());
      printf("Fig2 %-46s %s: %4zu points, max %.4f %s\n", TIT[p], cv == 1 ? "|L|" : "d  ", x.size(), ymax, cv == 1 ? "1e12 hbar" : "cm");
    }
  }
  c->cd(0); TLatex tt; tt.SetNDC(); tt.SetTextFont(42); tt.SetTextSize(0.024); tt.SetTextAlign(22); tt.DrawLatex(0.5, 0.975, "m_{Q} = 1.8 TeV,  #Lambda = 2 keV,  B = 2 T");
  Save(c, "Fig2", "fig2_L_and_d_vs_r");
}

void fig2_log() {
  Table t = ReadCSV("Fig2/fig2_log_scale_four_step_sizes.csv");
  const int NS[4] = {3000, 10000, 30000, 100000};
  const int COLS[4] = {C_COL, TColor::GetColor("#2a9d8f"), TColor::GetColor("#7b5ea7"), C_EW};
  TCanvas* c = new TCanvas("fig2_log_scale", "", 1650, 620); c->Divide(2, 1, 0.002, 0.002);
  c->cd(1)->SetPad(0.0, 0.0, 0.60, 1.0); c->cd(2)->SetPad(0.60, 0.0, 1.0, 1.0);
  double X0[2] = {0, 2.15}, X1[2] = {5, 2.50};
  for (int k = 0; k < 2; ++k) {
    c->cd(k + 1); gPad->SetLogy(); gPad->SetLeftMargin(k == 0 ? 0.10 : 0.15); gPad->SetRightMargin(0.03); gPad->SetTopMargin(0.09);
    Frame(Form("fr2log_%d", k), ";r (cm);|L| (#hbar), log scale", X0[k], X1[k], 1e5, 3e12);
    TLegend* lg = new TLegend(0.54, 0.13, 0.86, 0.43); lg->SetTextSize(0.032); lg->SetFillStyle(0);   // in the empty lower region, clear of the dips at r = 2.33 and 4.65 cm
    lg->SetHeader("RK4 steps / oscillation:", "L");
    for (int s : {-1, 3, 2, 1, 0}) {                                                 // s = -1: paper; finest step first, drawn widest, so that every curve stays visible
      std::vector<double> x, y;
      for (size_t i = 0; i < t.n; ++i) {
        bool paper = t["curve_id"][i] == 2; if (s < 0 ? !paper : (paper || t["steps_per_period"][i] != NS[s])) continue;
        x.push_back(t["r_cm"][i]); y.push_back(std::max(std::fabs(t["L_signed_hbar"][i]), 1.0));
      }
      TGraph* g = Graph(x, y); g->SetLineWidth(s < 0 ? 2 : (s == 3 ? 5 : s == 2 ? 3 : 2)); g->SetLineColor(s < 0 ? C_PAPER : COLS[s]); g->SetLineStyle(s < 0 ? 3 : 1); g->Draw("L same");
      lg->AddEntry(g, s < 0 ? "paper (from its figure)" : Form("this work, %s", s == 0 ? "3,000" : s == 1 ? "10,000" : s == 2 ? "30,000" : "100,000"), "l");
      if (k == 1) {                                                                  // printed check: smallest |L| near meeting 2 and the peak at the odd meetings
        double lmin = 1e30, rmin = 0, lmax = 0; for (size_t i = 0; i < x.size(); ++i) { if (x[i] > 2.0 && x[i] < 2.6 && y[i] < lmin) { lmin = y[i]; rmin = x[i]; } }
        for (size_t i = 0; i < t.n; ++i) { bool paper = t["curve_id"][i] == 2; if (s < 0 ? paper : (!paper && t["steps_per_period"][i] == NS[s])) lmax = std::max(lmax, std::fabs(t["L_signed_hbar"][i])); }
        printf("Fig2 log %-8s: %6zu points, smallest |L| for 2.0 < r < 2.6 cm: %.2e hbar at r = %.3f cm; largest |L| %.3e hbar\n", s < 0 ? "paper" : Form("%d", NS[s]), x.size(), lmin, rmin, lmax);
      }
    }
    TLine* l8 = new TLine(X0[k], 1e8, X1[k], 1e8); l8->SetLineColor(kRed + 1); l8->SetLineStyle(2); l8->Draw();
    TLine* lp = new TLine(X0[k], 6.4e11, X1[k], 6.4e11); lp->SetLineColor(C_MUTED); lp->SetLineStyle(3); lp->Draw();
    TLatex tl; tl.SetTextFont(42); tl.SetTextSize(k == 0 ? 0.033 : 0.040); double xt = X0[k] + 0.02 * (X1[k] - X0[k]);
    tl.DrawLatex(xt, 1.5e8, "10^{8} #hbar"); tl.DrawLatex(xt, 9e11, "peak 6.4#times10^{11} #hbar");
    if (k == 0) lg->Draw();
    gPad->RedrawAxis();
    TLatex tt; tt.SetNDC(); tt.SetTextFont(42); tt.SetTextSize(k == 0 ? 0.040 : 0.048);
    tt.DrawLatex(k == 0 ? 0.10 : 0.15, 0.93, k == 0 ? "Fig. 2 on a log scale: m_{Q} = 1.8 TeV, #Lambda = 2 keV, B = 2 T" : "zoom on meeting 2 (r #approx 2.33 cm), all step sizes");
  }
  Save(c, "Fig2", "fig2_log_scale");
}

void fig2_appA() {
  Table t = ReadCSV("Fig2/appendixA_d_L_vs_g.csv");
  TCanvas* c = new TCanvas("fig2_appendixA_d_L_vs_g", "", 1300, 820); c->Divide(1, 2, 0.002, 0.002);
  double gmax = *std::max_element(t["g"].begin(), t["g"].end());
  for (int k = 0; k < 2; ++k) {
    c->cd(k + 1); gPad->SetLeftMargin(0.09); gPad->SetRightMargin(0.03); gPad->SetTopMargin(0.12);
    const std::vector<double>& y = k == 0 ? t["d_cm"] : t["L_1e12_hbar"];
    Frame(Form("fr2a_%d", k), k == 0 ? ";g = time in units of half an oscillation (g = #Lambda^{2}t / (2m#rho));d (cm)" : ";g = time in units of half an oscillation (g = #Lambda^{2}t / (2m#rho));|L| (10^{12} #hbar)",
          0, gmax, 0, k == 0 ? 4.2 : 0.8);
    for (int m = 1; m <= (int)gmax; ++m) { TLine* l = new TLine(m, 0, m, k == 0 ? 4.2 : 0.8); l->SetLineColor(C_MUTED); l->SetLineStyle(3); l->Draw(); }
    TGraph* g = Graph(t["g"], y); g->SetLineWidth(2); g->SetLineColor(k == 0 ? C_EW : C_COL); g->SetLineStyle(k == 0 ? 2 : 1); g->Draw("L same");
    TLatex tt; tt.SetNDC(); tt.SetTextFont(42); tt.SetTextSize(0.055);
    tt.DrawLatex(0.09, 0.91, k == 0 ? "(b) Numerical simulation: separation d, zero at every meeting g = 1, 2, 3, 4"
                                    : "(c) Numerical simulation: |L| rises in each odd half and falls in each even half");
    for (int m = 1; m <= (int)gmax; ++m) {                                            // printed check: value at each meeting (nearest point to integer g)
      size_t best = 0; for (size_t i = 0; i < t.n; ++i) if (std::fabs(t["g"][i] - m) < std::fabs(t["g"][best] - m)) best = i;
      printf("Fig2 appendix A: g = %d (point at g = %.4f): %s = %.4f %s\n", m, t["g"][best], k == 0 ? "d" : "|L|", y[best], k == 0 ? "cm" : "1e12 hbar");
    }
    double ymax = *std::max_element(y.begin(), y.end()); printf("Fig2 appendix A: max %s = %.4f\n", k == 0 ? "d (cm)" : "|L| (1e12 hbar)", ymax);
  }
  Save(c, "Fig2", "fig2_appendixA_d_L_vs_g");
}

void fig2() {
  SetStyle(); gStyle->SetOptTitle(0);
  fig2_L_and_d(); fig2_log(); fig2_appA();
}
