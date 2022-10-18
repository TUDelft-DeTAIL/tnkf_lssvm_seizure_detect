import numpy as np
import tusz_data_processing.load_functions as lf
from tusz_data_processing.config import *
from tusz_data_processing.nedc_pystream import nedc_load_edf


def test_load_edf():

    # test_file = TUSZ_DIR + "/train/01_tcp_ar/044/00004456/s015_2014_06_19/00004456_s015_t002.edf"
    test_file = DATA_DIRECTORY + "/example.edf"
    param = lf.load_parameters(PARAMETERS)

    # compare with method from nedc_pystream
    edf = lf.load_edf(test_file)
    fsamp, sig, labels = nedc_load_edf(test_file)
    sig_eq = [
        True if np.allclose(edf.signals[i], sig[i]) else False
        for i in range(0, len(edf.signals))
    ]

    assert np.all(sig_eq)
    assert np.allclose(fsamp, edf.fs)
    assert np.array_equal(labels, [chan.replace(" ", "") for chan in edf.channels])

    # check some other stuff
    edf = lf.load_edf(test_file, param, annotate=False)

    assert np.array_equal(param.channels, edf.channels)

    assert np.allclose(param.fs, edf.fs)

    orig_len = len(sig[0])
    new_len = edf.signals.shape[0]
    assert np.isclose(orig_len / new_len, fsamp[0] / param.fs)

    # TODO check annotations


# def test_resample_edf():
#     test_file = DATA_DIRECTORY + "/example.edf"
#     param = lf.load_parameters(PARAMETERS)
