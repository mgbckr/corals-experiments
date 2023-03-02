# Large scale correlation network analysis for unraveling the coordination of complex biological systems

## Description

Advanced measurement and data storage technologies have enabled high-dimensional profiling of complex biological systems. For this, modern multiomics studies regularly produce datasets with hundreds of thousands of measurements per sample enabling a new era of precision medicine. Correlation analysis is an important first step to gain deeper insights into the coordination and underlying processes of such complex systems. However, the construction of large correlation networks in modern high-dimensional datasets remains a major computational challenge due to rapidly growing runtime and memory requirements. We address this challenge by introducing, CorALS, an open-source framework for the construction and analysis of large-scale parametric as well as nonparametric correlation networks for high-dimensional biological data. It features off-the-shelf algorithms suitable for both personal and high-performance computers enabling workflows and downstream analysis approaches. We illustrate the broad scope and potential of CorALS by exploring perspectives on complex biological processes in large-scale multiomics and single cell studies.

**Note:** This repository provides the code to reproduce the results and analyses from the manuscript. The corresponding [Python package](https://pypi.org/project/corals/) is maintained in a [separate repository](https://github.com/mgbckr/corals-python).

## System Requirements

### Software

Generally, the provided code is executable on any machine that can run `Docker`. It has been run and tested on `Docker version 20.10.7, build f0df350`.

### Hardware

Any regular hardware that can run Docker should be able to run the code. However, several baseline experiments as well as some of the large-scale experiments require dedicated server hardware. We recommend a machine with at least 64 cores and 312Gb of memory to produce comparable results to the benchmarks reported in the manuscript.

## Reproducing Results

### Clone repositories

Clone this repository:

```bash
git clone git@github.com:mgbckr/corals-experiments.git
# git clone https://github.com/mgbckr/corals-experiments.git
```

Clone the different implementation repositories:

```bash
git clone git@github.com:mgbckr/corals-lib-python.git
git clone git@github.com:mgbckr/corals-lib-julia.git
git clone git@github.com:mgbckr/corals-lib-r.git
```

### Install Docker

Make sure Docker is installed and configured properly. For this refer to the [official Docker installation guide](https://docs.docker.com/get-docker/).

### Get and start the Docker container

**Runtime:** Building the Docker container can take an hour or longer. This is due to having to compile various R libraries.

In the following, we assume you are running on Linux to start the Docker container. Please adjust as necessary.

```bash
# change into the experiments repository
cd corals-experiments

# docker build . -t corals-benchmark:local
docker pull mgbckr/corals-benchmark:1.0.0

docker run -v "$(pwd):/workspace" \
  -v "$(pwd)/../corals-lib-julia:/opt/libraries/julia" \
  -v "$(pwd)/../corals-lib-python:/opt/libraries/python" \
  -v "$(pwd)/../corals-lib-r:/opt/libraries/r" \
  -it mgbckr/corals-benchmark:1.0.0

# Then, WITHIN the Docker container:
# TODO: Currently this has to be done every time we start the container.
#       It should be part of the `environment.yml` but doesn't work for some reason.
pip install git+https://github.com/pythonprofilers/memory_profiler.git@88f0aae4488328dc6d4f4750f48e35927dafb09b#egg=memory_profiler

# TODO: Currently this has to be done every time we start the container.
#       There should be a better way to set this up.
python setup.py develop
```

### Download and prepare data

**Runtime:** About 15-20  minutes

After starting the Docker container, please run the following commands from inside the Docker container.

```bash
# create data dir
mkdir -p data/raw
mkdir -p data/processed
```

#### Preeclampsia

The preeclampsia dataset is not publicly available and may be requested directly from the authors. As it is solely used for runtime and memory benchmarking purposes, the benchmarks will automatically generate a substitute.

#### Pregnancy

```bash
mkdir tmp
wget https://nalab.stanford.edu/wp-content/uploads/termpregnancymultiomics.zip -P tmp/
unzip tmp/termpregnancymultiomics.zip -d tmp/
mv tmp/termpregnancymultiomics/Data.Rda data/raw/pregnancy.rda
rm -r tmp
```

#### Cancer

```bash
mkdir -p data/raw/cancer
bash src/coralsarticle/data/process/cancer_download.sh
```

#### Single cell

```bash
pip install gdown

# NOTE: download sometimes cancels prematurely; run again if that happens 
fileId=1NKPC1zp_UOIqJovxHoAmXYmT9qGKS8EJ
fileName=data/processed/immuneclock_singlecell_unstim.h5
gdown $fileId -O $fileName
```

#### Prepare data

```bash
python src/coralsarticle/data/prepare.py
```

### Run benchmarking experiments

**Runtime:** The currently enabled experiments can already take several hours. Full experiments can run up to a week or more. See the main manuscript for runtimes of individual experiments. Experiments are repeated two to ten times depending on runtime. Generally, running on a larger machine is recommended (at least 64 cores and 312Gb of memory), since particularly the baseline methods need a lot of memory.

**Note:** Particularly long-running or resource-intensive experiments are uncommented or excluded. See files in `config` folder for more details and additional experiments to reproduce all results.

#### Main: Full correlation matrix

```bash
# default
python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_default.yml
# python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_default_cancer_small.yml
# python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_default_cancer_medium.yml
# python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_default_singlecell.yml

# parallel
python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_parallel.yml
# python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_parallel_cancer_small.yml
# python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_parallel_cancer_medium.yml
# python src/coralsarticle/benchmark/resources.py -c config/full/bench_full_parallel_singlecell.yml
```

#### Main: Top-k correlation network

```bash
# default
python src/coralsarticle/benchmark/resources.py -c config/topk/bench_topk_default.yml
# python src/coralsarticle/benchmark/resources.py -c config/topk/bench_topk_default_cancer_small.yml
# python src/coralsarticle/benchmark/resources.py -c config/topk/bench_topk_default_cancer_medium-large.yml
# python src/coralsarticle/benchmark/resources.py -c config/topk/bench_topk_default_singlecell.yml

# parallel
# python src/coralsarticle/benchmark/resources.py -c config/topk/bench_topk_parallel_memory.yml
# python src/coralsarticle/benchmark/resources.py -c config/topk/bench_topk_parallel_runtime.yml
```

#### Supplement: Top-k correlation network

```bash
# full - r comparison 
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_full_r-comparison.yml

### top-k tree variants
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_tree-variants.yml

### full - synthetic
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_full_synthetic.yml

### topk - synthetic
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_synthetic_features.yml
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_synthetic_samples.yml

### top-k parallel 
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_parallel_memory.yml
python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_parallel_runtime.yml

# top-k parallel - slow
# python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_parallel_memory_slow.yml
# python src/coralsarticle/benchmark/resources.py -c config/supplement/bench_topk_parallel_runtime_slow.yml
```

#### Supplement: Accuracy

**Runtime**: Several hours

```bash
# topk
# python src/coralsarticle/benchmark/accuracy_topk.py --data preeclampsia_postprocessed_nonegatives_dropduplicates --k_ratio 0.001 --max_approx 10 --n_threads 64
# python src/coralsarticle/benchmark/accuracy_topk.py --data pregnancy_postprocessed_nonegatives_dropduplicates --k_ratio 0.001 --max_approx 10 --n_threads 64
# python src/coralsarticle/benchmark/accuracy_topk.py --data cancer_postprocessed_nonegatives_dropduplicates_sample-0.25 --k_ratio 0.001 --max_approx 10 --n_threads 64
```

```bash
# topk diff
# python src/coralsarticle/benchmark/accuracy_topkdiff.py --data pregnancy --k_ratio 0.001
```

#### Supplement: Comparison to other libraries

**Runtime**:

* Setup: ~1 hour
* Experiments: 10 minutes

The folder `scripts` contains additional code snippets for comparing a variety of other software packages to CorALS.
See `scripts/benchmark_cor.sh` and `scripts_topkdiff.py`

### Results and visualizations

#### Getting started

Start Jupyter server within the docker container:

```bash

docker run -v $(pwd):/workspace \
  -v $(pwd)/../corals-lib-julia:/opt/libraries/julia \
  -v $(pwd)/../corals-lib-python:/opt/libraries/python \
  -v $(pwd)/../corals-lib-r:/opt/libraries/r \
  --publish 17299:8888 \
  -it mgbckr/corals-benchmark:1.0.0

# Then, WITHIN the Docker container:
python setup.py develop
jupyter lab --allow-root --ip 0.0.0.0 --NotebookApp.token=''
```

Open `http://localhost:17299` in your browser an run the notebooks in the `notebooks` folder.

#### Application notebooks

**Runtime**: The application notebooks (`xx_application_*`) can run a long time taking from several hours up to a day. Running on a larger machine is recommended (at least 64 cores and 312Gb of memory).

The notebooks reproduce all results from the manuscript.

## Applying to custom data

**Note:** Upon publication this will be replaced by an installable package (`pip install corals`) and can be run directly and without the Docker container. Appropriate documentation will be provided.

Start the docker container and `python` or `ipython`.

```bash
docker run -v $(pwd):/workspace \
  -v $(pwd)/../corals-lib-julia:/opt/libraries/julia \
  -v $(pwd)/../corals-lib-python:/opt/libraries/python \
  -v $(pwd)/../corals-lib-r:/opt/libraries/r \
  -it mgbckr/corals-benchmark:1.0.0

ipython
```

Run *CorALS* on random data (alternatively you can place your own custom data in the `data` folder).

```python
# make sure we are not oversubscribing CPUs
# by adjusting `n_threads`, `corals.cor_matrix` can be parallelized
from corals.threads import set_threads_for_external_libraries
set_threads_for_external_libraries(n_threads=1)

# imports
import numpy as np
import corals

# create random data
n_features = 20000
n_samples = 50
X = np.random.random((n_samples, n_features))

# full correlation matrix computation
# runtime: ~2 sec
cor_matrix = corals.cor_matrix(X)

# top-k correlation matrix computation using Spearman correlation
# runtime: ~20 sec with `n_jobs=8`
cor_topk_result = corals.cor_topk(X, spearman=True, n_jobs=8)

# top-k differential correlation matrix computation using Spearman correlation
# runtime: ~30 sec with `n_jobs=8`
X1 = X
X2 = np.random.random((n_samples, n_features))
cor_topkdiff_result = corals.cor_topdiff(X1, X2, spearman=True, n_jobs=8)
```

## Recommendations

### Full correlation matrix calculation

CorALS generally outperforms comparable full correlation matrix methods like `numpy.corrcoef`.
Thus, we generally recommend using CorALS for full correlation matrix estimation as long as the final matrix fits into memory.
Otherwise, top-k estimation may be a better choice. 

### Top-k correlation discovery

For top-k correlation search, we recommend using the basic CorALS implementation (referred to as matrix in Table 3) as long as the full correlation matrix fits into memory, independent of the number of samples. 

However, as the number of features increases, memory issues will make this approach impossible to use. When this is the case, switching to the index based CorALS implementation is the best option.

**Note**: With increasing sample numbers, CorALS becomes slower, which may warrant other heuristics such as dimensionality reduction such as locality sensitive hashing or random projections. However, this exploration is left for future work.

