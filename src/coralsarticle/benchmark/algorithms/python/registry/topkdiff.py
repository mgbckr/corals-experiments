import collections

import corals.correlation.topkdiff.original as original


def load_experiments(X, **kwargs):

    k = kwargs["k"]
    n_jobs_range = [1,2,4,8,16,32,64]

    return collections.OrderedDict([
        # diff

        ("topkdiff_matrix", (
            lambda: original.topkdiff_matrix,
            [X[:X.shape[0] // 2,:], X[X.shape[0] // 2:,:]], 
            dict(k=k))),
        ("topkdiff_matrix_one", (
            lambda: original.topkdiff_matrix_one, 
            [X[:X.shape[0] // 2,:], X[X.shape[0] // 2:,:]], 
            dict(k=k))),

        # ("topkdiff_balltree_combined_tree_parallel_1", (
        #     original.topkdiff_balltree_combined_tree_parallel, 
        #     [X[:X.shape[0] // 2,:], X[X.shape[0] // 2:,:]], 
        #     dict(k=k, n_jobs=1))),

        *[(f"topkdiff_balltree_combined_tree_parallel_{n}", (
            lambda: original.topkdiff_balltree_combined_tree_parallel, 
            [X[:X.shape[0] // 2,:], X[X.shape[0] // 2:,:]], 
            dict(k=k, n_jobs=n)))
            for n in n_jobs_range],
            
        ("topkdiff_balltree_combined_tree_sym_parallel_64", (
            lambda: original.topkdiff_balltree_combined_tree_parallel, 
            [X[:X.shape[0] // 2,:], X[X.shape[0] // 2:,:]], 
            dict(k=k, symmetrize=True, n_jobs=64)))
    ])