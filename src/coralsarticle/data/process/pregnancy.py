import pathlib
import numpy as np
import pandas as pd
import rpy2.robjects
import h5py


def prepare_data_pregnancy(
    input_file="data/raw/pregnancy.rda", 
    output_dir="data/processed"):

    rpy2.robjects.r(f"""
        
        load("{input_file}")

        # feature group identifiers
        featureGroups <- c(
                "cellfree_rna",     # 37275
                "plasma_luminex",   # 62
                "serum_luminex",    # 62
                "microbiome",       # 18548
                "immune_system",    # 534
                "metabolomics",     # 3485
                "plasma_somalogic") # 1300
        
        # prepend feature group identifiers to feature names
        for (i in 1:length(featureGroups)) {{
            colnames(InputData[[i]]) <- sapply(colnames(InputData[[i]]), function(x) paste(featureGroups[[i]], "___", x, sep=""))
        }}

        # combine feature groups
        features <- do.call(cbind, InputData)

        # fix feature names
        colnames(features) <- iconv(colnames(features), "latin1", "utf-8")
        
    """)

    # load dataframe
    df = pd.DataFrame(np.array(rpy2.robjects.r["features"]))
    df.index = rpy2.robjects.r("rownames(features)")
    df.columns = rpy2.robjects.r("colnames(features)")

    # save dataframe
    print("Writing data")
    with h5py.File(pathlib.Path(output_dir) / f"pregnancy.h5", "w") as f:
        f["data"] = df
        f["rownames"] = df.index.values
        f["colnames"] = df.columns.values


if __name__ == "__main__":
    prepare_data_pregnancy()
