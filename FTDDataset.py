import os
import numpy as np
import pandas as pd
import json
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# for testing
from visualization.visualizeTimeseriesData import plot_IMU_data
import matplotlib.pyplot as plt

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")


class FloorTypeDetectionDataset(Dataset):
    """
        Dataset class for FTDD (Floor Type Detection Dataset).
    """

    def __init__(self, root_dir, sensors, mapping_filename, preprocessing_config_filename, faulty_data_creation_config_filename=""):
        """
            Constructor for FloorTypeDetectionDataset class.

            Parameters:
                - root_dir (str): Path to dataset
                - sensors (list): List of all sensors which shall be considered for this dataset
                - mapping_filename (str): filename of the label mapping JSON file
                - preprocessing_config_filename (str): Name of the preprocessing JSON file in the configs/ dir 
                - faulty_data_creation_config_filename (str): Default = "". Name of the faulty data creation JSON file in the configs/ dir 
        """
        self.root_dir = root_dir
        self.sensors = sensors
        self.preprocessing_config_filename = preprocessing_config_filename
        self.faulty_data_creation_config_filename = faulty_data_creation_config_filename
        self.transform = self.__get_composed_transforms()

        # get data for preprocessing and label mapping from configs/ dir
        self.label_mapping_dict = load_json_from_configs(mapping_filename)

        # get list of all files from labels
        self.filenames_labels_array = pd.read_csv(os.path.join(
            root_dir, "labels.csv"), sep=";", header=0).to_numpy()

    def __get_composed_transforms(self):
        """
            Private method to configure transformation for dataset based on self.preprocessing_config_filename.

            Returns:
                (torchvision.transforms.Compose): Composed transforms for the data for preprocessing and failure case creation
        """
        # create list of transformations to perform (data preprocessing + failure case creation)
        transformations_list = []

        # ## Creating faulty data according to fault config before image preprocessing, if fault config was provided
        if self.faulty_data_creation_config_filename != "":
            # only add class for faulty data creation if a path was added
            transformations_list.append(FTDD_CreateFaultyData(
                self.faulty_data_creation_config_filename))

        # ## Image preprocessing
        transformations_list.append(
            FTDD_Crop(self.preprocessing_config_filename))
        transformations_list.append(FTDD_Rescale(
            self.preprocessing_config_filename))
        transformations_list.append(FTDD_Normalize(
            self.preprocessing_config_filename))

        # ## Transform PIL images and numpy arrays to torch Tensors as final step
        transformations_list.append(FTDD_ToTensor())

        # save preprocessing config dict for logging from first transform
        self.preprocessing_config_dict = transformations_list[0].get_config_dict()

        return transforms.Compose(transformations_list)

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

        # perform preprocessing/ transform for data dict
        data_dict = self.transform(data_dict)

        # get the label for the index
        label = self.filenames_labels_array[index, 1]

        return (data_dict, self.label_mapping_dict[label])

    def get_mapping_dict(self):
        """
            Getter method to get label to number mapping dict self.label_mapping_dict.

            Returns:
                - self.label_mapping_dict (dict): Dict containing label to number mapping
        """
        return self.label_mapping_dict

    def get_preprocessing_config(self):
        """
            Getter method to get loaded self.config_dict.

            Returns:
                - self.config_dict (dict): Dict containing config for preprocessing/ transforms
        """
        return self.preprocessing_config_dict

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

    def __init__(self, config_filename):
        """
            Constructor for FTDD_Crop class.

            Parameters:
                - config_filename (str): Name of the config JSON file in the configs/ dir
        """
        self.config_dict = load_json_from_configs(
            config_filename)

    def get_config_dict(self):
        """
            Getter method to get loaded self.config_dict.

            Returns:
                - self.config_dict (dict): Dict containing config for preprocessing/ transforms
        """
        return self.config_dict


class FTDD_CreateFaultyData(FTDD_Transform_Superclass):
    """
        Class to create faulty data by adding noise, ... to the data.
    """

    def __call__(self, data_dict: dict):
        """
            Method to create faulty data in data_dict according to the config from self.config_dict.

            Parameters:
                - data_dict (dict): Dict containing one data sample from FTDD.

            Returns:
                - data_dict (dict): Dict after cropping is applied.
        """
        # modify data only in case create_faulty_data flag is set in config dict
        if self.config_dict["create_faulty_data"]:
            # iterate over the complete data_dict
            for sensor_name in data_dict.keys():
                # handle images and timeseries data separately
                if "Cam" in sensor_name:
                    data_dict[sensor_name] = self.__handle_images__(
                        data_dict[sensor_name], sensor_name)
                else:
                    data_dict[sensor_name] = self.__handle_timeseries_data__(
                        data_dict[sensor_name], sensor_name)

        return data_dict

    def __handle_timeseries_data__(self, data, sensor):
        """
            Method to modify provided timeseries data according to the config from self.config_dict for sensor.

            Parameters:
                - data (np.array): Data sample from FTDD for sensor
                - sensors (str): Name of the sensor

            Returns:
                - data (np.array): Modified data
        """
        return data

    def __handle_images__(self, image, sensor):
        """
            Method to modify provided images according to the config from self.config_dict for sensor.

            Parameters:
                - image (PIL.image): Image from FTDD for sensor
                - sensors (str): Name of the sensor

            Returns:
                - image (PIL.image): Modified image
        """
        return image


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
                # swap feature axis because (D = data, C = channels)
                # numpy data: D x C
                # torch image: C x D
                if len(np.shape(imu_data)) == 1:
                    # if there is only 1D data, a feature dimension must be added
                    imu_data = np.expand_dims(imu_data, 1)
                    # swapping is only needed if multiple feature channels are there
                imu_data = imu_data.transpose((1, 0))
                data_dict[sensor_name] = torch.tensor(
                    torch.from_numpy(imu_data), dtype=torch.float32)

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
    faulty_data_creation_config_filename = "faulty_data_creation_config.json"

    # list of sensors to use
    sensors = ["accelerometer", "BellyCamRight", "BellyCamLeft", "ChinCamLeft",
               "ChinCamRight", "HeadCamLeft", "HeadCamRight", "LeftCamLeft", "LeftCamRight", "RightCamLeft", "RightCamRight"]

    # create dataset
    transformed_dataset = FloorTypeDetectionDataset(
        dataset_path, sensors, mapping_filename, preprocessing_config_filename)
    faulty_dataset = FloorTypeDetectionDataset(
        dataset_path, sensors, mapping_filename, preprocessing_config_filename, faulty_data_creation_config_filename)


    # train_size = int(0.8 * len(transformed_dataset))
    # test_size = len(transformed_dataset) - train_size
    # train_dataset, test_dataset = torch.utils.data.random_split(
    #     transformed_dataset, [train_size, test_size])

    # loop for testing
    ones = 0
    zeros =0
    for index, (sample, label) in enumerate(transformed_dataset):
        if index == 20:
            for sensor in sensors:
                if "Cam" in sensor:
                    image = sample[sensor]
                    plt.imshow(image.permute(1, 2, 0))
                    plt.show()

                    # print same image of faulty dataset
                    (sample, label) = faulty_dataset.__getitem__(index)
                    faulty_image = sample[sensor]
                    plt.imshow(faulty_image.permute(1, 2, 0))
                    plt.show()
                    break
                else:
                    # plot_IMU_data(sample[sensor], sensor)
                    pass
            break

    # create dataloader
    normal_dataloader = DataLoader(transformed_dataset,
                                  batch_size=8, shuffle=False, drop_last=True)
    faulty_dataloader = DataLoader(faulty_dataset,
                                 batch_size=8, shuffle=False, drop_last=True)
