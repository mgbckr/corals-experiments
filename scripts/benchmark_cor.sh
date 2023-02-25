# TODO: would be nice to integrate this into the overall benchmark framework

# clone current benchmark environment
conda create --name tmp_cor --clone benchmark
conda activate tmp_cor

# deep graph
conda install -c conda-forge deepgraph==0.2.3
print("DeepGraph")
python scripts/cor_deepgraph.py

# dask
conda install -c conda-forge dask==2022.04.1
print("Dask")
python scripts/cor_dask.py

# spark
# before running this, make sure spark is running (see `cor_spark.py`)
conda install -c conda-forge pyspark==3.3.0  # this takes a while but works
print("Spark")
python scripts/cor_spark.py