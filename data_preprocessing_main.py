import os
import glob
from PIL import ImageFile, Image
import logging
# allow truncated images for PIL to process
ImageFile.LOAD_TRUNCATED_IMAGES = True

from custom_utils.utils import load_json_from_configs
from visualization.visualizeImages import show_image_comparison
from data_preprocessing.image_preprocessing import image_crop, image_rescale

def data_preprocessing_main(dataset_path, config_dict, preprocess_images, preprocess_IMU_data, resize_images):
    """
        Function to start the complete data preprocessing process for a dataset (or measurement).

        Parameters:
            - dataset_path (str): Path to dir where the measurement is stored (can also be a .zip file)
            - config_dict (dict): Dict containing the configuration for all sensors of the dataset
            - preprocess_images (bool): Boolean to enable preprocessing of images
            - preprocess_IMU_data (bool): Boolean to enable preprocessing of IMU data
            - resize_images (bool): Boolean to enable resizing of images
    """
    # preprocess files of each sensor (data for each sensor is stored in separate directory)
    for root, dirs, files in os.walk(dataset_path):
        for sensor in dirs:
            if "Cam" in sensor and preprocess_images == True:
                preprocess_images_for_camera(
                    dataset_path, sensor, config_dict, resize_images)
            else:
                if preprocess_IMU_data:
                    preprocess_timeseries_data(
                        dataset_path, sensor, config_dict)


def preprocess_images_for_camera(dataset_path, camera_name, config_dict, resize_images, plot_preprocessing_once=False):
    """
        Function to preprocess images from camera "camera_name" for a dataset (or measurement).

        Parameters:
            - dataset_path (str): Path to dir where the measurement is stored (can also be a .zip file)
            - camera_name (str): Name of the camera to perform preprocessing for 
            - config_dict (dict): Dict containing the configuration for all sensors of the dataset
            - resize_images (bool): Boolean to enable resizing of images
            - plot_preprocessing_once (bool): Flag whether preprocessing shall be plotted once and stopped 
                                              for debugging purposes (default = False)
    """
    # extract config for camera
    config_dict_cam_only = config_dict[camera_name]

    # get list of all images
    files_glob_pattern = os.path.join(dataset_path, camera_name, "*.jpg")
    cam_files = glob.glob(files_glob_pattern)
    cam_files.sort()

    # preprocess each image
    for file in cam_files:
        image = Image.open(file)
        raw_image = image

        # perform preprocessing
        image = image_crop(image, config_dict_cam_only)
        # images will be resized/ rescaled only if selected by function parameter
        if resize_images:
            image = image_rescale(image, config_dict_cam_only)

        # optionally plot preprocessing for debugging purposes
        if plot_preprocessing_once:
            show_image_comparison(raw_image, image, camera_name)
            return

        # remove old file and save modified image with same name afterwards
        os.remove(file)
        image.save(file)

    logging.info(f"Finished preprocessing for {camera_name}!")


def preprocess_timeseries_data(dataset_path, sensor, config_dict):
    """
        Function to preprocess data from IMU sensors for a dataset (or measurement).

        Parameters:
            - dataset_path (str): Path to dir where the measurement is stored (can also be a .zip file)
            - sensor (str): Name of the IMU data to perform preprocessing for 
            - config_dict (dict): Dict containing the configuration for all sensors of the dataset
    """
    logging.info(f"This would be the timeseries data preprocessing for {sensor}")


if __name__ == "__main__":
    # get and use gin config
    config_path = "preprocessing_config.json"
    config_dict = load_json_from_configs(config_path)

    measurement_path = "./results"

    data_preprocessing_main(measurement_path, config_dict)
