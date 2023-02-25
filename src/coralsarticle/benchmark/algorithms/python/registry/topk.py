import collections
import functools


def load_experiments(X, **kwargs):

    k = kwargs["k"]
    threshold = kwargs["threshold"]
    n_jobs_range = [1, 2, 4, 8, 16, 32, 64]

    experiments = collections.OrderedDict()

    def init_original(name):
        import corals.correlation.topk._deprecated.original as original
        return original.__dict__[name]

    experiments["topk_corrcoef"] = (
        functools.partial(init_original, "topk_corcoeff"), 
        [X], dict(k=k))
    experiments["topk_matrix"] = (
        functools.partial(init_original, "topk_matrix"), 
        [X], dict(k=k))
    experiments["topk_partition"] = (
        functools.partial(init_original, "topk_matrix"), 
        [X], dict(k=k, sorting="partition"))
    experiments["topk_balltree_twice"] = (
        functools.partial(init_original, "topk_balltree_twice"), 
        [X], dict(k=k))
    experiments["topk_balltree_combined_tree"] = (
        functools.partial(init_original, "topk_balltree_combined_tree"), 
        [X], dict(k=k))
    experiments["topk_balltree_combined_query"] = (
        functools.partial(init_original, "topk_balltree_combined_query"), 
        [X], dict(k=k))


    # Does not seem to make a memory difference, so drop it.
    experiments["topk_balltree_combined_tree_no-dual"] = (
            functools.partial(init_original, "topk_balltree_combined_tree"), 
            [X], 
            dict(k=k, dualtree=False))
    experiments["topk_balltree_combined_query_no-dual"] = (
            functools.partial(init_original, "topk_balltree_combined_query"), 
            [X], 
            dict(k=k, dualtree=False))
    experiments["topk_balltree_twice_no-dual"] = (
            functools.partial(init_original, "topk_balltree_twice"),
            [X], 
            dict(k=k, dualtree=False))
        
    # parallel query
    for n in n_jobs_range:
        experiments[f"topk_balltree_combined_query_parallel_{n}"] = (
            functools.partial(init_original, "topk_balltree_combined_query_parallel"), 
            [X], 
            dict(k=k, n_jobs=n))

    # parallel tree
    for n in n_jobs_range:
        experiments[f"topk_balltree_combined_tree_parallel_{n}"] = (
            functools.partial(init_original, "topk_balltree_combined_tree_parallel"), 
            [X], 
            dict(k=k, n_jobs=n))
        
    # tree - optimized
    experiments["topk_balltree_combined_tree_optimized"] = (
        functools.partial(init_original, "topk_balltree_combined_tree_parallel_optimized"),
        [X], 
        dict(k=k, n_jobs=1))

    # tree - optimized - parallel
    for n in n_jobs_range:
        experiments[f"topk_balltree_combined_tree_optimized_parallel_{n}"] = (
            functools.partial(init_original, "topk_balltree_combined_tree_parallel_optimized"),
            [X], 
            dict(
                k=k, 
                query_sort=True, 
                n_jobs=n))

    for n in n_jobs_range:
        experiments[f"topk_balltree_combined_tree_optimized_partition_parallel_{n}"] = (
            functools.partial(init_original, "topk_balltree_combined_tree_parallel_optimized"), 
            [X], 
            dict(
                k=k, 
                query_sort=True, 
                argtopk_method="argpartition", 
                n_jobs=n))

    for n in n_jobs_range:
        experiments[f"topk_balltree_combined_tree_optimized_direct_parallel_{n}"] = (
            functools.partial(init_original, "topk_balltree_combined_tree_parallel_optimized"),
            [X], 
            dict(
                k=k, 
                query_sort=True, 
                n_jobs=n, 
                n_jobs_transfer_mode="direct"))

    ###
    # new comparisons based on batch paradigm
    ###

    def init_balltree():
        from corals.correlation.topk.batched.base import topk_batched_generic
        from corals.correlation.topk.batched.nearest_neighbors_balltree import BalltreeTopkMapReduce
        return functools.partial(topk_batched_generic, mapreduce=BalltreeTopkMapReduce())

    for n_jobs in n_jobs_range:

        experiments[f"topk_batch_balltree_parallel_{n_jobs}"] = (
            init_balltree, 
            [X],
            dict(
                threshold=None,
                k=k,
                #
                approximation_factor=10,
                n_batches=n_jobs,
                n_jobs=n_jobs,
            ))

    for n_jobs in n_jobs_range:

        def init():
            from corals.correlation.topk.batched.base import topk_batched_generic
            from corals.correlation.topk.batched.nearest_neighbors_ann_ngt import NgtTopkMapReduce
            return functools.partial(
                topk_batched_generic, 
                mapreduce=NgtTopkMapReduce(
                    n_threads_build_index=n_jobs),
            )
        
        experiments[f"topk_batch_ngt_parallel_{n_jobs}"] = (
            init, 
            [X],
            dict(
                threshold=None,
                k=k,
                #
                approximation_factor=10,
                n_batches=n_jobs,
                n_jobs=n_jobs))

    for n_jobs in n_jobs_range:

        def init():
            from corals.correlation.topk.batched.base import topk_batched_generic
            from corals.correlation.topk.batched.nearest_neighbors_ann_nmslib import NmslibTopkMapReduce
            return functools.partial(
                topk_batched_generic, 
                mapreduce=NmslibTopkMapReduce(
                    # n_threads_build_index=n_jobs
                )
            )

        experiments[f"topk_batch_nmslib_parallel_{n_jobs}"] = (
            init, 
            [X],
            dict(
                threshold=None,
                k=k,
                #
                approximation_factor=10,
                n_batches=n_jobs,
                n_jobs=n_jobs,
                # preferred_backend="threads",  # does not really work for nmslib it seems
            ))

    def init_matmul():
        from corals.correlation.topk.batched.base import topk_batched_generic
        from corals.correlation.topk.batched.matmul import MatmulTopkMapReduce
        return functools.partial(
            topk_batched_generic, 
            mapreduce=MatmulTopkMapReduce()
        )

    for n_jobs in n_jobs_range:

        experiments[f"topk_batch_matmul_parallel_{n_jobs}"] = (
            init_matmul, 
            [X],
            dict(
                threshold=None,
                k=k,
                #
                approximation_factor=10,
                n_batches=n_jobs,
                n_jobs=n_jobs
            ))

    for n_jobs in n_jobs_range:

        experiments[f"topk_batch_matmul_threads_parallel_{n_jobs}"] = (
            init_matmul, 
            [X],
            dict(
                threshold=None,
                k=k,
                #
                approximation_factor=10,
                n_batches=n_jobs,
                n_jobs=n_jobs,
                preferred_backend="threads",
            ))
    
    return experiments
