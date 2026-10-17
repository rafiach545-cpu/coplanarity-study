// Fig. 2 driver for PreFASERQuirkSim (2026-10-12). Uses the package's own CalculateForces / CalculateCt and reproduces the
// main-loop step of quirk_run.cxx (lines 424-523): string direction s1/s2 (CM-frame simultaneity correction), dt1/dt2 from CalculateCt,
// p += F dt, trapezoidal r update. Changes for this test only: magnetic field uniform (0, 0, B) T (stub BctAdv), no material (loct = 0),
// production at the origin, stop when the CM transverse radius exceeds rstop. Units as in the package: um, ns, GeV, Lambda in eV.
// Usage: driver_cross mq Lambda_eV B_T p1x p1y p1z p2x p2y p2z rstop_um divStep q1 q2 > crossings.txt
// Variant (D30): prints the first outward crossing of each quirk with the 8 layer radii (linear interpolation between consecutive steps).
#include "PreFASERQuirkSim/include/QuirkDynamics.h"
#include "PreFASERQuirkSim/include/VectorUtils.h"
#include "PreFASERQuirkSim/include/MagneticField.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>
std::vector<Magnet> all_magnets;
static double BZ = 2.0;
std::vector<double> BctAdv(const std::vector<Magnet>&, double, double, double) { return {0.0, 0.0, BZ}; }
int main(int argc, char** argv) {
    double mq = atof(argv[1]), Lambda = atof(argv[2]); BZ = atof(argv[3]);
    std::vector<double> p1 = {atof(argv[4]), atof(argv[5]), atof(argv[6])}, p2 = {atof(argv[7]), atof(argv[8]), atof(argv[9])};
    double rstop = atof(argv[10]); int divStep = atoi(argv[11]); int q1 = atoi(argv[12]), q2 = atoi(argv[13]);
    double E1 = sqrt(mq * mq + DotProduct(p1, p1)), E2 = sqrt(mq * mq + DotProduct(p2, p2));
    std::vector<double> Beta = {(p1[0] + p2[0]) / (E1 + E2), (p1[1] + p2[1]) / (E1 + E2), (p1[2] + p2[2]) / (E1 + E2)};
    double t1q = 658 * ((2 * mq) / (Lambda * Lambda)) * sqrt(pow((E1 + E2) / (2 * mq), 2) - 1 / (1 - DotProduct(Beta, Beta)));   // as quirk_run.cxx l.289
    double dt = std::min(0.03, t1q / divStep);                                                                                    // as l.372
    std::vector<double> r1 = {0, 0, 0}, r2 = {0, 0, 0}, v1, v2; double t1 = 0, t2 = 0; int n = 1;
    const double RL[8] = {33250, 50500, 88500, 122500, 299000, 371000, 443000, 514000}; bool done[2][8] = {{false}};
    fprintf(stderr, "t1q %.6g ns, dt %.6g ns\n", t1q, dt);
    while (sqrt(pow((r1[0] + r2[0]) / 2, 2) + pow((r1[1] + r2[1]) / 2, 2)) < rstop) {
        E1 = sqrt(mq * mq + DotProduct(p1, p1)); v1 = DivideVector(p1, E1); E2 = sqrt(mq * mq + DotProduct(p2, p2)); v2 = DivideVector(p2, E2);
        Beta = {(p1[0] + p2[0]) / (E1 + E2), (p1[1] + p2[1]) / (E1 + E2), (p1[2] + p2[2]) / (E1 + E2)};

        std::vector<double> s1(3), s2(3);
        if (n == 1) { s1 = Normalize(SubtractVectors(v1, v2)); s2 = Normalize(SubtractVectors(v2, v1)); }
        else {
            s1 = Normalize(AddVectors(MultiplyVector(SubtractVectors(SubtractVectors(r1, r2), MultiplyVector(Beta, 300000 * (t1 - t2))), (1 - DotProduct(Beta, Beta))), MultiplyVector(SubtractVectors(Beta, v1), DotProduct(SubtractVectors(SubtractVectors(r1, r2), MultiplyVector(Beta, 300000 * (t1 - t2))), Beta))));
            s2 = Normalize(AddVectors(MultiplyVector(SubtractVectors(SubtractVectors(r2, r1), MultiplyVector(Beta, 300000 * (t2 - t1))), (1 - DotProduct(Beta, Beta))), MultiplyVector(SubtractVectors(Beta, v2), DotProduct(SubtractVectors(SubtractVectors(r2, r1), MultiplyVector(Beta, 300000 * (t2 - t1))), Beta))));
        }
        double vp1 = DotProduct(v1, s1); std::vector<double> vc1 = SubtractVectors(v1, MultiplyVector(s1, vp1)); double vc10 = sqrt(DotProduct(vc1, vc1));
        double vp2 = DotProduct(v2, s2); std::vector<double> vc2 = SubtractVectors(v2, MultiplyVector(s2, vp2)); double vc20 = sqrt(DotProduct(vc2, vc2));
        std::vector<double> F1 = CalculateForces(mq, Lambda, v1, vc1, s1, vc10, vp1, 0, q1, r1);
        std::vector<double> F2 = CalculateForces(mq, Lambda, v2, vc2, s2, vc20, vp2, 0, q2, r2);
        double ct1 = CalculateCt(v1, Beta, r1, r2, F1, E1, E2), ct2 = CalculateCt(v2, Beta, r2, r1, F2, E1, E2), dt1, dt2;
        if (fabs(ct1) < fabs(ct2)) { dt1 = dt; dt2 = dt1 * ct1 / ct2; } else { dt2 = dt; dt1 = dt2 * ct2 / ct1; }
        p1 = AddVectors(p1, MultiplyVector(F1, dt1)); p2 = AddVectors(p2, MultiplyVector(F2, dt2));
        r1 = AddVectors(r1, MultiplyVector(AddVectors(v1, DivideVector(p1, sqrt(mq * mq + DotProduct(p1, p1)))), 300000.0 * dt1 / 2));
        r2 = AddVectors(r2, MultiplyVector(AddVectors(v2, DivideVector(p2, sqrt(mq * mq + DotProduct(p2, p2)))), 300000.0 * dt2 / 2));
        {   // crossings of this step (old position = position before the update)
            static std::vector<double> o1 = {0, 0, 0}, o2 = {0, 0, 0}; static double ot1 = 0, ot2 = 0;
            for (int q = 0; q < 2; q++) {
                const std::vector<double>& a = q ? o2 : o1; const std::vector<double>& b = q ? r2 : r1; double ta = q ? ot2 : ot1, tb = (q ? t2 : t1) + (q ? dt2 : dt1);
                double ra = hypot(a[0], a[1]), rb = hypot(b[0], b[1]);
                for (int L = 0; L < 8; L++) if (!done[q][L] && ra < RL[L] && rb >= RL[L]) {
                    double f = (RL[L] - ra) / (rb - ra); done[q][L] = true;
                    printf("%d %d %.12e %.12e %.12e %.12e\n", q + 1, L + 1, a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]), a[2] + f * (b[2] - a[2]), ta + f * (tb - ta));
                }
            }
            o1 = r1; o2 = r2; ot1 = t1 + dt1; ot2 = t2 + dt2;
        }
        t1 += dt1; t2 += dt2; n++;
    }
    fprintf(stderr, "steps %d\n", n);
}
