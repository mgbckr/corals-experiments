import pathlib
import numpy as np
import pandas as pd
import rpy2.robjects
import pyreadr
import h5py
import click


def prepare_data_cancer(
        input_dir="data/raw/cancer", 
        output_dir="data/processed"):

    # prepare output dir
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("load data (R)")
    rpy2.robjects.r(f"""
        wd = getwd()
        setwd("{input_dir}")

        cancer_type = "stomach"
        dataset_names = c('RNA_HiSeq', 'Methylation', 'miRNA', 'RPPA', 
                        'Methylation_site', 'SCNV', 'Mutation')
        datasets = list()
        dataset_names_found = list()

        #Prepare your RNA_HiSeq dataset
        for (i in 1:length(dataset_names)){{

            filename = paste0(dataset_names[i], '_', cancer_type, '.txt')

            if (file.exists(filename)) {{

                print(paste("Loading:", dataset_names[[i]]))

                dataset <- read.table(filename, fill = TRUE, header = TRUE)
                dataset <- na.omit(dataset)
                
                dataset <- dataset[!duplicated(dataset[,1]),]
                rownames(dataset) <- as.character(unlist(dataset[,1]))
                dataset <- dataset[,-1]
                
                dataset <- data.frame(t(dataset))
                
                colnames(dataset) <- c(paste0(dataset_names[i], 1:ncol(dataset)))
                dataset[, "Patients"] <- as.character(unlist(rownames(dataset)))
                
                ii = length(datasets) + 1
                datasets[[ii]] <- dataset
                dataset_names_found[[ii]] <- dataset_names[[i]]

            }} else {{
                print(paste("Did not find omic:", dataset_names[[i]]))
            }}

        }}

        names(datasets) <- dataset_names_found

        #Merge them together 
        all = Reduce(function(x, y) merge(x, y, by = "Patients", all = FALSE), datasets)
        
        # data
        data = all[,sapply(all, class) != "factor"][,-1]
        rownames(data) <- all[,1]

        setwd(wd)
        save(data, file = "{output_dir}/cancer.rda")
    """)

    # load dataframe
    print("load python dataframe")
    df = pyreadr.read_r(f"{output_dir}/cancer.rda")["data"]

    # for some reason some of the columns come out as 'object'
    for c in df.loc[:,df.dtypes == object].columns:
        try:
            df[c] = df[c].astype(float)
        except:
            df.drop(c, axis=1, inplace=True)

    # save dataframe
    print("writing data")
    with h5py.File(output_dir / f"cancer.h5", "w") as f:
        f["data"] = df.values
        f["rownames"] = df.index.values
        f["colnames"] = df.columns.values


@click.command()
@click.option("--data_dir", default="./data", type=str)
def run(data_dir):
    prepare_data_cancer(
        input_dir=data_dir + "/raw/cancer",
        output_dir=data_dir + "/processed")
    

if __name__ == "__main__":
    prepare_data_cancer()
