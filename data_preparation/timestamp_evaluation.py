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
    elif filename[0] == "0" or filename[0] == "1" or filename[0] == "2" or filename[0] == "3" or filename[0] == "4" or filename[0] == "5" or filename[0] == "6" or filename[0] == "7" or filename[0] == "8" or filename[0] == "9":
        timestamp_string = filename[:-4]
    else:
        raise Exception(
            f"Unexpected picture filename in timestamp evaluation!\n'{filename}' does not start with 'L' or 'R' or a number!")

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


def get_timestamp_string_from_timestamp(timestamp: datetime):
    """
        Function to convert timestamp from datetime object to string. By using this function, the format can be changed at this single position.

        Parameters:
            - timestamp (datetime.datetime): datetime object to convert to string

        Return:
            - (str): Timestamp in format  "%H_%M_%S_%f"[:-3]
    """
    return timestamp.strftime("%H_%M_%S_%f")[:-3]

def remove_obsolete_data_at_end(measurement_path, last_allowed_timestamp_images):
    """
        Function to remove all obsolete images at the end of the measurement with the target that all sensors in measurement_path have
        an equal amount of images.

        Parameters:
            - measurement_path (str): Path to the measurement
            - last_allowed_timestamp_images (datetime.datetime): Last allowed timestamp of the images
    """
    # initialize local variables
    last_allowed_timestamp_IMU_checked = False
    deletion_for_IMU_needed = True
    last_allowed_timestamp = None
    
    # get measurement date first for all timestamps
    measurement_date, _ = get_data_from_info_json_for_timestamp_evaluation(
        measurement_path)

    # get list of all sensors
    sensor_list = []
    for root, dirs, files in os.walk(measurement_path):
        for dir in dirs:
            sensor_list.append(dir)

            # additionally get the last allowed timestamp from IMU measurement from the first checked IMU measurement
            if not last_allowed_timestamp_IMU_checked and not "Cam" in dir:
                # get filename of last file in the dir of IMU measurement
                glob_pattern = os.path.join(root, dir, "*.csv")
                files = glob.glob(glob_pattern)
                last_filename = files[-1].split(os.sep)[-1]

                # extract timestamp string from filename and convert it
                last_allowed_timestamp_string_IMU = last_filename[:-4]
                last_allowed_timestamp_IMU = get_timestamp_from_timestamp_string(last_allowed_timestamp_string_IMU, measurement_date)

                # set Flag to True so this check won't be done multiple times
                last_allowed_timestamp_IMU_checked = True

    # check which last allowed timestamp is earlier 
    if last_allowed_timestamp_IMU > last_allowed_timestamp_images:
        last_allowed_timestamp = last_allowed_timestamp_images
    else:
        last_allowed_timestamp = last_allowed_timestamp_IMU
        
        # in case the IMU timestamp is the last allowed timestamp, deletion for IMU data is not needed 
        deletion_for_IMU_needed = False
        print("No deletion of data from IMU measurements needed anymore, as they have the earliest last timestamp.")

    print(f"All data samples after {get_timestamp_string_from_timestamp(last_allowed_timestamp)} will be deleted now.")

    # delete obsolete files which not every camera contains
    for sensor in sensor_list:
        if not deletion_for_IMU_needed and not "Cam" in sensor:
            # skip IMU data, if there is no data to delete for IMU
            continue
        remove_obsolete_data_at_end_for_sensor(
            measurement_path, sensor, last_allowed_timestamp)

def remove_obsolete_data_at_end_for_sensor(measurement_path, sensor, last_allowed_timestamp):
    """
        Function to remove all obsolete images at the end of the sensor which are after last_allowed_timestamp.

        Parameters:
            - measurement_path (str): Path to the measurement
            - sensor (str): Name of the sensor to perform the function for
            - last_allowed_timestamp (datetime.datetime): Timestamp to use for further detection of obsolete images
    """
    # extract measurement date from earliest timestamp for get_timestamp_from_picture()
    measurement_date = datetime(year=last_allowed_timestamp.year,
                                month=last_allowed_timestamp.month, day=last_allowed_timestamp.day)

    # extract list of all files from sensor directory
    if "Cam" in sensor:
        # cameras have .jpg files
        files_glob_pattern = os.path.join(measurement_path, sensor, "*.jpg")
    else:
        # other sensors have .csv files
        files_glob_pattern = os.path.join(measurement_path, sensor, "*.csv")
    files = glob.glob(files_glob_pattern)

    # iterate over all files and check if file has to be removed
    for index, file in enumerate(files):
        # get timestamp of file
        current_filename = file.split(os.sep)[-1]
        current_timestamp = get_timestamp_from_picture(
            current_filename, measurement_date)

        if current_timestamp > last_allowed_timestamp:
            # remove cam_file after last_allowed_timestamp
            os.remove(file)


if __name__ == "__main__":
    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    # timestamps = get_synchronized_timestamps(temp_path)

    # for key, value in timestamps.items():
    #     print(key, value)

    test_date = datetime(year=2023, month=7, day=26, hour=12,
                        minute=59, second=12, microsecond=873000)
    remove_obsolete_data_at_end(temp_path, test_date)
