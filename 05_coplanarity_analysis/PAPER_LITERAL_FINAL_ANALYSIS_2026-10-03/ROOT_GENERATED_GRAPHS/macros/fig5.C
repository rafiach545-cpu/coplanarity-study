// Figure 5: distributions of Delta_s and Delta_w (cm) for signal and backgrounds, after the plane and hit-multiplicity cuts, before the Delta_s cut.
// Data: Fig5/fig5_<Z0|Z1160>.csv. Event rows (paper_var_id = -999): ds, dw in cm for each event of population_id (1 colored, 2 EW, 3 converted gamma + pile-up,
// 4 pile-up only; 4 exists only for SCT z 1.16 mm). Paper rows (paper_var_id 1 = ds, 2 = dw): the paper's histogram, bin edges lo, hi (cm), paper_frac = fraction per bin
// (each paper histogram sums to 1). The paper's bins are 0.1 decade wide and lie on the same 10^(k/10) grid as ours (checked below), so the fractions per bin
// are directly comparable. Ours: histogram of the events on 0.1-decade bins (Delta_s 1e-4 ... 1e-1 cm, Delta_w 1e-3 ... 10 cm; values outside are put in the
// first / last bin, as the report), normalised to unit sum. Vertical lines: signal-region cuts Delta_s < 0.01 cm, Delta_w < 1 cm.
#include "common.h"
#include "TH1D.h"
#include "TLegend.h"
#include "TLine.h"
#include "TLatex.h"
#include "TMath.h"
#include <cmath>

void one(const char* z, const char* lab) {
  Table d = ReadCSV(Form("Fig5/fig5_%s.csv", z));
  int npop = 0; for (size_t i = 0; i < d.n; ++i) npop = std::max(npop, (int)d["population_id"][i]);
  const char* PL[5] = {"", "colored", "EW", "converted #gamma + pile-up", "pile-up only"}; int COL[5] = {0, C_COL, C_EW, TColor::GetColor("#5aa469"), TColor::GetColor("#8a5bb5")};
  const char* VN[3] = {"", "ds", "dw"}; const char* VT[3] = {"", "#Deltas (cm)", "#Deltaw (cm)"}; double LO[3] = {0, -4, -3}, HI[3] = {0, -1, 1}, CUT[3] = {0, 0.01, 1.0};
  TCanvas* c = new TCanvas(Form("fig5_%s", z), "", 380 * npop, 760); c->Divide(npop, 2, 0.003, 0.003);
  int bad = 0;
  for (int v = 1; v <= 2; ++v) for (int pop = 1; pop <= npop; ++pop) {
    int nb = std::lround((HI[v] - LO[v]) / 0.1); std::vector<double> e; for (int k = 0; k <= nb; ++k) e.push_back(std::pow(10., LO[v] + 0.1 * k));
    TH1D* h = new TH1D(Form("h5_%s_%d_%d", z, v, pop), "", nb, e.data()); TH1D* hp = new TH1D(Form("p5_%s_%d_%d", z, v, pop), "", nb, e.data());
    std::vector<double> x;
    for (size_t i = 0; i < d.n; ++i) {
      if (d["population_id"][i] != pop) continue;
      if (d["paper_var_id"][i] == MISSING && d[VN[v]][i] != MISSING) { double a = d[VN[v]][i]; x.push_back(a); h->Fill(std::min(std::max(a, e.front() * 1.0001), e.back() * 0.9999)); }
      if (d["paper_var_id"][i] == v) {
        double lo = d["lo"][i], hi = d["hi"][i], k = (std::log10(lo) - LO[v]) / 0.1;
        if (std::fabs(k - std::lround(k)) > 0.01 || std::fabs(std::log10(hi / lo) - 0.1) > 0.005) { ++bad; printf("WARNING paper bin [%g, %g] not on our grid\n", lo, hi); }
        hp->Fill(std::sqrt(lo * hi), d["paper_frac"][i]); } }
    double n = h->Integral(); if (n > 0) h->Scale(1. / n);
    h->SetLineColor(COL[pop]); h->SetLineWidth(3); hp->SetLineColor(C_PAPER); hp->SetLineStyle(2); hp->SetLineWidth(2);
    c->cd((v - 1) * npop + pop); gPad->SetLogx(); gPad->SetLeftMargin(0.16);
    h->SetTitle(Form(";%s;fraction per bin", VT[v])); h->SetMaximum(1.35 * std::max(h->GetMaximum(), hp->GetMaximum())); h->SetMinimum(0);
    h->Draw("HIST"); hp->Draw("HIST same");
    TLine* l = new TLine(CUT[v], 0, CUT[v], h->GetMaximum()); l->SetLineColor(C_MUTED); l->SetLineWidth(2); l->Draw();
    TLatex t; t.SetNDC(); t.SetTextFont(42); t.SetTextSize(0.05); t.DrawLatex(0.16, 0.94, Form("%s; %s", PL[pop], lab));
    TLegend* lg = new TLegend(0.18, 0.74, 0.7, 0.9); lg->SetTextSize(0.045); lg->AddEntry(h, Form("this work (N = %zu)", x.size()), "l"); lg->AddEntry(hp, "paper", "l"); lg->Draw();
    double med = x.empty() ? NAN : TMath::Median(x.size(), x.data()); int below = 0; for (double a : x) below += a < CUT[v];
    printf("Fig5 %s %-28s %s: N = %4zu, median %.4g cm, below the cut %d (%.1f%%), paper bins %d\n", z, PL[pop], VN[v], x.size(), med, below, x.empty() ? 0. : 100. * below / x.size(), (int)hp->GetEntries());
  }
  if (bad) printf("WARNING: %d paper bins not on the 0.1-decade grid\n", bad); else printf("Fig5 %s: all paper bins lie on our 0.1-decade grid\n", z);
  Save(c, "Fig5", Form("fig5_ds_dw_%s", z));
}

void fig5() {
  SetStyle();
  one("Z0", "SCT z none");   // pile-up only was not simulated without SCT z smearing, so that column is absent
  one("Z1160", "SCT z 1.16 mm");
}
