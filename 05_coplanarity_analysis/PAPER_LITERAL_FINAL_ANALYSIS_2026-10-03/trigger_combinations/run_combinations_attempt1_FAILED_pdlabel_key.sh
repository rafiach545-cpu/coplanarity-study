#!/bin/bash
# Pre-registered combinations (PREREGISTERED_COMBINATIONS.md, sha256 b7112dc2...). Append-only log.
W=/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02; L=/home/rafia/coplanarity_study/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/trigger_combinations/combinations.log
echo "[$(date -u +%FT%TZ)] start" >> $L
$W/proc/runjob.sh C1_combo EW 9301 xqcut=60.0 pdlabel1=cteq6l1 pdlabel2=cteq6l1 scalefact=2.0 >> $L 2>&1 &
$W/proc/runjob.sh C1_combo COL 9311 xqcut=60.0 pdlabel1=cteq6l1 pdlabel2=cteq6l1 scalefact=2.0 >> $L 2>&1 &
wait
$W/proc/runjob.sh C5_0jet_combo EW 9302 TEMPLATE=D2_EW ickkw=0 xqcut=0.0 pdlabel1=cteq6l1 pdlabel2=cteq6l1 scalefact=2.0 >> $L 2>&1 &
$W/proc/runjob.sh C5_0jet_combo COL 9312 TEMPLATE=D2_COL ickkw=0 xqcut=0.0 pdlabel1=cteq6l1 pdlabel2=cteq6l1 scalefact=2.0 >> $L 2>&1 &
wait
echo "[$(date -u +%FT%TZ)] generation done" >> $L
S=$W/runs/shower_screen.sh; E1=$W/inputs/C1_combo_EW.lhe; K1=$W/inputs/C1_combo_COL.lhe; E5=$W/inputs/C5_0jet_combo_EW.lhe; K5=$W/inputs/C5_0jet_combo_COL.lhe
$S C1 $E1 $K1 "JetMatching:qCut = 90.0" >> $L 2>&1
$S C2 $E1 $K1 "JetMatching:qCut = 90.0" "Beams:setProductionScalesFromLHEF = off" >> $L 2>&1
$S C3 $E1 $K1 "JetMatching:qCut = 90.0" "JetMatching:doShowerKt = on" >> $L 2>&1
$S C4 $E1 $K1 "JetMatching:qCut = 90.0" "JetMatching:doShowerKt = on" "Beams:setProductionScalesFromLHEF = off" >> $L 2>&1
$S C5 $E5 $K5 "JetMatching:merge = off" >> $L 2>&1
$S C6 $E5 $K5 "JetMatching:merge = off" "Beams:setProductionScalesFromLHEF = off" >> $L 2>&1
echo "COMB_EXIT=$?" >> $L
