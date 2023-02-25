# prevent oversupscription of CPUs
from corals.threads import set_threads_for_external_libraries
set_threads_for_external_libraries(1)

import time
from dask.distributed import Client
import dask.array as da

client = Client(processes=False, n_workers=1, threads_per_worker=64, local_directory="/tmp/dask")

a = da.random.random((32000, 64), chunks=1e4 / 2)  # junk size is really important here! current settings seems to be a reasonable local minimum with regard to runtime
c = da.corrcoef(a)

start_time = time.time()
cc = c.compute()
end_time = time.time()
print(end_time - start_time)
