from coralsarticle.utils import execute
import pathlib
import yaml
import click
import re


@click.command()
@click.option("-c", "--config_file", default="config/test.yml", help="Config file")
@click.option("-o", "--overwrite", is_flag=True, help="Overwrite if experiment exists.")
@click.option("-e", "--conda_env", default="benchmark", help="Environment used to execute benchmarks.")
def run(config_file, overwrite, conda_env):

    # general settings
    # conda_env = "benchmark"
    # conda_env = "benchmark_py3.9.1_fixed"

    # benchmark files
    benchmark_dir = pathlib.Path("src/coralsarticle/benchmark/algorithms")
    benchmark_julia =   benchmark_dir / "julia/benchmark.jl"
    benchmark_r =       benchmark_dir / "r/benchmark.R"
    benchmark_python =  benchmark_dir / "python/benchmark.py"

    # load config
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    prefix = config["context"].get("prefix", "default")
    n_threads = config["context"].get("n_threads", 1)
    n_repeat = config["context"].get("n_repeat", 1)
    data_regex = config["context"].get("data", "synthetic_mn_m-50_n-5000_postprocessed")
    k_ratio = config["context"].get("k_ratio", 0.001)
    threshold = config["context"].get("threshold", 0.9)

    # load available data
    if data_regex.startswith("volatile_synthetic"):
        print("Creating new dataset ...")
        m = int(re.search("m-(.*?)_", data_regex).group(1))
        n = int(re.search("n-(.*?)_", data_regex).group(1))
        from coralsarticle.data.utils import load_data
        data_regex, _ = load_data(
            dataset="synthetic_mn", 
            m=m,
            n=n,
            data_dir="./data",
            dataset_name_prefix="volatile_")
        print("Created dataset:", data_regex)

    data = []
    print("Available data:")
    for p in pathlib.Path('./data/benchmark').iterdir():
        if p.is_file():
            f = p.with_suffix('').name
            selected = "x" if re.match(data_regex, f) else " "
            print(f"* [{selected}]", f)
            data.append(f)

    print()
    print("Running experiments:")
    for d in data:
        for exp in config["experiments"]:

            if re.match(data_regex, d):

                print()
                print("############################################################")
                print(f"Context:    {config['context']}")
                print(f"Experiment: {exp}")
                print(f"Overwrite:  {overwrite}")
                print("############################################################")

                execution_context = None
                if exp["lang"] == "python":
                    execution_context = f"python {benchmark_python}"
                    if "python" in config["context"]:
                        if "memory_backend" in config["context"]["python"]:
                            execution_context += f" --memory_backend {config['context']['python']['memory_backend']}"
                elif exp["lang"] == "julia":
                    execution_context = f"julia {benchmark_julia}"
                elif exp["lang"] == "r":
                    execution_context = f"Rscript {benchmark_r}"
                else:
                    raise ValueError(f"No execution context found for: {exp})")

                # overwrite threads if given
                if "n_threads" in exp:
                    n_threads_local = exp["n_threads"]
                else:
                    n_threads_local = n_threads

                # overwrite k_ratio if given
                if "k_ratio" in exp:
                    k_ratio_local = exp["k_ratio"]
                else:
                    k_ratio_local = k_ratio

                # TODO: make overwriting global values a bit more pretty

                # overwrite boolean must be lower case for Julia 
                overwrite_exec = overwrite
                if exp["lang"] == "julia":
                    overwrite_exec = str(overwrite).lower()

                execute(
                    execution_context +
                    f" --prefix {prefix}" +
                    f" --exp {exp['algorithm']}" + 
                    f" --data {d}" + 
                    f" --k_ratio {k_ratio_local}" + 
                    f" --threshold {threshold}" + 
                    f" --n_repeat {n_repeat}" +
                    f" --n_threads {n_threads_local}" +
                    f" --overwrite {overwrite_exec}", 
                    conda_env=conda_env)

if __name__ == "__main__":
    run()