# Before running this, install and run Spark (3.3.0) either locally or use a cluster
# * install java: 
#   * mkdir -p /usr/share/man/man1
#   * apt update
#   * apt-get install procps
#   * apt install default-jre
# * download: wget https://dlcdn.apache.org/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
# * extract archive: tar -xf spark-3.3.0-bin-hadoop3.tgz
# * change dir: cd spark-3.3.0-bin-hadoop3
# * start master: ./sbin/start-master.sh -h $HOSTNAME
# * start worker: ./sbin/start-worker.sh $HOSTNAME:7077
# * make sure the worker is connected (usually at http://localhost:8080)

# prevent oversupscription of CPUs
from corals.threads import set_threads_for_external_libraries
set_threads_for_external_libraries(1)

import time
import pyspark as spark

# create observations
from numpy.random import RandomState
prng = RandomState(0)
n_features = int(32211)  # originally: 5e3
n_samples = int(68)  # originally: 1e2
X = prng.random((n_features, n_samples))  # originally: X = prng.randint(100, size=(n_features, n_samples)).astype(np.float64)


# spark session
from pyspark.sql import SparkSession
import socket
hostname = socket.gethostname()
spark = SparkSession \
    .builder \
    .master(f"spark://{hostname}:7077") \
    .appName("Corals") \
    .getOrCreate()

# convert data to spark
from pyspark.ml.linalg import DenseMatrix, Vectors
from pyspark.ml.stat import Correlation

Xspark = [[Vectors.dense(row)] for row in X]
dataset = spark.createDataFrame(Xspark, ['features']).repartition(64)
dataset.rdd.getNumPartitions()

# calculate correlations
start_time = time.time()
cor = Correlation.corr(dataset, 'features', 'pearson').collect()[0][0].toArray()
end_time = time.time()
print(end_time - start_time)
