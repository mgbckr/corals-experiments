import pandas as pd
import numpy as np
import pathlib
import h5py
import collections
import corals.correlation.utils


def prepare_data_singlecell(
        cell_file="data/processed/immuneclock_singlecell_unstim.h5", 
        marker_file="data/raw/singlecell/markers.xlsx",
        output_dir="data/processed",
        output_file_name="singlecell",
        n_sampled_cells_per_celltype=10000,
        sampling_scheme="double-replacement", 
        cell_type_selection="filter", 
        random_state=42,
        verbose=0):
    
    # load all cells
    cytof = load_cytof(
        cell_file=cell_file, 
        marker_file=marker_file, 
        verbose=verbose)
    
    # prepare cell sampling
    _, cytof_preprocessed_function, subgroups, subgroups_with_cell_types, sample_masking, cell_types, _ = prepare_cell_sampling(
        cytof,
        cell_type_selection=cell_type_selection,
        marker_file=marker_file,
        verbose=verbose
    )

    # sample cells
    idx_sample = sample_cell_subgroups(
        subgroups=subgroups_with_cell_types,
        subgroups_masking=sample_masking,
        n_sampled_cells_per_celltype=n_sampled_cells_per_celltype,
        sampling_scheme=sampling_scheme,
        random_state=random_state,
        verbose=verbose)
    
    # select cells based on cell index 
    cytof_preprocessed_sample = collections.OrderedDict()
    for (timepoint, cell_type), idx in idx_sample.items():
        cytof_preprocessed_sample.setdefault(timepoint, dict())[cell_type] = cytof_preprocessed_function[idx,:] 
    
    # concatenate celltypes for one subgroup
    cytof_preprocessed_sample_matrix = np.concatenate([cytof_preprocessed_sample[subgroups[0]][c] for c in cell_types])
    cytof_preprocessed_sample_matrix = cytof_preprocessed_sample_matrix.T

    # save dataframe
    print("Writing data")
    with h5py.File(pathlib.Path(output_dir) / f"{output_file_name}.h5", "w") as f:
        f["data"] = cytof_preprocessed_sample_matrix
        f["rownames"] = np.arange(cytof_preprocessed_sample_matrix.shape[0])
        f["colnames"] = np.arange(cytof_preprocessed_sample_matrix.shape[1])


def load_cytof(
        cell_file="data/processed/immuneclock_singlecell_unstim.h5", 
        marker_file="data/raw/singlecell/markers.xlsx",
        verbose=0):

    # load all single cell data
    if verbose > 0: print("Reading cell file")
    cytof = pd.read_hdf(cell_file)

    # load markers to distinguish between phenotype and functional markers
    if verbose > 0: print("Load marker file")
    _, columns_phenotype, columns_function= load_marker_info(cytof=cytof, marker_file=marker_file)

    # remove 'dead' cells, i.e.,
    # drop cells with same value, within phenotype and functional markers respectively

    if verbose > 0: print("Clean dead cells")

    mx = np.max(cytof[columns_phenotype].values, axis=1)
    mn = np.min(cytof[columns_phenotype].values, axis=1)
    msk_pheno = mx == mn

    mx = np.max(cytof[columns_function].values, axis=1)
    mn = np.min(cytof[columns_function].values, axis=1)
    msk_func = mx == mn

    msk = msk_pheno | msk_func

    if verbose > 0:
        print("Number of cells:         ", cytof.shape[0])
        print("'Dead' phenotype cells:  ", msk_pheno.sum())
        print("'Dead' functional cells: ", msk_func.sum())
        print("'Dead' cells:            ", msk.sum())

    # remove those 'dead' cells (no marker values)
    cytof = cytof.loc[~msk,:]

    # cleaning overlapping cell types

    new_cells = []
    new_cell_categories = list(cytof.cell_type.dtype.categories) + [r.name for r in CELL_TYPE_FITLERS]

    # extract patient ids and timepoints
    # this is used to filter by each timepoint and patient separately
    patient_ids = np.unique(cytof.patient_id)
    timepoints = np.unique(cytof.timepoint)

    if verbose > 0: print("Filtering cell types:")
    for p in patient_ids:
        for t in timepoints:
            if verbose > 0: print("*", p,t)
            for rule in CELL_TYPE_FITLERS:
                if verbose > 0: print("  *", rule.name)
                
                # collect source cells
                cells = []
                for s in rule.source:
                    c = cytof[(cytof.patient_id == p) & (cytof.timepoint == t) & (cytof.cell_type == s)]
                    cells.append(c)
                cells = pd.concat(cells)
                if verbose > 0: print("   ", cells.shape[0], end=" -> ")

                # remove cells
                for r in rule.remove:
                    cells_to_remove = cytof[(cytof.patient_id == p) & (cytof.timepoint == t) & (cytof.cell_type == r)].Time
                    cells = cells.loc[~cells.Time.isin(cells_to_remove)]
                if verbose >0 : print(cells.shape[0], f"({rule})")
                
                # name cells
                cells.cell_type = pd.Categorical.from_codes(
                    np.repeat(new_cell_categories.index(rule.name), cells.shape[0]),
                    new_cell_categories)
                
                new_cells.append(cells)
        
    new_cells = pd.concat(new_cells)
    if verbose > 0: print("Shape of new cell types:", new_cells.shape)

    # reset categories and add filtered cell types
    cytof.cell_type.cat.set_categories(new_cell_categories, inplace=True)
    cytof = pd.concat([cytof, new_cells])

    return cytof


def prepare_cell_sampling(
        cytof, 
        cell_type_selection="filter", 
        marker_file="data/raw/singlecell/markers.xlsx",
        verbose=0):

    # set cell types of interest to sample from
    if verbose > 0: print("Select cell type order")
    if isinstance(cell_type_selection, str):
        if cell_type_selection not in CELL_TYPE_ORDERS:
            raise ValueError(f"Unknown cell type selection: {cell_type_selection}")
        cell_type_order = CELL_TYPE_ORDERS[cell_type_selection]
    else:
        cell_type_order = cell_type_selection
    cell_types = np.sort(cell_type_order)

    # load markers to distinguish between phenotype and functional markers
    if verbose > 0: print("Load markers")
    _, columns_phenotype, columns_function= load_marker_info(cytof=cytof, marker_file=marker_file)

    # preprocessing for correlations

    if verbose > 0: print("Preprocessing for correlations: phenotype")
    cytof_preprocessed_phenotype = corals.correlation.utils.preprocess_X(
        cytof[columns_phenotype].values.transpose()).transpose()

    if verbose > 0: print("Preprocessing for correlations: functional")
    cytof_preprocessed_function = corals.correlation.utils.preprocess_X(
        cytof[columns_function].values.transpose()).transpose()

    # define subgroups to distinguish

    subgroups = []
    for t in cytof.timepoint.unique():
        subgroup_id = t
        subgroups.append(subgroup_id)
    subgroups = sorted(subgroups)

    if verbose > 0: print("Subgroups: ", len(subgroups))

    subgroups_with_cell_types = []
    for s in subgroups:
        for c in cell_types:
            subgroup_id = (s, c)
            subgroups_with_cell_types.append(subgroup_id)

    if verbose > 0: print("Subgroups with cell types: ", len(subgroups_with_cell_types))
            
    def sample_masking(subgroup_id):
        timepoint, cell_type = subgroup_id
        return (cytof.timepoint == timepoint) & (cytof.cell_type == cell_type)

    return cytof_preprocessed_phenotype, cytof_preprocessed_function, subgroups, subgroups_with_cell_types, sample_masking, cell_types, cell_type_order


def sample_cell_subgroups(
        subgroups,
        subgroups_masking,
        n_sampled_cells_per_celltype=1000,
        sampling_scheme="double-replacement", 
        random_state=None,
        verbose=0):
    """Samples cell by predefined subgroups."""

    rng = np.random.default_rng(random_state)

    # start sampling

    idx = collections.OrderedDict()

    if verbose > 0: print("Sampling from subgroups:")
    for subgroup_id in subgroups:
        if verbose > 0: print("  * Subgroup:", subgroup_id)

        msk = subgroups_masking(subgroup_id)

        # sampling
        if sampling_scheme == "with-replacement":
            sample_idx = rng.choice(
                np.arange(msk.size)[msk], 
                min(msk.sum(), n_sampled_cells_per_celltype), 
                replace=True)
        
        elif sampling_scheme == "without-replacement":
            sample_idx = rng.choice(
                np.arange(msk.size)[msk], 
                min(msk.sum(), n_sampled_cells_per_celltype), 
                replace=False)
        
        elif sampling_scheme == "double-replacement":
            sample_idx = rng.choice(
                np.arange(msk.size)[msk], 
                msk.sum(), 
                replace=True)
            sample_idx = rng.choice(
                sample_idx, 
                n_sampled_cells_per_celltype, 
                replace=True)
        
        else:
            raise ValueError(f"Unknown sampling scheme: {sampling_scheme}")

        idx[subgroup_id] = sample_idx
            
    return idx


def load_marker_info(
        cytof=None,
        marker_file="data/raw/singlecell/markers.xlsx"):

    markers = pd.read_excel(marker_file)
    markers_map = { a:b for a,b in zip(markers["Code"],markers["Comment"]) if not isinstance(a, float) and not isinstance(b, float) }
    if cytof is not None:
        columns_phenotype = [c for c in cytof.columns if c in markers_map and markers_map[c] == "phenotype"]
        columns_function = [c for c in cytof.columns if c in markers_map and markers_map[c] == "function" ]
    else:
        columns_phenotype = None
        columns_function = None

    return markers, columns_phenotype, columns_function


CellTypeFilter = collections.namedtuple('CellTypeFilter', ['name', 'source', 'remove'])


CELL_TYPE_FITLERS = [
    CellTypeFilter(name="cMCs_clean",    source=["cMCs"],   remove=["pDCs", "mDCs", "M-MDSC"]),
    CellTypeFilter(name="intMCs_noMDSC", source=["intMCs"], remove=["M-MDSC"]),
    CellTypeFilter(name="ncMCs_noMDSC",  source=["ncMCs"],  remove=["M-MDSC"]),
    CellTypeFilter(name="mDCs_noMDSC",   source=["mDCs"],   remove=["M-MDSC"]),
    
    CellTypeFilter(name="CD25-CD8+Tcells_mem",   source=["CD8+Tcells_mem"],   remove=["CD25+CD8+Tcells_mem"]),
    CellTypeFilter(name="CD25-CD8+Tcells_naive", source=["CD8+Tcells_naive"], remove=["CD25+CD8+Tcells_naive"]),
    
    CellTypeFilter(name="CD25-CD4+Tcells_mem",   source=["CD4+Tcells_mem"],   remove=["CD25+CD4+Tcells_mem"]),
    CellTypeFilter(name="CD25-CD4+Tcells_naive", source=["CD4+Tcells_naive"], remove=["CD25+CD4+Tcells_naive"]),
    
    CellTypeFilter(name="CD25+CD4+Tcells_naive_noTregs", source=["CD25+CD4+Tcells_naive"], remove=["CD45RA+Tregs"]),
    CellTypeFilter(name="CD25+CD4+Tcells_mem_noTregs", source=["CD25+CD4+Tcells_mem"], remove=["CD45RA-Tregs"]),
    
]


CELL_TYPE_ORDERS = {
    "original": np.array([
        'CD56+CD16-NKcells',
        'CD16+CD56-NKcells',      # didn't see those in Figure S1 (Immune clock paper)
        
        'pDCs',
        'mDCs',
        'M-MDSC',
        
        'cMCs',
        'intMCs',
        'ncMCs',
        
    #     'CD235-CD61-',            # leukocytes
    #     'CD45+CD66-',             # mononuclear cells
    #     'CD66+CD45-',             # granulocytes
        'Bcells',
        
        'CD8+Tcells',
        'CD8+Tcells_mem',
        'CD8+Tcells_naive',
        
        'CD25+CD8+Tcells_mem',
        'CD25+CD8+Tcells_naive',
        
        'CD4+Tcells',
        'CD4+Tcells_mem',
        'CD4+Tcells_naive',
        'Tbet+CD4+Tcells_mem',
        
        'CD25+CD4+Tcells_mem',    # didn't see those in Figure S1 (Immune clock paper)
        'CD25+CD4+Tcells_naive',  # didn't see those in Figure S1 (Immune clock paper)
        
        'CD45RA+Tregs',
        'CD45RA-Tregs',
        
        'TCRgd+Tcells',           #gamma delta T-cells
    ]),
    
    # disentangled / filtering approach (20)
    "filter": np.array([
        'CD56+CD16-NKcells',
        'CD16+CD56-NKcells',      # didn't see those in Figure S1 (Immune clock paper)
        
    #     'cMCs',
    #     'cMCs_noMDSC',
        'cMCs_clean',
    #     'intMCs',
        'intMCs_noMDSC',
    #     'ncMCs'.
        'ncMCs_noMDSC',
        
        'pDCs',
    #     'mDCs',
        'mDCs_noMDSC',
        'M-MDSC',
        
    #     'CD235-CD61-',            # leukocytes
    #     'CD45+CD66-',             # mononuclear cells
    #     'CD66+CD45-',             # granulocytes
        'Bcells',
        
    #     'CD8+Tcells',
    #     'CD8+Tcells_mem',
    #     'CD8+Tcells_naive',
        'CD25-CD8+Tcells_mem',
        'CD25-CD8+Tcells_naive',
        
        'CD25+CD8+Tcells_mem',
        'CD25+CD8+Tcells_naive',
        
    #     'CD4+Tcells',
    #     'CD4+Tcells_mem',
    #     'CD4+Tcells_naive',
        'CD25-CD4+Tcells_mem',    # didn't see those in Figure S1 (Immune clock paper)
        'CD25-CD4+Tcells_naive',  # didn't see those in Figure S1 (Immune clock paper)

    #     'CD25+CD4+Tcells_mem',    # didn't see those in Figure S1 (Immune clock paper)
    #     'CD25+CD4+Tcells_naive',  # didn't see those in Figure S1 (Immune clock paper)
        'CD25+CD4+Tcells_mem_noTregs',    # didn't see those in Figure S1 (Immune clock paper)
        'CD25+CD4+Tcells_naive_noTregs',  # didn't see those in Figure S1 (Immune clock paper)
        
    #     'Tbet+CD4+Tcells_mem',
        
        'CD45RA+Tregs',
        'CD45RA-Tregs',
        
        'TCRgd+Tcells',           #gamma delta T-cells
    ]),

    # 'axing' (11)
    "removal": np.array([
        'CD56+CD16-NKcells',
        'CD16+CD56-NKcells',      # didn't see those in Figure S1 (Immune clock paper)
        
    #     'pDCs',
    #     'mDCs',
    #     'M-MDSC',
        
        'cMCs',
        'intMCs',
        'ncMCs',
        
    #     'CD235-CD61-',            # leukocytes
    #     'CD45+CD66-',             # mononuclear cells
    #     'CD66+CD45-',             # granulocytes
        'Bcells',
        
    #     'CD8+Tcells',
        'CD8+Tcells_mem',
        'CD8+Tcells_naive',
        
    #     'CD25+CD8+Tcells_mem',
    #     'CD25+CD8+Tcells_naive',
        
    #     'CD4+Tcells',
        'CD4+Tcells_mem',
        'CD4+Tcells_naive',
        
    #     'CD25+CD4+Tcells_mem',    # didn't see those in Figure S1 (Immune clock paper)
    #     'CD25+CD4+Tcells_naive',  # didn't see those in Figure S1 (Immune clock paper)
        
    #     'Tbet+CD4+Tcells_mem',
        
    #     'CD45RA+Tregs',
    #     'CD45RA-Tregs',
        
        'TCRgd+Tcells',           #gamma delta T-cells
    ])
}


if __name__ == "__main__":
    prepare_singlecell_data(verbose=1)
