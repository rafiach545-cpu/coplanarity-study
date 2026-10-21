// Figure 7 (paper's Appendix A): dE/dx and betagamma of the quirk hits on the 4 pixel layers, EW 800 GeV and colored 1800 GeV, Lambda = 2 keV.
// Data: Fig7/fig7_pixel_hits.csv: one row per hit (channel_id 1 colored / 2 EW, triggered, fiducial_event, in_25ns, order (0 = first crossing of the layer),
//       betagamma = |p|/m, dEdx_MPV_MeVcm2g = PDG Eq. 34.12 most probable value in MeV cm^2/g, -999 for betagamma < 0.1 as the paper's left panel).
//       Fig7/fig7_paper_curves.csv: the paper's step histograms from its vector figures (var_id 1 = dE/dx, 2 = betagamma; channel_id 1 colored / 2 EW; x, y = path vertices).
// The paper's y values are fractions per bin (each histogram sums to 1). Its bins: dE/dx 0.586 MeV cm^2/g wide, betagamma 0.1 decade wide.
// Ours: main selection = triggered, fiducial events, first crossing of each layer, t < 25 ns (as the report); dashed: all events, all crossings, t < 25 ns.
// Bins as the report: dE/dx 0-100 in steps of 2, betagamma 1e-4 ... 10 in 0.1 decades; values outside are put in the edge bins.
// dE/dx panel: both drawn as fraction per unit dE/dx (fraction / bin width), because the bin widths differ (0.586 vs 2); betagamma: fraction per 0.1 decade
// for both (same width).
#include "common.h"
#include "TH1D.h"
#include "TGraph.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TMath.h"
#include <cmath>

void fig7() {
  SetStyle();
  Table h = ReadCSV("Fig7/fig7_pixel_hits.csv"), p = ReadCSV("Fig7/fig7_paper_curves.csv");
  TCanvas* c = new TCanvas("fig7", "", 1500, 620); c->Divide(2, 1, 0.003, 0.003);
  const char* CH[3] = {"", "colored 1800 GeV", "EW 800 GeV"}; const char* CS[3] = {"", "colored", "EW"}; int COL[3] = {0, C_COL, C_EW};
  const char* COLN[3] = {"", "dEdx_MPV_MeVcm2g", "betagamma"};
  for (int v = 1; v <= 2; ++v) {
    c->cd(v); gPad->SetLogy(); if (v == 2) gPad->SetLogx(); gPad->SetLeftMargin(0.12);
    std::vector<double> e; if (v == 1) for (int k = 0; k <= 50; ++k) e.push_back(2. * k); else for (int k = 0; k <= 50; ++k) e.push_back(std::pow(10., -4 + 0.1 * k));
    TH1D* fr = new TH1D(Form("fr7_%d", v), v == 1 ? ";dE/dx (MeV cm^{2}/g), most probable value, #beta#gamma #geq 0.1;fraction of hits per MeV cm^{2}/g"
                                                 : ";#beta#gamma;fraction of hits per 0.1 decade", e.size() - 1, e.data());
    fr->SetMinimum(v == 1 ? 3e-4 : 1e-4); fr->SetMaximum(v == 1 ? 8.0 : 15.0); fr->Draw("AXIS");
    TLegend* lg = new TLegend(v == 1 ? 0.50 : 0.13, 0.70, v == 1 ? 0.97 : 0.60, 0.91); lg->SetTextSize(0.029);
    for (int ch = 1; ch <= 2; ++ch) {
      for (int sel = 0; sel < 2; ++sel) {
        TH1D* hh = new TH1D(Form("h7_%d_%d_%d", v, ch, sel), "", e.size() - 1, e.data()); std::vector<double> x;
        for (size_t i = 0; i < h.n; ++i) {
          if (h["channel_id"][i] != ch || h["in_25ns"][i] != 1) continue;
          if (sel == 0 && !(h["triggered"][i] == 1 && h["fiducial_event"][i] == 1 && h["order"][i] == 0)) continue;
          double a = h[COLN[v]][i]; if (a == MISSING) continue; x.push_back(a);
          hh->Fill(std::min(std::max(a, e.front()), e.back() * 0.9999)); }
        hh->Scale(1. / hh->Integral()); if (v == 1) hh->Scale(1., "width");
        hh->SetLineColor(COL[ch]); hh->SetLineWidth(sel == 0 ? 3 : 1); hh->SetLineStyle(sel == 0 ? 1 : 2); hh->Draw("HIST same");
        double med = TMath::Median(x.size(), x.data()); int low = 0; for (double a : x) low += a < 0.1;
        lg->AddEntry(hh, Form("this work, %s, %s (N = %zu)", CS[ch], sel == 0 ? "main" : "all hits", x.size()), "l");
        printf("Fig7 %s %-10s %-26s N = %5zu hits, median %.3f%s\n", v == 1 ? "dE/dx" : "betagamma", CH[ch], sel == 0 ? "main" : "all events, all crossings", x.size(), med,
               v == 2 ? Form(", fraction below 0.1: %.3f", (double)low / x.size()) : "");
      }
      // paper: path vertices of its step histogram; dE/dx divided by its bin width (0.586) to give fraction per unit dE/dx
      TGraph* g = new TGraph(); double w = 0, tot = 0; std::vector<std::pair<double, double>> seg;
      std::vector<double> px, py; for (size_t i = 0; i < p.n; ++i) if (p["var_id"][i] == v && p["channel_id"][i] == ch) { px.push_back(p["x"][i]); py.push_back(p["y"][i]); }
      for (size_t i = 0; i + 1 < px.size(); ++i) if (std::fabs(py[i] - py[i + 1]) < 1e-12 && px[i + 1] > px[i] && py[i] > 1e-6) { w = px[i + 1] - px[i]; tot += py[i]; seg.push_back({v == 1 ? 0.5 * (px[i] + px[i + 1]) : std::sqrt(px[i] * px[i + 1]), py[i]}); }   // bin centre: linear axis / log axis
      double scale = v == 1 ? 1. / w : 1.;
      for (size_t i = 0; i < px.size(); ++i) g->SetPoint(g->GetN(), px[i], std::max(py[i] * scale, 1e-6));
      g->SetLineColor(COL[ch]); g->SetLineStyle(3); g->SetLineWidth(2); g->Draw("L same");
      std::sort(seg.begin(), seg.end()); double cum = 0, pmed = NAN; for (auto& s : seg) { cum += s.second; if (cum >= tot / 2) { pmed = s.first; break; } }
      lg->AddEntry(g, Form("paper, %s", CS[ch]), "l");
      printf("Fig7 %s %-10s paper: %zu bins, sum of fractions %.3f, %s, median %.3f\n", v == 1 ? "dE/dx" : "betagamma", CH[ch], seg.size(), tot,
             v == 1 ? Form("bin width %.3f MeV cm2/g", w) : "bin width 0.1 decade", pmed);
    }
    lg->Draw(); gPad->RedrawAxis();
    TLatex t; t.SetNDC(); t.SetTextFont(42); t.SetTextSize(0.04); t.DrawLatex(0.12, 0.94, v == 1 ? "dE/dx of the pixel hits, colored 1800 GeV / EW 800 GeV, #Lambda = 2 keV" : "#beta#gamma of the pixel hits, colored 1800 GeV / EW 800 GeV, #Lambda = 2 keV");
  }
  Save(c, "Fig7", "fig7_dedx_betagamma");
}
