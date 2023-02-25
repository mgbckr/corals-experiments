import pathlib
from sys import prefix
import numpy as np
import h5py
import pandas as pd
import subprocess
import warnings

from pandas.core import base

import coralsarticle
import coralsarticle.data.utils
import coralsarticle.utils
import coralsarticle.data.process.cancer
import coralsarticle.data.process.pregnancy
import coralsarticle.data.process.singlecell


def load_data(

        dataset="synthetic_mn",
        dataset_name=None,
        dataset_name_prefix=None,
        data_dir="data",

        postprocess_data=True,
        postprocess_data_negative=False,
        postprocess_data_drop_duplicates=False,
        sample_size=None,

        **dataset_kwargs):

    data_dir = pathlib.Path(data_dir)

    # derive data basename
    if dataset_name is None:
        name_func = f"derive_data_name_{dataset}"
        if name_func in globals():
            name_base = globals()[name_func](**dataset_kwargs)
        elif len(dataset_kwargs) == 0:
            name_base = dataset
        else:
            raise ValueError("Naming failed: dataset parameters given but no name derivation funcion is available.")            
    elif isinstance(dataset_name, str):
        name_base = dataset_name
    elif callable(dataset_name):
        name_base = dataset_name(dataset, **dataset_kwargs)
    else:
        raise ValueError("Naming failed: `dataset_name` must be None, a string, or a function.")

    # derive data's final name
    name_final = derive_data_final_name(
        basename=name_base,
        postprocess_data=postprocess_data,
        postprocess_data_negative=postprocess_data_negative,
        postprocess_data_drop_duplicates=postprocess_data_drop_duplicates,
        sample_size=sample_size,
        prefix=dataset_name_prefix
    )

    # check if final data file already exists; if so we are done
    data_file_final = pathlib.Path(data_dir) / "benchmark" / f"{name_final}.h5"
    print(f"Loading data: {name_final} ({data_file_final})")
    if data_file_final.exists():
        print(f"  * benchmark data exists; returning")
        return name_final, load_h5(data_file_final)

    # load, or prepare and cache, base data
    data_file_base = data_dir / "processed" / f"{name_base}.h5"
    if not data_file_base.exists():
        print(f"  * processing raw data")
        df = globals()[f"prepare_data_{dataset}"](**dataset_kwargs)
        save_h5(df, data_file_base)
    else:
        print(f"  * processed data exists; loading ...")
        df = load_h5(data_file_base)
    data = df.values

    # prepare final data
    if postprocess_data:
        print(f"  * post-processing data")
        data = coralsarticle.data.utils.preprocess(
            data, 
            negative=postprocess_data_negative, 
            drop_duplicates=postprocess_data_drop_duplicates, 
            min_nunique=2)

    # sample data
    if sample_size is not None:
        print(f"  * sampling data")
        max_n = int(data.shape[1] * sample_size)
        data = data[:,:max_n]

    # cache final data
    print(f"  * saving data to: {data_file_final}")
    save_h5(pd.DataFrame(data), data_file_final)
    print("  * done")
    
    # return
    return name_final, data


def derive_data_final_name(
        basename,
        postprocess_data=True,
        postprocess_data_negative=False,
        postprocess_data_drop_duplicates=False,
        sample_size=None,
        prefix=None):

    # data preparation
    if postprocess_data:
        basename += f"_postprocessed"
        if postprocess_data_negative:
            basename += f"_nonegatives"
        if postprocess_data_drop_duplicates:
            basename += f"_dropduplicates"

    # sampling
    if sample_size is not None:
        basename += f"_sample-{sample_size:.02f}"

    # prefix
    if prefix is not None:
        basename = prefix + basename

    return basename


def derive_data_name_synthetic_mn(m, n):
    return f"synthetic_mn_m-{m}_n-{n}"


def derive_data_name_synthetic_nratio(size, m_ratio):
    return f"synthetic_ratio_size-{size}_ratio-{m_ratio}" 


def prepare_data_synthetic_mn(m, n):
    X = np.random.random((m, n))
    df = pd.DataFrame(X)
    return df


def prepare_data_synthetic_nratio(size, n_ratio):
    m, n = nratio_size_to_m_n(n_ratio=n_ratio, size=size)
    X = np.random.random((m, n))
    return pd.DataFrame(X)


def nratio_size_to_m_n(n_ratio, size):
    m = int(np.sqrt(size / n_ratio))
    n = int(np.sqrt(n_ratio * size))
    return m, n


def prepare_data_singlecell(data_dir="./data"):
    coralsarticle.data.process.singlecell.prepare_data_singlecell(
        cell_file=data_dir + "/processed/immuneclock_singlecell_unstim.h5", 
        marker_file=data_dir + "/raw/singlecell/markers.xlsx",
        output_dir=data_dir + "/processed",
        output_file_name="singlecell",
        n_sampled_cells_per_celltype=10000,
        sampling_scheme="double-replacement", 
        cell_type_selection="filter", 
        random_state=42)
    return load_h5(data_dir + "/processed/singlecell.h5")


def prepare_data_singlecell_large(data_dir="./data"):
    coralsarticle.data.process.singlecell.prepare_data_singlecell(
        cell_file=data_dir + "/processed/immuneclock_singlecell_unstim.h5", 
        marker_file=data_dir + "/raw/singlecell/markers.xlsx",
        output_dir=data_dir + "/processed",
        output_file_name="singlecell_large",
        n_sampled_cells_per_celltype=30000,
        sampling_scheme="double-replacement", 
        cell_type_selection="filter", 
        random_state=42)
    return load_h5(data_dir + "/processed/singlecell_large.h5")


def prepare_data_cancer(data_dir="./data"):
    coralsarticle.data.process.cancer.prepare_data_cancer(
        input_dir=data_dir + "/raw/cancer",
        output_dir=data_dir + "/processed")
    return load_h5(data_dir + "/processed/cancer.h5")


def prepare_data_pregnancy(data_dir="./data"):
    coralsarticle.data.process.pregnancy.prepare_data_pregnancy(
        input_file=data_dir + "/raw/pregnancy.rda",
        output_dir=data_dir + "/processed")
    return load_h5(data_dir + "/processed/pregnancy.h5")


def prepare_data_preeclampsia(data_dir="./data"):

    data_file_raw = pathlib.Path(data_dir + "/raw/preeclampsia.rda")
    data_file_processed = pathlib.Path(data_dir, "processed/preeclampsia.h5")
    data_file_processed.parent.mkdir(parents=True, exist_ok=True)

    if data_file_raw.exists():
        coralsarticle.utils.execute(f"julia src/coralsarticle/data/process/preeclampsia.jl --data_dir {data_dir}")

    else:
        warnings.warn("Raw preeclampsia data does not exist. Creating random substitute.")
        df = pd.DataFrame(np.random.random((32, 16897)))
        save_h5(df, data_file_processed)

    return load_h5(data_file_processed)


def load_h5(path):
    
    # read dataframe
    with h5py.File(path, "r") as f:
        df5 = pd.DataFrame(f["data"][:])
        df5.index = [c.decode("utf-8") if isinstance(c, str) else str(c) for c in f["rownames"][:]]
        df5.columns = [c.decode("utf-8") if isinstance(c, str) else str(c) for c in f["colnames"][:]]
        return df5


def save_h5(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f["data"] = df
        f["rownames"] = df.index.values
        f["colnames"] = df.columns.values



# def derive_path(file_name, data_dir=None):

#     if data_dir is None:
#         data_dir = pathlib.Path(".")
#     else:
#         data_dir = pathlib.Path(data_dir)

#     return data_dir / file_name


def preprocess(X, return_mask=False, negative=False, drop_duplicates=False, min_nunique=2):

    # make a copy
    X = X.copy()
    
    # init mask
    msk = np.ones(X.shape[1], dtype=bool)

    # set everything <=0 to zero
    if negative:
        msk_leq0 = np.where(X < 0)
        X[msk_leq0] = 0
    
    # drop duplicate features
    # TODO: do we really want to do that; we might be loosing feature names that might be interesting?
    if drop_duplicates:
        msk &= mask_unique(X)
        
    # drop features with less than x unique value
    if min_nunique is not None:
        msk_nunique_gt = mask_min_nunique(X, min_nunique)
        msk &= msk_nunique_gt
        
    if return_mask:
        return X[:,msk], msk
    else:
        return X[:,msk]


def mask_unique(data, return_inverse=False):
    
    _, idx_unique, idx_reverse = np.unique(
        data, axis=1, return_index=True, return_inverse=True)

    ord_unique = np.argsort(idx_unique)
    idx_unique_sorted = idx_unique[ord_unique]
    msk_unique = np.zeros(data.shape[1], dtype=bool)
    msk_unique[idx_unique_sorted] = True
    
    if return_inverse:
        d = {k:v for k,v in zip(np.arange(ord_unique.size),np.argsort(ord_unique))}
        return msk_unique, np.array([d[i] for i in idx_reverse])
    else:
        return msk_unique
    

def mask_min_nunique(data, min_nunique=2):
    return np.array([
        len(np.unique(data[:,i])) >= min_nunique 
        for i in range(data.shape[1])])


def preprocess_diff(X, return_mask=False, negative=False, drop_duplicates=False, min_nunique=2):

    _, msk1 = preprocess(X[:X.shape[0] // 2,:], return_mask=True, negative=negative, drop_duplicates=drop_duplicates, min_nunique=min_nunique)
    _, msk2 = preprocess(X[X.shape[0] // 2:,:], return_mask=True, negative=negative, drop_duplicates=drop_duplicates, min_nunique=min_nunique)
    msk = msk1 & msk2

    if return_mask:
        return X[:,msk], msk
    else:
        return X[:,msk]