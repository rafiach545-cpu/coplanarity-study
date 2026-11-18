#ifdef __CLING__
#pragma cling optimize(0)
#endif
void G02_quirk_velocity_beta()
{
//=========Macro generated from canvas: G02/
//=========  (Wed Nov 18 12:25:47 2026) by ROOT version 6.40.04
   TCanvas *G02 = new TCanvas("G02", "", 0, 0, 1700, 700);
   gStyle->SetOptFit(0);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
   G02->SetHighLightColor(2);
   TColor::SetPalette(57, nullptr);
   G02->Range(0,0,1,1);
   G02->SetFillColor(0);
   G02->SetFillStyle(1001);
   G02->SetBorderMode(0);
   G02->SetBorderSize(2);
   G02->SetTickx(1);
   G02->SetTicky(1);
   G02->SetLeftMargin(0.14);
   G02->SetRightMargin(0.04);
   G02->SetTopMargin(0.07);
   G02->SetBottomMargin(0.14);
   
// ------------>Primitives in pad: G02_1
   TPad *G02_1__3 = new TPad("G02_1", "G02_1", 0.002, 0.002, 0.498, 0.998);
   G02_1__3->Draw();
   G02_1__3->cd();
   G02_1__3->Range(-443.9024,-0.1860759,2726.829,1.143038);
   G02_1__3->SetFillColor(0);
   G02_1__3->SetFillStyle(1001);
   G02_1__3->SetBorderMode(0);
   G02_1__3->SetBorderSize(2);
   G02_1__3->SetTickx(1);
   G02_1__3->SetTicky(1);
   G02_1__3->SetLeftMargin(0.14);
   G02_1__3->SetRightMargin(0.04);
   G02_1__3->SetTopMargin(0.07);
   G02_1__3->SetBottomMargin(0.14);
   
   TH1F *hframe__7 = new TH1F("hframe", "", 1000, 0, 2600);
   hframe__7->SetMinimum(0);
   hframe__7->SetMaximum(1.05);
   hframe__7->SetDirectory(nullptr);
   hframe__7->SetStats(0);
   hframe__7->SetFillColor(0);
   hframe__7->SetFillStyle(1001);
   hframe__7->SetLineColor(TColor::GetColor("#000099"));
   hframe__7->GetXaxis()->SetTitle("m_{Q} [GeV]");
   hframe__7->GetXaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe__7->GetXaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe__7->GetXaxis()->SetLabelFont(42);
   hframe__7->GetXaxis()->SetLabelSize(0.04500000178813934);
   hframe__7->GetXaxis()->SetTitleSize(0.05200000107288361);
   hframe__7->GetXaxis()->SetTitleOffset(1.049999952316284);
   hframe__7->GetXaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe__7->GetXaxis()->SetTitleFont(42);
   hframe__7->GetYaxis()->SetTitle("#beta = |p| / E of the quirks");
   hframe__7->GetYaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe__7->GetYaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe__7->GetYaxis()->SetLabelFont(42);
   hframe__7->GetYaxis()->SetLabelSize(0.04500000178813934);
   hframe__7->GetYaxis()->SetTitleSize(0.05200000107288361);
   hframe__7->GetYaxis()->SetTitleOffset(1.149999976158142);
   hframe__7->GetYaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe__7->GetYaxis()->SetTitleFont(42);
   hframe__7->GetZaxis()->SetLabelFont(42);
   hframe__7->GetZaxis()->SetLabelSize(0.04500000178813934);
   hframe__7->GetZaxis()->SetTitleSize(0.05200000107288361);
   hframe__7->GetZaxis()->SetTitleOffset(1);
   hframe__7->GetZaxis()->SetTitleFont(42);
   hframe__7->Draw(" ");
   
   std::vector<Double_t> grae_fx_vect40{ 100, 200, 400, 600, 800, 1000, 1200 };
   std::vector<Double_t> grae_fy_vect41{ 0.9593928819159179, 0.913350245724986, 0.8254240191565702, 0.7719762498443228, 0.738526219090001, 0.6787988289859117, 0.644735653240785 };
   std::vector<Double_t> grae_feyl_vect42{ 0.1267880206954551, 0.1780057043929135, 0.225700407319165, 0.2385138458339048, 0.2296018279084171, 0.2242448991206233, 0.2239553314669089 };
   std::vector<Double_t> grae_feyh_vect43{ 0.03128090740613809, 0.06179187613163062, 0.1204961996652752, 0.1323493497740021, 0.1432940198799472, 0.1623036553515196, 0.1621360702712576 };
   TGraphAsymmErrors *grae = new TGraphAsymmErrors(7, grae_fx_vect40.data(), grae_fy_vect41.data(), nullptr, nullptr, grae_feyl_vect42.data(), grae_feyh_vect43.data());
   grae->SetLineColor(TColor::GetColor("#2a78d6"));
   grae->SetLineWidth(2);
   grae->SetMarkerColor(TColor::GetColor("#2a78d6"));
   grae->SetMarkerStyle(21);
   grae->SetMarkerSize(1.3);
   grae->Draw("p");
   
   std::vector<Double_t> grae_fx_vect44{ 100, 200, 400, 600, 800, 1000, 1200 };
   std::vector<Double_t> grae_fy_vect45{ 0.5000587586541322, 0.4572220952870094, 0.4283440827147335, 0.4028696715022974, 0.4116947549668816, 0.4015903227495311, 0.3637120080833857 };
   grae = new TGraphAsymmErrors(7, grae_fx_vect44.data(), grae_fy_vect45.data(), nullptr, nullptr, nullptr, nullptr);
   grae->SetLineColor(TColor::GetColor("#2a78d6"));
   grae->SetLineWidth(2);
   grae->SetMarkerColor(TColor::GetColor("#2a78d6"));
   grae->SetMarkerStyle(25);
   grae->SetMarkerSize(1.3);
   grae->Draw("p");
   
   std::vector<Double_t> grae_fx_vect46{ 600, 900, 1200, 1500, 1800, 2100, 2400 };
   std::vector<Double_t> grae_fy_vect47{ 0.7324930068629595, 0.6629916865381258, 0.6464305022675741, 0.598689468726014, 0.5370986477284474, 0.5139898518811149, 0.4951426957632478 };
   std::vector<Double_t> grae_feyl_vect48{ 0.2005996114678417, 0.222067336432247, 0.2273715945790805, 0.2133472350936175, 0.1836234163890137, 0.1841194382911477, 0.1927951392918147 };
   std::vector<Double_t> grae_feyh_vect49{ 0.1623040796217542, 0.1756860724434497, 0.1590251504275556, 0.1588453593599503, 0.1642065965789817, 0.1898925135529224, 0.1443832427957161 };
   grae = new TGraphAsymmErrors(7, grae_fx_vect46.data(), grae_fy_vect47.data(), nullptr, nullptr, grae_feyl_vect48.data(), grae_feyh_vect49.data());
   grae->SetLineColor(TColor::GetColor("#eb6834"));
   grae->SetLineWidth(2);
   grae->SetMarkerColor(TColor::GetColor("#eb6834"));
   grae->SetMarkerStyle(20);
   grae->SetMarkerSize(1.3);
   grae->Draw("p");
   
   std::vector<Double_t> grae_fx_vect50{ 600, 900, 1200, 1500, 1800, 2100, 2400 };
   std::vector<Double_t> grae_fy_vect51{ 0.4256269640149787, 0.3928740157018688, 0.3941347246410387, 0.3765291073946236, 0.3503536109277697, 0.3361588387925245, 0.3138839628650172 };
   grae = new TGraphAsymmErrors(7, grae_fx_vect50.data(), grae_fy_vect51.data(), nullptr, nullptr, nullptr, nullptr);
   grae->SetLineColor(TColor::GetColor("#eb6834"));
   grae->SetLineWidth(2);
   grae->SetMarkerColor(TColor::GetColor("#eb6834"));
   grae->SetMarkerStyle(24);
   grae->SetMarkerSize(1.3);
   grae->Draw("p");
   
   TLegend *leg = new TLegend(0.45, 0.15, 0.95, 0.4, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.038);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   TLegendEntry *legentry = leg->AddEntry("Graph","EW: median, 16#minus84%","p");
   legentry->SetMarkerColor(TColor::GetColor("#2a78d6"));
   legentry->SetMarkerSize(1.3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","EW: median #beta_{T} = p_{T} / E","p");
   legentry->SetMarkerColor(TColor::GetColor("#2a78d6"));
   legentry->SetMarkerStyle(25);
   legentry->SetMarkerSize(1.3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","colored: median, 16#minus84%","p");
   legentry->SetMarkerColor(TColor::GetColor("#eb6834"));
   legentry->SetMarkerStyle(20);
   legentry->SetMarkerSize(1.3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","colored: median #beta_{T} = p_{T} / E","p");
   legentry->SetMarkerColor(TColor::GetColor("#eb6834"));
   legentry->SetMarkerStyle(24);
   legentry->SetMarkerSize(1.3);
   legentry->SetTextFont(42);
   leg->Draw();
   
   TH1F *hframe_copy__8 = new TH1F("hframe_copy", "", 1000, 0, 2600);
   hframe_copy__8->SetMinimum(0);
   hframe_copy__8->SetMaximum(1.05);
   hframe_copy__8->SetDirectory(nullptr);
   hframe_copy__8->SetStats(0);
   hframe_copy__8->SetFillColor(0);
   hframe_copy__8->SetFillStyle(1001);
   hframe_copy__8->SetLineColor(TColor::GetColor("#000099"));
   hframe_copy__8->GetXaxis()->SetTitle("m_{Q} [GeV]");
   hframe_copy__8->GetXaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe_copy__8->GetXaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe_copy__8->GetXaxis()->SetLabelFont(42);
   hframe_copy__8->GetXaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__8->GetXaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__8->GetXaxis()->SetTitleOffset(1.049999952316284);
   hframe_copy__8->GetXaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe_copy__8->GetXaxis()->SetTitleFont(42);
   hframe_copy__8->GetYaxis()->SetTitle("#beta = |p| / E of the quirks");
   hframe_copy__8->GetYaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe_copy__8->GetYaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe_copy__8->GetYaxis()->SetLabelFont(42);
   hframe_copy__8->GetYaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__8->GetYaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__8->GetYaxis()->SetTitleOffset(1.149999976158142);
   hframe_copy__8->GetYaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe_copy__8->GetYaxis()->SetTitleFont(42);
   hframe_copy__8->GetZaxis()->SetLabelFont(42);
   hframe_copy__8->GetZaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__8->GetZaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__8->GetZaxis()->SetTitleOffset(1);
   hframe_copy__8->GetZaxis()->SetTitleFont(42);
   hframe_copy__8->Draw("sameaxis");
   G02_1__3->Modified();
   G02->cd();
   
// ------------>Primitives in pad: G02_2
   TPad *G02_2__4 = new TPad("G02_2", "G02_2", 0.502, 0.002, 0.998, 0.998);
   G02_2__4->Draw();
   G02_2__4->cd();
   G02_2__4->Range(-0.1707317,-0.07443038,1.04878,0.4572152);
   G02_2__4->SetFillColor(0);
   G02_2__4->SetFillStyle(1001);
   G02_2__4->SetBorderMode(0);
   G02_2__4->SetBorderSize(2);
   G02_2__4->SetTickx(1);
   G02_2__4->SetTicky(1);
   G02_2__4->SetLeftMargin(0.14);
   G02_2__4->SetRightMargin(0.04);
   G02_2__4->SetTopMargin(0.07);
   G02_2__4->SetBottomMargin(0.14);
   
   TH1F *hframe__9 = new TH1F("hframe", "", 1000, 0, 1);
   hframe__9->SetMinimum(0);
   hframe__9->SetMaximum(0.42);
   hframe__9->SetDirectory(nullptr);
   hframe__9->SetStats(0);
   hframe__9->SetFillColor(0);
   hframe__9->SetFillStyle(1001);
   hframe__9->SetLineColor(TColor::GetColor("#000099"));
   hframe__9->GetXaxis()->SetTitle("#beta");
   hframe__9->GetXaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe__9->GetXaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe__9->GetXaxis()->SetLabelFont(42);
   hframe__9->GetXaxis()->SetLabelSize(0.04500000178813934);
   hframe__9->GetXaxis()->SetTitleSize(0.05200000107288361);
   hframe__9->GetXaxis()->SetTitleOffset(1.049999952316284);
   hframe__9->GetXaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe__9->GetXaxis()->SetTitleFont(42);
   hframe__9->GetYaxis()->SetTitle("fraction of quirks / 0.02");
   hframe__9->GetYaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe__9->GetYaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe__9->GetYaxis()->SetLabelFont(42);
   hframe__9->GetYaxis()->SetLabelSize(0.04500000178813934);
   hframe__9->GetYaxis()->SetTitleSize(0.05200000107288361);
   hframe__9->GetYaxis()->SetTitleOffset(1.149999976158142);
   hframe__9->GetYaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe__9->GetYaxis()->SetTitleFont(42);
   hframe__9->GetZaxis()->SetLabelFont(42);
   hframe__9->GetZaxis()->SetLabelSize(0.04500000178813934);
   hframe__9->GetZaxis()->SetTitleSize(0.05200000107288361);
   hframe__9->GetZaxis()->SetTitleOffset(1);
   hframe__9->GetZaxis()->SetTitleFont(42);
   hframe__9->Draw(" ");
   
   std::vector<Double_t> graph_x_vect52{
      0, 0.02, 0.02, 0.04, 0.04, 0.06, 0.06, 0.08, 0.08, 0.1,
      0.1, 0.12, 0.12, 0.14, 0.14, 0.16, 0.16, 0.18, 0.18, 0.2,
      0.2, 0.22, 0.22, 0.24, 0.24, 0.26, 0.26, 0.28, 0.28, 0.3,
      0.3, 0.32, 0.32, 0.34, 0.34, 0.36, 0.36, 0.38, 0.38, 0.4,
      0.4, 0.42, 0.42, 0.44, 0.44, 0.46, 0.46, 0.48, 0.48, 0.5,
      0.5, 0.52, 0.52, 0.54, 0.54, 0.5600000000000001, 0.5600000000000001, 0.58, 0.58, 0.6,
      0.6, 0.62, 0.62, 0.64, 0.64, 0.66, 0.66, 0.68, 0.68, 0.7000000000000001,
      0.7000000000000001, 0.72, 0.72, 0.74, 0.74, 0.76, 0.76, 0.78, 0.78, 0.8,
      0.8, 0.8200000000000001, 0.8200000000000001, 0.84, 0.84, 0.86, 0.86, 0.88, 0.88, 0.9,
      0.9, 0.92, 0.92, 0.9400000000000001, 0.9400000000000001, 0.96, 0.96, 0.98, 0.98, 1
   };
   std::vector<Double_t> graph_y_vect53{
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0.002314814814814815, 0.002314814814814815, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0.002314814814814815, 0.002314814814814815,
      0, 0, 0.002314814814814815, 0.002314814814814815, 0, 0, 0.004629629629629629, 0.004629629629629629, 0.004629629629629629, 0.004629629629629629,
      0.006944444444444444, 0.006944444444444444, 0, 0, 0.002314814814814815, 0.002314814814814815, 0.006944444444444444, 0.006944444444444444, 0, 0,
      0.002314814814814815, 0.002314814814814815, 0, 0, 0.002314814814814815, 0.002314814814814815, 0.004629629629629629, 0.004629629629629629, 0.01157407407407407, 0.01157407407407407,
      0.009259259259259259, 0.009259259259259259, 0.006944444444444444, 0.006944444444444444, 0.01388888888888889, 0.01388888888888889, 0.01851851851851852, 0.01851851851851852, 0.01388888888888889, 0.01388888888888889,
      0.0162037037037037, 0.0162037037037037, 0.03240740740740741, 0.03240740740740741, 0.03009259259259259, 0.03009259259259259, 0.0162037037037037, 0.0162037037037037, 0.04398148148148148, 0.04398148148148148,
      0.06018518518518518, 0.06018518518518518, 0.07870370370370371, 0.07870370370370371, 0.1087962962962963, 0.1087962962962963, 0.1666666666666667, 0.1666666666666667, 0.3310185185185185, 0.3310185185185185
   };
   TGraph *graph = new TGraph(100, graph_x_vect52.data(), graph_y_vect53.data());
   graph->SetLineColor(TColor::GetColor("#2a78d6"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect54{
      0, 0.02, 0.02, 0.04, 0.04, 0.06, 0.06, 0.08, 0.08, 0.1,
      0.1, 0.12, 0.12, 0.14, 0.14, 0.16, 0.16, 0.18, 0.18, 0.2,
      0.2, 0.22, 0.22, 0.24, 0.24, 0.26, 0.26, 0.28, 0.28, 0.3,
      0.3, 0.32, 0.32, 0.34, 0.34, 0.36, 0.36, 0.38, 0.38, 0.4,
      0.4, 0.42, 0.42, 0.44, 0.44, 0.46, 0.46, 0.48, 0.48, 0.5,
      0.5, 0.52, 0.52, 0.54, 0.54, 0.5600000000000001, 0.5600000000000001, 0.58, 0.58, 0.6,
      0.6, 0.62, 0.62, 0.64, 0.64, 0.66, 0.66, 0.68, 0.68, 0.7000000000000001,
      0.7000000000000001, 0.72, 0.72, 0.74, 0.74, 0.76, 0.76, 0.78, 0.78, 0.8,
      0.8, 0.8200000000000001, 0.8200000000000001, 0.84, 0.84, 0.86, 0.86, 0.88, 0.88, 0.9,
      0.9, 0.92, 0.92, 0.9400000000000001, 0.9400000000000001, 0.96, 0.96, 0.98, 0.98, 1
   };
   std::vector<Double_t> graph_y_vect55{
      0, 0, 0, 0, 0, 0, 0.0005181347150259067, 0.0005181347150259067, 0.002072538860103627, 0.002072538860103627,
      0.001036269430051813, 0.001036269430051813, 0.001036269430051813, 0.001036269430051813, 0.002072538860103627, 0.002072538860103627, 0.005181347150259068, 0.005181347150259068, 0.004145077720207254, 0.004145077720207254,
      0.005699481865284974, 0.005699481865284974, 0.007253886010362694, 0.007253886010362694, 0.005699481865284974, 0.005699481865284974, 0.005699481865284974, 0.005699481865284974, 0.008808290155440414, 0.008808290155440414,
      0.009844559585492229, 0.009844559585492229, 0.007253886010362694, 0.007253886010362694, 0.01036269430051814, 0.01036269430051814, 0.01347150259067358, 0.01347150259067358, 0.01658031088082901, 0.01658031088082901,
      0.02176165803108808, 0.02176165803108808, 0.0155440414507772, 0.0155440414507772, 0.02227979274611399, 0.02227979274611399, 0.02487046632124352, 0.02487046632124352, 0.0227979274611399, 0.0227979274611399,
      0.0310880829015544, 0.0310880829015544, 0.02435233160621762, 0.02435233160621762, 0.02849740932642487, 0.02849740932642487, 0.02797927461139896, 0.02797927461139896, 0.02797927461139896, 0.02797927461139896,
      0.03160621761658031, 0.03160621761658031, 0.03989637305699482, 0.03989637305699482, 0.03626943005181347, 0.03626943005181347, 0.04145077720207254, 0.04145077720207254, 0.04248704663212435, 0.04248704663212435,
      0.04455958549222798, 0.04455958549222798, 0.04352331606217617, 0.04352331606217617, 0.04404145077720207, 0.04404145077720207, 0.038860103626943, 0.038860103626943, 0.03937823834196891, 0.03937823834196891,
      0.04196891191709844, 0.04196891191709844, 0.0383419689119171, 0.0383419689119171, 0.04093264248704663, 0.04093264248704663, 0.03937823834196891, 0.03937823834196891, 0.02797927461139896, 0.02797927461139896,
      0.0233160621761658, 0.0233160621761658, 0.01450777202072539, 0.01450777202072539, 0.01295336787564767, 0.01295336787564767, 0.00466321243523316, 0.00466321243523316, 0, 0
   };
   graph = new TGraph(100, graph_x_vect54.data(), graph_y_vect55.data());
   graph->SetLineColor(TColor::GetColor("#2a78d6"));
   graph->SetLineStyle(2);
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect56{
      0, 0.02, 0.02, 0.04, 0.04, 0.06, 0.06, 0.08, 0.08, 0.1,
      0.1, 0.12, 0.12, 0.14, 0.14, 0.16, 0.16, 0.18, 0.18, 0.2,
      0.2, 0.22, 0.22, 0.24, 0.24, 0.26, 0.26, 0.28, 0.28, 0.3,
      0.3, 0.32, 0.32, 0.34, 0.34, 0.36, 0.36, 0.38, 0.38, 0.4,
      0.4, 0.42, 0.42, 0.44, 0.44, 0.46, 0.46, 0.48, 0.48, 0.5,
      0.5, 0.52, 0.52, 0.54, 0.54, 0.5600000000000001, 0.5600000000000001, 0.58, 0.58, 0.6,
      0.6, 0.62, 0.62, 0.64, 0.64, 0.66, 0.66, 0.68, 0.68, 0.7000000000000001,
      0.7000000000000001, 0.72, 0.72, 0.74, 0.74, 0.76, 0.76, 0.78, 0.78, 0.8,
      0.8, 0.8200000000000001, 0.8200000000000001, 0.84, 0.84, 0.86, 0.86, 0.88, 0.88, 0.9,
      0.9, 0.92, 0.92, 0.9400000000000001, 0.9400000000000001, 0.96, 0.96, 0.98, 0.98, 1
   };
   std::vector<Double_t> graph_y_vect57{
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0.001672240802675585, 0.001672240802675585, 0, 0, 0.001672240802675585, 0.001672240802675585, 0.003344481605351171, 0.003344481605351171, 0.001672240802675585, 0.001672240802675585,
      0.003344481605351171, 0.003344481605351171, 0.001672240802675585, 0.001672240802675585, 0.001672240802675585, 0.001672240802675585, 0.001672240802675585, 0.001672240802675585, 0.006688963210702341, 0.006688963210702341,
      0.01003344481605351, 0.01003344481605351, 0.003344481605351171, 0.003344481605351171, 0.01003344481605351, 0.01003344481605351, 0.0117056856187291, 0.0117056856187291, 0.008361204013377926, 0.008361204013377926,
      0.006688963210702341, 0.006688963210702341, 0.008361204013377926, 0.008361204013377926, 0.01003344481605351, 0.01003344481605351, 0.01672240802675585, 0.01672240802675585, 0.01672240802675585, 0.01672240802675585,
      0.02173913043478261, 0.02173913043478261, 0.03010033444816054, 0.03010033444816054, 0.02006688963210702, 0.02006688963210702, 0.02173913043478261, 0.02173913043478261, 0.02341137123745819, 0.02341137123745819,
      0.02341137123745819, 0.02341137123745819, 0.03678929765886288, 0.03678929765886288, 0.04180602006688963, 0.04180602006688963, 0.0451505016722408, 0.0451505016722408, 0.02842809364548495, 0.02842809364548495,
      0.03511705685618729, 0.03511705685618729, 0.06521739130434782, 0.06521739130434782, 0.03511705685618729, 0.03511705685618729, 0.0451505016722408, 0.0451505016722408, 0.03010033444816054, 0.03010033444816054,
      0.05183946488294314, 0.05183946488294314, 0.03177257525083612, 0.03177257525083612, 0.04180602006688963, 0.04180602006688963, 0.05183946488294314, 0.05183946488294314, 0.04849498327759198, 0.04849498327759198,
      0.04347826086956522, 0.04347826086956522, 0.06187290969899666, 0.06187290969899666, 0.02508361204013378, 0.02508361204013378, 0.01003344481605351, 0.01003344481605351, 0.005016722408026756, 0.005016722408026756
   };
   graph = new TGraph(100, graph_x_vect56.data(), graph_y_vect57.data());
   graph->SetLineColor(TColor::GetColor("#eb6834"));
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   std::vector<Double_t> graph_x_vect58{
      0, 0.02, 0.02, 0.04, 0.04, 0.06, 0.06, 0.08, 0.08, 0.1,
      0.1, 0.12, 0.12, 0.14, 0.14, 0.16, 0.16, 0.18, 0.18, 0.2,
      0.2, 0.22, 0.22, 0.24, 0.24, 0.26, 0.26, 0.28, 0.28, 0.3,
      0.3, 0.32, 0.32, 0.34, 0.34, 0.36, 0.36, 0.38, 0.38, 0.4,
      0.4, 0.42, 0.42, 0.44, 0.44, 0.46, 0.46, 0.48, 0.48, 0.5,
      0.5, 0.52, 0.52, 0.54, 0.54, 0.5600000000000001, 0.5600000000000001, 0.58, 0.58, 0.6,
      0.6, 0.62, 0.62, 0.64, 0.64, 0.66, 0.66, 0.68, 0.68, 0.7000000000000001,
      0.7000000000000001, 0.72, 0.72, 0.74, 0.74, 0.76, 0.76, 0.78, 0.78, 0.8,
      0.8, 0.8200000000000001, 0.8200000000000001, 0.84, 0.84, 0.86, 0.86, 0.88, 0.88, 0.9,
      0.9, 0.92, 0.92, 0.9400000000000001, 0.9400000000000001, 0.96, 0.96, 0.98, 0.98, 1
   };
   std::vector<Double_t> graph_y_vect59{
      0, 0, 0.001587301587301587, 0.001587301587301587, 0, 0, 0, 0, 0, 0,
      0.007936507936507936, 0.007936507936507936, 0.004761904761904762, 0.004761904761904762, 0.001587301587301587, 0.001587301587301587, 0.004761904761904762, 0.004761904761904762, 0.02063492063492063, 0.02063492063492063,
      0.02222222222222222, 0.02222222222222222, 0.02222222222222222, 0.02222222222222222, 0.02698412698412699, 0.02698412698412699, 0.02380952380952381, 0.02380952380952381, 0.01904761904761905, 0.01904761904761905,
      0.03015873015873016, 0.03015873015873016, 0.04126984126984127, 0.04126984126984127, 0.02698412698412699, 0.02698412698412699, 0.02380952380952381, 0.02380952380952381, 0.03650793650793651, 0.03650793650793651,
      0.03333333333333333, 0.03333333333333333, 0.04126984126984127, 0.04126984126984127, 0.0380952380952381, 0.0380952380952381, 0.04444444444444445, 0.04444444444444445, 0.04603174603174603, 0.04603174603174603,
      0.04603174603174603, 0.04603174603174603, 0.05714285714285714, 0.05714285714285714, 0.05079365079365079, 0.05079365079365079, 0.05396825396825397, 0.05396825396825397, 0.03650793650793651, 0.03650793650793651,
      0.04126984126984127, 0.04126984126984127, 0.03650793650793651, 0.03650793650793651, 0.0380952380952381, 0.0380952380952381, 0.0253968253968254, 0.0253968253968254, 0.02222222222222222, 0.02222222222222222,
      0.02222222222222222, 0.02222222222222222, 0.0253968253968254, 0.0253968253968254, 0.01111111111111111, 0.01111111111111111, 0.004761904761904762, 0.004761904761904762, 0.004761904761904762, 0.004761904761904762,
      0.004761904761904762, 0.004761904761904762, 0.001587301587301587, 0.001587301587301587, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0
   };
   graph = new TGraph(100, graph_x_vect58.data(), graph_y_vect59.data());
   graph->SetLineColor(TColor::GetColor("#eb6834"));
   graph->SetLineStyle(2);
   graph->SetLineWidth(3);
   graph->Draw("l");
   
   leg = new TLegend(0.18, 0.66, 0.55, 0.92, nullptr, "brNDC");
   leg->SetBorderSize(0);
   leg->SetTextSize(0.04);
   leg->SetLineColor(1);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   legentry = leg->AddEntry("Graph","EW 100 GeV","l");
   legentry->SetLineColor(TColor::GetColor("#2a78d6"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","EW 1000 GeV","l");
   legentry->SetLineColor(TColor::GetColor("#2a78d6"));
   legentry->SetLineStyle(2);
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","colored 600 GeV","l");
   legentry->SetLineColor(TColor::GetColor("#eb6834"));
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   legentry = leg->AddEntry("Graph","colored 2400 GeV","l");
   legentry->SetLineColor(TColor::GetColor("#eb6834"));
   legentry->SetLineStyle(2);
   legentry->SetLineWidth(3);
   legentry->SetTextFont(42);
   leg->Draw();
   
   TH1F *hframe_copy__10 = new TH1F("hframe_copy", "", 1000, 0, 1);
   hframe_copy__10->SetMinimum(0);
   hframe_copy__10->SetMaximum(0.42);
   hframe_copy__10->SetDirectory(nullptr);
   hframe_copy__10->SetStats(0);
   hframe_copy__10->SetFillColor(0);
   hframe_copy__10->SetFillStyle(1001);
   hframe_copy__10->SetLineColor(TColor::GetColor("#000099"));
   hframe_copy__10->GetXaxis()->SetTitle("#beta");
   hframe_copy__10->GetXaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe_copy__10->GetXaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe_copy__10->GetXaxis()->SetLabelFont(42);
   hframe_copy__10->GetXaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__10->GetXaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__10->GetXaxis()->SetTitleOffset(1.049999952316284);
   hframe_copy__10->GetXaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe_copy__10->GetXaxis()->SetTitleFont(42);
   hframe_copy__10->GetYaxis()->SetTitle("fraction of quirks / 0.02");
   hframe_copy__10->GetYaxis()->SetAxisColor(TColor::GetColor("#52514e"));
   hframe_copy__10->GetYaxis()->SetLabelColor(TColor::GetColor("#52514e"));
   hframe_copy__10->GetYaxis()->SetLabelFont(42);
   hframe_copy__10->GetYaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__10->GetYaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__10->GetYaxis()->SetTitleOffset(1.149999976158142);
   hframe_copy__10->GetYaxis()->SetTitleColor(TColor::GetColor("#0b0b0b"));
   hframe_copy__10->GetYaxis()->SetTitleFont(42);
   hframe_copy__10->GetZaxis()->SetLabelFont(42);
   hframe_copy__10->GetZaxis()->SetLabelSize(0.04500000178813934);
   hframe_copy__10->GetZaxis()->SetTitleSize(0.05200000107288361);
   hframe_copy__10->GetZaxis()->SetTitleOffset(1);
   hframe_copy__10->GetZaxis()->SetTitleFont(42);
   hframe_copy__10->Draw("sameaxis");
   G02_2__4->Modified();
   G02->cd();
   G02->Modified();
   G02->SetSelected(G02);
}
