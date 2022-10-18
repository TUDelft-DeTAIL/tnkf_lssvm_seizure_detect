import numpy as np

import tusz_data_processing.data_sampling as ds
import primefac


def test_determine_quantization_par():

    n1 = 1
    n2 = 276538
    n3 = 12870
    n4 = 7581437

    n1_new = ds.determine_quantization_par(n1)
    n2_new = ds.determine_quantization_par(n2, max_rank=5)
    n3_new = ds.determine_quantization_par(n3)
    n4_new = ds.determine_quantization_par(n4)

    assert n1 == n1_new
    assert n3 == n3_new

    q_n2 = list(primefac.primefac(n2_new))
    q_n4 = list(primefac.primefac(n4_new))

    assert max(q_n2) <= 5
    assert max(q_n4) <= 19
    assert np.prod(q_n2) == n2_new
    assert np.prod(q_n4) == n4_new
