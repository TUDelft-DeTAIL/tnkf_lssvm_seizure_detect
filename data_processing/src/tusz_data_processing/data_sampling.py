import numpy as np
import pandas as pd
import primefac
from imblearn.over_sampling import SMOTE, RandomOverSampler
from scipy.io import savemat

# from imblearn.under_sampling import RandomUnderSampler
# from random import sample

# import os
import ast

# sys.path.append(".")

from tusz_data_processing.load_functions import (
    load_features,
    load_val_groups,
)
from tusz_data_processing.config import ENGINE_URL
from sqlalchemy import create_engine


def determine_quantization_par(n: int, max_rank=19) -> int:
    """Determine new quantization parameter.

    Args:
        n (int): Old size of dataset/vector.
        max_rank (int, optional): Maximum rank for TT. Defaults to 7.

    Returns:
        int: New dataset size/ quantization par.
    """

    n_new = n
    q = list(primefac.primefac(n_new))
    if len(q) == 0:
        return n_new

    while max(q) > max_rank:
        n_new = n_new - 1
        q = list(primefac.primefac(n_new))

    return n_new


def features_to_multiindex(df):
    """Convert the feature col names to a multiindex

    Args:
        df (DataFrame): with single index

    Returns:
        DataFrame: with multiindex
    """
    col_list = df.columns
    tuple_list = []
    for col in col_list:
        tuple_list.append(ast.literal_eval(col))

    mult_index = pd.MultiIndex.from_tuples(tuple_list)
    df.columns = mult_index
    return df


def oversample_data(
    features: pd.DataFrame, method="SMOTE"
) -> tuple[np.ndarray, np.ndarray]:
    """Oversample the minory class.

    Args:
        features (pd.DataFrame): Dataframe with feature and "annotation" column.
        method (str, optional): Oversampling method. Defaults to "SMOTE".

    Returns:
        tuple[np.ndarray, np.ndarray]: X : features, y: labels
    """
    y = features["annotation"].copy()
    X = features.drop(columns=["annotation"])

    if method == "SMOTE":
        X, y = SMOTE().fit_resample(X, y)
    elif method == "random":
        X, y = RandomOverSampler(random_state=0).fit_resample(X, y)

    # features.loc[:, ]

    return X, y


def undersample_data(
    features: pd.DataFrame, N_min: int, method="random"
) -> pd.DataFrame:
    """Undersample the data.

    Args:
        features (pd.DataFrame): Dataframe with the feature and "annotation" column.
        N_min (int): Amount of samples for majority class.
        method (str, optional): Undersampling method. Defaults to "random".

    Returns:
        pd.DataFrame: Dataframe with features. 
    """

    if method == "random":
        feats_min = features[features["annotation"] == -1].sample(
            n=N_min, replace=False, axis=0
        )
    else:
        raise "Undersampling method not yet defined"
    feats = pd.concat([feats_min, features[features["annotation"] == 1]])
    return feats


def create_balanced_trainset(
    features: pd.DataFrame, N: int, method="SMOTE"
) -> tuple[np.ndarray, np.ndarray]:
    """Create a balanced training set.

    Args:
        features (pd.DataFrame): Features dataframe with "annotation" column
        N (int): New number of data points
        method (str, optional): Oversampling method. Defaults to "SMOTE".

    Raises:
        Exception: If there is too much undersampling

    Returns:
        tuple[np.ndarray, np.ndarray]: X: features, y: labels.
    """
    if (N % 2) != 0:
        N = N + 1
        add1 = True
    else:
        add1 = False

    N_min = int(N / 2)
    num_min_class = len(features[features["annotation"] == 1])
    if num_min_class > N_min:
        raise Exception("Undersampling too much, choose larger N")

    features = undersample_data(features.copy(), N_min)

    X, y = oversample_data(features, method=method)

    assert len(y) == N
    if add1:
        X.drop(X.tail(1).index, inplace=True)
        y.drop(y.tail(1).index, inplace=True)

    return X, y


def save_features_to_sql(sql_engine, feature_data):
    """
    Save feature to SQL database
    ...

    Parameters
    ----------
    sql_engine : ENGINE object
        SQL engine object
    feature_data : DataFrame
     DataFrame containing the features

    Returns
    -------

    """
    sqlite_table = "Sorted_Features"
    # feature_data.columns = feature_data.columns.to_flat_index()
    feature_data["feat_id"] = feature_data.index
    feature_data = feature_data.convert_dtypes()
    dict_types = get_sqlite_types(feature_data)
    feature_data.to_sql(
        sqlite_table, con=sql_engine, if_exists="replace", index=False, dtype=dict_types
    )
    return


def get_sqlite_types(df):
    df = df.convert_dtypes()
    # df_types = df.infer_objects().dtypes
    int_cols = df.select_dtypes(include=["int"]).columns
    float_cols = df.select_dtypes(include=["float"]).columns
    text_cols = df.select_dtypes(include=["object"]).columns
    bool_cols = df.select_dtypes(include=["bool"]).columns

    dict_types = {i: INTEGER() for i in int_cols}
    dict_types.update({i: REAL() for i in float_cols})
    dict_types.update({i: TEXT() for i in text_cols})
    dict_types.update({i: BOOLEAN() for i in bool_cols})

    return dict_types


def save_to_mat(X_train, y_train, X_test, y_test, filename):

    mdic = {"X_train": X_train, "y_train": y_train, "X_test": X_test, "y_test": y_test}

    return savemat(filename, mdic)


def sort_features(features, anncols=None):
    """
    Sort the features to eliminate 'location' dependency for patient-independent
    classification.
    Args:
        features: DataFrame with the features, this dataframe has a multi-index with the second layer being the channels.

    Returns:
        DataFrame object with sorted features.
    """
    num_channels = features.columns.get_level_values(1).nunique()
    feature_names = features.columns.get_level_values(0).unique().to_list()
    new_multindex = pd.MultiIndex.from_product([feature_names, range(num_channels)])

    features.columns = new_multindex
    # features = features.apply(lambda row: row.groupby(level=0).apply(lambda x: x.sort_values(ascending=False, key=abs)), axis=0)
    # for i, row in features.iterrows():
    #     # sort values by their largest magnitude
    #     new_row = row.groupby(level=0).apply(lambda x: x.sort_values(ascending=False, key=abs)).copy(deep=True)
    #     new_row = new_row.droplevel(0)
    #     new_row.index = pd.MultiIndex.from_arrays(
    #         [new_row.index.get_level_values(0), new_row.groupby(level=0).cumcount()])
    #     features.loc[i, new_row.index] = new_row
    for i, feat in enumerate(feature_names):
        feat_i = features[feat].to_numpy()
        feat_i = np.flip(np.sort(feat_i, axis=1), axis=1)
        features[feat] = feat_i
        # feat_i = feat_i.apply(lambda x: x.sort_values(
        #     ascending=False, key=abs).reset_index(drop=True), axis=1)
        # feat_i.columns = pd.MultiIndex.from_product([[feat], range(num_channels)])
        # sorted_feat.append(feat_i)

    # sorted_features = pd.concat(sorted_feat)
    # return sorted_features
    return features


def patient_specific_sampling(
    features, patient, validation_groups, num_points, save_folder, oversample="SMOTE"
):
    """
    This function creates balanced datasets for a specific patient using a
    combination of over- and undersampling.

    Args:
        features: DataFrame containing the features
        patient: patient ID
        validation_groups: DataFrame with the validations groups
        num_points: number of datapoints for the new balanced dataset
        save_folder: folder to save the created balanced datasets
        oversample: (opt.) oversampling technique (default = SMOTE)

    Returns:

    """
    # ensure only features from the specified patient are used
    validation_groups = validation_groups.loc[val_groups["Patient"] == patient]
    # get the seizure 'groups' for leave-one-out cross-validation
    seizure_groups = validation_groups["seizure_group"].unique()
    for (i, seizure) in enumerate(seizure_groups):
        # -------- test set --------------
        test_idx = validation_groups.index[
            validation_groups["seizure_group"] == seizure
        ]
        test_set = features.loc[test_idx].copy()
        test_set = test_set[test_set["annotation"] != 0]
        y_test = test_set["annotation"].to_numpy()
        test_set.drop(columns=["annotation"], inplace=True)
        X_test = test_set.to_numpy()
        # ----------- train set ----------------------
        train_idx = validation_groups.index[
            validation_groups["seizure_group"] != seizure
        ]
        train_set = features.loc[train_idx].copy()
        train_set = train_set[train_set["annotation"] != 0]
        X_train, y_train = create_balanced_trainset(
            train_set, num_points, method=oversample
        )
        # ---------- save to mat file -----------------------
        filename = (
            save_folder
            + "/patient_dependent/"
            + str(patient)
            + "/"
            + oversample
            + "/leave_"
            + str(seizure)
            + "_out.mat "
        )
        save_to_mat(X_train.to_numpy(), y_train.to_numpy(), X_test, y_test, filename)
    return


if __name__ == "__main__":
    #%% # patient = 4473
    engine = create_engine(ENGINE_URL)
    # features = load_sorted_features(engine)
    patient = 4473
    features = load_features(engine, patients=patient, only_features=True)
    # annotations = features.loc[:, 'annotation']
    # features.drop(columns=['annotation'], inplace=True)
    # features = features_to_multiindex(features)
    # num_channels = features.columns.get_level_values(1).nunique()
    # feature_names = features.columns.get_level_values(0).unique().to_list()
    # new_multindex = pd.MultiIndex.from_product([feature_names, range(num_channels)])
    val_groups = load_val_groups(engine)
    # sorted_features = sort_features(features.copy())
    # # # %%
    # # temp = features.iloc[0:100, :]
    # # df = sort_features(temp.copy())
    # # sorted_features = pd.concat([annotations, sorted_features])
    # sorted_features.columns = sorted_features.columns.to_flat_index()
    # sorted_features['annotations'] = annotations
    # save_features_to_sql(engine, sorted_features)

    #
    N = 4e4
    Npat = 5240
    patient = 4473
    save_folder = r"U:\Seizure Data\validation_folds"
    patient_specific_sampling(
        features, patient, val_groups, Npat, save_folder, oversample="SMOTE"
    )
    #%%

    # patients = val_groups['Patient'].unique()
    # for patient in patients:
    #     # ------ test set --------------
    #     test_idx = val_groups.index[val_groups['Patient'] == patient]
    #     test_set = features.loc[test_idx].copy()
    #     y_test = test_set['annotation'].to_numpy()
    #     test_set.drop(columns=['annotation'], inplace=True)
    #     X_test = test_set.to_numpy()
    #     # ----------- train set ----------------------
    #     train_idx = val_groups.index[val_groups['Patient'] != patient]
    #     train_set = features.loc[train_idx].copy()
    #     X_train, y_train = create_balanced_trainset(train_set, N, method='random')
    #     # ---------- save to mat file -----------------------
    #     filename = save_folder + "\oversample" + "\leave_" + str(patient) + "_out.mat"
    #     save_to_mat(X_train.to_numpy(), y_train.to_numpy(), X_test, y_test, filename)

    # new_feat, y_new = create_balanced_trainset(features, N)
