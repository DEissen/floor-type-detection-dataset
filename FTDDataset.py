import os
import numpy as np
import pandas as pd
import glob
import json
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from visualization.visualizeTimeseriesData import plot_IMU_data

# for testing
import matplotlib.pyplot as plt

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")


class FloorTypeDetectionDataset(Dataset):
    """
        Dataset class for FTDD (Floor Type Detection Dataset).
    """

    def __init__(self, root_dir, sensors, mapping_filename, transform=None):
        """
            Constructor for FloorTypeDetectionDataset class.

            Parameters:
                - root_dir (str): Path to dataset
                - sensors (list): List of all sensors which shall be considered for this dataset
                - mapping_filename (str): filename of the label mapping JSON file
                - transform (torchvision.transforms.Compose): Composed transforms for the data for preprocessing and failure case creation
        """
        self.root_dir = root_dir
        self.sensors = sensors
        self.transform = transform

        # get data for preprocessing and label mapping from configs/ dir
        self.label_mapping_struct = load_json_from_configs(mapping_filename)

        # get list of all files from labels
        self.filenames_labels_array = pd.read_csv(os.path.join(
            root_dir, "labels.csv"), sep=";", header=0).to_numpy()

    def __getitem__(self, index):
        """
            Method to support indexing. For memory efficiency this function loads and transforms the data instead of doing this during init.

            Parameters:
                - index (int): Index for which data shall be returned.

            Returns:
                - data_dict (dict): Dict containing data for all sensors from self.sensors, where sensor name is the key
                - (int) Label for this data_dict
        """
        # get data for all sensors in self.sensors for the index
        data_dict = {}
        for sensor in self.sensors:
            if "Cam" in sensor:
                # data is stored as .jpg file for all cameras
                file_path = os.path.join(
                    self.root_dir, sensor, self.filenames_labels_array[index, 0]+".jpg")
                data_dict[sensor] = Image.open(file_path)
            else:
                # data is stored as .csv file for all other sensors
                file_path = os.path.join(
                    self.root_dir, sensor, self.filenames_labels_array[index, 0]+".csv")
                data_dict[sensor] = np.loadtxt(file_path, delimiter=";")

        # perform preprocessing/ transform for data dict if configured
        if self.transform:
            data_dict = self.transform(data_dict)

        # get the label for the index
        label = self.filenames_labels_array[index, 1]

        return (data_dict, self.label_mapping_struct[label])

    def __len__(self):
        """
            Method to get the size of the dataset.

            Returns:
                - (int) Number of unique data samples in the dataset 
        """
        return np.shape(self.filenames_labels_array)[0]


def load_json_from_configs(json_filename):
    """
        Helper function to load any JSON file from the configs/ dir of the repo.

        Parameters:
            - json_filename (str): Name of the JSON file in the configs/ dir

        Returns:
            - json_as_struct (struct): Struct containing the data from the file json_filename
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(file_dir, "configs", json_filename)

    with open(json_path, "r") as f:
        json_as_struct = json.load(f)

    return json_as_struct


class FTDD_Crop(object):
    """
        Class to crop images for preprocessing of FTDD. 
    """

    def __init__(self, preprocessing_config_filename):
        """
            Constructor for FTDD_Crop class.

            Parameters:
                - preprocessing_config_filename (str): Name of the preprocessing JSON file in the configs/ dir
        """
        self.config_struct = load_json_from_configs(
            preprocessing_config_filename)

    def __call__(self, data_dict: dict):
        """
            Method to crop all images in data_dict according to the config from self.config_struct.

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.
        """
        # transform only needed for cameras, other data shall stay unchanged
        for sensor_name in data_dict.keys():
            if "Cam" in sensor_name:
                # get image and current properties
                image = data_dict[sensor_name]

                # get values for new top, ... for cropping
                new_top = int(self.config_struct[sensor_name]["crop_top"])
                new_bottom = int(
                    self.config_struct[sensor_name]["crop_bottom"])
                new_left = int(self.config_struct[sensor_name]["crop_left"])
                new_right = int(
                    self.config_struct[sensor_name]["crop_right"])

                # replace image in sample dict with cropped image
                data_dict[sensor_name] = image.crop(
                    (new_left, new_top, new_right, new_bottom))

        return data_dict


class FTDD_Rescale(object):
    """
        Class to rescale images for preprocessing of FTDD.
    """

    def __init__(self, preprocessing_config_filename):
        """
            Constructor for FTDD_Rescale class.

            Parameters:
                - preprocessing_config_filename (str): Name of the preprocessing JSON file in the configs/ dir
        """
        self.config_struct = load_json_from_configs(
            preprocessing_config_filename)

    def __call__(self, data_dict: dict):
        """
            Method to rescale all images in data_dict according to the config from self.config_struct.

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.
        """
        # transform only needed for cameras, other data shall stay unchanged
        for sensor_name in data_dict.keys():
            if "Cam" in sensor_name:
                # get image and current properties
                image = data_dict[sensor_name]

                # get new target heigth and width from config struct
                new_h = int(self.config_struct[sensor_name]["final_height"])
                new_w = int(self.config_struct[sensor_name]["final_width"])

                # replace image in sample dict with resized image
                data_dict[sensor_name] = image.resize((new_w, new_h))

        return data_dict


if __name__ == "__main__":
    # variables for dataset and config to use
    dataset_path = r"C:\Users\Dominik\Downloads\FTDD_0.1"
    mapping_filename = "label_mapping_binary.json"
    preprocessing_config_filename = "preprocessing_config.json"

    # list of sensors to use
    sensors = ["accelerometer", "BellyCamRight", "BellyCamLeft", "ChinCamLeft",
               "ChinCamRight", "HeadCamLeft", "HeadCamRight", "LeftCamLeft", "LeftCamRight", "RightCamLeft", "RightCamRight"]

    # create list of transformations to perform (data preprocessing + failure case creation)
    transformations_list = []
    transformations_list.append(FTDD_Crop(preprocessing_config_filename))
    transformations_list.append(FTDD_Rescale(preprocessing_config_filename))
    composed_transforms = transforms.Compose(transformations_list)

    # create dataset
    test = FloorTypeDetectionDataset(
        dataset_path, sensors, mapping_filename, transform=composed_transforms)

    # loop for testing
    for index, (sample, label) in enumerate(test):
        if index == 0:
            for sensor in sensors:
                if "Cam" in sensor:
                    sample[sensor].show()
                    break
                else:
                    plot_IMU_data(sample[sensor], sensor)
