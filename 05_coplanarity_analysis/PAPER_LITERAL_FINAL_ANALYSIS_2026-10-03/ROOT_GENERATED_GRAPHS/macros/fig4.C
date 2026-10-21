// Figure 4: event display in the plane frame. For each sample, the event with the median Delta_s among the events passing the full signal region.
// Data: Fig4/fig4_hits_<Z0|Z1160>.csv. Rows with ellipse = 0: the hits of the shown event (n2_cm, n3_cm in cm; ds_cm, dw_cm = Delta_s, Delta_w of the
// event in cm; event_id; rank of n_sr_events). Rows with ellipse = 1: points tracing the detector layers in the same frame (drawn grey).
// sample_id 1 = COL2000 (colored 1.8 TeV, Lambda = 2 keV), 2 = EW2000 (EW 800 GeV, Lambda = 4 keV). The paper's Fig. 4 has no numeric data, so no overlay.
// Left: all hits (x and y scales nearly equal, as the paper); right: zoom |n2| < 1 cm with the band +-Delta_w (Delta_w = sqrt(lambda_2), Eq. 11).
#include "common.h"
#include "TGraph.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TBox.h"
#include "TLegend.h"
#include "TLatex.h"

void one(const char* z, const char* lab) {
  Table d = ReadCSV(Form("Fig4/fig4_hits_%s.csv", z));
  TCanvas* c = new TCanvas(Form("fig4_%s", z), "", 1400, 1000); c->Divide(2, 2, 0.004, 0.004);
  const char* LAB[3] = {"", "colored 1.8 TeV, #Lambda = 2 keV", "EW 800 GeV, #Lambda = 4 keV"}; int COL[3] = {0, C_COL, C_EW};
  for (int s = 1; s <= 2; ++s) {
    std::vector<double> hx, hy, ex, ey; double ds = 0, dw = 0, ev = 0, rk = 0, nsr = 0;
    for (size_t i = 0; i < d.n; ++i) if (d["sample_id"][i] == s) {
      if (d["ellipse"][i] == 1) { ex.push_back(d["n3_cm"][i]); ey.push_back(d["n2_cm"][i]); }
      else { hx.push_back(d["n3_cm"][i]); hy.push_back(d["n2_cm"][i]); ds = d["ds_cm"][i]; dw = d["dw_cm"][i]; ev = d["event_id"][i]; rk = d["rank"][i]; nsr = d["n_sr_events"][i]; } }
    printf("Fig4 %s %s: event %.0f (median Delta_s, %.0f of %.0f), %zu hits, Delta_s = %.1f um, Delta_w = %.4f cm; %zu layer points\n", z, LAB[s], ev, rk, nsr, hx.size(), ds * 1e4, dw, ex.size());
    TGraph* gl = new TGraph(ex.size(), ex.data(), ey.data()); gl->SetMarkerStyle(1); gl->SetMarkerColor(C_MUTED);
    TGraph* gh = new TGraph(hx.size(), hx.data(), hy.data()); gh->SetMarkerStyle(5); gh->SetMarkerSize(1.6); gh->SetMarkerColor(COL[s]);
    c->cd(2 * s - 1); gPad->SetLeftMargin(0.11);
    TH2D* f1 = new TH2D(Form("f4a_%s_%d", z, s), ";n_{3} (cm);n_{2} (cm)", 10, -20, 80, 10, -33, 30); f1->Draw("AXIS");
    gl->Draw("P same"); gh->Draw("P same");
    TLatex t; t.SetNDC(); t.SetTextFont(42); t.SetTextSize(0.042);
    t.DrawLatex(0.11, 0.94, Form("%s: event %.0f (median #Deltas, %.0f of %.0f)", LAB[s], ev, rk, nsr));
    TLegend* lg = new TLegend(0.13, 0.15, 0.6, 0.27); lg->AddEntry(gh, "quirk hits", "p"); lg->AddEntry(gl, "detector layers", "p"); lg->Draw();
    c->cd(2 * s); gPad->SetLeftMargin(0.13);
    TH2D* f2 = new TH2D(Form("f4b_%s_%d", z, s), ";n_{3} (cm);n_{2} (cm)", 10, 0, 80, 10, -1, 1); f2->Draw("AXIS");
    TBox* b = new TBox(0, -dw, 80, dw); b->SetFillColorAlpha(TColor::GetColor("#5aa469"), 0.25); b->Draw();
    gh->Draw("P same"); gPad->RedrawAxis();
    t.DrawLatex(0.13, 0.94, Form("zoom, |n_{2}| < 1 cm; %s", lab));
    TLegend* lg2 = new TLegend(0.15, 0.125, 0.75, 0.205); lg2->SetFillStyle(0); lg2->SetNColumns(2); lg2->SetTextSize(0.034); lg2->AddEntry(gh, Form("hits, #Deltas = %.0f #mum", ds * 1e4), "p"); lg2->AddEntry(b, Form("#pm#Deltaw = #pm%.3f cm", dw), "f"); lg2->Draw();   // below n2 = -0.8: no hits there
  }
  Save(c, "Fig4", Form("fig4_event_display_%s", z));
}

void fig4() {
  SetStyle();
  one("Z0", "signal without SCT z smearing");
  one("Z1160", "signal SCT z = 1.16 mm");
}
