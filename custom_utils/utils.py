import os
from distutils.dir_util import copy_tree
import shutil
import glob
import numpy as np
import zipfile

def clean_temp_dir():
    """
        Function to clear the temp/ directory in the repository which shall be called at the beginning of each data preparation step.
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    for root, dirs, files in os.walk(temp_path):
        # remove all subdirectories in temp/
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
        # remove all files in temp/
        for file in files:
            os.remove(os.path.join(root, file))

def copy_measurement_to_temp(measurement_path):
    """
        Util function to copy a measurement from measurement_path to the temp/ dir in the repository for further preprocessing.
        If measurement_path points to a zip file, the zip file will be extracted to temp/ instead.
        
        Parameters:
            - measurement_path: Path to the directory of the measurement which includes all the sensor data and the info.json file.
                                NOTE: If measurement_path ends with ".zip", this file will be extracted instead.
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")
    
    print(f"{measurement_path} will be copied/ extracted to {temp_path}")
    
    if ".zip" == measurement_path[-4:]:
        # unzip zip file to temp path if measurement path point to zip file
        with zipfile.ZipFile(measurement_path, "r") as zip_file:
            zip_file.extractall(temp_path)
    else:
        # if measurement path contains files, directly copy the measurement path content
        copy_tree(measurement_path, temp_path)

    print(f"Files were successfully copied to {temp_path}")

def copy_prepared_dataset(dataset_path=None):
    """
        Util function to copy a prepared dataset from the temp/ dir in the repository to dataset_path.
        If dataset_path is equal to None, the dataset will be copied to results/ dir in the repository.
        
        Parameters:
            - dataset_path: Path to the directory where the prepared dataset shall be copied to
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    if dataset_path == None:
        dataset_path = os.path.join(file_dir, os.pardir, "results")
    
    print(f"Prepared dataset will be copied to {dataset_path}")
    
    # if measurement path contains files, directly copy the measurement path content
    copy_tree(temp_path, dataset_path)

    print(f"Files were successfully copied to {dataset_path}")
