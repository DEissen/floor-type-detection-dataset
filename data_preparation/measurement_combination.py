import os
from distutils.dir_util import copy_tree
import pandas as pd
import numpy as np


def combine_measurements_to_dataset(prepared_measurements_base_path, dataset_path):
    """
        Function combine multiple prepared datasets to a single dataset.

        Parameters:
            - prepared_measurements_base_path (str): Path to dir where the prepared measurements are currently stored
            - dataset_path (str): Path to dir where the measurements shall be copied to
    """
    print(
        f"Start creating dataset from measurements at path: {prepared_measurements_base_path}")
    label_mapping_list = []
    measurement_names_for_logging = []
    # perform data preparation for every measurement in the measurement base path
    for root, dirs, files in os.walk(prepared_measurements_base_path):
        measurement_names_for_logging = dirs
        for measurement_dir in dirs:
            measurement_path = os.path.join(root, measurement_dir)

            copy_measurement_to_dataset(measurement_path, dataset_path)

            label_mapping_list.append(
                get_labels_timestamp_mapping(measurement_path))

        # break after first for loop to only explore the top level of measurement_base_path
        break

    print("\nCombining label files from all measurements")
    combined_label_mapping = np.asarray(label_mapping_list[0])
    for i in range(1, len(label_mapping_list)):
        combined_label_mapping = np.append(
            combined_label_mapping, np.asarray(label_mapping_list[i]), axis=0)

    # save labels file with all labels
    combined_label_file_path = os.path.join(dataset_path, "labels.csv")
    np.savetxt(combined_label_file_path,
               combined_label_mapping, delimiter=";", header="timestamp;label", fmt="%s")
    print(f"Saved new label file at {combined_label_file_path}")

    # final clean up of the dataset
    print("\nRemove obsolete files from dataset")
    os.remove(os.path.join(dataset_path, "data_preparation.log"))
    os.remove(os.path.join(dataset_path, "info.json"))

    # print infos about measurements added to dataset
    print(
        f"\nDataset was successfully created and can be found here: {dataset_path}")
    print("\nPlease update the datasheet.md file manually with the following details:")
    print(f"Total instances in the dataset: {len(combined_label_mapping)}")
    print("The following measurements are included:")
    for measurement in measurement_names_for_logging:
        print(f"- {measurement}")


def copy_measurement_to_dataset(measurement_path, dataset_path):
    """
        Function to copy the data from the measurement at measurement_path to the dataset at dataset_path.

        Parameters:
            - measurement_path (str): Path to dir where the measurement is currently stored
            - dataset_path (str): Path to dir where the measurement shall be copied to
    """
    print(f"Copy files from {measurement_path} to {dataset_path}")
    copy_tree(measurement_path, dataset_path)


def get_labels_timestamp_mapping(measurement_path):
    """
        Function to load and return the label-timestamp mapping from a labels.csv file located at measurement_path.

        Parameters:
            - measurement_path (str): Path to the dataset/ measurement where the labels.csv file is located

        Return:
            - (numpy.array): Numpy array with label-timestamp mapping from labels.csv file
    """
    return pd.read_csv(os.path.join(
        measurement_path, "labels.csv"), sep=";", header=0).to_numpy()


if __name__ == "__main__":
    prepared_measurements_base_path = r"update_with_path_to_prepared_datasets"
    dataset_path = r"update_with_path_to_new_datasets"

    combine_measurements_to_dataset(
        prepared_measurements_base_path, dataset_path)
