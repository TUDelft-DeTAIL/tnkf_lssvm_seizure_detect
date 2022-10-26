"""
    Preprocess the training data:
        - load the training edf files
        - extract features from the data
        - remove "bad" data
        - save features in separate files
        - construct full dataset to use for training using undersampling and SMOTE
        - save to .parquet file
"""

# from standard lib
import multiprocessing
import os
from glob import glob
from functools import partial

# external libs
# import numpy as np
import pandas as pd

# self made modules
# (if it doesn't work first run `pip install -e ./src/` , to add modules)
import tusz_data_processing.load_functions as lf
from tusz_data_processing.feature_functions import feature_extraction
import tusz_data_processing.data_sampling as ds

from tusz_data_processing.config import (
    TUSZ_DIR,
    PARAMETERS,
    FEATURES_DIR,
    PROJECT_DRIVE,
    DATA_DIRECTORY,
)

"""
    Global Variables
"""
CREATE_FEAT_PARQUET = True
CREATE_BALANCED_SET = False
SORT_FEATURES = True
DEBUG = False
DATASET = "eval"  # other options: 'dev' or 'eval', or 'all'

"""
    Function definitions
"""


def get_feat_df(file, dataset):
    """main(file) loads the parameters and edf-file and then extract the features for that file

    Args:
        file (str): string containing the directory of the edf-file

    Returns:
        DataFrame: dataframe with the features.
    """
    param = lf.load_parameters(PARAMETERS)
    edf = lf.load_edf(file, param, annotate=True)
    df = feature_extraction(
        edf,
        param,
        param.epoch_time,
        param.epoch_overlap,
        sort_features=SORT_FEATURES,
        dataset=dataset,
    )

    return df


def main(dataset):
    # get names and dirs of all edf files
    edf_files = [
        y
        for x in os.walk(TUSZ_DIR + "/" + dataset + "/")
        for y in glob(os.path.join(x[0], "*.edf"))
    ]

    # PARALLEL processing
    pool_obj = multiprocessing.Pool()
    df_list = pool_obj.map(partial(get_feat_df, dataset=dataset), edf_files)
    # remove None outputs (mostly for eval set --> if annotations incorrect)
    df_list = list(filter(lambda item: item is not None, df_list))
    df = pd.concat(df_list)  # concatenate the list of all dataframes
    del df_list  # delete list from memory
    # remove TUSZ directory from filename (since it can be different for different PC's)
    df.loc[:, "filename"].replace(TUSZ_DIR, "", regex=True, inplace=True)

    # try:
    #     df.to_parquet(PROJECT_DRIVE + "v1.5.2/Features/train.parquet")
    # except FileNotFoundError:   # if project drive not mounted save locally
    try:
        print("Project Drive not mounted, saving features locally.")
        df.to_parquet(FEATURES_DIR + "/" + dataset + ".parquet")
    except:
        print("Not able to save the features.")
        exit(-1)

    return


"""
    main script
"""
if __name__ == "__main__":
    if DEBUG:
        try:
            filepath = os.path.abspath(__file__)
            dirpath = os.path.dirname(filepath)
            os.chdir(dirpath)
        except:
            print("running in ipython kernel?")

        # files = pd.read_csv(DATA_DIRECTORY + "/nan_files.csv")
        # # files.loc[:,"filename"] = TUSZ_DIR + files.loc[:,"filename"]
        #
        # for index, file in files.iterrows():
        #     df = get_feat_df(TUSZ_DIR + file['filename'])
        #     # break
        df = get_feat_df(
            TUSZ_DIR
            + "/train/02_tcp_le/050/00005095/s001_2008_10_30/00005095_s001_t001.edf"
        )

    if CREATE_FEAT_PARQUET:

        if DATASET == "all":
            for data_set in ["train", "dev", "eval"]:
                main(data_set)
        else:
            main(DATASET)

    if CREATE_BALANCED_SET:
        # GLOBAL VARS
        METHOD = "random"
        FEATURES_FILE = FEATURES_DIR + "/train.parquet"
        DELIM_FEAT_CHAN = "|"

        # LOAD PARQUET
        df = pd.read_parquet(FEATURES_FILE)
        df.sort_index(inplace=True)
        feat_cols = [col for col in df.columns if DELIM_FEAT_CHAN in col]
        feat_cols.append("annotation")
        df = df.loc[:, feat_cols].copy()

        # CREATE BALANCED SET
        # Get new dataset size to enable easy quantization
        N_old = len(df)
        N_new = ds.determine_quantization_par(
            N_old, max_rank=7
        )  # no -1 should be quantisizable
        feats, labels = ds.create_balanced_trainset(df, N_new, method=METHOD)
        assert len(labels) == N_new
        del df
        feats["annotation"] = labels
        # new_df = pd.DataFrame(pd.concat((feats,labels)), columns=['annotation']+feat_cols)
        feats.to_parquet(FEATURES_DIR + "/balanced_train_" + METHOD + ".parquet")
