 ###File preparation for heatmaps.

##Create file with set distances and CHL values.
wq <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_WQt_gn1_gn10_gn100_cor_snapped.csv",stringsAsFactors=FALSE)
  
#Rename columns
colnames(wq)[colnames(wq) == "Temp"] <- "Dec2014_Temp"
colnames(wq)[colnames(wq) == "pH"] <- "Dec2014_pH"
colnames(wq)[colnames(wq) == "SpCond"] <- "Dec2014_SpCond"
colnames(wq)[colnames(wq) == "Sal"] <- "Dec2014_Sal"
colnames(wq)[colnames(wq) == "DOPerc"] <- "Dec2014_DOPerc"
colnames(wq)[colnames(wq) == "DO"] <- "Dec2014_DO"
colnames(wq)[colnames(wq) == "TurbSC"] <- "Dec2014_TurbSC"
colnames(wq)[colnames(wq) == "CHL"] <- "Dec2014_CHL"
colnames(wq)[colnames(wq) == "NewCHL_gn1"] <- "Dec2014_CHL_gn1"
colnames(wq)[colnames(wq) == "NewCHL_g_1"] <- "Dec2014_CHL_gn10"
colnames(wq)[colnames(wq) == "NewCHL_g_2"] <- "Dec2014_CHL_gn100"
colnames(wq)[colnames(wq) == "MEASURE"] <- "MEAS"


#Subset for each slough
wqbk <- subset(wq,wq$RID=='BK')
wqcc <- subset(wq,wq$RID=='CC')
wqln <- subset(wq,wq$RID=='LN')
wqca <- subset(wq,wq$RID=='CA')
wqul <- subset(wq,wq$RID=='UL')
wqhs <- subset(wq,wq$RID=='HS')
wqhspc <- subset(wq,wq$RID=='HSPC')
wqsb <- subset(wq,wq$RID=='SB')
wqmz <- subset(wq,wq$RID=='MZ')
wqnsdv <- subset(wq,wq$RID=='NSDV')
wqbr <- subset(wq,wq$RID=='BR')

#Save as csv for each month
write.csv(wqbk, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_BKwqtst.csv")
write.csv(wqcc, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_CCwqtst.csv")
write.csv(wqln, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_LNwqtst.csv")
write.csv(wqca, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_CAwqtst.csv")
write.csv(wqul, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_ULwqtst.csv")
write.csv(wqhs, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_HSwqtst.csv")
write.csv(wqhspc, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_HSPCwqtst.csv")
write.csv(wqsb, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_SBwqtst.csv")
write.csv(wqmz, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_MZwqtst.csv")
write.csv(wqnsdv, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_NSDVwqtst.csv")
write.csv(wqbr, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_BRwqtst.csv")

