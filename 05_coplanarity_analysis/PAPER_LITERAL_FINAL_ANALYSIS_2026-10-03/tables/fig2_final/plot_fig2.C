#include <algorithm>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>

#include "TROOT.h"
#include "TStyle.h"
#include "TCanvas.h"
#include "TGraph.h"
#include "TH1F.h"
#include "TGaxis.h"
#include "TLegend.h"
#include "TString.h"
#include "TColor.h"

TGraph* readCSV(const char* fname, int cx, int cy) {
    std::ifstream in(fname);
    if (!in) {
        printf("ERROR: Cannot open %s\n", fname);
        return nullptr;
    }

    std::string line;
    std::getline(in, line); // Skip header

    std::vector<double> x, y;

    while (std::getline(in, line)) {
        if (line.empty()) continue;

        std::stringstream ss(line);
        std::string token;
        std::vector<double> v;

        while (std::getline(ss, token, ',')) {
            try {
                v.push_back(std::stod(token));
            } catch (...) {
                v.clear();
                break;
            }
        }

        if (v.size() <= (size_t)std::max(cx, cy)) continue;
        if (!std::isfinite(v[cx]) || !std::isfinite(v[cy])) continue;

        x.push_back(v[cx]);
        y.push_back(v[cy]);
    }

    if (x.empty()) {
        printf("ERROR: No valid points in %s\n", fname);
        return nullptr;
    }

    printf("%s: %zu valid points\n", fname, x.size());
    return new TGraph((int)x.size(), x.data(), y.data());
}

void plot_fig2(const char* ours = "fig2_ours_constructed.csv",
               const char* tag = "constructed") {
    gStyle->SetOptStat(0);

    const double rmax = 5.1;
    const double Lmax = 0.9;
    const double dmax = 5.0;
    const double scale = Lmax / dmax;

    TGraph* oL = readCSV(ours, 0, 2);
    TGraph* od = readCSV(ours, 0, 1);
    TGraph* pL = readCSV("fig2_paper_L.csv", 0, 1);
    TGraph* pd = readCSV("fig2_paper_d.csv", 0, 1);

    if (!oL || !od || !pL || !pd) {
        printf("ERROR: One or more CSV files could not be read.\n");
        return;
    }

    for (int i = 0; i < od->GetN(); ++i)
        od->GetY()[i] *= scale;

    for (int i = 0; i < pd->GetN(); ++i)
        pd->GetY()[i] *= scale;

    TCanvas* c = new TCanvas("c_fig2", "Figure 2 comparison", 1000, 650);
    c->SetRightMargin(0.13);

    TH1F* frame = c->DrawFrame(0, 0, rmax, Lmax);
    frame->SetTitle(Form(
        "Quirk trajectory comparison (%s);r (cm);|L| (10^{12} #hbar)",
        tag));

    oL->SetLineColor(kBlue + 1);
    oL->SetLineWidth(2);
    oL->Draw("L same");

    pL->SetLineColor(kBlue + 1);
    pL->SetLineWidth(2);
    pL->SetLineStyle(2);
    pL->Draw("L same");

    od->SetLineColor(kOrange + 7);
    od->SetLineWidth(2);
    od->Draw("L same");

    pd->SetLineColor(kOrange + 7);
    pd->SetLineWidth(2);
    pd->SetLineStyle(2);
    pd->Draw("L same");

    TGaxis* ax = new TGaxis(rmax, 0, rmax, Lmax, 0, dmax, 510, "+L");
    ax->SetTitle("d (cm)");
    ax->SetLabelFont(42);
    ax->SetTitleFont(42);
    ax->SetLabelSize(0.035);
    ax->SetTitleSize(0.035);
    ax->Draw();

    TLegend* legend = new TLegend(0.56, 0.72, 0.86, 0.89);
    legend->AddEntry(oL, "|L|, simulation", "l");
    legend->AddEntry(pL, "|L|, paper data", "l");
    legend->AddEntry(od, "d, simulation", "l");
    legend->AddEntry(pd, "d, paper data", "l");
    legend->Draw();

    c->SaveAs(Form("fig2_%s.png", tag));
    c->SaveAs(Form("fig2_%s.pdf", tag));

    printf("Saved fig2_%s.png and fig2_%s.pdf\n", tag, tag);
}
