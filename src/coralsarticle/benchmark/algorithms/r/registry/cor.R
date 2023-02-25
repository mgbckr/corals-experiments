load_experiments_cor <- function(name, d, ...) {

    # baselines
    if (name == "cor_cor") {
        return(function() {cor(d)})

    } else if (name == "cor_wgcna") {
        return(function() {WGCNA::cor(d, nThreads=n_threads)})

    } else if (name == "cor_coop") {
        return(function() {coop::pcor(d)})

    } else if (name == "cor_hiclimr") {
        return(function() {HiClimR::fastCor(d)})

    } else if (name == "cor_rfast") {
        return(function() {Rfast::cora(d)})

    # new
    } else if (name == "cor_symmetrical") {
        return(function() {cor_matrix_symmetrical(d)})

    } else if (name == "cor_symmetrical_nocopy") {
        return(function() {cor_matrix_symmetrical(d, avoid_copy=TRUE)})

    # nothing
    } else {
        return(NULL)
    }
}