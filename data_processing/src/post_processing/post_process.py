"""
    This script post_processes the labeled data to .tse files as
    specified by the tuh documentation.
"""

import multiprocessing
import os
from glob import glob
import shutil
from functools import partial
import platform

import numpy as np
import pandas as pd
import mat73
import pyedflib

from tusz_data_processing.config import FEATURES_DIR, TUSZ_DIR
import tusz_data_processing.load_functions as lf

SET = "eval"
SIM = "2"
MOVING_WINDOW = 10  # length moving average filter
OFFSET = 0.0        # possible bias adjustment
VAL_FILE = FEATURES_DIR + "/" + SET + ".parquet"
CLASSIFIER = "tnkf"
REF = False
HYP = True
DEBUG = False

if CLASSIFIER == "lssvm":
    PREDICTIONS = (
        FEATURES_DIR + "/results/lssvm/" + SET + SIM + "_output.csv"
    )
    RESULTS_DIR = "../scoring/" + SET + "_hyp_lssvm/sim_" + SIM + "/"
elif CLASSIFIER == "tnkf":
    # PREDICTIONS = FEATURES_DIR + "/results/eval/tnkf_/" + SET + "_"+SIM+".csv"
    PREDICTIONS = FEATURES_DIR + "/results/eval/gamma=0.10_sigma2=6.00/predicted.mat"
    RESULTS_DIR = "../scoring/" + SET + "_hyp_tnkf/sim_" + SIM + "/"

def load_classifier_results(val_file, prediction_file):
    """_summary_

    Args:
        val_file (_type_): _description_
        prediction_file (_type_): _description_

    Returns:
        _type_: _description_
    """

    # %% Load predictions
    prediction_file = os.path.abspath(prediction_file)
    file, ext = os.path.splitext(prediction_file)
    if ext == ".mat":
        predictions = mat73.loadmat(prediction_file)
        predictions = pd.DataFrame(predictions)
    elif ext == ".csv":
        predictions = pd.read_csv(prediction_file)
    # predictions had cols: 'predicted_labels', 'svm_output', (opt.) 'vat_output'
    predictions.reset_index(inplace=True, drop=True)
    # %% load validation data
    cols = ["epoch", "start_time", "stop_time", "annotation", "filename"]
    val_df = pd.read_parquet(val_file, columns=cols)
    val_df.reset_index(inplace=True, drop=True)
    # %% join the true validation with the predicted labels
    assert len(val_df) == len(
        predictions
    ), "Prediction and validation data must be of same length."
    new_df = val_df.join(predictions)
    assert len(new_df) == len(val_df), "Concatenated df not same length."

    return new_df


def get_file_names(dataset):
    if isinstance(dataset, str):
        edf_files = [
            y
            for x in os.walk(TUSZ_DIR + "/" + dataset + "/")
            for y in glob(os.path.join(x[0], "*.edf"))
        ]
        edf_files = [y.replace(TUSZ_DIR + "/", "") for y in edf_files]

    elif isinstance(dataset, pd.DataFrame):
        edf_files = dataset["filename"].unique()
        edf_files = edf_files.tolist()
    elif isinstance(dataset, pd.Series):
        edf_files = dataset.unique()

    return edf_files


def get_file_length(edf_file):
    edf_file = TUSZ_DIR + edf_file
    edf_reader = pyedflib.EdfReader(edf_file)
    return edf_reader.file_duration


def write_tse(annotations, tse_file):
    """function: write_tse Load seizure events from a TSE file. This function is
        adapted from the one provided by xxx.

    Args:
        annotations: DataFrame with seizure, with columns
                 (start_time [s], stop_time [s], annotation ('seiz' or 'bkgn)
        tse_file: name of the tse_file with annotation of the edf_file.

    return:
      tse_file
    """
    VERSION = "version = tse_v1.0.0\n"

    # dataframe to list
    # seizures['probability'] = 1.0
    parsed_seizures = "\n".join(
        [" ".join(row) for row in annotations.values.astype(str).tolist()]
    )

    # make dirs if not exist
    os.makedirs(os.path.dirname(tse_file), exist_ok=True)

    # Parse TSE file
    #
    with open(tse_file, "w") as tse:
        tse.write(VERSION)

        # write empty second line
        tse.write("\n")

        # write all events
        tse.write(parsed_seizures)

    return annotations


def stitch_annotations(
    ann_df,
    file_duration,
    ann_label="predicted_labels",
    min_seiz_length=25.0,
    time_between=90.0,
):
    """Stitch together the annotations to take time into account. 

    Args:
        ann_df (DataFrame): DataFrame with columns (start_time, stop_time, annotation)
        file_duration: Duration in s of the edf file.
        ann_label (str, optional): Label of the annotations. Defaults to "predicted_labels".
        min_seiz_length (float, optional): Minimum length of a seizure in seconds. Defaults to 8..
        seiz_percentage (float, optional): Percentage of segments that need to be classified as seizure. Defaults to 0.8.
        time_between (float, optional): If > time_between seizure segments they are 'different' seizures. Defaults to 3..

    Returns:
        DataFrame: with columns (start_time, stop_time, annotation)
    """

    ann_df.loc[:, "stop_time"] = ann_df["stop_time"].round()
    ann_df.loc[:, "start_time"] = ann_df["start_time"].round()
    seizures = ann_df[ann_df[ann_label] == 1]
    cols = ["start_time", "stop_time", ann_label, "probability"]
    if seizures.empty:
        new_ann = pd.DataFrame([[0.0, file_duration, "bckg", 1.0]], columns=cols)
        return new_ann

    seizures.reset_index(inplace=True, drop=True)
    seizures.sort_values(by="start_time", inplace=True)

    # First step auto stitch if time between < time_between
    # check if a seizure exist
    # new_seizures = pd.DataFrame(columns=seizures.columns)
    i_seiz = 0
    start_seizure = [seizures.loc[0, "start_time"]]  # initialize start 1st seizure
    stop_seizure = [seizures.loc[0, "stop_time"]]
    for i, row in seizures.iterrows():
        if i == 0:
            continue
        curr_start = row["start_time"]  # initialize start 1st seizure
        curr_stop = row["stop_time"]
        if abs((curr_start - stop_seizure[i_seiz])) <= time_between:
            stop_seizure[i_seiz] = curr_stop
        else:
            i_seiz += 1
            start_seizure.append(curr_start)
            stop_seizure.append(curr_stop)

    new_seizures = pd.DataFrame(
        np.array([start_seizure, stop_seizure]).T, columns=["start_time", "stop_time"]
    )

    # step: remove seizure < min_seiz_length
    new_seizures = new_seizures.sort_values(by="start_time")
    new_seizures.reset_index(inplace=True, drop=True)
    new_seizures["seizure_length"] = (
        new_seizures["stop_time"] - new_seizures["start_time"]
    )
    new_seizures = new_seizures[new_seizures["seizure_length"] >= min_seiz_length]
    if new_seizures.empty:
        new_ann = pd.DataFrame([[0.0, file_duration, "bckg", 1.0]], columns=cols)
        return new_ann

    new_seizures.reset_index(inplace=True, drop=True)
    new_seizures.drop(columns=["seizure_length"], inplace=True)
    new_seizures.loc[:, ann_label] = "seiz"


    new_seizures.loc[:, "probability"] = 1.0

    # Add background segments
    time = 0
    background_start = []
    background_stop = []
    for index, row in new_seizures.iterrows():
        if index == 0 and row["start_time"] == 0:
            continue
        background_start.append(time)
        background_stop.append(row["start_time"])

        time = row["stop_time"]

    # Background dataframe
    assert len(background_start) == len(background_stop)
    N_back = len(background_start)
    background_df = pd.DataFrame(
        {
            "start_time": background_start,
            "stop_time": background_stop,
            ann_label: ["bckg"] * N_back,
            "probability": [1.0] * N_back,
        }
    )

    # concatenate background and seizure df's
    new_ann = pd.concat([background_df, new_seizures])
    new_ann.sort_values(
        by="start_time", ascending=True, ignore_index=True, inplace=True
    )
    idx_last = new_ann.index[-1]
    last_row = new_ann.loc[idx_last, :].copy()
    if last_row["stop_time"] != file_duration:
        if (
            last_row[ann_label] == "seiz"
            and (file_duration - last_row["stop_time"]) <= time_between
        ):
            new_ann.loc[idx_last, "stop_time"] = file_duration
        elif last_row[ann_label] == "bckg":
            new_ann.loc[idx_last, "stop_time"] = file_duration
        else:
            new_last_row = pd.Series(
                [
                    new_ann.loc[new_ann.index[-1], "stop_time"],
                    file_duration,
                    "bckg",
                    1.0,
                ],
                index=new_ann.columns,
            )
            new_ann.loc[idx_last + 1, :] = new_last_row

    assert np.all((new_ann["stop_time"] - new_ann["start_time"]) > 0)

    return new_ann


def stitch_file(file: str, validation_df: pd.DataFrame) -> str:
    """Stitch the annotation of the specified file as save the anntotations as
        .tse file  

    Args:
        file (str): the respective file
        validation_df (DataFrame): dataframe with the validation features

    Returns:
        str: name of the .tse file
    """
    file_length = get_file_length(file)
    check = lf.check_file_duration(file)
    if not check:
        return None

    # get dataframe of current file
    df = validation_df[validation_df["filename"] == file].copy()
    # apply moving average filter to svm output
    N_filt = np.min([MOVING_WINDOW, len(df)-1])
    df.loc[:, 'svm_output'] = moving_average(
        df.loc[:, 'svm_output'].to_numpy(), N=N_filt, axis=0
    )
    if CLASSIFIER == "tnkf":
        df.loc[:, 'svm_output'] = df.loc[:,'svm_output'] + OFFSET   # adjust bias
    # new labels after moving average filter
    df.loc[:, 'predicted_labels'] = np.sign(df.loc[:, 'svm_output'])

    # stitch labels and make ready for .tse file
    stitched_df = stitch_annotations(df, file_length)

    # save to .tse file
    file = os.path.basename(file)
    tse_file_name = RESULTS_DIR + file.replace(".edf", "") + ".tse"
    write_tse(stitched_df, tse_file_name)

    return tse_file_name


def moving_average(x: np.ndarray, N: int, axis: int = 0) -> np.ndarray:
    """Moving average filter.

    Args:
        x (ndarray): numpy array of signals
        N (int): lag of the filter, N must be >= length of x
        axis (int): axis to filter over, 0 for over the rows, 1 for over the columns
        
    Returns:
        ndarray: averaged signals (same length as original)
    """
    if x.ndim == 1:
        assert len(x) >= N, "length of array must be larger than lag"
        return np.convolve(x, np.ones(N) / N, mode="same")

    assert axis == 0 or axis == 1, "axis must be equal to 0 or 1"
    assert x.shape[axis] >= N, "length of array must be larger than lag"

    if axis == 0:
        x_avg = np.zeros_like(x, dtype=float)
        print(x_avg.shape)
        for i, column in enumerate(x.T):
            x_avg[:, i] = np.convolve(column.T, np.ones(N) / N, mode="same")
    elif axis == 1:
        x_avg = np.zeros_like(x, dtype=float)
        for i, row in enumerate(x):
            x_avg[i, :] = np.convolve(row, np.ones(N) / N, mode="same")

    return x_avg  # moving average --> same length as original


def copy_ref_files_to_folder(tse_files: list[str], folder: str) -> list:
    """Copy the reference .tse files of the dev or eval set to the specified folder.

    Args:
        tse_files (list[str]): list of the .tse files to copy
        folder (str): folder directory to copy to.

    Returns:
        list: list of the .tse files in the new directory.
    """
    new_files = []
    for file in tse_files:
        if os.path.isfile(file):
            shutil.copy2(file, folder)
            new_files.append(folder + "/" + os.path.basename(file))

    return new_files


def save_tse_filenames_to_list(tse_file_names: list[str], mode: str = "hyp"):
    """Save the names of the tse files to a .list file

    Args:
        tse_file_names (list[str]): list of tse file names
        mode (str, optional): hypothesis or reference. Defaults to 'hyp'.
    """
    # TODO: write function to save the names/directories of the .tse files for
    # reference and hypothesis

    tse_file_names = list(filter(lambda item: item is not None, tse_file_names))

    if platform.system() == "Windows":
        tse_file_names = [file.replace("C:/", "/mnt/c/") for file in tse_file_names]

    tse_file_names = [file.replace("../scoring/", "") for file in tse_file_names]

    parsed_names = "\n".join(tse_file_names)
    if mode == "hyp":
        list_file = "../scoring/" + SET + "_" + mode + "_" + CLASSIFIER + "_" + SIM + ".list"
    elif mode == "ref":
        list_file = "../scoring/" + SET + "_" + mode + ".list"

    with open(list_file, "w") as f:
        f.write(parsed_names)
    return


if __name__ == "__main__":
    val_df = load_classifier_results(VAL_FILE, PREDICTIONS)
    file_names = get_file_names(val_df)
    if DEBUG:
        for file in file_names:
            tse = stitch_file(file, validation_df=val_df)

    if HYP:
        pool_obj = multiprocessing.Pool()
        tse_list = pool_obj.map(partial(stitch_file, validation_df=val_df), file_names)
        save_tse_filenames_to_list(tse_list, mode="hyp")

    if REF:
        tse_list = [
            TUSZ_DIR + file.replace(".edf", ".tse_bi")
            for file in file_names
            if lf.check_file_duration(file)
        ]
        new_list = copy_ref_files_to_folder(tse_list, "../scoring/" + SET + "_ref")
        save_tse_filenames_to_list(new_list, mode="ref")


