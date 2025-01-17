import os
import gin
import shutil
import logging
import json
import numpy as np

# custom imports
from custom_utils.utils import copy_measurement_to_temp, clean_temp_dir, copy_prepared_dataset, clean_results_dir, load_json_from_configs, CustomLogger
from data_preparation.timestamp_evaluation import get_synchronized_timestamps, remove_obsolete_data_at_end, create_label_csv, get_earliest_timestamp_from_IMU, get_data_from_info_json_for_timestamp_evaluation
from data_preparation.timeseries_preparation import TimeseriesDownsamplingForWholeMeasurement, remove_obsolete_values, load_complete_IMU_measurement, create_sliding_windows_and_save_them
from data_preparation.image_preparation import remove_obsolete_images_at_beginning, unify_image_timestamps
from data_preparation.incomplete_data_cleanup import get_incomplete_data_samples, delete_incomplete_data_samples, update_labels_csv, get_list_of_corrupt_IMU_files
from data_preparation.measurement_combination import combine_measurements_to_dataset
from visualization.visualizeTimeseriesData import plot_IMU_data
from visualization.visualizeImages import show_all_images_afterwards, show_all_images_afterwards_including_imu_data
from data_preprocessing_main import data_preprocessing_main


@gin.configurable
def data_preparation_main(measurement_path, temp_path=None, dataset_path=None, window_size=50, normalize_IMU_data_measurement_based=True, preprocess_IMU_data_dataset_based=False, preprocess_images=False, resize_images=False):
    """
        Function to start the complete data preparation process for a new measurement.

        Parameters:
            - measurement_path (str): Path to dir where the measurement is stored (can also be a .zip file)
            - temp_path (str): Path to temp folder where dataset is prepared. (Default = None)
                               If temp_path != None then raw data must be available at temp_path, otherwise data from measurement_path will be copied to location "./temp"
            - dataset_path (str): Path to dir where the prepared data shall be copied to.
                                  Default = None -> the dataset will be copied to results/ dir in the repository.
            - window_size (int): Size of the windows to create for IMU data (default = 50)
            - normalize_IMU_data_measurement_based (bool): Select whether to apply Z Score normalization to IMU data for each measurement (default = True)
            - preprocess_IMU_data_dataset_based (bool): Select whether IMU data shall be preprocessed (default = False)
            - preprocess_images (bool): Select whether images shall be preprocessed (default = False)
            - resize_images (bool): Boolean to enable resizing of images (default = False)
    """
    measurements_are_copied = True
    if temp_path == None:
        # create path name for the temp dir and clean it if no temp_path is provided (handled by caller otherwise)
        file_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.join(file_dir, "temp")
        clean_temp_dir()
        measurements_are_copied = False

    # create logger to log the progress for later analysis
    logger = CustomLogger()
    logger.start_logger(temp_path)

    logging.info(
        f"### Start data preparation for measurement {measurement_path} ###")

    if normalize_IMU_data_measurement_based and preprocess_IMU_data_dataset_based:
        logging.info(
            "Dataset creation aborted, due to invalid config (IMU data was selected to be preprocessed/ normalized twice!)")
        return

    if measurements_are_copied == False:
        # copy the desired measurement to the temp_dir afterwards if no temp_path is provided (handled by caller otherwise)
        logging.info("### Step 1: Copy measurements ###")
        copy_measurement_to_temp(measurement_path)
    else:
        logging.info("### Step 1.1: Measurement already available ###")

    # uncomment to check how data looks before preparation step
    # visualize_result()

    logging.info(
        "\n\n### Step 2: Downsampling of IMU data and create windows for IMU data ###")
    timeseries_downsampler = TimeseriesDownsamplingForWholeMeasurement(
        temp_path)
    timeseries_downsampler.start_downsampling()

    # get starting timestamp for sliding windows
    measurement_timestamp, _ = get_data_from_info_json_for_timestamp_evaluation(
        temp_path)
    earliest_timestamp = get_earliest_timestamp_from_IMU(
        temp_path, measurement_timestamp)
    # create sliding windows
    for sensor in timeseries_downsampler.timeseries_sensors:
        create_sliding_windows_and_save_them(
            temp_path, earliest_timestamp, sensor, window_size, normalize_IMU_data_measurement_based)

    logging.info(
        "\n\n### Step 3: Get synchronized timestamps and delete data previous to synchronized timestamp ###")
    timestamps = get_synchronized_timestamps(temp_path)

    for key, timestamp in timestamps.items():
        # logging.info(f"Starting timestamp for {key} is {timestamp}")
        if "IMU" in key:
            for sensor in timeseries_downsampler.timeseries_sensors:
                remove_obsolete_values(temp_path, sensor, timestamp)
        elif "Cam" in key:
            remove_obsolete_images_at_beginning(temp_path, key, timestamp)

    logging.info("\n\n### Step 4: Unify image timestamps ###")
    earliest_last_image_timestamp = unify_image_timestamps(
        temp_path, timestamps["IMU"])

    logging.info(
        "\n\n### Step 5: Deletion of data for timestamps that are not available for all sensors ###")
    remove_obsolete_data_at_end(temp_path, earliest_last_image_timestamp)

    logging.info("\n\n### Step 6: Create labels csv file ###")
    create_label_csv(temp_path)

    logging.info("\n\n### Step 7: Remove incomplete data samples ###")
    incomplete_samples_list, complete_incomplete_samples_list = get_incomplete_data_samples(
        temp_path)
    logging.info(
        f"The files for the following timestamps will be deleted now:")
    # log info about missing files
    for incomplete_samples in complete_incomplete_samples_list:
        logging.info(incomplete_samples)
    delete_incomplete_data_samples(temp_path, incomplete_samples_list)
    update_labels_csv(temp_path, incomplete_samples_list)
    logging.info(
        "Data for other sensors was removed for above mentioned incomplete samples including update of 'lables.csv'")

    logging.info(
        "\n\n### Step 8: Perform preprocessing for all data samples ###")
    config_path = "preprocessing_config.json"
    config_dict = load_json_from_configs(
        run_path="", json_filename=config_path)
    data_preprocessing_main(
        temp_path, config_dict, preprocess_images, preprocess_IMU_data_dataset_based, resize_images)

    logging.info("\n\n### Step 9: Copy prepared dataset ###")
    if dataset_path == None:
        # clean results/ dir if it shall be used
        clean_results_dir()
    copy_prepared_dataset(temp_path, dataset_path)

    logging.info("\n\n### Step 10: Copy datasheed.md to results dir ###")
    if dataset_path == None:
        shutil.copy("./datasheet.md", "./results/")
        logging.info("datasheet.md was copied to ./results/")
    else:
        shutil.copy("./datasheet.md", dataset_path)
        logging.info(f"datasheet.md was copied to {dataset_path}")

    # uncomment to check how data looks after preparation step
    # visualize_result(window_size)


def visualize_result(imu_offset=0, temp_path=None):
    """
        Helper function to load and visualize data from one IMU sensor and one picture of each stereo camera present in temp/ dir.
        Can be used the show e.g. intermediate results.

        Parameters:        
            - imu_offset (int): Offset for vertical line in IMU plot (needed if sliding windows were already created)
            - temp_path (str): Path to temp folder from where data shall be visualized. (Default = None)
                               If temp_path != None then raw data must be available at temp_path, otherwise data from measurement_path will be copied to location "./temp"
    """
    if temp_path == None:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.join(file_dir, "temp")

    # determines which sensor is used for visualization
    data = load_complete_IMU_measurement(
        temp_path, "accelerometer", load_from_sliding_window=True)
    show_all_images_afterwards_including_imu_data(temp_path, data, imu_offset)


def calculate_std_and_mean_for_timeseries_sensor(dataset_path, sensor):
    """
        Function to calculate std and mean values for all channels for the provided sensor based on all files present in dataset.

        Parameters:
            - dataset_path (str): Path to dataset
            - sensor (str): Name of sensor to determine std and mean for

        Returns:
            - res (dict): Dict containing mean and std values for the sensor (keys are "std" and "mean")
    """
    print(f"Determine std and mean for {sensor}")

    res = {}
    data_from_sliding_window = load_complete_IMU_measurement(
        dataset_path, sensor, load_from_sliding_window=True)

    res["mean"] = np.mean(data_from_sliding_window, axis=0).tolist()
    res["std"] = np.std(data_from_sliding_window, axis=0).tolist()

    return res


def determine_and_store_all_std_and_mean_for_dataset(dataset_path):
    """
        Function to create json file containing std and mean values for all channels of each time series sensor, which can be used for normalization later.

        Parameters:
            - dataset_path (str): Path to dataset
    """
    std_mean_dict = {}

    print("Start determining std and mean values for all timeseries sensors.")

    # get std and mean for all time series sensors
    for root, dirs, files in os.walk(dataset_path):
        for dir in dirs:
            if not "Cam" in dir:
                std_mean_dict[dir] = calculate_std_and_mean_for_timeseries_sensor(
                    dataset_path, dir)

        # break after first for loop to only explore the top level of measurement_base_path
        break

    # store dict with the values in dataset
    json_filename = os.path.join(dataset_path, "std_mean_values.json")

    with open(json_filename, "w") as fp:
        json.dump(std_mean_dict, fp, indent=3)

    print(f"Stored result in file {json_filename}")


if __name__ == "__main__":
    # get and use gin config
    gin_config_path = "./configs/data_preparation_config.gin"
    variant_specific_bindings = []
    gin.parse_config_files_and_bindings(
        [gin_config_path], variant_specific_bindings)

    # ######### measurement based solution
    # # measurement_path = "./testdata/measurement_25_07__15_03"
    # data_preparation_main(measurement_path)

    # ######## create dataset from multiple measurements
    measurement_base_path = r"/home/simon/Go1/_FTDDataset_RawData"
    final_dataset_path = r"/home/simon/Go1/_FTDDataset_RawData/FTDD_2.0_new"
    file_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.join(file_dir, "results")

    # clean result and temp dir at the start
    print("### Step 0: Clean temp and results dirs ###")
    clean_results_dir()
    clean_temp_dir()

    # copy all measurements
    print("### Step 1: Copy measurements ###")
    copy_measurement_to_temp(measurement_base_path)

    # perform data preparation for every measurement in the measurement base path
    for root, dirs, files in os.walk(measurement_base_path):
        for measurement_dir in dirs:
            measurement_path = os.path.join(root, measurement_dir)
            measurement_result_dir = os.path.join(result_dir, measurement_dir)
            measurement_temp_dir = os.path.join(
                file_dir, "temp", measurement_dir)

            data_preparation_main(
                measurement_path, dataset_path=measurement_result_dir, temp_path=measurement_temp_dir)
        # break after first for loop to only explore the top level of measurement_base_path
        break

    # combine measurements to dataset at the end
    combine_measurements_to_dataset(result_dir, final_dataset_path)

    print("Start classification of corrupted IMU data samples")
    corrupted_files_list = get_list_of_corrupt_IMU_files(final_dataset_path)
    print(
        f"The following {len(corrupted_files_list)} corrupted IMU files will be deleted now:")
    for incomplete_samples in corrupted_files_list:
        print(incomplete_samples)

    delete_incomplete_data_samples(final_dataset_path, corrupted_files_list)
    num_data_samples = update_labels_csv(final_dataset_path, corrupted_files_list)

    print(f"Total instances in the dataset after removal of corrupt data: {num_data_samples}")

    determine_and_store_all_std_and_mean_for_dataset(final_dataset_path)
