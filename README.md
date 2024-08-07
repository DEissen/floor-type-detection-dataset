# The Floor-Type-Detection-Dataset (FTDD) repository
Repository for the floor type detection dataset (FTDD/ FTD Dataset) recorded with the [Unitree Go1 Edu robot dog](https://www.unitree.com/go1/) by using the code from [data-collection-unitree-go1](https://github.com/DEissen/data-collection-unitree-go1) repository.

# How to use the FTDDataset class
1. Import the class FloorTypeDetectionDataset() class from file ./FTDDataset.py
2. Consider the parameters for your dataset class:
    - *root_dir (str):* Path to prepared dataset
    - *sensors (list):* List of all sensors which shall be considered
    - *run_path (str):* Run path to previous run from where config can be loaded. If run_path == "" the default config from the repo will be used.
    - [Optional] *create_faulty_data (bool):* Default = False. Select whether faulty data shall be created or not. No data modification will happen, if create_faulty_data == False.
3. [Optional] Change config to your needs. The following config files are relevant for the dataset creation:
    - *configs/faulty_data_creation_config.json:* Config for failure case creation (selection of parameters for data modification and which sensors shall be modified)
    - *configs/label_mapping.json:* Mapping of label name to integer value.
    - *configs/preprocessing_config.json:* Config for the data preprocessing, e.g. image cropping and resizing
4. Create list with sensor names which shall be used, e.g.: *sensors = ["accelerometer", "BellyCamRight"]*
5. Create instance of FloorTypeDetectionDataset() class by providing parameters from step 2
6. Use the dataset as every other PyTorch dataset

# Folder structure and module descriptions
This section contains a brief overview about all files in the repository. The code is structured in four modules/subfolder which contain code for different purposes.
- **configs/** \
This directory contains all config files for data preparation and dataset creation.
    - *faulty_data_creation_config.json:* Config file for failure case creation
    - *label_mapping.json:* Mapping of label name to integer value when complete dataset is used
    - *preprocessing_config.json:* Config file for the data preprocessing, e.g. image cropping and resizing used in data preparation and when dataset is used by FloorTypeDetectionDataset() class
- **custom_utils/** \
This module contains some custom utility functions used in the repository.
    - *utils.py:* Utility functions to handle data (copy data and clear temporary directories)
- **failure_case_creation/** \
This module contains all code related to data manipulation for failure case creation.
    - *frostX.png* (with X = [1,6]): Images to be used for frost() failure case 
    - *modify_images.py:* Functions to modify images from dataset
    - *modify_timeseries.py:* Functions to modify timeseries data from dataset
- **fisheye_calibration** \
Contains files for a prototype of correction of fisheye perspective. Not used anywhere else in the repo and thus further explained.
- **testdata/** \
This directory contains some example data, so you can run *data_preparation_main.py* by default to get an idea of how to use it.
- *example_data.png*: Image showing example data for README.md
- *FTDDataset.py*: File containing the FTDDataset() class including an example of how to use it at the end of the file
- *LICENSE.txt*: License file
- *README.md*: The file you are reading right now :)
- *requirements.txt*: File which lists the used python packages

# Supported sensors and example data
In theory two kinds of sensors are supported:
- Sensors with "Cam" in their directory name will be handled as cameras (including data preprocessing, ...) 
- Every other sensor will be handled as timeseries sensor (including normalization, ...) 

Still, you should always check for incompatibilities when adding new sensors. Here is a full list of the sensors currently expected and supported:
- accelerometer
- BellyCamLeft
- BellyCamRight
- bodyHeight
- ChinCamLeft
- ChinCamRight
- footForce
- gyroscope
- HeadCamLeft
- HeadCamRight
- LeftCamLeft
- LeftCamRight
- mode
- RightCamLeft
- RightCamRight
- rpy
- velocity
- yawSpeed

Here is an example of the camera images (without preprocessing) and the corresponding accelerometer data which can be also found in **testdata/** directory:
![Example data](./example_data.png)
# Authors
- Dominik Eißen (st177975@stud.uni-stuttgart.de)