"""
    Set global variables.
"""
DATA_DIRECTORY = "<absolute_path_to_code_directory>/data"

PARAMETERS = DATA_DIRECTORY + "/parameters.csv"

PATIENTS = [
    258,
    473,
    529,
    1543,
    2297,
    2806,
    3208,
    3636,
    3977,
    4434,
    4473,
    5452,
    5943,
    6083,
    6413,
    6507,
    7234,
]

SQLITE_DB = DATA_DIRECTORY + "/tuh_seiz_annotate.db"

ENGINE_URL = "sqlite:///" + SQLITE_DB

HEADER_FILE = DATA_DIRECTORY + "/header.csv"

TUSZ_DIR = "<path_to_TUSZ_database>/edf"

SEIZ_ANNOTATIONS = TUSZ_DIR + "/../_DOCS/seizures_v36r.xlsx"

FEATURES_DIR = "<path_to_a_directory>/Features"

PROJECT_DRIVE = "<directory used to store results and TUSZ data>"

DELIM_FEAT_CHAN = "|"
