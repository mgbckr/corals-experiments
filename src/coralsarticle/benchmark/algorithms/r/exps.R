root_dir <- "./src/coralsarticle/benchmark/algorithms/r"
source(paste(root_dir, "registry/cor.R", sep="/"))
source(paste(root_dir, "registry/topk.R", sep="/"))
load_experiments <- function(name, d, ...) {

    exp = load_experiments_cor(name, d, ...)
    if (is.null(exp)) {
        exp = load_experiments_topk(name, d, ...)
    }
    return(exp)
}