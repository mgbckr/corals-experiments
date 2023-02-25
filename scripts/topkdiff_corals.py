from corals.threads import set_threads_for_external_libraries
set_threads_for_external_libraries(1)

import time
import numpy as np
from corals.correlation.topkdiff.original import topkdiff_balltree_combined_tree_parallel


n = 10000
# n = 300
m = 17 * 2

a = np.random.random((m, n))
groups = np.tile([0,1], int(m / 2))

a0 = a[groups == 0]
a1 = a[groups == 1]

start = time.time()
topkdiff_balltree_combined_tree_parallel(a0, a1, k=0.001, approximation_factor=10)
end = time.time()
print(end - start) 


# n=32221: ~79 s = 1.33 m
# n=10000: ~7.5 s