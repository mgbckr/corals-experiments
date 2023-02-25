import click
from numpy.core.fromnumeric import sort


@click.command()
@click.option("--data", default="synthetic_mn_m-50_n-20000")
@click.option("--k_ratio", default=0.01)
@click.option("--max_approx", default=10)
@click.option("--method", default="tree")
@click.option("--overwrite", default=False)
@click.option("--n_threads", default=4)
def main(
        k_ratio, 
        data, 
        overwrite,
        max_approx,
        n_threads,
        method):

    import coralsarticle.utils
    coralsarticle.utils.set_threads_for_external_libraries(n_threads=n_threads)

    import numpy as np
    import scipy.sparse
    import sklearn.metrics
    import collections
    import pathlib
    import h5py
    import datetime

    import coralsarticle.data.utils
    import corals.correlation.topk
    import corals.correlation.fast

    # data
    X = coralsarticle.data.utils.load_h5(f"data/benchmark/{data}.h5").values

    # k
    k = int(X.shape[1] * X.shape[1] * k_ratio)
    k_name = f"{k_ratio * 100:.02f}"

    exp_name = f"acccuracy___data-{data}___topk-{k_name}percent___method-{method}"
    file = pathlib.Path(f"_out/benchmark") / f"{exp_name}.h5"
    print(exp_name)
    print(f"* Data: {X.shape}")

    # stop if experiment already exists
    if file.exists():
        if overwrite:
            print("* OVERWRITE: File exists, but overwrite requested")
            file.unlink()
        else:
            print("* SKIPPING: Experiment already exists")
            return

    #%%
    # reference
    print("* Calculate reference topk")
    cor_topk_ref, idx_topk_ref = corals.correlation.topk.topk_matrix(X, k=k)
    cor_topk_ref_matrix1 = scipy.sparse.coo_matrix((cor_topk_ref, idx_topk_ref))
    values1 = cor_topk_ref_matrix1.toarray()[np.tril_indices(n=X.shape[1], k=-1)]

    #%%
    approximation_factors = np.arange(1, max_approx + 1)
    metrics = collections.OrderedDict()
    for approximation_factor in approximation_factors:
        print()
        print(f"* Approximation factor: {approximation_factor}")
        print(f"* Start time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"  * calculate topk")
        if method == "tree":
            cor2, idx2 = corals.correlation.topk.topk_balltree_combined_tree_parallel(
                X, k=k, approximation_factor=approximation_factor, n_jobs=n_threads)
        else:
            raise ValueError(f"Unknown method: {method}")


        print("  * prepare data")
        m2 = scipy.sparse.coo_matrix((cor2, idx2))
        v2 = m2.toarray()[np.tril_indices(n=X.shape[1], k=-1)]

        print("  * metrics")
        
        print("    * accuracy:  ", end="")
        a = sklearn.metrics.accuracy_score(values1 != 0, v2 != 0)
        metrics.setdefault("accuracy", []).append(a)
        print(f"{a:.02f}")

        print("    * precision: ", end="")
        p = sklearn.metrics.precision_score(values1 != 0, v2 != 0)
        metrics.setdefault("precision", []).append(p)
        print(f"{p:.02f}")

        print("    * recall:    ", end="")
        r = sklearn.metrics.recall_score(values1 != 0, v2 != 0)
        metrics.setdefault("recall", []).append(r)
        print(f"{r:.02f}")

        print("    * f1:        ", end="")
        f1 = sklearn.metrics.f1_score(values1 != 0, v2 != 0)
        metrics.setdefault("f1", []).append(f1)
        print(f"{f1:.02f}")

    
    # write results
    print("* Write results")
    file.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(file, "a") as f:
        
        f[f"approximation_factors"] =  approximation_factors

        for key, value in metrics.items():
            f[f"metrics/{key}"] =  value


if __name__ == "__main__":
    main()