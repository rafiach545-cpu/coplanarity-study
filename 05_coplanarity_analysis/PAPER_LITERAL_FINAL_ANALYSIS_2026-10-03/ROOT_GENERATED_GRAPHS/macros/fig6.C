// Figure 6: contours of 3 (exclusion) and 5 (discovery) signal events at 300 fb^-1, no background, in the (m_Q, Lambda) plane.
// Data (all in ../ROOT_CSV_FIGURES_2026-10-21/Fig6/):
//   fig6_our_contours.csv  our lines, traced from the grid (channel_id 1 colored / 2 EW, sctz_um 0 / 1160, charge_factor 1 = with the both-charged factor
//                          (colored main line; EW always 1), 0 = colored without it, n_events 3 / 5, segment, point, mass_GeV, lambda_eV)
//   fig6_paper_curves.csv  the paper's curves from its vector figures (curve_id 0-4 = d_cm 100 m, 100 um, 1 cm, 1 m, 1 mm; 5 = discovery; 6 = exclusion;
//                          7 / 8 = HSCP 12.9 / 300 fb-1; 9 / 10 = monojet 12.9 / 300 fb-1; ids from ROOT_CSV_2026-10-19/README.txt)
//   fig6_grid.csv          grid points (mass_gev, lambda_keV, k, N_with_f, N_with_f_UL95_if_k0, status_with_f_id 1 computed / 2 bound)
//   F6_reach_numeric.csv   maximum mass reach (numbers in the boxes)
//   fig6_kfactor_lines.csv, F6_reach_sensitivity_numeric.csv  for the normalisation-sensitivity figure (no SCT z smearing)
// y axis: Lambda in eV on a log scale. The paper draws Lambda on a mixed axis (log below 1 keV, linear above); the curves are in eV in both, so only the
// look differs. Hatched: not computed (Lambda > 25 keV, Lambda < 100 eV, masses outside the generated samples).
#include "common.h"
#include "TGraph.h"
#include "TH2D.h"
#include "TBox.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TPad.h"
#include <set>
#include <cmath>

static Table PC, OC, GR, RC, KL, RS;
std::vector<TGraph*> Lines(const Table& t, std::function<bool(size_t)> sel, const char* gx, const char* gy, const char* seg) {   // one TGraph per segment, ordered by point
  std::map<int, std::vector<std::pair<double, std::pair<double, double>>>> m;
  for (size_t i = 0; i < t.n; ++i) if (sel(i)) m[seg ? (int)t[seg][i] : 0].push_back({t["point"][i], {t[gx][i], t[gy][i]}});
  std::vector<TGraph*> out;
  for (auto& kv : m) { std::sort(kv.second.begin(), kv.second.end()); TGraph* g = new TGraph();
    for (auto& q : kv.second) g->SetPoint(g->GetN(), q.second.first, q.second.second); out.push_back(g); }
  return out;
}
TGraph* Thin(TGraph* g, int step) {   // for dashed drawing only: the traced lines have hundreds of very short pieces and the dash pattern restarts on each
  int im = 0; for (int i = 1; i < g->GetN(); ++i) if (g->GetX()[i] > g->GetX()[im]) im = i;                  // always keep the maximum-mass point
  TGraph* t = new TGraph(); for (int i = 0; i < g->GetN(); ++i) if (i % step == 0 || i == im) t->SetPoint(t->GetN(), g->GetX()[i], g->GetY()[i]);
  if ((g->GetN() - 1) % step) t->SetPoint(t->GetN(), g->GetX()[g->GetN() - 1], g->GetY()[g->GetN() - 1]); return t; }
void Style(std::vector<TGraph*>& v, int col, int ls, double lw) {
  for (auto& g : v) { if (ls != 1 && g->GetN() > 40) g = Thin(g, 6); g->SetLineColor(col); g->SetLineStyle(ls); g->SetLineWidth(lw); } }
void DrawAll(std::vector<TGraph*>& v) { for (auto g : v) g->Draw("L same"); }
double MaxX(std::vector<TGraph*>& v) { double m = -1; for (auto g : v) for (int i = 0; i < g->GetN(); ++i) m = std::max(m, g->GetX()[i]); return m; }

void Hatch(double x0, double x1, double y0, double y1) { TBox* b = new TBox(x0, y0, x1, y1); b->SetFillStyle(3354); b->SetFillColor(C_MUTED); b->SetLineWidth(0); b->Draw(); }
TH2D* Frame(const char* name, int ch) {
  double x0 = ch == 1 ? 500 : 0, x1 = ch == 1 ? 2500 : 1200;
  TH2D* f = new TH2D(name, ";m_{Q} (GeV);#Lambda (eV)", 10, x0, x1, 10, 3, 4e4); f->GetYaxis()->SetMoreLogLabels(false); f->Draw("AXIS");
  gPad->SetLogy(); return f;
}
void NotComputed(int ch) {   // computed: Lambda 100 eV - 25 keV, masses colored 600-2400 GeV, EW 100-1000 GeV
  double x0 = ch == 1 ? 500 : 0, x1 = ch == 1 ? 2500 : 1200, m0 = ch == 1 ? 600 : 100, m1 = ch == 1 ? 2400 : 1000;
  Hatch(x0, x1, 25000, 4e4); Hatch(x0, x1, 3, 100); Hatch(x0, m0, 100, 25000); Hatch(m1, x1, 100, 25000);
}
std::vector<TGraph*> PaperLines(int ch, int id, int col, int ls, double lw) { auto v = Lines(PC, [&](size_t i) { return PC["channel_id"][i] == ch && PC["curve_id"][i] == id; }, "m_GeV", "lambda_eV", nullptr); Style(v, col, ls, lw); return v; }

void Contours() {
  const char* CH[3] = {"", "colored (3,1)_{2/3}", "EW (1,1)_{1}"}; const char* SC[2] = {"no SCT z smearing", "SCT z = 1.16 mm (paper text)"};
  TCanvas* c = new TCanvas("fig6", "", 1500, 1500);
  TPad* pl = new TPad("leg", "", 0, 0, 1, 0.13); pl->Draw();
  TPad* p[4]; for (int i = 0; i < 4; ++i) { p[i] = new TPad(Form("p%d", i), "", (i % 2) * 0.5, 0.13 + (1 - i / 2) * 0.435, (i % 2) * 0.5 + 0.5, 0.13 + (2 - i / 2) * 0.435); p[i]->Draw(); }
  TGraph *lPex = nullptr, *lPdi = nullptr, *lOex = nullptr, *lOdi = nullptr, *lNf = nullptr, *lH = nullptr, *lM = nullptr, *lD = nullptr, *mC = nullptr, *mX = nullptr, *mR = nullptr, *mB = nullptr;
  int k = 0;
  for (int ch = 1; ch <= 2; ++ch) for (int zi = 0; zi < 2; ++zi) {
    int sct = zi == 0 ? 0 : 1160; p[k++]->cd(); gPad->SetLeftMargin(0.13); gPad->SetTopMargin(0.11);
    Frame(Form("f6_%d_%d", ch, sct), ch); NotComputed(ch);
    for (int id = 0; id <= 4; ++id) { auto v = PaperLines(ch, id, TColor::GetColor("#9cb9d1"), 3, 1.5); DrawAll(v); if (!lD) lD = v[0]; }
    { auto v = PaperLines(ch, 7, TColor::GetColor("#7fbf7f"), 1, 2); DrawAll(v); lH = v[0]; auto w = PaperLines(ch, 8, TColor::GetColor("#7fbf7f"), 2, 2); DrawAll(w); }
    { auto v = PaperLines(ch, 9, TColor::GetColor("#b5b5b5"), 1, 2); DrawAll(v); lM = v[0]; auto w = PaperLines(ch, 10, TColor::GetColor("#b5b5b5"), 2, 2); DrawAll(w); }
    auto pe = PaperLines(ch, 6, C_PAPER, 2, 2.5); auto pd = PaperLines(ch, 5, C_PAPER, 1, 2.5); DrawAll(pe); DrawAll(pd); lPex = pe[0]; lPdi = pd[0];
    for (int cf = (ch == 1 ? 0 : 1); cf <= 1; ++cf) for (int nev : {3, 5}) {
      auto v = Lines(OC, [&](size_t i) { return OC["channel_id"][i] == ch && OC["sctz_um"][i] == sct && OC["charge_factor"][i] == cf && OC["n_events"][i] == nev; }, "mass_GeV", "lambda_eV", "segment");
      double mx = MaxX(v); Style(v, cf ? C_COL : C_ALT, nev == 3 ? 2 : 1, cf ? 3.5 : 2); DrawAll(v);
      if (cf && nev == 3) lOex = v[0]; if (cf && nev == 5) lOdi = v[0]; if (!cf && nev == 5) lNf = v[0];
      printf("Fig6 %s, SCT z %d um, charge factor %d, %d events: %zu segments, max mass on the line %.0f GeV\n", ch == 1 ? "colored" : "EW", sct, cf, nev, v.size(), mx); }
    // grid points (status with the charge factor; EW always 1)
    TGraph *gc = new TGraph(), *gx = new TGraph(), *gr = new TGraph(), *gb = new TGraph();
    for (size_t i = 0; i < GR.n; ++i) if (GR["channel_id"][i] == ch && GR["sctz_um"][i] == sct) {
      double m = GR["mass_gev"][i], l = GR["lambda_keV"][i] * 1e3;
      if (GR["status_with_f_id"][i] == 2) gb->SetPoint(gb->GetN(), m, l);
      else if (GR["k"][i] > 0) gc->SetPoint(gc->GetN(), m, l);
      else if (GR["N_with_f_UL95_if_k0"][i] < 3) gx->SetPoint(gx->GetN(), m, l); else gr->SetPoint(gr->GetN(), m, l); }
    gc->SetMarkerStyle(20); gc->SetMarkerSize(0.5); gc->SetMarkerColor(kGray + 3); gx->SetMarkerStyle(5); gx->SetMarkerSize(0.8); gx->SetMarkerColor(kGray + 1);
    gr->SetMarkerStyle(5); gr->SetMarkerSize(0.8); gr->SetMarkerColor(kRed + 1); gb->SetMarkerStyle(24); gb->SetMarkerSize(0.6); gb->SetMarkerColor(kGray + 1);
    for (auto g : {gc, gx, gr, gb}) if (g->GetN()) g->Draw("P same");
    mC = gc; mX = gx; mR = gr; mB = gb; gPad->RedrawAxis();
    TLatex t; t.SetNDC(); t.SetTextFont(42); t.SetTextSize(0.042); t.DrawLatex(0.13, 0.95, Form("%s: signal %s", CH[ch], SC[zi]));
    double rr[6][3] = {{0}}, pap[6] = {0};
    for (size_t i = 0; i < RC.n; ++i) if (RC["channel_id"][i] == ch && RC["sctz_um"][i] == sct && RC["charge_factor"][i] == 1) {
      int nev = (int)RC["n_events"][i]; rr[nev][0] = RC["m_max_GeV"][i]; rr[nev][1] = RC["m_max_lo"][i]; rr[nev][2] = RC["m_max_hi"][i]; pap[nev] = RC["paper_m_max_GeV"][i]; }
    t.SetTextSize(0.027); t.SetTextColor(C_COL);
    t.DrawLatex(0.13, 0.905, Form("reach (#pm1#sigma): excl. %.0f (%.0f-%.0f), disc. %.0f (%.0f-%.0f) GeV; paper %.0f / %.0f GeV",
                                  rr[3][0], rr[3][1], rr[3][2], rr[5][0], rr[5][1], rr[5][2], pap[3], pap[5]));
  }
  pl->cd(); TLegend* lg = new TLegend(0.02, 0.02, 0.98, 0.98); lg->SetNColumns(3); lg->SetTextSize(0.105);
  lg->AddEntry(lPex, "paper: exclusion (3 events)", "l"); lg->AddEntry(lOex, "this work: exclusion (3 events)", "l"); lg->AddEntry(lH, "HSCP 12.9 / 300 fb^{-1} (paper)", "l");
  lg->AddEntry(lPdi, "paper: discovery (5 events)", "l"); lg->AddEntry(lOdi, "this work: discovery (5 events)", "l"); lg->AddEntry(lM, "monojet 12.9 / 300 fb^{-1} (paper)", "l");
  lg->AddEntry(lNf, "colored without charge factor (thin)", "l"); lg->AddEntry(lD, "d_{cm} lines (paper)", "l"); lg->AddEntry(mC, "grid point, #geq 1 event in signal region", "p");
  lg->AddEntry(mX, "0 events passed, 95% UL on N < 3", "p"); lg->AddEntry(mR, "0 events passed, not resolved (UL #geq 3)", "p"); lg->AddEntry(mB, "not propagated: N < 3 even with #varepsilon_{fid} = #varepsilon_{reco} = 1", "p");
  lg->Draw();
  Save(c, "Fig6", "fig6_contours");
}

void KFactor() {
  // kfactor lines: variant_id 1 K1, 2 K1.5, 3 K1.8, 4 K2, 5 K0.9, 6 K1.4, 7 EW LO-ratio trigger (ids of fig6_kfactor_lines.csv);
  // reach numbers: F6_reach_sensitivity_numeric.csv has its own variant ids (9 = EW LO-ratio trigger), so K variants are matched by the K column.
  TCanvas* c = new TCanvas("fig6k", "", 1500, 1250); c->Divide(2, 2, 0.003, 0.003);
  int cols[] = {C_COL, C_ALT, TColor::GetColor("#5aa469"), TColor::GetColor("#6a3d9a")};
  int pad = 0;
  for (int ch = 1; ch <= 2; ++ch) for (int nev : {3, 5}) {
    c->cd(++pad); gPad->SetLeftMargin(0.13); Frame(Form("fk_%d_%d", ch, nev), ch);
    { double x0 = ch == 1 ? 500 : 0, x1 = ch == 1 ? 2500 : 1200; Hatch(x0, x1, 25000, 4e4); Hatch(x0, x1, 3, 100); }
    auto pp = PaperLines(ch, nev == 3 ? 6 : 5, C_PAPER, nev == 3 ? 2 : 1, 2.5); DrawAll(pp);
    TLegend* lg = new TLegend(0.15, 0.135, 0.94, 0.42); lg->SetTextSize(0.031); lg->SetFillColor(kWhite); lg->SetFillStyle(1001); lg->AddEntry(pp[0], Form("paper %s", nev == 3 ? "exclusion" : "discovery"), "l");   // legend in the empty Lambda < 100 eV region
    std::vector<std::pair<double, int>> vars; std::set<int> seen;
    for (size_t i = 0; i < KL.n; ++i) if (KL["channel_id"][i] == ch && !seen.count((int)KL["variant_id"][i])) { seen.insert((int)KL["variant_id"][i]); vars.push_back({KL["K"][i] == MISSING ? 99 : KL["K"][i], (int)KL["variant_id"][i]}); }
    std::sort(vars.begin(), vars.end(), [](auto a, auto b) { return (a.first == 1) != (b.first == 1) ? a.first == 1 : a.first < b.first; });   // K = 1 first
    int ic = 0;
    for (auto& kv : vars) {
      int vid = kv.second; double K = kv.first;
      auto v = Lines(KL, [&](size_t i) { return KL["channel_id"][i] == ch && KL["variant_id"][i] == vid && KL["n_events"][i] == nev; }, "mass_GeV", "lambda_eV", "segment");
      bool lo = (K == 99); double mx = MaxX(v); Style(v, lo ? C_MUTED : cols[ic++ % 4], lo ? 3 : (nev == 3 ? 2 : 1), K == 1 ? 3.5 : 2); DrawAll(v);
      double m = -1, mlo = -1, mhi = -1;
      for (size_t i = 0; i < RS.n; ++i) if (RS["channel_id"][i] == ch && RS["sctz_um"][i] == 0 && RS["n_events"][i] == nev && (lo ? RS["variant_id"][i] == 9 : std::fabs(RS["K"][i] - K) < 1e-6)) {
        m = RS["m_max_GeV"][i]; mlo = RS["m_max_lo"][i]; mhi = RS["m_max_hi"][i]; }
      printf("Fig6 K-factor %s %d events, %s: reach %.0f GeV (table), line maximum %.0f GeV\n", ch == 1 ? "colored" : "EW", nev, lo ? "LO-ratio trigger" : Form("K = %.1f", K), m, mx);
      lg->AddEntry(v[0], lo ? Form("alternative: LO-ratio trigger, #sigma #times 1: %.0f (%.0f-%.0f) GeV", m, mlo, mhi)
                            : Form("this work, #sigma #times %g%s: %.0f (%.0f-%.0f) GeV", K, K == 2 ? " (N_{Q} = 2 reading)" : "", m, mlo, mhi), "l");
    }
    lg->Draw(); gPad->RedrawAxis();
    TLatex t; t.SetNDC(); t.SetTextFont(42); t.SetTextSize(0.04); t.DrawLatex(0.13, 0.945, Form("%s: %s (%d events), no SCT z smearing", ch == 1 ? "colored" : "EW", nev == 3 ? "exclusion" : "discovery", nev));
  }
  Save(c, "Fig6", "fig6_kfactor_sensitivity");
}

void fig6() {
  SetStyle();
  PC = ReadCSV("Fig6/fig6_paper_curves.csv"); OC = ReadCSV("Fig6/fig6_our_contours.csv"); GR = ReadCSV("Fig6/fig6_grid.csv");
  RC = ReadCSV("Fig6/F6_reach_numeric.csv"); KL = ReadCSV("Fig6/fig6_kfactor_lines.csv"); RS = ReadCSV("Fig6/F6_reach_sensitivity_numeric.csv");
  Contours(); KFactor();
}
