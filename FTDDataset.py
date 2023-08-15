import os
import numpy as np
import pandas as pd
import json
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# for testing
# from visualization.visualizeTimeseriesData import plot_IMU_data
# import matplotlib.pyplot as plt

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
        self.label_mapping_dict = load_json_from_configs(mapping_filename)

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

        return (data_dict, self.label_mapping_dict[label])

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
            - json_as_dict (dict): Dict containing the data from the file json_filename
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(file_dir, "configs", json_filename)

    with open(json_path, "r") as f:
        json_as_dict = json.load(f)

    return json_as_dict


class FTDD_Transform_Superclass():
    """
        Superclass for all transform classes for FTDD. Provides __init__() method to load config.
    """

    def __init__(self, preprocessing_config_filename):
        """
            Constructor for FTDD_Crop class.

            Parameters:
                - preprocessing_config_filename (str): Name of the preprocessing JSON file in the configs/ dir
        """
        self.config_dict = load_json_from_configs(
            preprocessing_config_filename)


class FTDD_Crop(FTDD_Transform_Superclass):
    """
        Class to crop images for preprocessing of FTDD. Child of FTDD_Transform_Superclass, where __init__() method is relevant.
    """

    def __call__(self, data_dict: dict):
        """
            Method to crop all images in data_dict according to the config from self.config_dict.

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.

            Returns:
                - data_dict (dict): Dict after cropping is applied.
        """
        # transform only needed for cameras, other data shall stay unchanged
        for sensor_name in data_dict.keys():
            if "Cam" in sensor_name:
                # get image and current properties
                image = data_dict[sensor_name]

                # get values for new top, ... for cropping
                new_top = int(self.config_dict[sensor_name]["crop_top"])
                new_bottom = int(
                    self.config_dict[sensor_name]["crop_bottom"])
                new_left = int(self.config_dict[sensor_name]["crop_left"])
                new_right = int(
                    self.config_dict[sensor_name]["crop_right"])

                # replace image in sample dict with cropped image
                data_dict[sensor_name] = image.crop(
                    (new_left, new_top, new_right, new_bottom))

        return data_dict


class FTDD_Rescale(FTDD_Transform_Superclass):
    """
        Class to rescale images for preprocessing of FTDD. Child of FTDD_Transform_Superclass, where __init__() method is relevant.
    """

    def __call__(self, data_dict: dict):
        """
            Method to rescale all images in data_dict according to the config from self.config_dict.

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.

            Returns:
                - data_dict (dict): Dict after rescaling is applied.
        """
        # transform only needed for cameras, other data shall stay unchanged
        for sensor_name in data_dict.keys():
            if "Cam" in sensor_name:
                # get image and current properties
                image = data_dict[sensor_name]

                # get new target heigth and width from config dict
                new_h = int(self.config_dict[sensor_name]["final_height"])
                new_w = int(self.config_dict[sensor_name]["final_width"])

                # replace image in sample dict with resized image
                data_dict[sensor_name] = image.resize((new_w, new_h))

        return data_dict


class FTDD_ToTensor():
    """
        Class to convert images and numpy arrays to Tensors as final step for preprocessing of FTDD.
    """

    def __call__(self, data_dict: dict):
        """
            Method to convert all images and imu measurement in data_dict to Tensors.

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.

            Returns:
                - data_dict (dict): Dict after transform is applied.
        """
        for sensor_name in data_dict.keys():
            if "Cam" in sensor_name:
                image = np.array(data_dict[sensor_name])
                # swap color axis because
                # numpy image: H x W x C
                # torch image: C x H x W
                image = image.transpose((2, 0, 1))
                data_dict[sensor_name] = torch.from_numpy(image)
            else:
                imu_data = data_dict[sensor_name]
                data_dict[sensor_name] = torch.from_numpy(imu_data)

        return data_dict


class FTDD_Normalize(FTDD_Transform_Superclass):
    def __call__(self, data_dict: dict):
        """
            Method to normalize all images data_dict by dividing through 255 and converts PIL image to np.array.
            Note: Normalization for IMU data is already handled in data preparation step and thus not necessary. 

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.

            Returns:
                - data_dict (dict): Dict after normalization is applied.
        """
        for sensor_name in data_dict.keys():
            if "Cam" in sensor_name:
                if self.config_dict["normalize_images"]:
                    data_dict[sensor_name] = np.array(
                        data_dict[sensor_name], dtype=np.float32) / 255
            else:
                pass  # IMU data is already normalized during data preparation

        return data_dict


if __name__ == "__main__":
    """
        This main contains a template of how to use the FloorTypeDetectionDataset() including data preprocessing.
    """
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
    transformations_list.append(FTDD_Normalize(preprocessing_config_filename))
    transformations_list.append(FTDD_ToTensor())
    composed_transforms = transforms.Compose(transformations_list)

    # create dataset
    transformed_dataset = FloorTypeDetectionDataset(
        dataset_path, sensors, mapping_filename, transform=composed_transforms)

    train_size = int(0.8 * len(transformed_dataset))
    test_size = len(transformed_dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(
        transformed_dataset, [train_size, test_size])

    # # loop for testing
    # ones = 0
    # zeros =0
    # for index, (sample, label) in enumerate(test_dataset):
    #     if index == 0:
    #         for sensor in sensors:
    #             if "Cam" in sensor:
    #                 image = sample[sensor]
    #                 # plt.imshow(image.permute(1, 2, 0))
    #                 # plt.show()
    #                 print(type(image), image.shape, torch.max(image))
    #             else:
    #                 # plot_IMU_data(sample[sensor], sensor)
    #                 pass
    #     if label == 1:
    #         ones +=1
    #     else:
    #         zeros +=1
    # print(f"Test set contains {ones} ones and {zeros} zeros")
    # create dataloader
    train_dataloader = DataLoader(train_dataset,
                            batch_size=8, shuffle=True, drop_last=True)
    test_dataloader = DataLoader(test_dataset,
                            batch_size=8, shuffle=True, drop_last=True)
