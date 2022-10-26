# Data Processing
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This folder contains the code used for pre- and post-processing. 
The code assumes the use of the [TUSZ database](https://isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml) from Temple University. 
The `nedc_eval_eeg` package from the TUSZ database is used for algorithm evaluation (in the [score](score/) folder).

## Start up
The code was developed with Python version 3.9. 
The used packages and their version number are listed in [requirements.txt](requirements.txt).

To install the packages in your python (virtual) environment, use:

    pip install requirements.txt

Furthermore, to ensure that the import of the self-created function goes correctly the `tusz_data_processing` package was created.
In this package there is a [config_example.py](src/tusz_data_processing/config_example.py) file, which contains an example 
of a config file. A config file should contain all of the paths to the data and an empty folder for the features. To create your own:

    cd src/tusz_data_processing
    cp config_example.py config.py

And fill in your own path directories. 

After this you can install `tusz_data_processing` by doing the following:

    cd src/
    pip install -e .

This installs the [tusz_data_processing](src/tusz_data_processing/) 'package'.






