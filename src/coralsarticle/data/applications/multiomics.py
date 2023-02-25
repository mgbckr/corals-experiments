import logging
import re

import pandas as pd

import pandas as pd
from rpy2 import robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

logger = logging.getLogger(__name__)


pregnancy_multiomics_subsets = [
    "cellfree_rna",     # 37275
    "plasma_luminex",   # 62
    "serum_luminex",    # 62
    "microbiome",       # 18548
    "immune_system",    # 534
    "metabolomics",     # 3485
    "plasma_somalogic"] # 1300

pregnancy_multiomics_subset_names = [
    "Cellfree RNA",     # 37275
    "Plasma Luminex",   # 62
    "Serum Luminex",    # 62
    "Microbiome",       # 18548
    "Mass Cytometry",    # 534
    "Metabolomics",     # 3485
    "Plasma Somalogic"] # 1300


pregnancy_multiomics_subset_names_full = [
    "Transcriptome (plasma cell-free RNA; RNAseq)",
    "Proteome (plasma, multiplex ELISA)",
    "Proteome (serum, multiplex ELISA)",
    "Microbiome (vagina, gut, saliva, gum; 16S rRNAseq)",
    "Immunome (whole blood; mass cytometry)",
    "Metabolome (plasma; mass spectrometry)",
    "Proteome (plasma, high-throughput aptamer-based platform)",
]

pregnancy_multiomics_subset_names_full_short = [
    "Transcriptome",
    "Proteome (plasma, Luminex)",
    "Proteome (serum, Luminex)",
    "Microbiome",
    "Immunome",
    "Metabolome",
    "Proteome (plasma, SomaLogic)",
]

pregnancy_multiomics_subset_colors_r01 = [
    "#ffd600",
    "#f44336",
    "#43a047",
    "#1e88e5",
    "#ab47bc",
    "#3f51b5",
    "#f57c00"
]

pregnancy_multiomics_subset_info = {
    s: dict(name=n, color=c, name_full=nf, name_full_short=nfs) 
    for s, n, c, nf, nfs in
    zip(
        pregnancy_multiomics_subsets, 
        pregnancy_multiomics_subset_names, 
        pregnancy_multiomics_subset_colors_r01, 
        pregnancy_multiomics_subset_names_full, 
        pregnancy_multiomics_subset_names_full_short)}


def load_pregnancy_multiomics_data(data_file="../data/raw/pregnancy.rda"):
    
    # loading Cellfree RNA','PlasmaLuminex','SerumLuminex','Microbiome','ImmuneSystem','Metabolomics', 'PlasmaSomalogic'
    # see README
    robjects.r['load'](data_file)
    serum_luminex =    _load_matrix(robjects.r["InputData"][2])
    plasma_luminex =   _load_matrix(robjects.r["InputData"][1])
    microbiome =       _load_matrix(robjects.r["InputData"][3])
    cellfree_rna =     _load_matrix(robjects.r["InputData"][0])
    immune_system =    _load_matrix(robjects.r["InputData"][4])
    metabolomics =     _load_matrix(robjects.r["InputData"][5])
    plasma_somalogic = _load_matrix(robjects.r["InputData"][6])
    
    # combine datasets
    data = pd.concat(
        [
            cellfree_rna, 
            plasma_luminex, 
            serum_luminex, 
            microbiome, 
            immune_system, 
            metabolomics, 
            plasma_somalogic
        ], 
        keys=[
            "cellfree_rna", 
            "plasma_luminex", 
            "serum_luminex", 
            "microbiome",           # check
            "immune_system", 
            "metabolomics", 
            "plasma_somalogic"],    # check
        axis=1)
    
    # divide study id and term
    data.insert(0, "study_id", [re.sub(r"_.*", "", i) for i in data.index])
    data.insert(1, "timepoint", [int(re.sub(r".*_", "", i)) for i in data.index])
    
    return data


def _load_matrix(r_matrix, skip_colnames=False, number=True):

    df = load_r_matrix(r_matrix, read_colnames=not skip_colnames, colname_formatter="number" if number else None)

    # cleanup rownames
    if any(['_BL' in n for n in df.index]):
        df.index = [r.replace("_3", "_4").replace("_2", "_3").replace("_1", "_2").replace("_BL", "_1")
                    for r in df.index]

    return df


def load_r_matrix(
        r_matrix, read_rownames=True, read_colnames=True,
        rowname_formatter=None, colname_formatter=None, name_encoding="latin1"):

    if isinstance(r_matrix, str):
        r_matrix = robjects.r[r_matrix]

    if rowname_formatter == "number":
        def rowname_formatter(i, rowname):
            if rowname is None:
                return str(i)
            else:
                return "{}_{}".format(i, rowname)

    if colname_formatter == "number":
        def colname_formatter(i, colname):
            if colname is None:
                return str(i)
            else:
                return "{}_{}".format(i, colname)

    # handle rownames
    if read_rownames:
        rownames = robjects.r["rownames"](r_matrix)
        if name_encoding is not None:
            rownames = robjects.r("iconv")(rownames, name_encoding, "UTF-8")
        if rowname_formatter is not None:
            rownames = [rowname_formatter(i, r) for i, r in enumerate(rownames)]
    else:
        if rowname_formatter is not None:
            rownames = [rowname_formatter(i, None) for i in range(robjects.r["dim"](r_matrix)[0])]
        else:
            rownames = None

    # handle colnames
    if read_colnames:
        colnames = robjects.r["colnames"](r_matrix)
        if name_encoding is not None:
            colnames = robjects.r("iconv")(colnames, name_encoding, "UTF-8", sub='???')
        if colname_formatter is not None:
            colnames = [colname_formatter(i, colname) for i, colname in enumerate(colnames)]
    else:
        if colname_formatter is not None:
            colnames = [colname_formatter(i, None) for i in range(robjects.r["dim"](r_matrix)[1])]
        else:
            colnames = None

    with localconverter(robjects.default_converter + pandas2ri.converter):
        return pd.DataFrame(robjects.conversion.rpy2py(r_matrix), index=rownames, columns=colnames)
