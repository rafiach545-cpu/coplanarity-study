// Figure 5 in the paper's layout (2026-10-21): four plots, Delta_s and Delta_w, each without and with SCT z smearing; all samples of a case on one plot.
// Paper's Fig. 5 (figures/Deltat.pdf, Deltaw.pdf of arXiv:1708.02243 v2): two plots, Delta_s (left) and Delta_w (right), four samples each:
//   colored quirk (m_Q = 1.8 TeV, Lambda = 2 keV; purple, solid), EW quirk (800 GeV, 4 keV; red, solid), pile-up (green, dashed), converted gamma (blue, dashed);
//   0.1-decade bins on log x; log y; Delta_s axis 1e-3 ... 1e-1 cm with the cut Delta_s < 0.01 cm marked; Delta_w axis 5e-3 ... 1 cm.
//   y: Delta_s plot dsigma/dlog(Delta_s) in fb/bin (absolute); Delta_w plot (1/sigma) dsigma/dlog(Delta_w) (unit area).
// Here: both plots unit area (fraction of the events per 0.1-decade bin), because the CSVs give no cross section per sample at this selection stage; the
// paper's histograms (Fig5/fig5_<sct>.csv, paper_frac, normalised to unit sum) are overlaid with the same normalisation (thin dotted, same colours).
// Data: Fig5/fig5_Z0.csv (no SCT z smearing, signal and backgrounds) and Fig5/fig5_Z1160.csv (SCT z 1.16 mm, signal and backgrounds); event rows: ds, dw (cm),
//   population_id 1 colored, 2 EW, 3 converted gamma + pile-up, 4 pile-up only (only with smearing: it was not simulated without). Selection (as the report):
//   after the plane and hit-multiplicity cuts, before the Delta_s cut. Our bins: the paper's 0.1-decade grid over a wide range (no value is moved into an edge
//   bin); events outside the drawn axis range are counted and printed. The paper's histograms are taken from fig5_Z1160.csv for all four plots: its paper rows
//   are identical to those of fig5_Z0.csv (108 rows, checked) and it also has the paper's pile-up, which fig5_Z0.csv lacks.
#include "common.h"
#include "TH1D.h"
#include "TLegend.h"
#include "TLine.h"
#include "TArrow.h"
#include "TLatex.h"
#include <cmath>

const std::string OUTD = "Fig5/paper_style_4plots";
const char* PN[5] = {"", "Colored Quirk", "EW Quirk", "Converted #gamma (+ pile-up #mu = 50)", "Pileup"};   // ours: conversions with pile-up overlaid
const char* PNP[5] = {"", "Colored Quirk", "EW Quirk", "Converted #gamma", "Pileup"};                              // paper's legend
int PCOL(int p) { static int c[5] = {0, TColor::GetColor("#800080"), TColor::GetColor("#ff0000"), TColor::GetColor("#0000ff"), TColor::GetColor("#008000")}; return c[p]; }

void plot(const char* z, int v) {
  Table d = ReadCSV(Form("Fig5/fig5_%s.csv", z));
  Table P = ReadCSV("Fig5/fig5_Z1160.csv");   // the paper's histograms: the same rows in both files (checked), but only this one has the paper's pile-up
  bool sm = std::string(z) == "Z1160"; const char* VN = v == 1 ? "ds" : "dw";
  double xlo = v == 1 ? 1e-3 : 5e-3, xhi = v == 1 ? 1e-1 : 1.0, glo = v == 1 ? -5 : -4, ghi = 1;           // drawn range; binning grid 10^glo ... 10^ghi
  int nb = std::lround((ghi - glo) / 0.1); std::vector<double> e; for (int k = 0; k <= nb; ++k) e.push_back(std::pow(10., glo + 0.1 * k));
  TCanvas* c = new TCanvas(Form("fig5_%s_%s", VN, sm ? "smeared" : "unsmeared"), "", 900, 720);
  c->SetLogx(); c->SetLogy(); c->SetLeftMargin(0.15); c->SetBottomMargin(0.13); c->SetTopMargin(0.09);
  TH1D* fr = new TH1D(Form("fr_%s_%s", VN, z), v == 1 ? ";#Deltas (cm);fraction of events per bin,  #frac{1}{N} #frac{dN}{d log #Deltas}"
                                                      : ";#Deltaw (cm);fraction of events per bin,  #frac{1}{N} #frac{dN}{d log #Deltaw}", 10, xlo, xhi);
  fr->SetMinimum(1e-3); fr->SetMaximum(30); fr->GetYaxis()->SetTitleOffset(1.45); fr->GetXaxis()->SetTitleOffset(1.1); fr->Draw("AXIS");
  TLegend* lo = new TLegend(0.17, 0.72, 0.62, 0.90); lo->SetHeader("this work", "L"); lo->SetTextSize(0.028); lo->SetFillStyle(0);
  TLegend* lp = new TLegend(0.62, 0.72, 0.95, 0.90); lp->SetHeader("paper (unit area)", "L"); lp->SetTextSize(0.028); lp->SetFillStyle(0);
  int order[4] = {1, 2, 4, 3};                                                                                 // paper's legend order: colored, EW, pile-up, converted
  for (int pop : order) {
    TH1D* h = new TH1D(Form("h_%s_%s_%d", VN, z, pop), "", nb, e.data()); TH1D* hp = new TH1D(Form("p_%s_%s_%d", VN, z, pop), "", nb, e.data());
    int n = 0, out = 0;
    for (size_t i = 0; i < d.n; ++i) {
      if (d["population_id"][i] != pop) continue;
      if (d["paper_var_id"][i] == MISSING && d[VN][i] != MISSING) { double a = d[VN][i]; ++n; out += (a < xlo || a >= xhi); h->Fill(a); }
    }
    for (size_t i = 0; i < P.n; ++i) if (P["population_id"][i] == pop && P["paper_var_id"][i] == v) hp->Fill(std::sqrt(P["lo"][i] * P["hi"][i]), P["paper_frac"][i]);
    bool bkg = pop >= 3; int col = PCOL(pop);
    if (hp->GetEntries() > 0) { hp->SetLineColor(col); hp->SetLineStyle(3); hp->SetLineWidth(2); hp->Draw("HIST same"); lp->AddEntry(hp, PNP[pop], "l"); }
    if (n == 0) { printf("Fig5 %s %s %-30s: no events (not simulated in this case)\n", z, VN, PN[pop]); continue; }
    if (h->GetBinContent(0) + h->GetBinContent(nb + 1) > 0) printf("WARNING: %s %s pop %d has values outside the binning grid\n", z, VN, pop);
    h->Scale(1. / n); h->SetLineColorAlpha(col, 0.55); h->SetLineWidth(4); h->SetLineStyle(bkg ? 9 : 1); h->Draw("HIST same");   // backgrounds long-dashed (paper: dashed); paper overlay: thin dotted
    double hmax = h->GetMaximum(); int below = 0; for (size_t i = 0; i < d.n; ++i) if (d["population_id"][i] == pop && d["paper_var_id"][i] == MISSING && d[VN][i] != MISSING) below += d[VN][i] < (v == 1 ? 0.01 : 1.0);
    lo->AddEntry(h, Form("%s (N = %d)", PN[pop], n), "l");
    printf("Fig5 %s %s %-30s: N = %3d, outside the drawn range %d, below the cut %d (%.1f%%), largest bin fraction %.3f; paper bins %d\n", z, VN, PN[pop], n, out, below,
           100. * below / n, hmax, (int)hp->GetEntries());
  }
  if (!sm) lo->AddEntry((TObject*)nullptr, "Pileup: not simulated without smearing", "");
  lo->Draw(); lp->Draw();
  if (v == 1) {                                                                                                // the paper's cut marker on the Delta_s plot
    TLine* l = new TLine(0.01, 0.7, 0.01, 2.2); l->SetLineStyle(2); l->SetLineWidth(3); l->Draw();                 // above the data, below the legends
    TArrow* a = new TArrow(0.0098, 1.25, 0.0062, 1.25, 0.015, "|>"); a->SetLineWidth(2); a->SetLineColor(kGray + 2); a->SetFillColor(kGray + 2); a->Draw();
    TLatex t; t.SetTextFont(42); t.SetTextSize(0.03); t.SetTextAlign(32); t.DrawLatex(0.0058, 1.25, "#Deltas < 0.01 cm");
  }
  TLatex tt; tt.SetNDC(); tt.SetTextFont(42); tt.SetTextSize(0.034);
  tt.DrawLatex(0.15, 0.94, Form("%s, %s (signal and backgrounds)", v == 1 ? "#Deltas" : "#Deltaw", sm ? "WITH SCT z smearing (1.16 mm)" : "WITHOUT SCT z smearing"));
  gPad->RedrawAxis();
  Save(c, OUTD, Form("fig5_%s_%s", VN, sm ? "with_smearing" : "without_smearing"));
}

void fig5_paper_style() {
  SetStyle(); gStyle->SetLegendTextSize(0.028);
  plot("Z0", 1); plot("Z0", 2); plot("Z1160", 1); plot("Z1160", 2);
}
