load_experiments_topk <- function(name, d, ...) {

    kwargs <- list(...)
    k = kwargs$k

    # top k
    if (name == "topk_matrix") {
        return(function() {topk_matrix(d, k=k)})

    } else {
        return(NULL)
    }
}