#!/bin/sh
#
#SBATCH --job-name="val_TT"
#SBATCH --partition=compute
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G

echo "Loading required modules"
module load matlab

# VARIABLES
if [ -z "${TRAIN_FILE}" ]; then
    FEATURE_DIR="<path_to_features>"
    TRAIN_FEATURES="${FEATURE_DIR}balanced_train.parquet"
    VAL_FEATURES="${FEATURE_DIR}dev.parquet"
    TRAIN_FILE="${FEATURE_DIR}train/data.mat"
    # PARAMETERS="parameters.json"
    SAVE_FILE="${FEATURE_DIR}train/trained_model_1.mat"
    RESULTS="${FEATURE_DIR}results/"
fi

N_WORKERS=$(($SLURM_CPUS_PER_TASK-1))

# function validate(VALIDATION_FEATURES, TRAINED_MODEL, TRAINING_FILE, RESULTS_DIR)
echo "Starting MATLAB"
matlab -nodisplay -batch "run('setup.m'); parpool($N_WORKERS);validate('$VAL_FEATURES','$SAVE_FILE','$TRAIN_FILE','$RESULTS');"

echo "Exiting code 0"