# testing numpy's memmap memory consumption
# see: https://numpy.org/doc/stable/reference/generated/numpy.memmap.html

import os
import numpy as np
from memory_profiler import memory_usage


# benchmark parameters
memory_usage_kwargs = dict(
    # doesn't make a difference either it seems
    # default value (0.1) seems fine
    interval=0.1,
    # we are only interested in maximum memory consumption over time
    max_usage=True,  
    # combines memory usage of parent and children processes
    # NOTE: This measures RSS and might overestimate memory usage! 
    #       There is an updated version of `memory_profiler` coming up 
    #       that can measure PSS and USS which might be more accurate 
    include_children=True,
    # also keep track of children's memory consumption separately ... we don't really use this
    multiprocess=True,
    # default backend measures RSS which may overestimate memory usage in parallel case
    backend="psutil_uss"
)

# create data

tmp = "/tmp/X.npy"
data_shape = (1000000, 100)

def create_data():
    X = np.random.random(data_shape)
    np.save(tmp, X)
    
def delete_data():
    os.unlink(tmp)

def test_numpy():
    XX = np.load(open(tmp, "rb"))

def test_memmap_small():
    memmap_shape = (100,100)
    XX = np.memmap(tmp, shape=memmap_shape, dtype=float, mode="r")

def test_memmap_full():
    memmap_shape = data_shape
    XX = np.memmap(tmp, shape=memmap_shape, dtype=float, mode="r")


def test_numpy_op():
    XX = np.load(open(tmp, "rb"))
    XX + 1

def test_memmap_small_op():
    memmap_shape = (100,100)
    XX = np.memmap(tmp, shape=memmap_shape, dtype=float, mode="r")
    XX + 1

def test_memmap_full_op():
    memmap_shape = data_shape
    XX = np.memmap(tmp, shape=memmap_shape, dtype=float, mode="r")
    XX + 1

def test_memmap_full_iter():
    memmap_shape = data_shape
    XX = np.memmap(tmp, shape=memmap_shape, dtype=float, mode="r")
    for i in range(XX.shape[0]):
        a = XX[i] + 1
        del a

def test_memmap_full_iter_inner():
    # Keep memory usage down but is a lot slower than `test_memmap_full_iter`
    # Use chunks for performance improvement: 
    # https://stackoverflow.com/questions/45132940/numpy-memmap-memory-usage-want-to-iterate-once/61472122#61472122
    memmap_shape = data_shape
    for i in range(memmap_shape[0]):
        XX = np.memmap(tmp, shape=memmap_shape, dtype=float, mode="r")
        a = XX[i] + 1
        del a


create_data()

mem = memory_usage(proc=test_numpy, **memory_usage_kwargs)
print(f"* Numpy:                {mem:8.02f}")

mem = memory_usage(proc=test_memmap_small, **memory_usage_kwargs)
print(f"* Memmap (small):       {mem:8.02f}")

mem = memory_usage(proc=test_memmap_full, **memory_usage_kwargs)
print(f"* Memmap (full):        {mem:8.02f}")

mem = memory_usage(proc=test_numpy_op, **memory_usage_kwargs)
print(f"* Numpy +1:             {mem:8.02f}")

mem = memory_usage(proc=test_memmap_small_op, **memory_usage_kwargs)
print(f"* Memmap (small) +1:    {mem:8.02f}")

mem = memory_usage(proc=test_memmap_full_op, **memory_usage_kwargs)
print(f"* Memmap (full) +1:     {mem:8.02f}")

mem = memory_usage(proc=test_memmap_full_iter, **memory_usage_kwargs)
print(f"* Memmap (full); iter:  {mem:8.02f}")

mem = memory_usage(proc=test_memmap_full_iter_inner, **memory_usage_kwargs)
print(f"* Memmap (full); iter2: {mem:8.02f}")

delete_data()
