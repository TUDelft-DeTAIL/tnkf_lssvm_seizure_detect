import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import sys

from tusz_data_processing.load_functions import load_edf, load_parameters, Edf
from tusz_data_processing.config import TUSZ_DIR, PARAMETERS


def plot_eeg(data, channels=None, fsamp=None):

    if isinstance(data, pd.DataFrame):
        channels = data.columns.to_list()

        if "time" in channels:
            if fsamp == None:
                fsamp = np.round(1 / (data["time"].iloc[1] - data["time"].iloc[0]))
            channels.remove("time")
        elif "time" not in channels and fsamp == None:
            time = data.index.to_numpy()
            fsamp = np.round(1 / (time[1] - time[0]))

        signals = data.to_numpy()
        signals = np.transpose(signals)
    elif isinstance(data, Edf):
        channels = data.channels
        fsamp = data.fs
        signals = np.transpose(data.signals)
    elif isinstance(data, np.ndarray):
        if channels == None or fsamp == None:
            print("channels and sampling frequency not specified")
            exit(0)
        num_channels = len(channels)
        if data.shape[0] == num_channels:
            signals = data
        elif data.shape[1] == num_channels:
            signals = np.transpose(data)
        else:
            print(
                "Dimension mismatch number of channels in array does not match channels list"
            )
            exit(0)

    info = mne.create_info(channels, fsamp, ch_types="eeg")
    raw = mne.io.RawArray(signals * 1e-6, info)
    raw.plot()

    return


def plot_eeg_hist(data, channels, width=4, bins="auto"):
    # sns.set()
    num_channels = len(channels)
    height = int(np.ceil(num_channels / width))

    fig, axs = plt.subplots(height, width, sharey=True)
    # fig.subtitle("Hist of channels")
    for i, ax in enumerate(fig.axes):
        if i > num_channels - 1:
            break
        ax.set_title(channels[i])

        cur_ax = sns.histplot(ax=ax, data=data[:, i], bins=bins)
        # x0, x1 = cur_ax.get_xlim()
        # mu, std = norm.fit(data[:, i])
        # x_norm = np.linspace(x0, x1, 100)
        # y_norm = norm.pdf(x_norm, mu, std)
        # cur_ax.plot(x_norm, y_norm, 'r', label='pdf')
        # cur_ax.legend()
        # axs[i].hist(data[:,i])
        # axs[i].plt(data[:,i])
    plt.show()
    return


if __name__ == "__main__":
    from src.tusz_data_processing.load_functions import load_edf, Edf

    fname = (
        TUSZ_DIR
        + "/train/02_tcp_le/044/00004473/s001_2008_02_11/00004473_s001_t000"
        + ".edf"
    )
    param = load_parameters(PARAMETERS)
    edf = load_edf(fname, param)
    plot_eeg_hist(edf.signals, edf.channels)
