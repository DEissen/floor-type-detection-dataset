
from os import path
import os
import pandas as pd
import numpy as np

def get_incomplete_data_samples(dataset_path):
    """

        Parameters:
            - dataset_path (str): Path to the dataset
    """
    filenames_array = pd.read_csv(os.path.join(dataset_path, "labels.csv"), sep=";", header=0).to_numpy()[:,0]
    filenames_list = list(filenames_array)

    sensors = []
    for root, dirs, files in os.walk(dataset_path):
        for sensor in dirs:
            sensors.append(sensor)

    incomplete_samples_list = []
    complete_incomplete_samples_list = []
    for index, file in enumerate(filenames_array):
        for sensor in sensors:
            if "Cam" in sensor:
                # data is stored as .jpg file for all cameras
                file_path = os.path.join(
                    dataset_path, sensor, filenames_array[index]+".jpg")
            else:
                # data is stored as .csv file for all other sensors
                file_path = os.path.join(dataset_path, sensor, filenames_array[index]+".csv")

            if not path.exists(file_path):
                # print(f"{file_path} does not exit for every sensor")
                incomplete_samples_list.append(file)
                complete_incomplete_samples_list.append(file_path)
    
    return set(incomplete_samples_list), complete_incomplete_samples_list


def delete_incomplete_data_samples(dataset_path, incomplete_samples_list):
    """

        Parameters:
            - dataset_path (str): Path to the dataset
    """

    # modified_array = test[np.where(test[:,0] != 3)]

    # get list of all sensors
    sensors = []
    for root, dirs, files in os.walk(dataset_path):
        for sensor in dirs:
            sensors.append(sensor)

    # remove samples of incomplete_samples_list for all sensors
    for sample_name in incomplete_samples_list:
        for sensor in sensors:
            if "Cam" in sensor:
                # cameras have .jpg files
                filename = os.path.join(dataset_path, sensor, sample_name+".jpg")
            else:
                # other sensors have .csv files
                filename = os.path.join(dataset_path, sensor, sample_name+".csv")

            try:
                os.remove(filename)
                print("Deleted something")
            except:
                # print(f"File {filename} could not be deleted for {sensor} as it's already not present")
                pass

def update_labels_csv(dataset_path, incomplete_samples_list):
    # load list
    sample_label_mapping = pd.read_csv(os.path.join(dataset_path, "labels.csv"), sep=";", header=0).to_numpy()
    prev_length = np.shape(sample_label_mapping)[0]

    # remove samples from incomplete_samples_list
    for incomplete_sample in incomplete_samples_list:
        sample_label_mapping = sample_label_mapping[np.where(sample_label_mapping[:,0] != incomplete_sample)]

        # check whether update was plausible
        new_length = np.shape(sample_label_mapping)[0]
        if prev_length != new_length + 1:
            raise Exception(f"Something went wrong during label list modification! for {incomplete_sample}, {prev_length}, {new_length}")
        prev_length = new_length

    # save modified version
    np.savetxt(os.path.join(dataset_path, "labels.csv"),
               sample_label_mapping, delimiter=";", header="timestamp;label", fmt="%s")


if __name__ =="__main__":
    pass
    # dataset_path = r"C:\Users\Dominik\Downloads\FTDD_1.0"
    # incomplete_samples_list, _ = get_incomplete_data_samples(dataset_path)

    # delete_incomplete_data_samples(dataset_path, incomplete_samples_list)

    # update_labels_csv(dataset_path, incomplete_samples_list)