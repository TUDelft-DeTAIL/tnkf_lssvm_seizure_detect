import numpy as np
import pandas as pd
from scipy import signal
from scipy.fft import fft, fftfreq
from pywt import wavedec
from sklearn.preprocessing import StandardScaler
import tusz_data_processing.data_sampling as ds
import tusz_data_processing.load_functions as lf
from scipy.signal import welch
from scipy.stats import skew, kurtosis


def chunker(arr, size, overlap):
    """chunker (with overlap) for numpy array"""
    for pos in range(0, len(arr), size - overlap):
        yield arr[pos : pos + size]


def df_chunker(seq, size, overlap):
    """chunker with overlap for dataframe"""
    for pos in range(0, len(seq), size - overlap):
        yield seq.iloc[pos : pos + size]


def bandpass_filter(x, fsamp, min_freq, max_freq, axis=-1, order=4):
    """filters the given signal x using a Butterworth bandpass filter

    Parameters
    ----------
    x : ndarray
        signal to filter
    fsamp : float
        sampling frequency
    min_freq : float
        cut-off frequency lower bound
    max_freq : float
        cut-off frequency upper bound
    axis : int, optional
        axis to filter, by default -1  (0 for filter along the row, 1 for along the columns)
    order : int, optional
        order of Butterworth filter, by default 4

    Returns
    -------
    ndarray
        filtered_signal
    """
    sos = signal.butter(
        order,
        [min_freq, max_freq],
        btype="bandpass",
        fs=fsamp,
        output="sos",
        analog=False,
    )

    return signal.sosfiltfilt(sos, x, axis=axis)


def highpass_filter(x, fsamp, min_freq, axis=-1, order=4):
    """filters the given signal x using a Butterworth bandpass filter

    Parameters
    ----------
    x : ndarray
        signal to filter
    fsamp : float
        sampling frequency
    min_freq : float
        cut-off frequency lower bound
    axis : int, optional
        axis to filter, by default -1  (0 for filter along the row, 1 for along the columns)
    order : int, optional
        order of Butterworth filter, by default 4

    Returns
    -------
    ndarray
        filtered_signal
    """
    sos = signal.butter(
        order, min_freq, btype="highpass", fs=fsamp, output="sos", analog=False
    )

    return signal.sosfiltfilt(sos, x, axis=axis)


def number_zero_crossings(x):
    # use this to calculate the number of zero crossings per column
    # of an I x J array or a I dimensional list
    if np.ndim(x) == 1:
        x = np.c_[x]
    return np.sum(x[:-1, :] * x[1:, :] < 0, axis=0)


def df_zero_crossings(df, col=None):
    """
    number of zero crossings of the columns of a dataframe object
    :param df:
    :param col:
    :return: numpy array
    """
    if not col:
        nzc = number_zero_crossings(df.to_numpy())
    else:
        nzc = number_zero_crossings(df.to_numpy())
    return nzc


def number_min(x):
    # use this to calculate the number of minima per column
    # of an I x J array or a I dimensional list
    num_mins = np.zeros(x.shape[1])
    for i in range(0, x.shape[1]):
        num_mins[i] = len(signal.argrelmin(x[:, i], axis=0)[0])
    return num_mins


def number_max(x):
    # use this to calculate the number of maxima per column
    # of an I x J array or a I dimensional list
    num_max = np.zeros(x.shape[1])
    for i in range(0, x.shape[1]):
        num_max[i] = len(signal.argrelmax(x[:, i], axis=0)[0])
    return num_max


def rms(x, axis=None):
    d = np.ndim(x)
    # if d != 2:
    #    raise Exception("rms(x) not specified for arrays of this dimension")
    if axis == None:  # axis=None
        return np.sqrt(np.sum(x * x, axis=None) / x.size)
    elif axis == 0 or axis == 1:
        return np.sqrt(np.sum(x * x, axis=axis) / x.shape[axis])
    else:
        raise Exception("rms(x) not defined for axis = %d", axis)


def mean_power(f, Pxx_den, min_freq, max_freq):
    ind = np.where((f >= min_freq) & (f <= max_freq))[0]
    return np.sum(Pxx_den[ind, :], axis=0)


def dwt_transform(data, wavelet, level=4, axis=0):
    """
    Discrete Time Wavelet transform of the bandpass-filtered data (0. - 50 Hz)
    Args:
        data (ndarray):
        wavelet:
        level:
        axis:

    Returns:

    """
    coef = wavedec(data, wavelet, mode="symmetric", level=level, axis=axis)

    return coef


def dwt_relative_power(
    data, epoch_size, overlap, l=0.99923, N=120, wavelet="db4", level=4, axis=0
):
    """Calculate the relative power feature based on the DWT.

    Args:
        data (ndarray): EEG data (1 channel only)
        epoch_size (int): length of epoch
        overlap (int): length of overlap epochs
        l (float, optional): lambda, forgetting factor. Defaults to 0.99923.
        N (int, optional): Memory index. Defaults to 120.
        wavelet (str, optional): Mother wavelet. Defaults to 'db4'.
        level (int, optional): Number of wavelet transform levels. Defaults to 4.
        axis (int, optional): axis on which to perform DWT. Defaults to 0.

    Raises:
        Exception: If number of channels > 1

    Returns:
        ndarray: N_epochs x N_coef array
    """

    n_data, n_chan = data.shape
    if n_chan > 1:
        raise Exception("relative_power not yet implemented for more than 1 channel")

    n_feature = int(n_data / (epoch_size - overlap))

    rp = np.zeros((n_feature, level + 1))
    FG = np.zeros((n_feature, level + 1))
    BG = np.zeros((1, level + 1))  # initialize background power
    for i, chunk in enumerate(chunker(data, epoch_size, overlap)):
        coef = wavedec(chunk, wavelet=wavelet, mode="symmetric", level=level, axis=axis)
        FG[i, :] = [np.median(c ** 2) for c in coef]  # median(D_i^2)

        if i > N:
            BG = (l - 1) * np.median(
                FG[i - N : i, :], axis=0
            ) + l * BG  # med(FG(e-1)..FG(e-N))
        else:
            BG = (l - 1) * np.median(
                FG[0:i, :], axis=0
            ) + l * BG  # med(FG(e-1)..FG(e-N))

        rp[i, :] = FG[i, :] / BG

    return rp


def line_length(x, axis=0):
    """Calculate the line length feature.

    Args:
        x (ndarray): Data epoch (N, N_chan)
        axis (int, optional): axis along which to calculate the feature. Defaults to 0.

    Returns:
        ndarray: (N_chan,) array with the line length(s)
    """
    diff = np.abs(x[0:-2, :] - x[1:-1, :])

    return np.sum(diff, axis=axis)


def normalize_feature(feature, method="standard", epoch_time=2, buffer=120, labda=0.92):
    # input: np array (cols: features, rows:epochs), epoch length (s), buffer (s)
    # median decaying memory method or standard scaler

    if method == "median-decay":
        z = np.zeros((1, feature.shape[1]))
        memory_epochs = int(buffer / epoch_time)  # num epochs for buffer (s)

        norm_features = np.zeros(feature.shape)
        norm_features[0, :] = feature[0, :]
        for i in range(1, feature.shape[0]):
            old_z = z
            trans = i > memory_epochs  # past max transient duration (buffer)
            index_memory = 0 + (i - memory_epochs + 1) * trans
            z = (1 - labda) * np.median(
                feature[index_memory:i, :], axis=0
            ) + labda * old_z
            norm_features[i, :] = feature[i, :] / z
            scaler = []

    elif method == "standard":
        scaler = StandardScaler()
        scaler.fit(feature)
        norm_features = scaler.transform(feature)

    return norm_features, scaler


def initialize_features(cols):
    """initialize_feature(cols): initializes a dictionary with (empty) dataframes
            for all the features. Names of the channels are given by cols.

    Args:
        cols (list): list of strings containing the names of the channels (columns of the dataframe)

    Returns:
        dict: dictionary of dataframe objects.
    """
    features = {
        "min": pd.DataFrame(columns=cols),
        "max": pd.DataFrame(columns=cols),
        "nzc": pd.DataFrame(columns=cols),
        "skewness": pd.DataFrame(columns=cols),
        "kurtosis": pd.DataFrame(columns=cols),
        "RMS_amplitude": pd.DataFrame(columns=cols),
        "total_power": pd.DataFrame(columns=cols),
        "peak_freq": pd.DataFrame(columns=cols),
        "mean_power_delta": pd.DataFrame(columns=cols),
        "mean_power_theta": pd.DataFrame(columns=cols),
        "mean_power_alpha": pd.DataFrame(columns=cols),
        "mean_power_beta": pd.DataFrame(columns=cols),
        "mean_power_HF": pd.DataFrame(columns=cols),
        "norm_power_delta": pd.DataFrame(columns=cols),
        "norm_power_theta": pd.DataFrame(columns=cols),
        "norm_power_alpha": pd.DataFrame(columns=cols),
        "norm_power_beta": pd.DataFrame(columns=cols),
        "norm_power_HF": pd.DataFrame(columns=cols),
    }

    return features


def feature_extraction(
    edf, param, epoch_time=2, overlap=1, sort_features=True, dataset="train"
):
    """feature_extraction(..) extract the features of a single edf-file.

    Args:
        edf (Edf): Edf object with EEG signals from an edf-file
        param (namedtuple): namedtuple with parameters from the .csv file
        epoch_time (float, optional): length of the epochs/windows in sec. Defaults to 2.0.
        overlap (float, optional): amount of overlap of the epoch/windows in sec. Defaults to 1.0.
        sort_features (bool, optional): options to directly sort the features. Defaults to True.

    Raises:
        Exception: if length of features != length of annotations
        Exception: if nan values found in the features
        Exception: if power in an epoch ~equals zero

    Returns:
        DataFrame: Features.

    """

    assert edf.fs == param.fs, "Loaded edf file has different Fs than specified"
    if dataset == "train":
        epoch_remove = True
    else:
        epoch_remove = False

    fs = param.fs
    epoch_size = epoch_time * fs
    overlap_size = overlap * fs
    min_amplitude = 11  # uV
    max_amplitude = 150  # uV

    if not lf.check_file_duration(edf.file_name):
        return None

    Ts = 1 / fs
    time = np.arange(0, Ts * edf.signals.shape[0], Ts)
    time_chunks = list(chunker(time, epoch_size, overlap_size))
    # ----------------------- features -----------------------------
    i_feat = 0  # feature index
    index_remove = []
    ann_chunks = list(chunker(edf.annotations, epoch_size, overlap_size))
    annotations = []
    feat_start_time = []
    feat_stop_time = []

    # filter the signals
    filtered_signals = bandpass_filter(
        edf.signals.copy(), fs, param.min_frequency, param.max_frequency, axis=0
    )
    orig_signals = highpass_filter(edf.signals.copy(), fs, param.min_frequency, axis=0)

    # apply montage if specified
    if not param.montage:
        cols = edf.channels
    else:
        filtered_signals = lf.apply_montage(
            filtered_signals, edf.channels, param.montage
        )
        orig_signals = lf.apply_montage(orig_signals, edf.channels, param.montage)
        cols = param.montage

    # initialize
    orig_signals = list(chunker(orig_signals, epoch_size, overlap_size))
    features = initialize_features(cols)

    # loop over the segments/chunks
    for i_chunk, epoch in enumerate(
        chunker(filtered_signals, epoch_size, overlap_size)
    ):
        if epoch.shape[0] < epoch_size:  # remove the last if smaller than epoch size
            # remove_time.append(time_chunks[i_chunk][0])
            continue

        # remove epochs with too high/low rms
        if epoch_remove:
            rms_epoch = rms(epoch, axis=0)
            if (np.sum(rms_epoch > max_amplitude) > 3) or (
                np.mean(rms_epoch) < min_amplitude
            ):
                index_remove.append(i_chunk)
                continue
        # elif np.any(rms(epoch, axis=0) < 5 * np.finfo(float).eps):
        #     index_remove.append(i_chunk)
        #     # remove_time.append(time_chunks[i_chunk][0])
        #     continue
        # elif (
        #     np.sum(orig_signals[i_chunk] < np.finfo(float).eps)
        #     > 0.8 * orig_signals[i_chunk].size
        # ):  # remove if most of original signal saturated around 0
        #     index_remove.append(i_chunk)
        #     # remove_time.append(time_chunks[i_chunk][0])
        #     continue

        # -------------- annotations of the features --------------------------
        num_seiz = np.sum(ann_chunks[i_chunk])  # num indices with seiz points
        if num_seiz >= epoch_size - overlap_size:
            annotations.append(1)
            # seizure_id.append(ann_chunks[i_chunk][0])
        # elif -epoch_size < num_seiz < epoch_size:
        #     annotations.append(0)  # part seizure, part non seizure
        #     # seizure_id.append(np.nan)
        else:
            annotations.append(-1)
            # seizure_id.append(np.nan)

        # ------------------ Feature calculation ----------------------------
        features["min"].loc[i_feat] = number_min(epoch)
        features["max"].loc[i_feat] = number_max(epoch)
        features["nzc"].loc[i_feat] = number_zero_crossings(epoch)
        features["skewness"].loc[i_feat] = skew(epoch, axis=0)
        features["kurtosis"].loc[i_feat] = kurtosis(epoch, axis=0, nan_policy="raise")
        features["RMS_amplitude"].loc[i_feat] = rms(epoch, axis=0)

        # -------------- Frequency domain features
        # power spectral density
        f, Pxx_den = welch(epoch, edf.fs, axis=0, nperseg=0.5 * epoch_size)
        # total power
        ind = np.where((f >= param.min_frequency) & (f <= param.max_frequency))[0]
        features["total_power"].loc[i_feat] = np.sum(Pxx_den[ind, :], axis=0)

        # if np.any(features["total_power"].loc[i_feat] < np.finfo(float).eps):
        #     print(edf.file_name)
        # raise Exception("total_power equal to zero. This should not be possible.")
        # peak frequency
        features["peak_freq"].loc[i_feat] = np.max(Pxx_den[ind, :], axis=0)
        # delta band
        features["mean_power_delta"].loc[i_feat] = mean_power(f, Pxx_den, 1, 3)
        # theta band
        features["mean_power_theta"].loc[i_feat] = mean_power(f, Pxx_den, 4, 8)
        # alpha
        features["mean_power_alpha"].loc[i_feat] = mean_power(f, Pxx_den, 9, 13)
        # beta
        features["mean_power_beta"].loc[i_feat] = mean_power(f, Pxx_den, 14, 20)
        # for high frequencies use unfiltered signal
        f, Pxx_den = welch(
            orig_signals[i_chunk], edf.fs, axis=0, nperseg=0.5 * epoch_size
        )
        # HF 40-80
        features["mean_power_HF"].loc[i_feat] = mean_power(f, Pxx_den, 40, 80)

        # feature time
        feat_start_time.append(time_chunks[i_chunk][0])
        feat_stop_time.append(time_chunks[i_chunk][-1])

        # continue counting features
        i_feat += 1

    features["norm_power_delta"] = (
        features["mean_power_delta"] / features["total_power"]
    )
    features["norm_power_theta"] = (
        features["mean_power_theta"] / features["total_power"]
    )
    features["norm_power_alpha"] = (
        features["mean_power_alpha"] / features["total_power"]
    )
    features["norm_power_beta"] = features["mean_power_beta"] / features["total_power"]
    features["norm_power_HF"] = features["mean_power_HF"] / features["total_power"]

    # '0/0' situation fill nan values
    features["norm_power_delta"].fillna(method="ffill", inplace=True)
    features["norm_power_theta"].fillna(method="ffill", inplace=True)
    features["norm_power_alpha"].fillna(method="ffill", inplace=True)
    features["norm_power_beta"].fillna(method="ffill", inplace=True)
    features["norm_power_HF"].fillna(method="ffill", inplace=True)

    # convert to numpy array
    annotations = np.array(annotations)
    feat_start_time = np.array(feat_start_time)
    feat_stop_time = np.array(feat_stop_time)

    assert len(annotations) == len(
        features["min"]
    ), "Length of annotations should be equal to number of features."

    # Combine everything into 1 dataframe
    df = pd.concat(features.values(), axis=1, keys=features.keys())

    # sort features large to small
    if sort_features:
        df = ds.sort_features(df)

    df.columns = ["|".join([str(val) for val in col]) for col in df.columns.values]
    add_columns = {
        "epoch": df.index,
        "annotation": annotations,
        "start_time": feat_start_time,
        "stop_time": feat_stop_time,
    }
    df = pd.concat((pd.DataFrame(add_columns, index=df.index), df), axis=1)
    df["filename"] = edf.file_name

    assert not np.any(df.isnull()), "Found nan values in the features."

    return df  # dataframe with features


if __name__ == "__main__":
    from config import TUSZ_DIR, PARAMETERS
    from load_functions import load_edf, load_parameters
    from plot_eeg_data import plot_eeg

    file = (
        TUSZ_DIR
        + "/train/01_tcp_ar/044/00004456/s015_2014_06_19/00004456_s015_t002.edf"
    )
    param = load_parameters(PARAMETERS)
    edf = load_edf(file, param, annotate=True)
    # plot_eeg(edf.signals, edf.channels, edf.fs)
    temp_df = feature_extraction(edf, param)
