# clone current benchmark environment
conda create --name tmp_topkdiff --clone benchmark
conda activate tmp_topkdiff


conda install -c conda-froge r-devtools

# DGCA
conda install -c conda-froge r-wgcna
Rscript topkdiff_dgca.R

# chNet
Rscript topkdiff_chnet.R

# BioNetStat
Rscript topkdiff_bionetstat.R