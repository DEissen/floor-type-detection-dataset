import os
import numpy as np
import pandas as pd
import json
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import ImageFile, Image
# allow truncated images for PIL to process
ImageFile.LOAD_TRUNCATED_IMAGES = True


# custom imports
if __name__ == "__main__":
    from failure_case_creation.modify_images import change_brightness, change_contrast, change_sharpness, gaussian_noise, shot_noise, impulse_noise, speckle_noise, defocus_blur, glass_blur, motion_blur, zoom_blur, gaussian_blur, snow, frost, fog, spatter, brightness, contrast, saturate, jpeg_compression, pixelate
    from failure_case_creation.modify_timeseries import offset_failure, precision_degradation, total_failure, drifting_failure
    from visualization.visualizeTimeseriesData import plot_IMU_data
    from custom_utils.utils import load_json_from_configs
else:
    # else statement needed when FloorTypeDetectionDataset() class is used as submodule in other project
    from FTDDataset.failure_case_creation.modify_images import change_brightness, change_contrast, change_sharpness, gaussian_noise, shot_noise, impulse_noise, speckle_noise, defocus_blur, glass_blur, motion_blur, zoom_blur, gaussian_blur, snow, frost, fog, spatter, brightness, contrast, saturate, jpeg_compression, pixelate
    from FTDDataset.failure_case_creation.modify_timeseries import offset_failure, precision_degradation, total_failure, drifting_failure
    from FTDDataset.visualization.visualizeTimeseriesData import plot_IMU_data
    from FTDDataset.custom_utils.utils import load_json_from_configs

# Ignore warnings
import warnings  # nopep8
warnings.filterwarnings("ignore")


class FloorTypeDetectionDataset(Dataset):
    """
        Dataset class for FTDD (Floor Type Detection Dataset).
    """

    def __init__(self, root_dir, sensors, run_path, create_faulty_data=False):
        """
            Constructor for FloorTypeDetectionDataset class.

            Parameters:
                - root_dir (str): Path to dataset
                - sensors (list): List of all sensors which shall be considered for this dataset
                - run_path (str): Run path to previous run from where config can be loaded. 
                                  If run_path == "" the default config from the repo will be used.
                - create_faulty_data (bool): Default = False. Select whether faulty data shall be created or not.
                                             No data modification will happen, if create_faulty_data == False.
        """
        # names of the config files:
        self.preprocessing_config_filename = "preprocessing_config.json"
        self.faulty_data_creation_config_filename = "faulty_data_creation_config.json"
        mapping_filename = "label_mapping.json"

        # take of of function parameters
        self.root_dir = root_dir
        self.sensors = sensors
        self.run_path = run_path
        self.create_faulty_data = create_faulty_data
        self.faulty_data_creation_config_dict = {}

        # get transformations for data based on configuration
        self.transform = self.__get_composed_transforms()

        # get data for preprocessing and label mapping from configs/ dir
        self.label_mapping_dict = load_json_from_configs(run_path, mapping_filename)

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
        if self.create_faulty_data:
            # only add class for faulty data creation if a path was added
            transformations_list.append(FTDD_CreateFaultyData(self.run_path,
                self.faulty_data_creation_config_filename))

            # save faulty data creation config dict for logging if it was provided
            self.faulty_data_creation_config_dict = transformations_list[0].get_config_dict(
            )

        # ## Image preprocessing
        # TODO: make crop and rescale configurable or detect automatically whether it is needed!
        # ## Crop and Rescale is obsolete here as it is already done in the dataset!
        # transformations_list.append(
        #     FTDD_Crop(self.preprocessing_config_filename))
        transformations_list.append(FTDD_Rescale(self.run_path,
            self.preprocessing_config_filename))
        transformations_list.append(FTDD_Normalize(self.run_path,
            self.preprocessing_config_filename))

        # ## Transform PIL images and numpy arrays to torch Tensors as final step
        transformations_list.append(FTDD_ToTensor())

        # save preprocessing config dict for logging from first transform (transform at position 1 will be either rescale or normalize with preprocessing config)
        self.preprocessing_config_dict = transformations_list[1].get_config_dict(
        )

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
                - self.preprocessing_config_dict (dict): Dict containing config for preprocessing/ transforms
        """
        return self.preprocessing_config_dict

    def get_faulty_data_creation_config(self):
        """
            Getter method to get loaded self.config_dict.

            Returns:
                - self.faulty_data_creation_config_dict (dict): Dict containing config for faulty data creation
        """
        return self.faulty_data_creation_config_dict

    def __len__(self):
        """
            Method to get the size of the dataset.

            Returns:
                - (int) Number of unique data samples in the dataset 
        """
        return np.shape(self.filenames_labels_array)[0]


class FTDD_Transform_Superclass():
    """
        Superclass for all transform classes for FTDD. Provides __init__() method to load config.
    """

    def __init__(self, run_path, config_filename):
        """
            Constructor for FTDD_Crop class.

            Parameters:
                - run_path (str): Run path to previous run from where config can be loaded. If run_path == "" the default config from the repo will be used.
                - config_filename (str): Name of the config JSON file in the configs/ dir
        """
        self.config_dict = load_json_from_configs(run_path,
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

    def __handle_images__(self, image, sensor_name):
        """
            Method to modify provided images according to the config from self.config_dict for sensor.

            Parameters:
                - image (PIL.image): Image from FTDD for sensor
                - sensor_name (str): Name of the sensor

            Returns:
                - image (PIL.image): Modified image
        """
        if sensor_name in self.config_dict['images']["Cams for brightness"]:
            image = change_brightness(
                image, self.config_dict["images"]["brightness_min"], self.config_dict["images"]["brightness_max"])
        elif sensor_name in self.config_dict['images']["Cams for contrast"]:
            image = change_contrast(
                image, self.config_dict["images"]["contrast_min"], self.config_dict["images"]["contrast_max"])
        elif sensor_name in self.config_dict['images']["Cams for sharpness"]:
            image = change_sharpness(
                image, self.config_dict["images"]["sharpness_min"], self.config_dict["images"]["sharpness_max"])
        elif sensor_name in self.config_dict["images"]["Cams for guassian_noise"]:
            image = gaussian_noise(
                image, self.config_dict["images"]["noise intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for shot_noise"]:
            image = shot_noise(
                image, self.config_dict["images"]["noise intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for impulse_noise"]:
            image = impulse_noise(
                image, self.config_dict["images"]["noise intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for speckle_noise"]:
            image = speckle_noise(
                image, self.config_dict["images"]["noise intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for defocus_blur"]:
            image = defocus_blur(
                image, self.config_dict["images"]["blur intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for glass_blur"]:
            image = glass_blur(
                image, self.config_dict["images"]["blur intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for motion_blur"]:
            image = motion_blur(
                image, self.config_dict["images"]["blur intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for zoom_blur"]:
            image = zoom_blur(
                image, self.config_dict["images"]["blur intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for gaussian_blur"]:
            image = gaussian_blur(
                image, self.config_dict["images"]["blur intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for snow"]:
            image = snow(
                image, self.config_dict["images"]["weather intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for frost"]:
            image = frost(
                image, self.config_dict["images"]["weather intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for fog"]:
            image = fog(image, self.config_dict["images"]["weather intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for spatter"]:
            image = spatter(
                image, self.config_dict["images"]["weather intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for new brightness"]:
            image = brightness(
                image, self.config_dict["images"]["digital intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for new contrast"]:
            image = contrast(
                image, self.config_dict["images"]["digital intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for saturate"]:
            image = saturate(
                image, self.config_dict["images"]["digital intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for jpeg_compression"]:
            image = jpeg_compression(
                image, self.config_dict["images"]["digital intensity"])
        elif sensor_name in self.config_dict["images"]["Cams for pixelate"]:
            image = pixelate(
                image, self.config_dict["images"]["digital intensity"])
        return image

    def __handle_timeseries_data__(self, data, sensor_name):
        """
            Method to modify provided timeseries data according to the config from self.config_dict for sensor.

            Parameters:
                - data (np.array): Data sample from FTDD for sensor
                - sensor_name (str): Name of the sensor

            Returns:
                - data (np.array): Modified data
        """
        if sensor_name in set(self.config_dict["timeseries"]["Sensors for offset"]):
            data = offset_failure(
                data, self.config_dict["timeseries"]["offset_min"], self.config_dict["timeseries"]["offset_max"])
        elif sensor_name in self.config_dict["timeseries"]["Sensors for drifting"]:
            data = drifting_failure(
                data, self.config_dict["timeseries"]["drifting_min"], self.config_dict["timeseries"]["drifting_max"])
        elif sensor_name in self.config_dict["timeseries"]["Sensors for prec deg"]:
            data = precision_degradation(
                data, self.config_dict["timeseries"]["prec_deg_var"])
        elif sensor_name in self.config_dict["timeseries"]["Sensors for tot fail"]:
            data = total_failure(
                data, self.config_dict["timeseries"]["total_failure_value"])
        else:
            pass

        return data

    def __handle_timeseries_data_randomly__(self, data, sensor_name):
        """
            Method to modify provided timeseries data according to the config from self.config_dict for sensor.
            NOTE: Currently unused!

            Parameters:
                - data (np.array): Data sample from FTDD for sensor
                - sensor_name (str): Name of the sensor

            Returns:
                - data (np.array): Modified data
        """
        # randomly select one of three possible faults with 15% chance each
        selection_value = torch.rand(1)
        if selection_value < 0.15:
            data = offset_failure(
                data, self.config_dict["timeseries"]["offset_min"], self.config_dict["timeseries"]["offset_max"])
        elif selection_value < 0.3:
            data = drifting_failure(
                data, self.config_dict["timeseries"]["drifting_min"], self.config_dict["timeseries"]["drifting_max"])
        elif selection_value < 0.45:
            data = precision_degradation(
                data, self.config_dict["timeseries"]["prec_deg_var"])
        elif selection_value < 0.6:
            data = total_failure(
                data, self.config_dict["timeseries"]["total_failure_value"])
        else:
            pass
        return data

    def __handle_images_randomly__(self, image, sensor_name):
        """
            Method to modify provided images according to the config from self.config_dict for sensor.
            NOTE: Currently unused!

            Parameters:
                - image (PIL.image): Image from FTDD for sensor
                - sensor_name (str): Name of the sensor

            Returns:
                - image (PIL.image): Modified image
        """
        # randomly select one of three possible faults with 20% chance each
        selection_value = torch.rand(1)
        if selection_value < 0.2:
            image = change_brightness(
                image, self.config_dict["images"]["brightness_min"], self.config_dict["images"]["brightness_max"])
        elif selection_value < 0.4:
            image = change_contrast(
                image, self.config_dict["images"]["contrast_min"], self.config_dict["images"]["contrast_max"])
        elif selection_value < 0.6:
            image = change_sharpness(
                image, self.config_dict["images"]["sharpness_min"], self.config_dict["images"]["sharpness_max"])
        else:
            pass
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
    dataset_path = r"D:\MA_Daten\FTDD1.6\test"

    # list of sensors to use
    sensors = ["BellyCamRight"]
    # sensors = ["accelerometer", "BellyCamRight", "BellyCamLeft", "ChinCamLeft",
    #            "ChinCamRight", "HeadCamLeft", "HeadCamRight", "LeftCamLeft", "LeftCamRight", "RightCamLeft", "RightCamRight"]

    # create dataset
    transformed_dataset = FloorTypeDetectionDataset(
        dataset_path, sensors, run_path="")
    faulty_dataset = FloorTypeDetectionDataset(
        dataset_path, sensors, run_path="", create_faulty_data=True)

    # train_size = int(0.8 * len(transformed_dataset))
    # test_size = len(transformed_dataset) - train_size
    # train_dataset, test_dataset = torch.utils.data.random_split(
    #     transformed_dataset, [train_size, test_size])

    # loop for testing
    for index, (sample, label) in enumerate(transformed_dataset):
        if index == 20:
            for sensor in sensors:
                if not "Cam" in sensor:
                    data = sample[sensor]
                    x = np.arange(0, data.size()[1])
                    plt.plot(x, data.transpose(1, 0))

                    (sample, label) = faulty_dataset.__getitem__(index)
                    faulty_data = sample[sensor]
                    plt.plot(x, faulty_data.transpose(1, 0))
                    plt.show()
                if "Cam" in sensor:
                    image = sample[sensor]
                    # plt.imshow(image.permute(1, 2, 0))
                    # plt.show()

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
