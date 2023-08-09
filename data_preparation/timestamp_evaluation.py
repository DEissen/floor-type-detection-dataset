import glob
import os
from datetime import datetime, timedelta
import json


def get_synchronized_timestamps(measurement_path, earliest_IMU_timestamp=None):
    """
        Function to return the closest timestamp for each camera to the earliest possible timestamp of the IMU measurements.
        The time diff between the timestamps of cameras and the IMU is not allowed to be bigger than 200 ms (due to 5 FPS for camera capturing) to ensure pictures belong to IMU data. 

        Parameters:
            - measurement_path (str): path to the measurement
            - earliest_IMU_timestamp (datetime.datetime): timestamp to use for further calculations. If equal to "None", this function will be called recursively with an corrected IMU timestamp.

        Returns:
            - (dict): Dictionary containing the closest timestamps for each camera and the earliest timestamp of the IMU measurements
    """
    timestamps = {}  # struct to store all the timestamps
    time_diffs = {}  # struct to store all time diffs
    checked_dirs = []  # list of checked dirs for debugging info
    camera_dir_found = False  # Flag for error detection

    # get measurement date first for all timestamps
    measurement_date, time_diff_data = get_data_from_info_json_for_timestamp_evaluation(
        measurement_path)

    # get the earliest timestamp of the IMU measurements from files if it's not provided as function parameter
    if earliest_IMU_timestamp == None:
        timestamps["IMU"] = get_earliest_timestamp_from_IMU(
            measurement_path, measurement_date)
    else:
        timestamps["IMU"] = earliest_IMU_timestamp

    # get the timestamp string for all cameras
    for root, dirs, files in os.walk(measurement_path):
        for dir in dirs:
            checked_dirs.append(dir)
            # only further process dirs which contain "Cam" in their name
            if "Cam" in dir:
                camera_dir_found = True

                # get closest timestamp and time_diff to corrected reference timestamp for the current camera
                timestamps[dir], time_diffs[dir] = get_closest_timestamp_for_camera(
                    measurement_path, dir, measurement_date, timestamps["IMU"], time_diff_data)

    if not camera_dir_found:
        raise Exception(
            f"No camera directory present in directory {measurement_path}\nIt only contains the following dirs: {checked_dirs}")

    # # print statement for debugging purposes
    # for key, value in timestamps.items():
    #     try:
    #         print(key, value, "\twith time diff:", time_diffs[key])
    #     except:
    #         print(key, value)

    # check if max_time_diff is greater than 200 ms for any camera started, which is the sampling rate of the images (5 FPS)
    max_time_diff = max(time_diffs.values())
    if max_time_diff > timedelta(milliseconds=200):
        # in earliest_IMU_timestamp was not provided as a parameter but taken from files, this is plausible as the first IMU measurement might have started too early
        if earliest_IMU_timestamp == None:
            print("The maximum time diff of all cameras is greater than 200 ms (sampling rate of cameras), which means earliest IMU measurement is older than earliest picture! \
                    \nThus synchronized timestamps will be recalculated for expected first parallel IMU measurement when last camera started taking pictures.\n")

            # new timestamp must be fitting to the 50 Hz capturing rate of the IMU data => thus corrected IMU timestamp must updated by time diff in 20 ms steps
            max_time_diff_ms = round(max_time_diff.microseconds / 1000)
            if max_time_diff_ms % 20 != 0:
                max_time_diff_ms = max_time_diff_ms - (max_time_diff_ms % 20)
            corrected_earliest_IMU_timestamp = timestamps["IMU"] + timedelta(
                milliseconds=max_time_diff_ms)

            timestamps = get_synchronized_timestamps(
                measurement_path, earliest_IMU_timestamp=corrected_earliest_IMU_timestamp)
        else:
            raise Exception(
                f"Time diff for a camera is greater than 200 ms for a corrected earliest IMU timestamp. This shouldn't be possible! Please check your data.\nResults of synchronized timestamp calculation: {time_diffs}")

    return timestamps


def get_closest_timestamp_for_camera(measurement_path, camera_name, measurement_date, reference_timestamp, time_diff_data):
    """
        Function to return closest timestamp to the reference_timestamp considering time_diff_data for the camera.

        Parameters:
            - measurement_path (str): path to the measurement
            - camera_name (str): name of the camera to check which is also the directory name
            - measurement_date (datetime.datetime): date of the measurement for the timestamp
            - reference_timestamp (datetime.datetime): reference timestamp for search
            - time_diff_data (struct): struct containing the time_diff_data from the info.json

        Returns:
            - return values of function get_closest_timestamp()
    """
    # local variables
    timestamps = []
    time_diff = None
    later_timestamp = None

    # extract all timestamps from camera directory
    files_glob_pattern = os.path.join(measurement_path, camera_name, "*.jpg")
    cam_files = glob.glob(files_glob_pattern)
    for cam_file in cam_files:
        filename = cam_file.split(os.sep)[-1]
        timestamps.append(get_timestamp_from_picture(
            filename, measurement_date))

    # get fitting time_diff_data for camera for reference_timestamp correction
    if "ChinCam" in camera_name or "HeadCam" in camera_name:
        time_diff = time_diff_data["time_diff_13_in_ms"]["corrected"]
        later_timestamp = time_diff_data["time_diff_13_in_ms"]["later timestamp on"]
    elif "RightCam" in camera_name or "LeftCam" in camera_name:
        time_diff = time_diff_data["time_diff_14_in_ms"]["corrected"]
        later_timestamp = time_diff_data["time_diff_14_in_ms"]["later timestamp on"]
    elif "BellyCam" in camera_name:
        time_diff = time_diff_data["time_diff_15_in_ms"]["corrected"]
        later_timestamp = time_diff_data["time_diff_15_in_ms"]["later timestamp on"]
    else:
        raise Exception(
            f"Unexpected camera name: '{camera_name}', thus execution is stopped!")

    # correct reference_timestamp by using time_diff_data
    if later_timestamp == "local PC":
        # as reference timestamp is from local PC, the time_diff must be subtracted in case local PC had the later time = was in front of remote time
        reference_timestamp = reference_timestamp - \
            timedelta(milliseconds=time_diff)
    # value "local PC (only uncorrected)" for later_timestamp means remote PC was later timestamp for corrected time_diff
    elif later_timestamp == "remote PC" or later_timestamp == "local PC (only uncorrected)":
        # as reference timestamp is from local PC, the time_diff must be added in case local PC had the later time = was behind of remote time
        reference_timestamp = reference_timestamp + \
            timedelta(milliseconds=time_diff)
    else:
        raise Exception(
            f"Unexpected value for later_timestamp: '{later_timestamp}', thus execution is stopped!")

    # # print statement for debugging purposes
    # print(
    #     f"Corrected IMU timestamp for {camera_name} as reference_timestamp is: ", reference_timestamp)

    return get_closest_timestamp(timestamps, reference_timestamp)


def get_closest_timestamp(timestamps, reference_timestamp):
    """
        Function to get closest timestamp from timestamps (list) to reference_timestamp.
        Function is based on the following post: https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date

        Parameters:
            - timestamps (list): list of timestamps where closest timestamp shall be searched
            - reference_timestamp (datetime.datetime): reference for search

        Returns:
            - closest_timestamp (datetime.datetime): closest timestamp
            - time_diff (datetime.timedelta): timedelta of closest_timestamp to reference_timestamp
    """
    closest_timestamp = min(
        timestamps, key=lambda x: abs(x - reference_timestamp))
    time_diff = abs(closest_timestamp - reference_timestamp)
    return closest_timestamp, time_diff


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


def get_timestamp_from_timestamp_string(timestamp_string: str, measurement_date: datetime):
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


def get_data_from_info_json_for_timestamp_evaluation(measurement_path):
    """
        Function to get data from info.json file needed for timestamp evaluation.

        Parameters:
            - measurement_path (str): path to the measurement

        Returns:
            - measurement_date (datetime.datetime): datetime object of the date from the info.json file
            - time_diff_data (struct): strut containing the time diff data
    """
    json_path = os.path.join(measurement_path, "info.json")

    with open(json_path, "r") as f:
        info_struct = json.load(f)
        measurement_date = datetime.strptime(
            info_struct["measurement_date"], "%d.%m.%Y")
        time_diff_data = {"time_diff_13_in_ms": info_struct["time_diff_13_in_ms"],
                          "time_diff_14_in_ms": info_struct["time_diff_14_in_ms"],
                          "time_diff_15_in_ms": info_struct["time_diff_15_in_ms"]}
        return measurement_date, time_diff_data


if __name__ == "__main__":
    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    timestamps = get_synchronized_timestamps(temp_path)

    for key, value in timestamps.items():
        print(key, value)
