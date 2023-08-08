import os
from distutils.dir_util import copy_tree
import shutil
import glob
import numpy as np

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
        Util function to copy a measurement from measurement_path to the temp/ dir in the repository for further preprocessing
        
        Parameters:
            - measurement_path: Path to the directory of the measurement which includes all the sensor data and the info.json file
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")
    copy_tree(measurement_path, temp_path)

def load_complete_IMU_measurement(measurement_path, sensor):
    """
        Function to load a complete IMU measurement for sensor from measurement_path in one array.

        Parameters:
            - measurement_path (str): Path to the measurement
            - sensor (str): Name of the sensor to load the data for
    """
    files_glob_pattern = os.path.join(measurement_path, sensor, "*.csv")
    filename_list = glob.glob(files_glob_pattern)
    
    data_list = []
    for file in filename_list:
        data_list.extend(np.genfromtxt(file, delimiter=';'))

    return np.asarray(data_list)