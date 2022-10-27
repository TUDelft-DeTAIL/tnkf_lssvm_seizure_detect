#!/bin/sh
#

if [ -z "${TRAIN_FILE}" ]; then # if empty then to default
    FEATURE_DIR="<path_to_features>"
    TRAIN_FEATURES="${FEATURE_DIR}balanced_train_random.parquet"
    TRAIN_FILE="${FEATURE_DIR}train/data.mat"
    KERNEL_FILE="${FEATURE_DIR}train/kernel_rows/kernel_rows"
    PARAMETERS="parameters.json"
fi

N=40
joblist=""
echo N=$N
# for ((i=0; i<$N; i++))
for i in 8 14 15 23 
do 
    echo i=$i
    sbatch --export=i=$i,N=$N --job-name="kernel_rows_$i" kernel_rows_slurm.sh
done

echo "Jobs submitted"