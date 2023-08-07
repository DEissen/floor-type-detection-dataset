import glob
import os
from datetime import datetime, timedelta
import json


def get_synchronized_timestamps(measurement_path):
    """
        Function to return the closest timestamp for each camera to the earliest timestamp of the IMU measurements.

        Parameters:
            - measurement_path (str): path to the measurement
    """
    # struct to store all the timestamps
    timestamps = {}
    # get measurement date first for all timestamps
    measurement_date = get_measurement_date_from_info_json(temp_path)

    # get the earliest timestamp of the IMU measurements
    timestamps["IMU"] = get_earliest_timestamp_from_IMU(
        measurement_path, measurement_date)

    # # TODO:
    # headCam_path = os.path.join(measurement_path, "HeadCam", "*.jpg")

    # headCam_files = glob.glob(headCam_path)
    # test = headCam_files[0].split(os.sep)[-1]
    # timestamp = get_timestamp_from_picture(test, measurement_date)


def get_timestamp_from_picture(filename, measurement_date):
    """
        Function to convert the filename of a picture to it's timestamp as a datetime object for further processing.

        Parameters:
            - filename (str): The name of a picture from a measurement
            - measurement_date (datetime.datetime): date of the measurement for the timestamp

        Returns:
            - (datetime.datetime): datetime object of the timestamp for further processing
    """
    # get timestamp string from filename which has a different starting position depending whether filename starts with "Left" or "Right"
    timestamp_string = ""
    if filename[0] == "L":
        timestamp_string = filename[5:-4]
    elif filename[0] == "R":
        timestamp_string = filename[6:-4]
    else:
        raise Exception(
            f"Unexpected picture filename in timestamp evaluation!\n'{filename}' does not start with 'L' or 'R'!")

    return get_timestamp_from_timestamp_string(timestamp_string, measurement_date)


def get_earliest_timestamp_from_IMU(measurement_path, measurement_date):
    """
        Function to the earliest timestamp of the IMU measurements as a datetime object for further processing.

        Parameters:
            - measurement_path (str): path to the measurement
            - measurement_date (datetime.datetime): date of the measurement for the timestamp

        Returns:
            - (datetime.datetime): datetime object of the earliest timestamp for further processing
    """
    # list of checked dirs for debugging info
    checked_dirs = []

    # get the timestamp string from any IMU measurement folder (all measurements are done in parallel, thus it doesn't matter which one is taken)
    for root, dirs, files in os.walk(measurement_path):
        # check for IMU measurement dir (all dirs without "Cam" in the name)
        for dir in dirs:
            checked_dirs.append(dir)
            if not "Cam" in dir:
                # get filename of first file in the dir
                glob_pattern = os.path.join(root, dir, "*.csv")
                files = glob.glob(glob_pattern)
                first_filename = files[0].split(os.sep)[-1]

                # extract timestamp string from filename and convert it
                earliest_timestamp_string = first_filename[:-4]
                return get_timestamp_from_timestamp_string(earliest_timestamp_string, measurement_date)

    raise Exception(
        f"No IMU measurement present in directory {measurement_path}\nIt only contains the following dirs: {checked_dirs}")


def get_timestamp_from_timestamp_string(timestamp_string:str, measurement_date:datetime):
    """
        Function to convert a timestamp string in the format "hh_mm_ss_xxx" (where xxx are the milliseconds) to a datetime object for further processing.

        Parameters:
            - timestamp_string (str): The timestamps string to convert which mus have the format "hh_mm_ss_xxx" where xxx are the milliseconds
            - measurement_date (datetime.datetime): date of the measurement for the timestamp

        Returns:
            - (datetime.datetime): datetime object of the timestamp for further processing
    """
    # get hours, ... from timestamp string and convert it to seconds and milliseconds only which are needed for timedelta object
    hours = int(timestamp_string.split("_")[0])
    minutes = int(timestamp_string.split("_")[1])
    seconds = int(timestamp_string.split("_")[2])
    millis = int(timestamp_string.split("_")[3])
    total_seconds = seconds + minutes * 60 + hours * 3600
    timestamp = timedelta(seconds=total_seconds, milliseconds=millis)

    # return timestamp by adding timestamp to the measurement date (thus timestamp must be of timedelta type)
    return measurement_date + timestamp


def get_measurement_date_from_info_json(measurement_path):
    """
        Function to get measurement date from info.json file.

        Parameters:
            - measurement_path (str): path to the measurement

        Returns:
            - (datetime.datetime): datetime object of the date from the info.json file
    """
    json_path = os.path.join(measurement_path, "info.json")

    with open(json_path, "r") as f:
        info_struct = json.load(f)
        return datetime.strptime(info_struct["measurement_date"], "%d.%m.%Y")


if __name__ == "__main__":
    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    get_synchronized_timestamps(temp_path)
