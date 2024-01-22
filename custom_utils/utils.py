import os
from distutils.dir_util import copy_tree
import shutil
import json
import zipfile
import logging


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


def clean_results_dir():
    """
        Function to clear the results/ directory in the repository which shall be called at the beginning of each data preparation step.
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "results")

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

    logging.info(f"{measurement_path} will be copied/ extracted to {temp_path}")

    if ".zip" == measurement_path[-4:]:
        # unzip zip file to temp path if measurement path point to zip file
        with zipfile.ZipFile(measurement_path, "r") as zip_file:
            zip_file.extractall(temp_path)
    else:
        # if measurement path contains files, directly copy the measurement path content
        copy_tree(measurement_path, temp_path)

    logging.info(f"Files were successfully copied to {temp_path}")


def copy_prepared_dataset(temp_path=None, dataset_path=None):
    """
        Util function to copy a prepared dataset from the temp/ dir in the repository to dataset_path.
        If dataset_path is equal to None, the dataset will be copied to results/ dir in the repository.

        Parameters:
            - temp_path (str): Path to the directory where the prepared dataset shall be copied from (Default = None)
                               If temp_path == None, then the default path will be taken "../temp"
            - dataset_path (str): Path to the directory where the prepared dataset shall be copied to (Default = None)
                               If temp_path == None, then the default path will be taken "../results"
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    if temp_path == None:
        temp_path = os.path.join(file_dir, os.pardir, "temp")

    if dataset_path == None:
        dataset_path = os.path.join(file_dir, os.pardir, "results")

    logging.info(f"Prepared dataset will be copied to {dataset_path}")

    # if measurement path contains files, directly copy the measurement path content
    copy_tree(temp_path, dataset_path)

    logging.info(f"Files were successfully copied to {dataset_path}")

def load_json_from_configs(json_filename):
    """
        Helper function to load any JSON file from the configs/ dir of the repo.

        Parameters:
            - json_filename (str): Name of the JSON file in the configs/ dir

        Returns:
            - json_as_dict (dict): Dict containing the data from the file json_filename
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(file_dir, os.pardir, "configs", json_filename)

    with open(json_path, "r") as f:
        json_as_dict = json.load(f)

    return json_as_dict

class CustomLogger():
    """
        CustomLogger class necessary to handle logging.Handler objects in case of multiple runs (to stop logging to previous runs).
    """

    def __init__(self, logging_level=0):
        """
            Init method which creates the std logger

            Parameters:
                - logging_level (int): Logging level to be assigned to the logger (e.g. DEBUG, INFO,...)
        """
        # create std logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging_level)

        # disable matplotlib font_manager logging as it's not needed
        logging.getLogger('matplotlib.font_manager').disabled = True

    def start_logger(self, log_dir_path, stream_log=False):
        """
            Update logger to stream/ save logging to file and stream and potentially remove old Handlers (from previous runs).

            Parameters:
                - log_dir_path (str): Path to dir where the log file shall be stored
                - stream_log (bool): boolean flag for plotting to console or not
        """
        # create log file
        log_file_path = os.path.join(log_dir_path, "data_preparation.log")
        with open(log_file_path, "a"):
            pass

        # add logging to file
        self.file_handler = logging.FileHandler(log_file_path)
        self.logger.addHandler(self.file_handler)

        # plot to console if wanted
        if stream_log:
            self.stream_handler = logging.StreamHandler()
            self.logger.addHandler(self.stream_handler)