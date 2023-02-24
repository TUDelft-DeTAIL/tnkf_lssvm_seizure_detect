# TNKF-LSSVM for Seizure Detection

Public repo for paper: "Enabling Large-Scale Probabilistic Seizure Detection with a Tensor-Network Kalman Filter for LS-SVM" by S.J.S de Rooij, K. Batselier and B. Hunyadi.

## Code
The code in this repository is divided into two sections [classification](classification/) and [data_processing](data_processing/). 
- The `data_processing` section contains all the code used for pre- and post-processing (including feature extraction). This code is in Python.
- The `classification` section contains code for the TNKF-LSSVM classifier and the regular LS-SVM classifier (including LSVMlab code). This part of the code was done in MATLAB. 

The package dependencies of both code bases are listed in the respective folders.

For the hyperparameters go [here](https://github.com/sderooij/tnkf_lssvm_seizure_detect/tree/main/classification#hyperparameters).


## Citation
When using the code please cite our paper (a `citation.cff` file will be added to specify how to cite).






