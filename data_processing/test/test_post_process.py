"""
    Test post-processing functions.
"""
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np
from tusz_data_processing.config import *
from post_processing.post_process import stitch_annotations


def test_stitch_annotations():

    start_times = [0, 20, 25, 30, 50, 100]
    stop_times = [20, 25, 30, 50, 100, 120]
    label = [-1, 1, -1, 1, -1, 1]
    df = pd.DataFrame({
        "start_time": start_times,
        "stop_time": stop_times,
        "label": label
    })

    temp = stitch_annotations(df, 150, ann_label="label", min_seiz_length=10., time_between=30.)
    des_result = pd.DataFrame({
        "start_time": [0, 20, 50, 100],
        "stop_time": [20, 50, 100, 150],
        "label": ['bckg', 'seiz', 'bckg', 'seiz'],
        "probability": [1.,1.,1.,1.]
    })

    assert_frame_equal(temp, des_result,check_dtype=False)

    # end time > 30 s past seizure
    start_times = [0, 20, 25, 30, 50, 100]
    stop_times = [20, 25, 30, 50, 100, 120]
    label = [-1, 1, -1, 1, -1, 1]
    df = pd.DataFrame({
        "start_time": start_times,
        "stop_time": stop_times,
        "label": label
    })

    temp = stitch_annotations(df, 160, ann_label="label", min_seiz_length=10., time_between=30.)
    des_result = pd.DataFrame({
        "start_time": [0, 20, 50, 100, 120],
        "stop_time": [20, 50, 100, 120, 160],
        "label": ['bckg', 'seiz', 'bckg', 'seiz', 'bckg'],
        "probability": [1.,1.,1.,1.,1.]
    })

    assert_frame_equal(temp, des_result, check_dtype=False)

    ## smaller time_between
    start_times = [0, 20, 25, 30, 50, 100]
    stop_times = [20, 25, 30, 50, 100, 120]
    label = [-1, 1, -1, 1, -1, 1]
    df = pd.DataFrame({
        "start_time": start_times,
        "stop_time": stop_times,
        "label": label
    })

    temp = stitch_annotations(df, 160, ann_label="label", min_seiz_length=5., time_between=4.)
    des_result = pd.DataFrame({
        "start_time": [0, 20, 25, 30, 50, 100, 120],
        "stop_time": [20, 25, 30, 50, 100, 120, 160],
        "label": ['bckg', 'seiz', 'bckg', 'seiz', 'bckg', 'seiz', 'bckg'],
        "probability": [1,1,1,1,1,1,1]
    })

    assert_frame_equal(temp, des_result, check_dtype=False)


