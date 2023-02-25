# requires:
# * utils.jl 
# * fast.jl

using Statistics
using LinearAlgebra
using BenchmarkTools
using Printf
using HDF5
using ArgParse
using Dates
using Statistics


include("./exps.jl")


function parse_commandline()
    s = ArgParseSettings()

    @add_arg_table s begin
        "--exp"
            arg_type = String
            default = "topk_matrix"
        "--data"
            arg_type = String
            default = "synthetic_mn_m-50_n-20000"
        "--n_repeat"
            arg_type = Int64
            default = 10
        "--k_ratio"
            arg_type = Float64
            default = 0.01
        "--threshold"
            arg_type = Float64
            default = 0.75
        "--n_threads"
            arg_type = Int64
            default = 1
        "--overwrite"
            arg_type = Bool
            default = false
        "--skip"
            arg_type = String
            default = ""
        "--prefix"
            arg_type = String
            default = "default"
    end

    return parse_args(s)
end


function main()

    # parse command line arguments
    parsed_args = parse_commandline()

    # set number of threads
    n_threads = parsed_args["n_threads"]
    BLAS.set_num_threads(n_threads)

    # repeat
    n_repeat = parsed_args["n_repeat"]

    # k
    k_ratio = parsed_args["k_ratio"]
    k_name = "$(@sprintf("%.02f", k_ratio * 100))percent"

    # threshold
    threshold = parsed_args["threshold"]

    # set prefix
    prefix = parsed_args["prefix"]

    # derive experiment name
    experiment_name = parsed_args["exp"]
    experiment_name *= if (n_threads == 1) "" else "_nthreads-$(n_threads)" end

    # derive algorithm context
    if Base.startswith(experiment_name, "cor")
        context = "fast"
    elseif Base.startswith(experiment_name, "topk")
        context = "topk-$(k_name)"
    elseif Base.startswith(experiment_name, "threshold")
        context = "threshold-$(@sprintf("%.02f", threshold))"
    else
        throw(ArgumentError("No matching context found for experiment: $(experiment_name)"))
    end

    # file name to store results
    data = parsed_args["data"]
    file = "_out/benchmark/benchmark___prefix-$(prefix)___context-$(context)___lang-julia___data-$(data)___algorithm-$(experiment_name)___repeat-$(n_repeat).h5"

    println()
    println("Experiment:   " * experiment_name)
    println("* File:       " * file)

    # skip if experiment already exists
    skip = false
    h5open(file, "cw") do f
        if !parsed_args["overwrite"] && haskey(read(f), experiment_name)
            println("* SKIPPED: Experiment already exists")
            skip = true
        end
    end
    if sum(findall(experiment_name .== Base.split(parsed_args["skip"], ","))) > 0  # WTF? Can this be done easier?
        println("* SKIPPED: Skip requested ($(parsed_args["skip"]))")
        skip = true
    end
    if skip
        return
    end

    # load data
    X = nothing
    h5open("data/benchmark/$(data).h5", "r") do f
        X = transpose(read(f["data"]))
    end

    # derive k
    k = trunc(Int, size(X, 2)^2 * k_ratio)

    println("* Threads     $(n_threads)")
    println("* Data        $(size(X))")
    println("* Threshold:  $threshold")
    println("* K ratio:    $k_ratio")
    println("* K:          $k")

    # experiments
    include("./exps.jl")
    experiments = load_experiments(X; k=k, threshold=threshold)
    f, args, kwargs = experiments[parsed_args["exp"]]

    # run experiment
    println("Run experiment:")
    results = Dict()
    for i = 1:n_repeat
        println("* Round $i ($(Dates.format(now(), "YYYY-mm-dd HH:MM:SS"))): ")

        if haskey(results, experiment_name)
            exp_results = results[experiment_name]
        else
            exp_results = Dict(
                :memory => Vector{Float64}(), 
                :runtime => Vector{Float64}())
            results[experiment_name] = exp_results
        end
        b = @timed f(args...; kwargs...)
        mem = b.bytes / 1024 / 1024  # to Mb
        run = b.time
        append!(exp_results[:memory], mem)
        append!(exp_results[:runtime], run)

        println(@sprintf("  %s (%.02f Mb)", hmss(run), mem))
    end

    # write results
    h5open(file, "cw") do f
        for (key, value) in results
            if haskey(read(f), key)
                f["$key/memory"][:] =  value[:memory]
                f["$key/runtime"][:] =  value[:runtime]
            else
                f["$key/memory"] =  value[:memory]
                f["$key/runtime"] =  value[:runtime]
            end
        end
    end

end

function hmss(dt)
    (h,r) = divrem(dt,60*60)
    (m,r) = divrem(r, 60)
    #(s,r) = divrem(r, 60)
    string(Int(h),":", Int(m),":", @sprintf("%.04f", r))
end

main()


