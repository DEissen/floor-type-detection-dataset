
from os import path
import os
import pandas as pd
import numpy as np
import gin


def get_incomplete_data_samples(dataset_path):
    """
        Function to determine all data samples (identified by it's timestamp) where not all data is present from.

        Parameters:
            - dataset_path (str): Path to the dataset

        Returns:
            - incomplete_samples_set (set): Set containing all timestamp strings for which at least one sensors does not provide data
            - complete_incomplete_samples_list (list): List containing the exact filename of the missing files.
    """
    # initialize local variables
    incomplete_samples_list = []
    complete_incomplete_samples_list = []

    # get np.array of filename from labels.csv
    filenames_array = pd.read_csv(os.path.join(
        dataset_path, "labels.csv"), sep=";", header=0).to_numpy()[:, 0]

    # get list of all sensors in the dataset
    sensors = []
    for root, dirs, files in os.walk(dataset_path):
        for sensor in dirs:
            sensors.append(sensor)

    # check for all timestamps/ filenames whether every sensor has an data sample for it
    for index, filename in enumerate(filenames_array):
        for sensor in sensors:
            # create exact filename for sensor based on the sensor name
            if "Cam" in sensor:
                # data is stored as .jpg file for all cameras
                file_path = os.path.join(
                    dataset_path, sensor, filenames_array[index]+".jpg")
            else:
                # data is stored as .csv file for all other sensors
                file_path = os.path.join(
                    dataset_path, sensor, filenames_array[index]+".csv")

            # append the filename and the exact filename to the lists
            if not path.exists(file_path):
                incomplete_samples_list.append(filename)
                complete_incomplete_samples_list.append(file_path)

    # convert incomplete_samples_list to a set to remove doubled values
    incomplete_samples_set = set(incomplete_samples_list)

    return incomplete_samples_set, complete_incomplete_samples_list


@gin.configurable
def get_list_of_corrupt_IMU_files(dataset_path, corrupt_threshold):
    """
        Function to get the list of IMU files which contain the same value for at least corrupt_threshold times.

        Parameters:
            - dataset_path (str): Path to the dataset which shall be checked
            - corrupt_threshold (int): Threshold for selection criteria to classify corrupted files

        Returns:
            - corrupt_files_list (list): List of filenames (without type extension) which are corrupt
    """
    # determine first IMU sensor (all have the same corrupted data due to parallel measurement from the same data source)
    IMU_sensor = None
    for root, dirs, files in os.walk(dataset_path):
        for sensor in dirs:
            if not "Cam" in sensor:
                IMU_sensor = sensor
                break
        break

    # load array with filenames from dataset
    filenames_array = pd.read_csv(os.path.join(
        dataset_path, "labels.csv"), sep=";", header=0).to_numpy()[:, 0]

    corrupt_files_list = []

    for index, filename in enumerate(filenames_array):
        file_path = os.path.join(
            dataset_path, IMU_sensor, filename+".csv")
        data = np.loadtxt(file_path, delimiter=";")

        # get counts of unique elements to determine max occurrence within file
        unique, counts = np.unique(data, return_counts=True)
        max_occurrence = max(counts)

        if max_occurrence > corrupt_threshold:
            corrupt_files_list.append(filename)

    return corrupt_files_list


def delete_incomplete_data_samples(dataset_path, incomplete_samples_set):
    """
        Function to delete all incomplete data samples (where not all data for each sensors is present from) based on provided incomplete_samples_set.

        Parameters:
            - dataset_path (str): Path to the dataset
            - incomplete_samples_set (set): Set containing all timestamp strings for which at least one sensors does not provide data
    """
    # get list of all sensors
    sensors = []
    for root, dirs, files in os.walk(dataset_path):
        for sensor in dirs:
            sensors.append(sensor)

    # remove samples of incomplete_samples_set for all sensors
    for sample_name in incomplete_samples_set:
        for sensor in sensors:
            if "Cam" in sensor:
                # cameras have .jpg files
                filename = os.path.join(
                    dataset_path, sensor, sample_name+".jpg")
            else:
                # other sensors have .csv files
                filename = os.path.join(
                    dataset_path, sensor, sample_name+".csv")

            # use try/except, to handle case where file is already missing (which is always the case for at least sensor)
            try:
                os.remove(filename)
            except:
                pass


def update_labels_csv(dataset_path, incomplete_samples_set):
    """
        Function to remove incomplete data samples (where not all data for each sensors is present from) from labels.csv based on provided incomplete_samples_set.

        Parameters:
            - dataset_path (str): Path to the dataset
            - incomplete_samples_set (set): Set containing all timestamp strings for which at least one sensors does not provide data

        Returns:
            - new_length (int): Length of the new labels file 
    """
    # load current labels list
    sample_label_mapping = pd.read_csv(os.path.join(
        dataset_path, "labels.csv"), sep=";", header=0).to_numpy()
    # get length of the list for later plausibility checks
    prev_length = np.shape(sample_label_mapping)[0]

    # remove samples from incomplete_samples_list
    new_length = None
    for incomplete_sample in incomplete_samples_set:
        sample_label_mapping = sample_label_mapping[np.where(
            sample_label_mapping[:, 0] != incomplete_sample)]

        # check whether update was plausible (only one entry was removed)
        new_length = np.shape(sample_label_mapping)[0]
        if prev_length != new_length + 1:
            raise Exception(
                f"Something went wrong during label list modification! for {incomplete_sample}, {prev_length}, {new_length}")
        prev_length = new_length

    # save modified version
    np.savetxt(os.path.join(dataset_path, "labels.csv"),
               sample_label_mapping, delimiter=";", header="timestamp;label", fmt="%s")

    return new_length


if __name__ == "__main__":
    pass
    # dataset_path = r"C:\Users\Dominik\Downloads\FTDD_1.0"
    # incomplete_samples_list, _ = get_incomplete_data_samples(dataset_path)

    # delete_incomplete_data_samples(dataset_path, incomplete_samples_list)

    # update_labels_csv(dataset_path, incomplete_samples_list)
