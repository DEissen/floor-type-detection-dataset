# The Floor-Type-Detection-Dataset (FTDD) repository
Repository for the floor type detection dataset (FTDD/ FTD Dataset) recorded with the Unitree Go1 Edu robot dog by using the code from [Unitree-Go1-Edu](https://github.tik.uni-stuttgart.de/ac136427/Unitree-Go1-Edu) repository. The program is split in two parts:
1. Data preparation: Prepare raw measurement data to be easily loadable by a custom PyTorch dataset class (including unification of timestamps, window creation for timeseries data, ...)
2. Dataset creation: Create a PyTorch dataset with configurable data preprocessing (image cropping, ...) data selection (usage of subset of sensors possible) and failure case creation (by modifying the data)

For more details about how to create a dataset see the following chapters. 

# How to use the code to create a new dataset from measurements?
This section explains how to use the code in this repo for creating a dataset usable in PyTorch from measurements. Further details about the code can be found in later chapters.
### Prerequisites
1. Measurements with the Unitree Go1 by using the code from [Unitree-Go1-Edu](https://github.tik.uni-stuttgart.de/ac136427/Unitree-Go1-Edu) are available

### Data preparation
#### Solution to create a single dataset from multiple measurements (currently 'active' at lines 227 - 258 in *data_preparation_main.py*)
1. Change variable "measurement_base_path" in *data_preparation_main.py* to the location of the measurements for which data preparation shall be done (is **not** allowed to contain zip files!)
2. Change variable "final_dataset_path" in *data_preparation_main.py* to the location where the final dataset shall be stored
3. [Optional] Change config for data preparation in *configs/data_preparation_config.gin*
4. Execute program *data_preparation_main.py* and wait till it finished
    - *NOTE:* Do **not** uncomment the call of function visualize_result() in line 141 which will show a plot for each timestamp after data preparation finished, as this will not work properly in this setup!
5. Update all locations with "TODO" in *datasheet.md* in your dataset location after execution of *data_preparation_main.py* is finished
    - *NOTE:* In the Terminal you will get the information about the number of total instances in the dataset and which measurements are included in the dataset which can be copied
#### Measurement based solution (currently commented out at lines 220 - 225 in *data_preparation_main.py*)
1. Change variable "measurement_path" in *data_preparation_main.py* to the location of the measurement for which data preparation shall be done (can be a normal directory or a zip file)
2. [Optional] Change config for data preparation in *configs/data_preparation_config.gin*
3. Execute program *data_preparation_main.py* and wait till it finished
    - *NOTE:* If you want to have a look at the results, you can uncomment the call of function visualize_result() in line 141 which will show a plot for each timestamp after data preparation finished => If you don't want to have a look at all images, you can abort the execution with Ctrl + c in the command line
4. Copy results from newly created **results/** dir to a new location for your dataset
5. Repeat step 1 for the next measurement
6. Copy only directories containing data from **results/** dir to your dataset location
7. Append the content of *results/labels.csv* to the *labels.csv* file in you dataset location
8. Repeat from step 5 until you performed data preparation for all measurements
9. Update all locations with "TODO" in *datasheet.md* in your dataset location  

### FTDDataset class
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
    - *data_preparation_config.gin:* Config file for data preparation
    - *faulty_data_creation_config.json:* Config file for failure case creation
    - *label_mapping.json:* Mapping of label name to integer value when complete dataset is used
    - *preprocessing_config.json:* Config file for the data preprocessing, e.g. image cropping and resizing
- **custom_utils/** \
This module contains some custom utility functions used in the repository.
    - *utils.py:* Utility functions to handle data (copy data and clear temporary directories)
- **data_preparation/** \
This module contains all code related to data preparation.
    - *image_preparation.py:* Functions to modify timestamps of images and remove obsolete images
    - *incomplete_data_cleanup.py:* Functions to identify and delete timestamps for which data of at least one sensor is missing
    - *measurement_combination.py:* Functions for combining multiple measurements to a single dataset by copying data and extending labels.csv file
    - *timeseries_preparation.py:* Functions for window creation and downsampling
    - *timestamp_evaluation.py:* Functions for timestamp unification
- **data_preprocessing/** \
This module contains all code related to data preprocessing during data preparation.
    - *image_preprocessing.py:* Functions to modify images during data preparation (e.g. cropping) based on config
- **failure_case_creation/** \
This module contains all code related to data manipulation for failure case creation.
    - *frostX.png* (with X = [1,5]): Images to be used for frost() failure case 
    - *modify_images.py:* Functions to modify images from dataset
    - *modify_timeseries.py:* Functions to modify timeseries data from dataset
- **fisheye_calibration** \
Contains files for a prototype of correction of fisheye perspective. Not used anywhere else in the repo and thus further explained.
- **testdata/** \
This directory contains some example data, so you can run *data_preparation_main.py* by default to get an idea of how to use it.
- **visualization/** \
This module contains files with different visualization functions for different kinds of data.
    - *visualizeImages.py:* Functions to visualize images (optionally also with timeseries/ IMU data)
    - *visualizePointCloud.py:* Functions to visualize point clouds
    - *visualizeTimeseriesData.py:* Functions to visualize timeseries/ IMU data
- *data_preparation_main.py*: Program to perform data preparation for a measurement, including timestamp unification, window creation for timeseries data, deletion of obsolete data, ... 
- *data_preprocessing_main.py*: Program to perform data preprocessing for timeseries data and images which is used in data_preparation_main.py*
- *datasheet.md*: Template for the datasheet which will be copied to a prepared dataset (including TODO's for points which must be updated)
- *example_data.png*: Image showing example data for README.md
- *FTDDataset.py*: File containing the FTDDataset() class including an example of how to use it at the end of the file
- *README.md*: The file you are reading right now :)
- *requirements.txt*: File which lists the used python packages
- *test.ipynb*: Jupyter Notebook for testing of functions which already contains different imports for testing
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