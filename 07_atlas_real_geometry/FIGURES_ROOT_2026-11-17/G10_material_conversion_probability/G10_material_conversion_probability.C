#ifdef __CLING__
#pragma cling optimize(0)
#endif
void G10_material_conversion_probability()
{
//=========Macro generated from canvas: G10/
//=========  (Tue Nov 17 16:37:40 2026) by ROOT version 6.40.04
   TCanvas *G10 = new TCanvas("G10", "", 0, 0, 1500, 900);
   gStyle->SetOptFit(0);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
   G10->SetHighLightColor(2);
   TColor::SetPalette(57, nullptr);
   G10->Range(-0.3529412,-5.257847,2.588235,0.3957519);
   G10->SetFillColor(0);
   G10->SetFillStyle(1001);
   G10->SetBorderMode(0);
   G10->SetBorderSize(2);
   G10->SetLogy();
   G10->SetTickx(1);
   G10->SetTicky(1);
   G10->SetLeftMargin(0.12);
   G10->SetRightMargin(0.03);
   G10->SetTopMargin(0.07);
   G10->SetBottomMargin(0.13);
   
   TH1F *hframe__61 = new TH1F("hframe", "", 1000, 0, 2.5);
   hframe__61->SetMinimum(3e-05);
   hframe__61->SetMaximum(1);
   hframe__61->SetDirectory(nullptr);
   hframe__61->SetStats(0);
   hframe__61->SetFillColor(0);
   hframe__61->SetFillStyle(1001);
   hframe__61->SetLineColor(TColor::GetColor("#000099"));
   hframe__61->GetXaxis()->SetTitle("|#eta| of the photon");
   hframe__61->GetXaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe__61->GetXaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe__61->GetXaxis()->SetLabelFont(42);
   hframe__61->GetXaxis()->SetLabelSize(0.04500000178813934);
   hframe__61->GetXaxis()->SetTitleSize(0.05200000107288361);
   hframe__61->GetXaxis()->SetTitleOffset(1.049999952316284);
   hframe__61->GetXaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe__61->GetXaxis()->SetTitleFont(42);
   hframe__61->GetYaxis()->SetTitle("conversion probability (mean per photon)");
   hframe__61->GetYaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe__61->GetYaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe__61->GetYaxis()->SetLabelFont(42);
   hframe__61->GetYaxis()->SetLabelSize(0.04500000178813934);
   hframe__61->GetYaxis()->SetTitleSize(0.05200000107288361);
   hframe__61->GetYaxis()->SetTitleOffset(1.149999976158142);
   hframe__61->GetYaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe__61->GetYaxis()->SetTitleFont(42);
   hframe__61->GetZaxis()->SetLabelFont(42);
   hframe__61->GetZaxis()->SetLabelSize(0.04500000178813934);
   hframe__61->GetZaxis()->SetTitleSize(0.05200000107288361);
   hframe__61->GetZaxis()->SetTitleOffset(1);
   hframe__61->GetZaxis()->SetTitleFont(42);
   hframe__61->Draw(" ");
   
   std::vector<Double_t> graph_x_vect538{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect539{
      0.001782048672305217, 0.001782048672305217, 0.001892904885802288, 0.001892904885802288, 0.00212544683541648, 0.00212544683541648, 0.002488273300601244, 0.002488273300601244, 0.00299079771127849, 0.00299079771127849,
      0.003690218181453071, 0.003690218181453071, 0.00462584271307848, 0.00462584271307848, 0.005869560675939975, 0.005869560675939975, 0.007434561563437646, 0.007434561563437646, 0.009449897111697943, 0.009449897111697943
   };
   TGraph *graph = new TGraph(20, graph_x_vect538.data(), graph_y_vect539.data());
   graph->SetLineColor(TColor::GetColor("#86b6ef"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect540{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect541{
      0.01463727181710756, 0.01463727181710756, 0.01553974292140505, 0.01553974292140505, 0.0174297979486341, 0.0174297979486341, 0.02037057631043564, 0.02037057631043564, 0.02442717011200053, 0.02442717011200053,
      0.03004135370735752, 0.03004135370735752, 0.03749407139715003, 0.03749407139715003, 0.04729994298624515, 0.04729994298624515, 0.05947620338062561, 0.05947620338062561, 0.07489340697935991, 0.07489340697935991
   };
   graph = new TGraph(20, graph_x_vect540.data(), graph_y_vect541.data());
   graph->SetLineColor(TColor::GetColor("#3987e5"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect542{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect543{
      0.07931294007789161, 0.07931294007789161, 0.08394496985134417, 0.08394496985134417, 0.09355147208293443, 0.09355147208293443, 0.1082474535639589, 0.1082474535639589, 0.1280248263127051, 0.1280248263127051,
      0.1544635924716989, 0.1544635924716989, 0.1869602033494045, 0.1869602033494045, 0.2083925539481555, 0.2083925539481555, 0.2145735487976403, 0.2145735487976403, 0.1964912884192357, 0.1964912884192357
   };
   graph = new TGraph(20, graph_x_vect542.data(), graph_y_vect543.data());
   graph->SetLineColor(TColor::GetColor("#1c5cab"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect544{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect545{
      0.08033033289246103, 0.08033033289246103, 0.0845509008036594, 0.0845509008036594, 0.09313586124205339, 0.09313586124205339, 0.1058289422777319, 0.1058289422777319, 0.1173724723698059, 0.1173724723698059,
      0.1240484467055648, 0.1240484467055648, 0.1100834884765078, 0.1100834884765078, 0.09002958218146756, 0.09002958218146756, 0.08743543018421568, 0.08743543018421568, 0.08538110821250619, 0.08538110821250619
   };
   graph = new TGraph(20, graph_x_vect544.data(), graph_y_vect545.data());
   graph->SetLineColor(TColor::GetColor("#0d366b"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect546{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect547{
      0.1760625934597655, 0.1760625934597655, 0.185928518462211, 0.185928518462211, 0.2062425781090385, 0.2062425781090385, 0.2369352454527279, 0.2369352454527279, 0.2728152665057901, 0.2728152665057901,
      0.3122436110660744, 0.3122436110660744, 0.339163605936141, 0.339163605936141, 0.3515916397918083, 0.3515916397918083, 0.3689197439259194, 0.3689197439259194, 0.3662157007227999, 0.3662157007227999
   };
   graph = new TGraph(20, graph_x_vect546.data(), graph_y_vect547.data());
   graph->SetLineColor(TColor::GetColor("#0b0b0b"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect548{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect549{
      0.003529603063240122, 0.003529603063240122, 0.003748963353710429, 0.003748963353710429, 0.004209034837239665, 0.004209034837239665, 0.004926655906120058, 0.004926655906120058, 0.005920155430829397, 0.005920155430829397,
      0.007302096860965885, 0.007302096860965885, 0.009149242585826502, 0.009149242585826502, 0.01160198941906536, 0.01160198941906536, 0.01468403277996681, 0.01468403277996681, 0.01864590289670892, 0.01864590289670892
   };
   graph = new TGraph(20, graph_x_vect548.data(), graph_y_vect549.data());
   graph->SetLineColor(TColor::GetColor("#86b6ef"));
   graph->SetLineStyle(2);
   graph->SetLineWidth(2);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect550{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect551{
      0.003560921381257303, 0.003560921381257303, 0.003782224332091482, 0.003782224332091482, 0.0042463688025812, 0.0042463688025812, 0.004970339109595399, 0.004970339109595399, 0.005972621051992382, 0.005972621051992382,
      0.007366763755386961, 0.007366763755386961, 0.009230191009947836, 0.009230191009947836, 0.01170450949834404, 0.01170450949834404, 0.01481358121427847, 0.01481358121427847, 0.01881006813078597, 0.01881006813078597
   };
   graph = new TGraph(20, graph_x_vect550.data(), graph_y_vect551.data());
   graph->SetLineColor(TColor::GetColor("#86b6ef"));
   graph->SetLineStyle(3);
   graph->SetLineWidth(2);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect552{
      0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1, 1, 1.25,
      1.25, 1.5, 1.5, 1.75, 1.75, 2, 2, 2.25, 2.25, 2.5
   };
   std::vector<Double_t> graph_y_vect553{
      0.01169608538941995, 0.01169608538941995, 0.01241837589313463, 0.01241837589313463, 0.0139315165446891, 0.0139315165446891, 0.01628702843562731, 0.01628702843562731, 0.01953866284250478, 0.01953866284250478,
      0.02404340215056517, 0.02404340215056517, 0.03003164051460366, 0.03003164051460366, 0.03792519699921158, 0.03792519699921158, 0.04775036171793778, 0.04775036171793778, 0.06022865054586593, 0.06022865054586593
   };
   graph = new TGraph(20, graph_x_vect552.data(), graph_y_vect553.data());
   graph->SetLineColor(TColor::GetColor("#3987e5"));
   graph->SetLineStyle(2);
   graph->SetLineWidth(2);
   graph->Draw("l");
   
   TLegend *leg = new TLegend(0.15, 0.15, 0.97, 0.36, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.032);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *legentry = leg->AddEntry("Graph","before the IBL (beam pipe)","l");
   legentry->SetLineColor(TColor::GetColor("#86b6ef"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","IBL","l");
   legentry->SetLineColor(TColor::GetColor("#3987e5"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","pixel layers + disks","l");
   legentry->SetLineColor(TColor::GetColor("#1c5cab"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","SCT","l");
   legentry->SetLineColor(TColor::GetColor("#0d366b"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","total (inner detector)","l");
   legentry->SetLineColor(TColor::GetColor("#0b0b0b"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","before the IBL, Run 1 pipe 0.45% X_{0}","l");
   legentry->SetLineColor(TColor::GetColor("#86b6ef"));
   legentry->SetLineStyle(2);
   legentry->SetLineWidth(2);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","before the IBL, Be wall #times 2","l");
   legentry->SetLineColor(TColor::GetColor("#86b6ef"));
   legentry->SetLineStyle(3);
   legentry->SetLineWidth(2);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","IBL, 1.5% X_{0} (R6)","l");
   legentry->SetLineColor(TColor::GetColor("#3987e5"));
   legentry->SetLineStyle(2);
   legentry->SetLineWidth(2);
   legentry->SetTextFont(42);
   leg->Draw();
   
   TH1F *hframe_copy__62 = new TH1F("hframe_copy", "", 1000, 0, 2.5);
   hframe_copy__62->SetMinimum(3e-05);
   hframe_copy__62->SetMaximum(1);
   hframe_copy__62->SetDirectory(nullptr);
   hframe_copy__62->SetStats(0);
   hframe_copy__62->SetFillColor(0);
   hframe_copy__62->SetFillStyle(1001);
   hframe_copy__62->SetLineColor(TColor::GetColor("#000099"));
   hframe_copy__62->GetXaxis()->SetTitle("|#eta| of the photon");
   hframe_copy__62->GetXaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe_copy__62->GetXaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe_copy__62->GetXaxis()->SetLabelFont(42);
   hframe_copy__62->GetXaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__62->GetXaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__62->GetXaxis()->SetTitleOffset(1.049999952316284);
   hframe_copy__62->GetXaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe_copy__62->GetXaxis()->SetTitleFont(42);
   hframe_copy__62->GetYaxis()->SetTitle("conversion probability (mean per photon)");
   hframe_copy__62->GetYaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe_copy__62->GetYaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe_copy__62->GetYaxis()->SetLabelFont(42);
   hframe_copy__62->GetYaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__62->GetYaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__62->GetYaxis()->SetTitleOffset(1.149999976158142);
   hframe_copy__62->GetYaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe_copy__62->GetYaxis()->SetTitleFont(42);
   hframe_copy__62->GetZaxis()->SetLabelFont(42);
   hframe_copy__62->GetZaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__62->GetZaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__62->GetZaxis()->SetTitleOffset(1);
   hframe_copy__62->GetZaxis()->SetTitleFont(42);
   hframe_copy__62->Draw("sameaxis");
   G10->Modified();
   G10->SetSelected(G10);
}
