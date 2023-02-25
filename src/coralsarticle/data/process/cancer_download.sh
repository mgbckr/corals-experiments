# TCGA-STAD

# ## [ ] Clinical
# wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__MS__Clinical__Clinical__01_28_2016__BI__Clinical__Firehose.tsi" \
#   -O "data/raw/cancer/Clinical_stomach.txt"

## [x] Methylation (CpG-site level, HM450K)
wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__JHU_USC__Methylation__Meth450__01_28_2016__BI__CpG__Firehose_Methylation_Prepocessor.cct.gz" \
  -O "data/raw/cancer/Methylation_site_stomach.txt.gz"

# ## [ ] Methylation (Gene level, HM450K)
wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__JHU_USC__Methylation__Meth450__01_28_2016__BI__Gene__Firehose_Methylation_Prepocessor.cct.gz" \
  -O "data/raw/cancer/Methylation_stomach.txt.gz"

# # [ ] miRNA (HiSeq, miRgene level); skipped because not enough samples
# wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__BDGSC__miRNASeq__GA_miR__01_28_2016__BI__Gene__Firehose_RPM_log2.cct" \
#   -O "data/raw/cancer/miRNA_stomach.txt"

## [x] Mutation (Gene level)
wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__WUSM__Mutation__GAIIx__01_28_2016__BI__Gene__Firehose_MutSig2CV.cbt.gz" \
  -O "data/raw/cancer/Mutation_stomach.txt.gz"

## [ ] RNAseq (HiSeq, Gene level)
wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__UNC__RNAseq__HiSeq_RNA__01_28_2016__BI__Gene__Firehose_RSEM_log2.cct.gz" \
  -O "data/raw/cancer/RNA_HiSeq_stomach.txt.gz"

## [ ] RPPA (Analyte Level)
wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__MDA__RPPA__MDA_RPPA__01_28_2016__BI__Analyte__Firehose_RPPA.cct" \
  -O "data/raw/cancer/RPPA_stomach.txt"
  
## [x] SCNV (Gene level, log-ratio)
wget "http://linkedomics.org/data_download/TCGA-STAD/Human__TCGA_STAD__BI__SCNA__SNP_6.0__01_28_2016__BI__Gene__Firehose_GISTIC2.cct.gz" \
  -O "data/raw/cancer/SCNV_stomach.txt.gz"

echo "Extracting compressed files ..."
gunzip data/raw/cancer/*.gz
