#!/bin/sh
#
#SBATCH --job-name="check_rows"
#SBATCH --partition=compute
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=24G

echo "Loading required modules"
module load matlab


FEATURE_DIR="<path_to_features>"
TRAIN_FEATURES="${FEATURE_DIR}balanced_train.parquet"
TRAIN_FILE="${FEATURE_DIR}train/data.mat"
KERNEL_FOLDER="${FEATURE_DIR}train/kernel_rows/"
PARAMETERS="parameters.json"
SAVE_FILE="${FEATURE_DIR}train/trained_model.mat"


echo "Starting MATLAB"
matlab -nodisplay -batch "run('setup.m'); check_rows('$KERNEL_FOLDER');"

echo "Exiting code 0"