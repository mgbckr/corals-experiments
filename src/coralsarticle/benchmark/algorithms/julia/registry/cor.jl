function load_experiments_cor(X; kwargs...)
    return Dict([
        ("cor_cor", (
            cor,
            [X],
            Dict())),
        ("cor_asymmetrical", (
            Corals.cor_asymmetrical,
            [X],
            Dict())),
        ("cor_symmetrical", (
            Corals.cor_symmetrical,
            [X],
            Dict())),
        ("cor_symmetrical_nocopy2", (
            Corals.cor_symmetrical,
            [X],
            Dict(:avoid_copy => true))),
    ])
end