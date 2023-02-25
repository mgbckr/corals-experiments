import click


@click.command()
@click.option("--k_ratio", default=0.01)
@click.option("--data", default="synthetic_mn")
@click.option("--m", default=100)
@click.option("--n", default=1000)
@click.option("--n_ratio", default=10)
@click.option("--size", default=200000)
@click.option("--data_neg", default=False)
@click.option("--data_dropduplicates", default=False)
@click.option("--data_sample", default=-1.0)
@click.option("--overwrite", default=False)
@click.option("--max_approx", default=10)
@click.option("--n_threads", default=4)
@click.option("--method", default="tree")
@click.option("--spearman", default=False)
def main(
        k_ratio, 
        data, 
        m, 
        n, 
        n_ratio, 
        size, 
        data_neg, 
        data_dropduplicates, 
        overwrite,
        max_approx,
        data_sample,
        n_threads,
        method,
        spearman):

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
    import corals.correlation.topkdiff
    import corals.correlation.fast

    # data
    if data == "synthetic_mn":

        data_name, X1 = coralsarticle.data.utils.load_data(
            "synthetic_mn", m=m, n=n, return_name=True)
        data_name, X2 = coralsarticle.data.utils.load_data(
            "synthetic_mn", m=m, n=n, return_name=True)

    elif data == "synthetic_nratio":

        data_name, X1 = coralsarticle.data.utils.load_data(
            "synthetic_nratio", n_ratio=n_ratio, size=size, return_name=True)
        data_name, X2 = coralsarticle.data.utils.load_data(
            "synthetic_nratio", n_ratio=n_ratio, size=size, return_name=True)

    elif data == "pregnancy":

        data_name, d = coralsarticle.data.utils.load_data(
            data, 
            return_name=True, 
            prepare_data_negative=data_neg, 
            prepare_data_drop_duplicates=data_dropduplicates, 
            sample_size=None if data_sample < 0 else data_sample)

        X1 = d[-2*17:-1*17,:]
        X2 = d[-1*17:,:]

        msk1 = coralsarticle.data.utils.mask_min_nunique(X1, min_nunique=2)
        msk2 = coralsarticle.data.utils.mask_min_nunique(X2, min_nunique=2)
        msk = msk1 & msk2

        print("Drop columsn with only one value in either timepoint")
        print(X1.shape, X2.shape)

        X1 = X1[:, msk]
        X2 = X2[:, msk]

        print(X1.shape, X2.shape)

    else: 
        raise ValueError(f"Data type not supported: '{data}'")

    # k
    k = int(X1.shape[1] * X1.shape[1] * k_ratio)
    k_name = f"{k_ratio * 100:.02f}"

    exp_name = f"acccuracy___data-{data_name}___topkdiff-{k_name}percent___method-{method}___spearman-{spearman}"
    file = pathlib.Path(f"_out/benchmark") / f"{exp_name}.h5"
    print(exp_name)
    print(f"* Data: {X1.shape} / {X2.shape}")

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

    cor_topkdiff_ref, idx_topkdiff_ref = corals.correlation.topkdiff.topkdiff_matrix(X1, X2, k=k, spearman=spearman)
    
    cor_topk_ref_matrix1 = scipy.sparse.csr_matrix((cor_topkdiff_ref, idx_topkdiff_ref), shape=[X1.shape[1]] * 2)
    values1 = cor_topk_ref_matrix1.toarray()[np.tril_indices(n=X1.shape[1], k=-1)]

    #%%
    approximation_factors = np.arange(1, max_approx + 1)
    metrics = collections.OrderedDict()
    for approximation_factor in approximation_factors:
        print()
        print(f"* Approximation factor: {approximation_factor}")
        print(f"* Start time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"  * calculate topk")
        if method == "tree":
            cor2, idx2 = corals.correlation.topkdiff.topkdiff_balltree_combined_tree_parallel(
                X1, X2, k=k, n_jobs=n_threads, approximation_factor=approximation_factor, spearman=spearman)
        else:
            raise ValueError(f"Unknown method: {method}")

        print("  * prepare data")
        m2 = scipy.sparse.csr_matrix((cor2, idx2), shape=[X1.shape[1]] * 2)
        v2 = m2.toarray()[np.tril_indices(n=X1.shape[1], k=-1)]

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