#!/bin/sh
#
#SBATCH --job-name="train_TT"
#SBATCH --partition=compute
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=24G

echo "Loading required modules"
module load matlab

if [ -z "${TRAIN_FILE}" ]; then
    FEATURE_DIR="<path_to_features>"
    TRAIN_FEATURES="${FEATURE_DIR}balanced_train_random.parquet"
    TRAIN_FILE="${FEATURE_DIR}train/data.mat"
    KERNEL_FOLDER="${FEATURE_DIR}train/kernel_rows/"
    PARAMETERS="parameters.json"
    SAVE_FILE="${FEATURE_DIR}train/trained_model_1.mat"
fi

echo "Starting MATLAB"
matlab -nodisplay -batch "run('setup.m'); train_model('$TRAIN_FILE', '$KERNEL_FOLDER', '$SAVE_FILE');"

echo "Exiting code 0"
