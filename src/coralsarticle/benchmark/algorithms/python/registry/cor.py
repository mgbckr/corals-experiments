import collections

import corals.correlation.full.baselines as baselines
import corals.correlation.full.matmul as matmul


def load_experiments(X, **kwargs):

    return collections.OrderedDict([
        ("cor_corrcoef", (
            lambda: baselines.full_corrcoef, 
            [X], 
            {})),
        ("cor_matrix_symmetrical", (
            lambda: matmul.full_matmul_symmetrical, 
            [X], 
            {})),
        ("cor_matrix_symmetrical_nocopy", (
            lambda: matmul.full_matmul_symmetrical, 
            [X],
            dict(avoid_copy=True))),
        ("cor_matrix_asymmetrical", (
            lambda: matmul.full_matmul_asymmetrical, 
            [X], 
            {})),
    ])
