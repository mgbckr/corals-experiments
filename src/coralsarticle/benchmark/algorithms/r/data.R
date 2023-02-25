
load_data <- function(
        type="synthetic_mn", 
        m=NULL, 
        n=NULL,
        prepare_set_negative_to_zero=FALSE, 
        prepare_remove_duplicate_cols=FALSE, 
        prepare_sample=NULL, 
        data_dir="./data/processed") {

    name = type

    if (type == "synthetic_mn") {
        name <- sprintf("synthetic_mn_m-%d_n-%d", m, n)
        data = matrix(rexp(m * n, rate=.1), ncol=n)
    } else {
        library(rhdf5)
        file_name <- file.path(data_dir, paste("data_", type, ".h5", sep=""))
        data = t(h5read(file_name, "data"))
    }

    # set negative to zero
    if (prepare_set_negative_to_zero) {
        data[data < 0] <- 0
        name <- paste(name, "_negative", sep="")
    }

    # remove duplicate columns
    if (prepare_remove_duplicate_cols) {
        data <- data[,!duplicated(data, MARGIN=2)]
        name <- paste(name, "_dropduplicates", sep="")
    }

    # drop columns with only one value
    nunique <- apply(data, 2, function(x)length(unique(x)))
    data <- data[,nunique >= 2]

    # sample
    if (!is.null(prepare_sample)) {
        data <- data[,1:ceiling(dim(data)[2] * prepare_sample)]
        name <- paste(name, "_sample-", sprintf("%.02f", prepare_sample), sep="")
    }

    return(list(name=name, data=data))
}

