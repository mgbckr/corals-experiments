library(RhpcBLASctl)
library(bench)
library(rhdf5)
library(optparse)

# settings

parser <- OptionParser()
parser <- add_option(parser, c('--prefix'), default="default")
parser <- add_option(parser, c('--exp'), default="cor_symmetrical")
parser <- add_option(parser, c('--n_threads'), default=1)
parser <- add_option(parser, c('--n_repeat'), default=10)
parser <- add_option(parser, c('--data'), default="synthetic_mn_m-50_n-20000")
parser <- add_option(parser, c('--k_ratio'), default=0.01)
parser <- add_option(parser, c('--threshold'), default=0.75)
parser <- add_option(parser, c('--overwrite'), action="store_true", default=FALSE)
parser <- add_option(parser, c('--library_update'), default=TRUE)
parser <- add_option(parser, c('--library_path'), default="/opt/libraries/r")

args <- parse_args(parser)

# update library
if (args$library_update) {
    print(paste("Updating library:", args$library_path))
    devtools::document(args$library_path)
    devtools::install(args$library_path)
}
library(corals)

n_threads <- args$n_threads
n_repeat <- args$n_repeat

prefix <- args$prefix
name <- args$exp
data <- args$data

# for top k only
k_ratio = args$k_ratio

# for threshold only
threshold = args$threshold

# controlling threads

# control threads
# omp_get_max_threads()
omp_set_num_threads(n_threads)
# blas_get_num_procs()
blas_set_num_threads(n_threads)

# prepare k name
k_name = sprintf("%.02fpercent", k_ratio * 100)

# parse context
if (startsWith(name, "cor")) {
    context = "fast"
} else if (startsWith(name, "topk")) {
    context = paste("topk-", k_name, sep="")
} else {
    throw("Unknown context: ", name)
}

# final setting of experimetn name
exp_name <- name
if (n_threads > 1) {
    exp_name <- paste(exp_name, "_nthreads-", n_threads, sep="")
} 

# prare file
file = paste("_out/benchmark/benchmark___prefix-", prefix, "___context-", context, "___lang-r___data-", data, "___algorithm-", exp_name, "___repeat-", n_repeat, ".h5", sep="")


print(sprintf("Experiment:  %s", exp_name))
print(sprintf("* File:      %s", file))

h5createFile(file)
if (!args$overwrite) {
    tryCatch({
        h5read(file, paste(exp_name, "runtime", sep="/"))
        print("SKIPPING; experiment already exists")
        quit()
    }, error=function(e) {})
}

library(rhdf5)
file_name <- file.path("./data/benchmark", paste(data, ".h5", sep=""))
d = t(h5read(file_name, "data"))

k = floor(dim(d)[2]^2 * k_ratio) 

print(sprintf("* Data:      %d x %d", dim(d)[1], dim(d)[2]))
print(sprintf("* K ratio:   %f", k_ratio))
print(sprintf("* K:         %d", k))
print(sprintf("* Threshold: %f", threshold))
print(sprintf("* Threads:   %d", n_threads))

results_run = list()
results_mem = list()

print(getwd())
source("./src/coralsarticle/benchmark/algorithms/r/exps.R")
f = load_experiments(name, d, k=k, threshold=threshold)

for (i in 1:n_repeat) {

    print(paste("Repetition: ", i, "/", n_repeat, "(", Sys.time(), ")"))

    b <- bench::mark(f(), max_iterations=1)
   
    run <- b$median
    mem <- b$mem_alloc / 1024 / 1024  # to Mb

    results_run[[i]] = run
    results_mem[[i]] = mem

    print(paste("  * Experiment:", name, "( threads =", n_threads, ")"))
    print(paste("  * Runtime:", run))
    print(paste("  * Memory: ", mem * 1024 * 1024))
}

# write results
h5createFile(file)
h5createGroup(file, exp_name)
h5write(unlist(results_run), file=file, name=paste(exp_name, "runtime", sep="/"))
h5write(unlist(results_mem), file=file, name=paste(exp_name, "memory", sep="/"))

print("Done")
