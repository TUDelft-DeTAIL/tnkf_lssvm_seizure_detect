#!/bin/sh
#
#SBATCH --job-name="feat_to_mat"
#SBATCH --partition=compute
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G
#SBATCH --mail-type=END,FAIL

echo "Loading required modules"
module load matlab

oversamp="random"
if [ -z "${TRAIN_FILE}" ]; then # if empty then to default
    FEATURE_DIR="<path_to_features>"
    TRAIN_FEATURES="${FEATURE_DIR}balanced_train_$oversamp.parquet"
    TRAIN_FILE="${FEATURE_DIR}train/data.mat"
    KERNEL_FILE="${FEATURE_DIR}train/kernel_rows/kernel_rows"
    PARAMETERS="parameters.json"
fi

echo "Starting matlab"

matlab -nodisplay -batch "run('setup.m'); features_to_mat('$TRAIN_FEATURES', '$TRAIN_FILE', '$PARAMETERS'); exit"
