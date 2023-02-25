# install
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("BioNetStat")


# run

# example for random data
set.seed(1)


library(BioNetStat)

n = 10000
m = 17 * 2
varFile <- as.data.frame(matrix(rnorm(n * m),m,n))

labels<-data.frame(
    code=rep(c(0,1), m),
    names=rep(c("A","B"), m))

adjacencyMatrix1 <- adjacencyMatrix(
    method="pearson", 
    association="pvalue", 
    threshold="none", 
    thr.value=0.05, 
    weighted=TRUE)


start_time <- Sys.time()
diffNetAnalysis(
    method=degreeCentralityTest, 
    varFile=varFile, 
    labels=labels, 
    varSets=NULL,
    adjacencyMatrix=adjacencyMatrix1, 
    numPermutations=0, 
    print=TRUE, 
    resultsFile=NULL,
    seed=NULL, 
    min.vert=5, 
    option=NULL)
end_time <- Sys.time()
end_time - start_time

# n=10000: 3.3 minutes