// Standalone LHE -> Pythia8 shower + MLM (JetMatchingMadgraph) driver.
//
// Purpose: version-matched EW quirk trigger pilot (EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02).
// Mirrors MG5aMC_PY8_interface / Pythia main89 logic for jet matching:
//   - settings read verbatim from a .cmd file
//   - JetMatchingMadgraph UserHook when JetMatching:merge = on
//   - loop pythia.next() until end of LHE file; next()==false => vetoed/aborted
// Output: one CSV row per accepted (matched) event with final-state (status 1)
// and hard-process (status 23) quirk momenta. No physics selection is applied here.
//
// Compiles against Pythia 8.212 (raw UserHooks*) and 8.3xx (shared_ptr UserHooks).
#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/JetMatching.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <cmath>
using namespace Pythia8;

int main(int argc, char* argv[]) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s settings.cmd out.csv\n", argv[0]);
    return 2;
  }
  Pythia pythia;
  pythia.readFile(argv[1]);
  bool doMatch = pythia.settings.flag("JetMatching:merge");
#ifdef PY8_RAW_HOOKS
  JetMatchingMadgraph* matching = 0;
  if (doMatch) { matching = new JetMatchingMadgraph(); pythia.setUserHooksPtr(matching); }
#else
  std::shared_ptr<JetMatchingMadgraph> matching;
  if (doMatch) { matching = std::make_shared<JetMatchingMadgraph>(); pythia.setUserHooksPtr(matching); }
#endif
  if (!pythia.init()) { std::fprintf(stderr, "init failed\n"); return 1; }

  std::ofstream out(argv[2]);
  out.precision(12);
  out << "seq,n_final_quirks,pdg1,px1,py1,pz1,E1,pdg2,px2,py2,pz2,E2,"
         "h_px1,h_pz1,h_px2,h_pz2,pair_pt_final,pair_pt_hard\n";
  long nTried = 0, nAcc = 0, nFalse = 0;
  while (true) {
    ++nTried;
    if (!pythia.next()) {
      if (pythia.info.atEndOfFile()) { --nTried; break; }
      ++nFalse;
      continue;
    }
    int f[2] = {-1, -1}, h[2] = {-1, -1};
    int nf = 0, nh = 0;
    for (int i = 0; i < pythia.event.size(); ++i) {
      const Particle& p = pythia.event[i];
      if (std::abs(p.id()) != 9000011) continue;
      if (p.isFinal()) { if (nf < 2) f[nf] = i; ++nf; }
      if (p.status() == -23 || p.status() == 23) { if (nh < 2) h[nh] = i; ++nh; }
    }
    double ptf = -1, pth = -1;
    if (nf == 2) ptf = std::hypot(pythia.event[f[0]].px() + pythia.event[f[1]].px(),
                                  pythia.event[f[0]].py() + pythia.event[f[1]].py());
    if (nh == 2) pth = std::hypot(pythia.event[h[0]].px() + pythia.event[h[1]].px(),
                                  pythia.event[h[0]].py() + pythia.event[h[1]].py());
    out << nAcc << "," << nf;
    for (int k = 0; k < 2; ++k) {
      if (nf == 2) {
        const Particle& p = pythia.event[f[k]];
        out << "," << p.id() << "," << p.px() << "," << p.py() << "," << p.pz() << "," << p.e();
      } else out << ",,,,,";
    }
    for (int k = 0; k < 2; ++k) {
      if (nh == 2) out << "," << pythia.event[h[k]].px() << "," << pythia.event[h[k]].pz();
      else out << ",,";
    }
    out << "," << ptf << "," << pth << "\n";
    ++nAcc;
  }
  pythia.stat();
  std::printf("DRIVER_SUMMARY lhe_events_read=%ld accepted=%ld next_false=%ld\n", nTried, nAcc, nFalse);
  return 0;
}
