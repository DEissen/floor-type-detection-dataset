# Datasheet for Floor Type Detection Dataset (FTD dataset/ FTDD)
This README acts as a datasheet for FTDD.

# General Infos
FTDD -  Version 0.1_stable \
**Author:** Dominik Eißen \
**Mail:** st177975@stud.uni-stuttgart.de

# How to use FTD dataset?
**Note: FTDD can only be used with PyTorch!** \
In order to use the FTD dataset, you have to use the FloorTypeDetectionDataset() class from file ./FTDDataset.py in the [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset) repository. Thus it's recommended to copy the repo into your repository as a submodule. In order to use the FloorTypeDetectionDataset() class, you have to provide following parameters:
- **root_dir (str):** Path to prepared dataset
- **sensors (list):** List of all sensors which shall be considered
- **mapping_filename (str):** filename of the label mapping JSON file
- **preprocessing_config_filename (str):** Name of the preprocessing JSON file in the configs/ dir of the repository
- **[optional] faulty_data_creation_config_filename (str):** Name of the faulty data creation JSON file in the configs/ dir of the repository. If nothing is provided, the data won't be manipulated.

An example of how to use the class is directly provided at the end of the ./FTDDataset.py file in the [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset) repository.


# Folder structure of FTDD
root_dir:
- XXXCamYYY: (XXX = name of stereocamera (e.g. Head, Belly, ...) / YYY = Left or Right)
    - timestamp1.jpg
    - timestamp2.jpg
    - ... 
    - timestampX.jpg
- sensorname: (timeseries sensors like accelerometer, gyroscope, ...)
    - timestamp1.csv
    - timestamp2.csv
    - ... 
    - timestampX.csv
- labels.csv (csv with label information for each timestamp)
- datasheet.md (this file)
# Details about dataset
In this section you will find answers to several questions about FTDD. The questions are a subset of the questions proposed in the paper "Datasheets for Datasets" from T. Gebru et al. which can be found here: https://arxiv.org/pdf/1803.09010 \
The purpose of this chapter is to hopefully answer all questions which could arise when using this dataset.
## Motivation
### **Q: For what purpose was the dataset created?**
A: The dataset was created for the research thesis FA 3526 at the IAS Institute from University Stuttgart. The aim of the research thesis was to create a dataset for multi-modal machine learning for classifying different types of floor (e.g. tiles, parquet, ...) which a mobile robot ([Unitree Go1](https://www.unitree.com/en/go1/)) is moving on.
### **Q: Who created the dataset and on behalf of which entity?** 
A: The dataset was created by the student Dominik Eißen, supported by his supervisor Simon Kamm on behalf of University Stuttgart.

## Composition
### **Q: What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?** 
A: The dataset consists of images of five stereocameras and measurements of different sensors (like accelerometer, gyroscope, ...)  of the [Unitree Go1](https://www.unitree.com/en/go1/). The only thing that shall be represented by all the data is the floor type which the Go1 was moving on. \
Nonetheless there is more to see on the images of some of the stereocameras (Head, Right and Left camera) as they capture the surrounding of the Go1 while moving.
### **Q: How many instances are there in total (of each type, if appropriate)?** 
A: There are TODO instances in total.
### **Q: Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?** 
A: The dataset contains all possible instances. Still it is possible to only select a subset of the complete set when loading the dataset with the FloorTypeDetectionDataset() class provided in the repository [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset).
### **Q: What data does each instance consist of?** 
A: Each instance (one instance = data of all sensors and cameras for one timestamp). Consists of images of the different stereocameras and timeseries measurement of the other present sensors. The following cameras and sensors are present in this version:
- Accelerometer
- BellyCam (images of left and right camera)
- BodyHeight
- ChinCam (images of left and right camera)
- FootForce
- Gyroscope
- HeadCam (images of left and right camera)
- LeftCam (images of left and right camera)
- Mode
- Rpy
- RightCam (images of left and right camera)
- Velocity
- YawSpeed
### **Q: Is there a label or target associated with each instance?** 
A:  Yes, the label-timestamp mapping can be found in the labels.csv file.
### **Q :Are there recommended data splits (e.g., training, development/validation, testing)?** 
A: The recommended split is 90% for training and 10% for testing. If a separate validation set is wanted, this should be taken from training set. If possible, it's recommended to use data from different measurements which are not included in this dataset for testing
### **Q: Is any information missing from individual instances?** 
A: No. All instances/ timestamps contain the data of all sensors. In case there was data missing for a sensors for a timestamp, the timestamp was removed during data preparation step.
### **Q: Are relationships between individual instances made explicit (e.g., users’ movie ratings, social network links)?** 
A: No.
### **Q: Are there any errors, sources of noise, or redundancies in the dataset?** 
A: As the data was captured with cameras and sensors on a moving robot, there are typical errors which occur while capturing data with a moving robot included (like motion blur in images, ...). \
Redundancies might also occur at least from human perspective, e.g. if the robot was standing still for a longer period of time during a measurement (nearly identical images, ...). 
### **Q: Is the dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)?** 
A: The dataset is self-contained and does not rely on external resources.
### **Q: Does the dataset contain data that might be considered confidential (e.g., data that is protected by legal privilege or by doctor– patient confidentiality, data that includes the content of individuals’ non-public communications)?** 
A: No, the dataset does not contain data that might be considered confidential.
### **Q: Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?** 
A: No, the dataset does not contain such data.

## Collection Process

### **Q: How was the data associated with each instance acquired?** 
A:  The data was collected using the ./main.py program of the repository [Unitree-Go1-Edu](https://github.tik.uni-stuttgart.de/ac136427/Unitree-Go1-Edu). The instances/ timestamps as present in the dataset were then created during data preparation by using the program ./data_preparation_main.py of the repository [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset).
### **Q: What mechanisms or procedures were used to collect the data (e.g., hardware apparatuses or sensors, manual human curation, software programs, software APIs)?** 
A: The data was collected with the [Unitree Go1](https://www.unitree.com/en/go1/) robot dog which was controlled by the remote control by a human. \
The data was collected using the ./main.py program of the repository [Unitree-Go1-Edu](https://github.tik.uni-stuttgart.de/ac136427/Unitree-Go1-Edu).
- TODO Used version: [Version_1.0](https://github.tik.uni-stuttgart.de/ac136427/Unitree-Go1-Edu/releases/tag/Version_1.0)

Finally the data was prepared using the program ./data_preparation_main.py of the repository [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset).
- TODO Used version: [FTDD_1.0](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset/releases/tag/FTDD_1.0)
### **Q: If the dataset is a sample from a larger set, what was the sampling strategy (e.g., deterministic, probabilistic with specific sampling probabilities)?** 
A:  The dataset is not a sample from a larger set.
### **Q: Who was involved in the data collection process (e.g., students, crowdworkers, contractors) and how were they compensated (e.g., how much were crowdworkers paid)?** 
A: Master and PhD students were involved in the data collection process.
### **Q: Over what timeframe was the data collected?** 
A: The data was collected over several measurements at the same day.

## Preprocessing/ cleaning/ labeling
### **Q: Was any preprocessing/ cleaning/ labeling of the data done (e.g., discretization or bucketing, tokenization, part-of-speech tagging, SIFT feature extraction, removal of instances, processing of missing values)?** 
A: Yes, the data was prepared/ preprocessed by using the the program ./data_preparation_main.py of the repository [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset). Steps done during data preparation:
- Downsampling of timeseries data to 50 Hz signal (captured with ~100 Hz)
- Z Score normalization of the downsampled timeseries data
- Window creation for timeseries measurements
- Timestamp synchronization (assign data of all sensors to one instance by common timestamp based on time diff information between clocks of all included PC's)
- Removal of instances where data of at least one sensor is missing for
### **Q: Was the “raw” data saved in addition to the preprocessed/ cleaned/ labeled data (e.g., to support unanticipated future uses)?** 
A: The raw data might be still available if it was separately stored. The following measurements are included in this version:
- TODO measurement_DD_MM__HH_mm
### **Q: Is the software that was used to preprocess/ clean/ label the data available?** 
A: Yes, the SW can be found in the repository [Floor-Type-Detection-Dataset](https://github.tik.uni-stuttgart.de/ac136427/Floor-Type-Detection-Dataset). Details about the used version can be found in question *"What mechanisms or procedures were used to collect the data (e.g., hardware apparatuses or sensors, manual human curation, software programs, software APIs)?"*.

## Uses
### **Q: Has the dataset been used for any tasks already?** 
A: The dataset was used for the research Thesis FA 3526 at the IAS Institute from University Stuttgart.
### **Q: What (other) tasks could the dataset be used for?** 
A: There are no other tasks which the dataset could be used for directly, as no further information besides the floor type was stored for each measurement. Of course new labels could created for each instance manually based on what can be seen on the images (e.g. object detection, image segmentation, weather classification, ...). Still this is not recommended as it would need a lot of time to manually create the new labels. \
*Note:* New data can be collected by using the SW available in the repository [Unitree-Go1-Edu](https://github.tik.uni-stuttgart.de/ac136427/Unitree-Go1-Edu) where new labels can be directly captured during the measurement with small modifications on the SW. This might be faster than creating new labels manually.
### **Q: Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?** 
A: There was no additional information stored besides the labels about the surrounding conditions. This makes it hard to create new labels for different uses.

## Maintenance
### **Q: Will the dataset be maintained or updated?** 
A: The dataset might be maintained or updated by future student work.
