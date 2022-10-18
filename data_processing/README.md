# Data Processing
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This folder contains the code used for pre- and post-processing.

## Start up
The code was developed with Python version 3.9. 
The used packages and their version number are listed in [requirements.txt](requirements.txt).

To install the packages in you python (virtual) environment, use:

    pip install requirements.txt

Furthermore, to ensure that import of the self-created package goes correctly the `tusz_data_processing` package was created.
In this package the is a [config_example.py](src/tusz_data_processing/config_example.py) file, which contains an example 
of a config file. A config file should contain all of the paths to the data. To create you own:

    cd src/tusz_data_processing
    cp config_example.py config.py

And fill in your path directories. 

After this you can install `tusz_data_processing` by doing the following:

    cd src/
    pip install -e .

This installs the [tusz_data_processing](src/tusz_data_processing/) 'package'.





