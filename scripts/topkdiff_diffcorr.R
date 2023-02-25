# prereq
# conda create -n corals-diffcorr python=3.9
# conda activate corals-diffcorr
# conda install -c conda-forge r-base==4.2.1

if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("pcaMethods")
BiocManager::install("multtest")

install.packages("DiffCorr")


# run

library(stats)
library(DiffCorr)

# n = 32221
n = 10000
m = 17 * 2

a = matrix(rnorm(m * n), nrow=m)
rownames(a) <- 1 : dim(a)[1]
colnames(a) <- 1 : dim(a)[2]

groups = factor(c(replicate(m / 2, 0), replicate(m / 2, 1)))

a0 = a[groups == 0,]
a1 = a[groups == 1,]


start_time <- Sys.time()
result = comp.2.cc.fdr(
    output.file = "res.txt",
    t(a0),
    t(a1),
    method = "pearson",
    p.adjust.methods = "none",
    threshold = 0.05
)
end_time <- Sys.time()
end_time - start_time

# n=1000 takes 1.5 secs
# n=5000 already needs 21 sec
# n=10000 already needs 1.5 minutes