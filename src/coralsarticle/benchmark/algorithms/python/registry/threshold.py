import collections

import corals.correlation.threshold._deprecated.original as deprecated


def load_experiments(X, **kwargs):

    threshold = kwargs["threshold"]
    n_jobs_range = [1,2,4,8,16,32,64]

    return collections.OrderedDict([

        # thresholds
        ("threshold_matrix", (
            lambda: deprecated.cor_threshold_matrix_symmetrical, 
            [X], 
            dict(threshold=threshold))),
        ("threshold_balltree_combined_tree", (
            lambda: deprecated.cor_threshold_balltree_combined_tree, 
            [X], 
            dict(threshold=threshold))),
        ("threshold_balltree_combined_query", (
            lambda: deprecated.cor_threshold_balltree_combined_query, 
            [X], 
            dict(threshold=threshold))),
        ("threshold_balltree_twice", (
            lambda: deprecated.cor_threshold_balltree_twice, 
            [X], 
            dict(threshold=threshold))),
            
        *[(f"threshold_balltree_combined_query_parallel_{n}", (
            lambda: deprecated.cor_threshold_balltree_combined_query_parallel, 
            [X], 
            dict(threshold=threshold, n_jobs=n)))
            for n in n_jobs_range],

    ])