# Classification

This folder contains all the code for the classifier (TNKF-LSSVM). 
It also contains the following external packages:
- [LS-SVMlab](lssvmlab) available at [https://www.esat.kuleuven.be/sista/lssvmlab/](https://www.esat.kuleuven.be/sista/lssvmlab/)
- [natsort](natsort) by Stephen23, available on [MATLAB file exchange](https://www.mathworks.com/matlabcentral/fileexchange/47434-natural-order-filename-sort). 

Please note that the rights to these packages are **not** my own, and the license provided does not include these packages!

## Hyperparameters

### TNKF-LSSVM
In the paper results were presented of the TNKF-LSSVM when trained on a 'small' sample and trained on a 'large' sample. The corresponding hyperparameters can be found in the files: 
- [parameters_small.json](parameters_small.json)
- [parameters_large.json](parameters_large.json)

### LS-SVM
The hyperparameters for the LS-SVM were: 
- $\sigma^2 = 2.6\times 10^3$
- $\gamma = 150$

## Notes on the code
The coding was done with MATLAB version 2021b. To initialize and add the required function to the Matlab search path run:

    setup

There is also a [config](config.m) file which contains the path to the directory with the features. 

The [pipeline](pipeline/) folder contains the scripts and function used in the training and prediction pipeline. It also contains the scripts used for the training and tuning of the LS-SVM reference method ([reference_method](pipeline/reference_method)).

For large-scale classification a SLURM cluster was used to parallelize the kernel rows calculation. The corresponding submission scripts are found in the [slurm](slurm/) folder (without account ID).

## Using a SLURM cluster

Order of submission to the cluster (wait for step to be finished before continuing).
1) Run `sbatch feat_to_mat.sh `
2) Run `kernel_rows.sh` to calculate and save the rows of the kernel matrix. Check that the rows have all been calculated and updated. 
3) Run `sbatch train.sh` to train the TNKF-LSSVM model, corresponding to the calculated kernel rows
4) Run `sbatch validate.sh` to validate the results.