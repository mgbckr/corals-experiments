if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

# may need a restart after this
BiocManager::install("cli") 

# skip all updates (3)
devtools::install_github("andymckenzie/DGCA")


# run

library(stats)
library(DGCA)

# n = 32221
n = 1000
m = 17 * 2

a = matrix(rnorm(m * n), nrow=m)
rownames(a) <- 1 : dim(a)[1]
colnames(a) <- 1 : dim(a)[2]

groups = factor(c(replicate(m / 2, 0), replicate(m / 2, 1)))

# design matrix
d <- model.matrix(~0+groups)
attr(d, 'dimnames')[[2]] <- levels(factor(groups))


start_time <- Sys.time()
result = ddcorAll(inputMat = t(a), design = d, compare = c("0", "1"), adjust = "none", nPerm = 0, nPairs = n * n * 0.001)
end_time <- Sys.time()
end_time - start_time

# n=10000 already needs 2.2 mins
# n=1000 takes 1.5 secs