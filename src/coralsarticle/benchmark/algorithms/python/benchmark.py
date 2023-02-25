import click

@click.command()
@click.option("--prefix", default="default", help="Prefix")
@click.option("--exp", default="topk_corrcoef", help="Experiment")
@click.option("--n_repeat", default=10)
@click.option("--data", default="synthetic_mn_m-50_n-20000")
@click.option("--k_ratio", default=0.01)
@click.option("--threshold", default=0.75)
@click.option("--n_threads", default=1)
@click.option("--overwrite", default=False, type=bool)
@click.option("--memory_backend", default="psutil")
def run(prefix, exp, n_repeat, data, k_ratio, threshold, n_threads, overwrite, memory_backend):

    # set threads
    import corals.threads
    corals.threads.set_threads_for_external_libraries(n_threads=n_threads)
    threads_context = "" if n_threads == 1 else f"_nthreads-{n_threads}"

    import pathlib
    import time
    import datetime
    import collections
    import h5py
    import gc

    from memory_profiler import memory_usage

    import coralsarticle.data.utils

    # benchmark parameters
    memory_usage_kwargs = dict(
        # doesn't make a difference either it seems
        # default value (0.1) seems fine
        interval=0.1,
        # we are only interested in max imum memory consumption over time
        max_usage=True,  
        # combines memory usage of parent and children processes
        # NOTE: This measures RSS and might overestimate memory usage! 
        #       There is an updated version of `memory_profiler` coming up 
        #       that can measure PSS and USS which might be more accurate 
        include_children=True,
        # also keep track of children's memory consumption separately ... we don't really use this
        multiprocess=True,
        # default backend measures RSS which may overestimate memory usage in parallel case
        backend=memory_backend
    )

    # k
    k_name = f"{k_ratio * 100:.02f}percent"
    if k_ratio * 100 < 0.01:
        k_name = f"{k_ratio * 100:.06f}percent"

    # experiment name
    experiment_name = exp
    if experiment_name.startswith("cor"):
        context = "fast"
    elif experiment_name.startswith("topk"):
        context = f"topk-{k_name}"
    elif experiment_name.startswith("topkdiff"):
        context = f"topkdiff-{k_name}"
    elif experiment_name.startswith("threshold"):
        context = f"threshold-{threshold:.02f}"
        if threshold < 0.01:
            context = f"threshold-{threshold:.06f}"
    else:
        raise ValueError(f"No matching context found for experiment: {experiment_name}")

    experiment_name += threads_context
    file = pathlib.Path(f"_out/benchmark/benchmark___prefix-{prefix}___context-{context}___lang-python___data-{data}___algorithm-{experiment_name}___repeat-{n_repeat}___memory_backend-{memory_backend}.h5")
    file.parent.mkdir(parents=True, exist_ok=True)

    # experiment
    print()
    print(f"Experiment:  {experiment_name}")
    print(f"* File:      {file}")
    print(f"* Threads:   {n_threads}")
    print(f"* Backend:   {memory_backend}")
    print(f"* Overwrite: {overwrite}")

    # stop if experiment already exists
    with h5py.File(file, "a") as f:
        if not overwrite and experiment_name in f:
            print("SKIPPING: Experiment already exists")
            return
            
    # load and prepare dataset
    X = coralsarticle.data.utils.load_h5(f"data/benchmark/{data}.h5").values
    if "topkdiff" in exp:
        print(f"* Prepare diff experiment: {X.shape}")
        X = corals.data.utils.preprocess_diff(X)
    
    print(f"* Data:      {X.shape}")

    # drive k
    k = int(X.shape[1]**2 * k_ratio)  # top 1%
    print(f"* K ratio:   {k_ratio}")
    print(f"* K:         {k}")

    # threshold
    print(f"* Threshold: {threshold}")
    
    # experiments
    from exps import load_experiments
    experiments = load_experiments(X, k=k, threshold=threshold)
    exp_init_func, exp_args, exp_kwargs = experiments[exp]
    exp_func = exp_init_func()

    # run rounds
    print("Running experiments")
    results = collections.OrderedDict()
    timestamp = time.time()
    for i in range(n_repeat):

        print(f"* Round {i} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}): ")

        exp_results = results.setdefault(experiment_name, {"memory":[], "runtime":[]})

        # NOTE: runtime may be slower due to memory monitoring
        gc.collect()
        start_time = time.time()
        if memory_backend == "none":
            exp_func(*exp_args, **exp_kwargs)
            mem = -1
        else:
            mem = memory_usage(proc=(exp_func, exp_args, exp_kwargs), **memory_usage_kwargs)
        end_time = time.time()

        exp_results["memory"].append(mem)
        exp_results["runtime"].append(end_time - start_time)

        runtime = datetime.datetime.fromtimestamp(end_time) - datetime.datetime.fromtimestamp(start_time)
        print(f"  {str(runtime)} ({mem:.02f} Mb)")

    # write results
    print("Writing results")
    file.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(file, "a") as f:
        for key, value in results.items():
            if key not in f:
                f[f"{key}/memory"] =  value["memory"]
                f[f"{key}/runtime"] =  value["runtime"]
            else:
                f[f"{key}/memory"][...] =  value["memory"]
                f[f"{key}/runtime"][...] =  value["runtime"]

            f[f"{key}"].attrs["timestamp"] = timestamp
            f[f"{key}"].attrs["memory_backend"] = memory_backend


if __name__ == "__main__":
    run()
