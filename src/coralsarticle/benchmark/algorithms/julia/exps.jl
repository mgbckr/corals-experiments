using Corals
include("./registry/cor.jl")
include("./registry/topk.jl")

function load_experiments(X; kwargs...)

    experiments  = Dict()

    merge!(experiments, load_experiments_cor(X; kwargs...))
    merge!(experiments, load_experiments_topk(X; kwargs...))

    return experiments
end