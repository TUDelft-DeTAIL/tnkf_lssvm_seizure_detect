#!/bin/sh
#
#SBATCH --job-name="update_param"
#SBATCH --partition=compute
#SBATCH --time=00:10:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G

echo "Loading required modules"
module load 2022r2
module load matlab


# VARIABLES
FEATURE_DIR="<path_to_features>"
TRAIN_FEATURES="${FEATURE_DIR}balanced_train.parquet"
VAL_FEATURES="${FEATURE_DIR}val.parquet"
TRAIN_FILE="${FEATURE_DIR}train/data.mat"
KERNEL_FOLDER="${FEATURE_DIR}train/kernel_rows/"
PARAMETERS="parameters.json"
SAVE_FILE="${FEATURE_DIR}train/trained_model.mat"
RESULTS="${FEATURE_DIR}results/"

echo "Starting MATLAB"
matlab -nodisplay -batch "run('setup.m'); update_param('$TRAIN_FILE','$PARAMETERS');"

echo "Exiting code 0"