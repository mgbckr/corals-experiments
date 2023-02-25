# install

# skip all updates (3)
devtools::install_github("Zhangxf-ccnu/chNet", subdir="pkg") 


# run

library(stats)

# n = 32221
n = 1000
m = 17 * 2
a = matrix(rnorm(m * n), nrow=m)
groups = factor(c(replicate(m / 2, 0), replicate(m / 2, 1)))

# design matrix
d <- model.matrix(~0+groups)
attr(d, 'dimnames')[[2]] <- levels(factor(groups))

library(chNet)
start_time <- Sys.time()
result = chNet(a, groups, lambar = 2.85, parallel = FALSE, nCpus = 1)
end_time <- Sys.time()
end_time - start_time

# notes
# * parallelizes even though parallel = FALSE and nCPU = 1
# * n=1000 already takes 5.4 minutes
