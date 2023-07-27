import os
from distutils.dir_util import copy_tree

def copy_measurement_to_temp(measurement_path):
    """
        Util function to copy a measurement from measurement_path to the temp/ dir in the repository for further preprocessing
        
        Parameters:
            - measurement_path: Path to the directory of the measurement which includes all the sensor data and the info.json file
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")
    copy_tree(measurement_path, temp_path)