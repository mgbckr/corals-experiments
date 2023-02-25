function load_experiments_topk(X; kwargs...)

    k = values(kwargs).k

    return Dict([
        ("topk_matrix", (
            Corals.topk_matrix,
            [X],
            Dict(:k => k))),
        ("topk_matrix_fsort", (
            Corals.topk_matrix,
            [X],
            Dict(:k => k, :fsort => true))),
        ("topk_balltree_mlpack_twice", (
            Corals.topk_balltree_mlpack_twice,
            [X],
            Dict(:k => k))),
        ("topk_balltree_mlpack_combined_query", (
            Corals.topk_balltree_mlpack_combined_query,
            [X],
            Dict(:k => k))),
        ("topk_balltree_nn_combined_query", (
            Corals.topk_balltree_nn_combined_query,
            [X],
            Dict(:k => k))),
        ("topk_balltree_nn_combined_query_parallel", (
            Corals.topk_balltree_nn_combined_query_parallel,
            [X],
            Dict(:k => k))),
        ("topk_balltree_mlpack_combined_tree", (
            Corals.topk_balltree_mlpack_combined_tree,
            [X],
            Dict(:k => k))),
        ("topk_balltree_nn_combined_tree", (
            Corals.topk_balltree_nn_combined_tree,
            [X],
            Dict(:k => k))),
        ("topk_balltree_nn_combined_tree_parallel", (
            Corals.topk_balltree_nn_combined_tree_parallel,
            [X],
            Dict(:k => k)))
    ])
end