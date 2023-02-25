import collections


def load_experiments(X, **kwargs):

    experiments = collections.OrderedDict()

    from registry.cor import load_experiments as load
    experiments.update(load(X, **kwargs))

    from registry.topk import load_experiments as load
    experiments.update(load(X, **kwargs))

    from registry.threshold import load_experiments as load
    experiments.update(load(X, **kwargs))

    from registry.topkdiff import load_experiments as load
    experiments.update(load(X, **kwargs))
    
    return experiments
