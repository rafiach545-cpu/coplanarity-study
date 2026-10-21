// Shared helpers for the ROOT figure macros (2026-10-21).
// CSV reader: the CSVs of ../ROOT_CSV_FIGURES_2026-10-21 are numeric with one header line (missing = -999); every column is read as double.
#pragma once
#include <fstream>
#include <sstream>
#include <map>
#include <vector>
#include <string>
#include <stdexcept>
#include <algorithm>
#include "TStyle.h"
#include "TColor.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "TFile.h"

const std::string DATA = "../ROOT_CSV_FIGURES_2026-10-21/";   // relative to ROOT_GENERATED_GRAPHS/ (macros are run from there)
const double MISSING = -999.;

struct Table {
  std::string file; std::vector<std::string> cols; std::map<std::string, std::vector<double>> v; size_t n = 0;
  const std::vector<double>& operator[](const std::string& c) const {
    auto it = v.find(c); if (it == v.end()) throw std::runtime_error("column " + c + " not in " + file); return it->second; }
};

inline Table ReadCSV(const std::string& rel) {
  Table t; t.file = DATA + rel; std::ifstream in(t.file);
  if (!in) throw std::runtime_error("cannot open " + t.file);
  std::string line; std::getline(in, line); std::stringstream hs(line); std::string c;
  while (std::getline(hs, c, ',')) { c.erase(std::remove(c.begin(), c.end(), '\r'), c.end()); t.cols.push_back(c); t.v[c] = {}; }
  while (std::getline(in, line)) {
    if (line.empty()) continue; std::stringstream ls(line); std::string f; size_t k = 0;
    while (std::getline(ls, f, ',')) { if (k < t.cols.size()) t.v[t.cols[k]].push_back(f.empty() ? MISSING : std::stod(f)); ++k; }
    if (k != t.cols.size()) throw std::runtime_error("wrong number of fields in " + t.file + ": " + line);
    ++t.n;
  }
  printf("read %-55s %8zu rows, %zu columns\n", rel.c_str(), t.n, t.cols.size());
  return t;
}

// one style for every figure
const int C_COL = TColor::GetColor("#1f5fbf");   // colored channel / colored sample
const int C_EW  = TColor::GetColor("#d9622b");   // EW channel / EW sample
const int C_ALT = TColor::GetColor("#e8a33a");   // alternative of ours (e.g. colored without the charge factor)
const int C_PAPER = kBlack;
const int C_MUTED = TColor::GetColor("#8a949b");

inline void SetStyle() {
  gStyle->SetOptStat(0); gStyle->SetOptTitle(1); gStyle->SetTitleFont(42, ""); gStyle->SetTitleFontSize(0.045);
  gStyle->SetTitleBorderSize(0); gStyle->SetTitleFillColor(0); gStyle->SetTitleX(0.12); gStyle->SetTitleAlign(13);
  gStyle->SetLabelFont(42, "xyz"); gStyle->SetTitleFont(42, "xyz"); gStyle->SetLabelSize(0.042, "xyz"); gStyle->SetTitleSize(0.046, "xyz");
  gStyle->SetPadTickX(1); gStyle->SetPadTickY(1); gStyle->SetPadLeftMargin(0.13); gStyle->SetPadBottomMargin(0.12);
  gStyle->SetPadRightMargin(0.04); gStyle->SetPadTopMargin(0.08); gStyle->SetLegendBorderSize(0); gStyle->SetLegendFont(42);
  gStyle->SetLegendTextSize(0.034); gStyle->SetEndErrorSize(0); gStyle->SetFrameLineWidth(1); gStyle->SetHatchesLineWidth(1);
}

inline void Save(TCanvas* c, const std::string& dir, const std::string& name) {   // png + pdf (+ the canvas in a .root file)
  gSystem->mkdir(dir.c_str(), true);
  c->SaveAs((dir + "/" + name + ".pdf").c_str()); c->SaveAs((dir + "/" + name + ".png").c_str());
  TFile f((dir + "/" + name + ".root").c_str(), "RECREATE"); c->Write(name.c_str()); f.Close();
}
