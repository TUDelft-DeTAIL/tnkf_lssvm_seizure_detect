#!/bin/sh
#
#SBATCH --job-name="kernel_rows_%j"
#SBATCH --partition=compute
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G

echo "Loading required modules"
module load matlab

if [ -z "${TRAIN_FILE}" ]; then # if empty then to default
    FEATURE_DIR="<path_to_features>"
    TRAIN_FEATURES="${FEATURE_DIR}balanced_train_random.parquet"
    TRAIN_FILE="${FEATURE_DIR}train/data.mat"
    KERNEL_FILE="${FEATURE_DIR}train/kernel_rows/kernel_rows"
    PARAMETERS="parameters.json"
fi

echo i=$i
echo N=$N

echo "Starting matlab"
matlab -nodisplay -batch "run('setup.m'); kernel_rows_slurm('$TRAIN_FILE', '$KERNEL_FILE', $N, $i);" 