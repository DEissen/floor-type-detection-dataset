import os
import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
from PIL import ImageFile, Image
import cv2
import json

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

def data_preprocessing_main(measurement_path, config_dict):    
    # get list of all sensors
    for root, dirs, files in os.walk(measurement_path):
        for sensor in dirs:
            if "Cam" in sensor:
                preprocess_images_for_camera(measurement_path, sensor, config_dict)
            else:
                preprocess_timeseries_data(measurement_path, sensor, config_dict)

def preprocess_images_for_camera(measurement_path, camera_name, config_dict, plot_preprocessing_once=False):
    config_dict_cam_only = config_dict[camera_name]

    files_glob_pattern = os.path.join(measurement_path, camera_name, "*.jpg")
    cam_files = glob.glob(files_glob_pattern)
    cam_files.sort()
    
    for file in cam_files:
        image = Image.open(file)
        raw_image = image
        image = image_crop(image, config_dict_cam_only)
        # image = image_rescale(image, config_dict_cam_only)

        if plot_preprocessing_once:
            show_image_comparison(raw_image, image, camera_name)
            return

        # remove old file
        os.remove(file)
        # save modified image with same name
        image.save(file)

    print(f"Finished preprocessing for {camera_name}!")

def preprocess_timeseries_data(measurement_path, sensor, config_dict):
    print(f"This would be the timeseries data preprocessing for {sensor}")

def image_crop(image, config_dict):
    """
        Method to crop all images in data_dict according to the config from config_dict.

        Parameters:
            - data_dict (dict): Dict containing one data sample from FTDD.

        Returns:
            - data_dict (dict): Dict after cropping is applied.
    """
    # transform only needed for cameras, other data shall stay unchanged
    # get values for new top, ... for cropping
    new_top = int(config_dict["crop_top"])
    new_bottom = int(
        config_dict["crop_bottom"])
    new_left = int(config_dict["crop_left"])
    new_right = int(
        config_dict["crop_right"])

    # replace image in sample dict with cropped image
    image = image.crop(
        (new_left, new_top, new_right, new_bottom))

    return image


def image_rescale(image, config_dict):
    """
        Method to rescale all images in data_dict according to the config from config_dict.

        Parameters:
            - data_dict (dict): Dict containing one data sample from FTDD.

        Returns:
            - data_dict (dict): Dict after rescaling is applied.
    """
    # get new target heigth and width from config dict
    new_h = int(config_dict["final_height"])
    new_w = int(config_dict["final_width"])

    # replace image in sample dict with resized image
    image = image.resize((new_w, new_h))

    return image

def show_image_comparison(old_image, new_image, title):
    columns = 2
    rows = 1
    fig = plt.figure(figsize=(20, 13))
    ax = []

    plt.title(title)
    
    ax.append(fig.add_subplot(rows, columns, 1))
    ax[-1].set_title("old image")
    plt.imshow(old_image)

    ax.append(fig.add_subplot(rows, columns, 2))
    ax[-1].set_title("preprocessed image")
    plt.imshow(new_image)
    plt.show()
    
if __name__ == "__main__":
    # get and use gin config
    config_path = "preprocessing_config.json"
    config_dict = load_json_from_configs(config_path)

    measurement_path = "./temp - Kopie"
    # measurement_path = r""

    data_preprocessing_main(measurement_path, config_dict)
