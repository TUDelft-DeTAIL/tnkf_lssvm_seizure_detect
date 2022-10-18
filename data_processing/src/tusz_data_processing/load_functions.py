# import packages
import os
from matplotlib.pyplot import get
import pandas as pd
import numpy as np
import pyedflib
import re
from collections import namedtuple
from scipy.signal import resample, resample_poly
from tusz_data_processing.config import TUSZ_DIR

# type definition
# Edf = namedtuple("Edf", ["signals", "labels", "fs", "file_name"])
Parameters = namedtuple(
    "Parameters",
    [
        "channels",
        "fs",
        "montage",
        "min_frequency",
        "max_frequency",
        "epoch_time",
        "epoch_overlap",
    ],
)


class Edf:
    """Class to hold edf files.
    """

    def __init__(self, signals, channels, fs, file_duration, file_name):
        self.signals = signals
        self.channels = channels
        self.fs = fs
        self.file_duration = file_duration
        self.file_name = file_name
        self.annotations = None

    def __repr__(self):
        return "<Edf object, attributes: signals, channels, fs, file_name>"

    def __str__(self):
        return str(self.__dict__)


def load_annotation_data(engine, by=None, arg_list=None):

    if by == "patient":
        placeholders = ",".join("?" for i in range(len(arg_list)))  # '?,?'

        query = (
            """SELECT Patient, Filename, Seizure_Start, Seizure_Stop,
            Seizure_Type, file_id, seizure_id 
            FROM Seizure_Annotations
            WHERE Patient IN (%s)"""
            % placeholders
        )

        df = pd.read_sql(query, engine, params=arg_list)

    elif by == "file":
        placeholders = ",".join("?" for i in range(len(arg_list)))  # '?,?'

        query = (
            """SELECT Patient, Filename, Seizure_Start, Seizure_Stop,
            Seizure_Type, file_id, seizure_id
            FROM Seizure_Annotations
            WHERE Filename IN (%s)"""
            % placeholders
        )

        df = pd.read_sql(query, engine, params=arg_list)

    elif by is None:  # load all annotations
        query = """ SELECT Patient, Filename, Seizure_Start, Seizure_Stop,
        Seizure_Type, file_id FROM Seizure_Annotations"""

        df = pd.read_sql(query, engine)
    else:
        raise Exception("Unsupported input format")

    return df


def load_file_properties(engine, by=None, arg_list=None):

    if by == "patient":
        placeholders = ",".join("?" for i in range(len(arg_list)))  # '?,?'
        query = (
            """ SELECT Patient, "No. Seizures/File", Filename, file_id 
                FROM File_Properties
                WHERE Patient IN (%s)"""
            % placeholders
        )
        return pd.read_sql(query, engine, index_col="file_id", params=arg_list)
    elif by == "file_id":
        # placeholders = ','.join('?' for i in range(len(arg_list)))  # '?,?'
        params = ",".join(str(elem) for elem in arg_list)
        query = (
            """ SELECT Patient, "No. Seizures/File", Filename, file_id 
                FROM File_Properties
                WHERE file_id IN (%s)"""
            % params
        )
        return pd.read_sql(query, engine, index_col="file_id")
    elif by is None or by == "all":
        query = """ SELECT Patient, "No. Seizures/File", Filename, file_id 
                FROM File_Properties"""
        return pd.read_sql(query, engine, index_col="file_id")
    else:
        raise Exception("Unsupported input format")


def load_features(engine, patients=None, only_features=False):
    # TODO make applicable to different inputs
    if patients is not None:
        if not np.isscalar(patients):
            patients = ",".join(str(elem) for elem in patients)

        query = (
            """ SELECT Features.* FROM Features 
                    INNER JOIN File_Properties 
                    ON File_Properties.file_id = Features.file_id 
                    WHERE Patient = (%s) """
            % patients
        )
    else:
        query = """
                SELECT Features.* FROM Features"""

    features = pd.read_sql(query, engine, index_col="feat_id")
    # features = features.drop(columns=['file_id', 'epoch'])
    if only_features:
        features.drop(columns=["file_id", "epoch", "seizure_id"], inplace=True)

    return features


def load_sorted_features(engine, patients=None):
    # TODO make applicable to different inputs
    if patients is not None:
        if not np.isscalar(patients):
            patients = ",".join(str(elem) for elem in patients)

        query = (
            """ SELECT Sorted_Features.* FROM Sorted_Features 
                    INNER JOIN File_Properties 
                    ON File_Properties.file_id = Sorted_Features.file_id 
                    WHERE Patient = (%s) """
            % patients
        )
    else:
        query = """
                SELECT Sorted_Features.* FROM Sorted_Features"""

    features = pd.read_sql(query, engine, index_col="feat_id")
    # features = features.drop(columns=['file_id', 'epoch'])
    return features


def load_val_groups(engine):

    query = """ SELECT * FROM Validation_Groups"""
    df = pd.read_sql(query, engine, index_col="feat_id")
    return df


def load_parameters(parameters_file):
    parameters = pd.read_csv(parameters_file, delimiter=",", index_col=["parameter"])

    channels = str(parameters.loc["channels"]["value"])
    channels = re.split(";", channels)

    fs = pd.to_numeric(parameters.loc["sampling_frequency"]["value"])
    min_frequency = pd.to_numeric(parameters.loc["min_frequency"]["value"])
    max_frequency = pd.to_numeric(parameters.loc["max_frequency"]["value"])
    epoch_time = pd.to_numeric(parameters.loc["epoch_time"]["value"])
    epoch_overlap = pd.to_numeric(parameters.loc["epoch_overlap"]["value"])

    montage = parameters.loc["montage"]["value"]
    if montage == montage:  # if not nan
        montage = re.split(";", str(montage))

    return Parameters(
        channels, fs, montage, min_frequency, max_frequency, epoch_time, epoch_overlap
    )


def get_pos_edf(label_list: list, target_labels: list):
    """Get position of channels in edf file.

    Args:
        label_list (list): List of labels/channels
        target_labels (list): List of target labels (labels to extract)

    Raises:
        Exception: Failed to find label

    Returns:
        tuple: (indices, T_12)
    """
    T_12 = True  # T1 and T2 electrode in EEG recording
    indices = []  # indices of the target labels
    for lbl in target_labels:
        index = [
            i for i, elem in enumerate(label_list) if lbl.casefold() in elem.casefold()
        ]
        if len(index) == 0 and (lbl == "T1" or lbl == "T2"):
            T_12 = False
            continue
        elif len(index) == 0 and not (lbl == "T1" or lbl == "T2"):
            raise Exception("Failed to find label %s" % lbl)
        else:
            indices.append(index[0])

    return indices


def resample_edf(signals, old_fs, new_fs):
    """
    Resample edf data to new sampling frequency.

    Args:
        signals (ndarray): {time x channels} array containing the EEG data
        old_fs (int): current sampling frequency
        new_fs (int): new (desired) sampling frequency

    Returns:
       ndarray: array with resampled data

    """
    if np.all(old_fs == new_fs):
        return signals
    elif not np.isscalar(old_fs):
        raise Exception("Original sampling frequency not a scalar")

    # number of points new signal
    num_sec = int(signals.shape[0] / old_fs)
    signals = signals[0 : (num_sec * old_fs), :]  # to ensure correct resampling
    assert (signals.shape[0] % old_fs) == 0

    num_points = num_sec * new_fs

    return resample(signals, num_points, axis=0, window=None, domain="time")


def apply_montage(signals, channels: list, montage: list):
    """apply a montage to the EEG signals

    Args:
        signals (ndarray): (time x channels) numpy array
        channels (list): list with names of the selected channels
        montage (list): list of montage

    Returns:
        ndarray: (time x montage) numpy array
    """

    ## Split montage
    montage_split = np.array([part.split("-") for part in montage])
    indices_first = get_pos_edf(channels, montage_split[:, 0].tolist())
    indices_second = get_pos_edf(channels, montage_split[:, 1].tolist())

    montaged_signals = signals[:, indices_first] - signals[:, indices_second]

    return montaged_signals


def load_edf(
    path_to_edf_file, param=None, properties_only=False, annotate=False, montage=None
):
    """load signals from an EDF file

    Args:
        path_to_edf_file (str): Path to edf file
        param (namedtuple, optional): Parameters struc. Defaults to None.
        properties_only (bool, optional): Only extract properties from the file. Defaults to False.
        annotate (bool, optional): Annotate the edf file (using .tse file). Defaults to False.
        montage (str, optional): EEG montage (separated by ;). Defaults to None.

    Returns:
        Edf: Edf object containing the signals, frequency, file path (and annotation)
    """
    try:
        f = pyedflib.EdfReader(path_to_edf_file)
    except IOError:
        print("Failed to open %s" % path_to_edf_file)
        raise

    # ----------- get channels and fs --------------
    channels = f.getSignalLabels()
    num_channels = f.signals_in_file
    fs = f.getSampleFrequencies()  # sampling frequency

    if param is None:  # output all channels
        signals = []
        for i in range(num_channels):
            signals.append(f.readSignal(i))
        signals = np.transpose(signals)
        return Edf(signals, channels, fs, f.getFileDuration(), path_to_edf_file)

    # get indices of the selected channels (/labels)
    ch_indices = get_pos_edf(channels, param.channels)
    # if not T12:  # remove T1 and T2 from param.channels if not in file
    #     param.channels.remove("T1")
    #     param.channels.remove("T2")

    fs = fs[ch_indices]  # fs of selected channels
    if properties_only and np.all(fs == fs[0]):
        return fs[0], f.getFileDuration()
    elif properties_only:  # different sample frequencies in file so return nan
        return np.nan, f.getFileDuration()

    if np.all(fs == fs[0]):
        fs = fs[0]

    # ------------------ read signals --------------------
    signals = []
    for i in ch_indices:
        signals.append(f.readSignal(i))

    try:
        signals = np.transpose(signals)  # cols different channels, rows time
    except:
        print("Different length of signals:")
        print([len(elem) for elem in signals])
        exit(0)

    # print("fs = ", fs)
    # print("param.fs = ", param.fs)

    signals = resample_edf(signals, fs, param.fs)
    fs = param.fs  # resampled fs
    # if not param.montage or np.isnan(param.montage):
    edf = Edf(signals, param.channels, fs, f.getFileDuration(), path_to_edf_file)
    # else:
    #     signals = apply_montage(signals, param.channels, param.montage)
    #     edf = Edf(signals, param.montage, fs, f.getFileDuration(), path_to_edf_file)

    if annotate:
        # TODO add possibility for seizure type
        if not np.isscalar(fs):
            raise Exception("Cannot annotate file for non-scalar Fs.")
        seizures = load_tse(os.path.splitext(path_to_edf_file)[0] + ".tse_bi")
        Ts = 1 / fs
        time = np.arange(0, Ts * edf.signals.shape[0], Ts)
        annotations = np.ones_like(time) * (-1)  # intialize annotations array
        for seizure in seizures:
            start_time = seizure[0]
            stop_time = seizure[1]
            annotations[np.where((time >= start_time) & (time <= stop_time))] = 1

        edf.annotations = annotations

    return edf


def load_tse(tse_file, dataframe=False):
    """function: loadTSE Load seizure events from a TSE file.

    Args:
      tse: TSE event file
      dataframe (bool): output as dataframe. Default to False.

    return:
      seizures: output list of seizures. Each event is tuple of 4 items:
                 (seizure_start [s], seizure_end [s], seizure_type, probability)
    """
    VERSION = "version = tse_v1.0.0\n"
    SEIZURES = (
        "seiz",
        "fnsz",
        "gnsz",
        "spsz",
        "cpsz",
        "absz",
        "tnsz",
        "cnsz",
        "tcsz",
        "atsz",
        "mysz",
        "nesz",
    )
    seizures = list()

    # Parse TSE file
    #
    with open(tse_file, "r") as tse:
        firstLine = tse.readline()

        # Check valid TSE
        if firstLine != VERSION:
            raise ValueError(
                'Expected "{}" on first line but read \n {}'.format(VERSION, firstLine)
            )

        # Skip empty second line
        tse.readline()

        # Read all events
        for line in tse.readlines():
            fields = line.split(" ")

            if fields[2] in SEIZURES:
                # Parse fields
                start = float(fields[0])
                end = float(fields[1])
                seizure = fields[2]
                prob = float(fields[3][:-1])

                seizures.append((start, end, seizure, prob))

    if dataframe:
        seizures = np.array(seizures)
        seizures = pd.DataFrame(
            seizures, columns=["start_time", "stop_time", "annotation", "probability"]
        )

    return seizures


def get_duration_tse(tse_file):
    """function: loadTSE Load seizure events from a TSE file.

    Args:
      tse: TSE event file

    return:
      stop_time (s), float
    """
    VERSION = "version = tse_v1.0.0\n"

    # Parse TSE file
    #
    with open(tse_file, "r") as tse:
        firstLine = tse.readline()
        # Check valid TSE
        if firstLine != VERSION:
            raise ValueError(
                'Expected "{}" on first line but read \n {}'.format(VERSION, firstLine)
            )

        lines = tse.readlines()
        lastLine = lines[-1]
        fields = lastLine.split(" ")
        stop_time = float(fields[1])

    return stop_time


def edf_to_df(edf):
    """Single edf file to dataframe conversion plus add time column"""
    # create time vector
    Ts = 1 / edf.fs
    time = np.arange(0, Ts * edf.signals.shape[0], Ts)

    # add time to signals
    # signals = np.row_stack((time, edf.signals))

    # create database
    # signals = np.transpose(signals)  # to match format
    # header = ['time']
    # header.extend(edf.channels)
    edf_df = pd.DataFrame(edf.signals, columns=edf.channels, index=time)
    edf_df.index.name = "time"

    return edf_df


def check_file_duration(file):
    # check that edf duration and annotation duration are same in length
    if TUSZ_DIR not in file:
        file = TUSZ_DIR + file
    if ".edf" in file:
        file = file.replace(".edf", "")
    elif ".tse" in file:
        file = file.replace(".tse", "")

    edf_file = file + ".edf"
    tse_file = file + ".tse"
    edf_reader = pyedflib.EdfReader(edf_file)
    edf_duration = edf_reader.file_duration
    tse_duration = get_duration_tse(tse_file)
    check = np.isclose(edf_duration, tse_duration)

    return check
