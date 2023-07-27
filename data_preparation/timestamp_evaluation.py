import glob
import os
from datetime import datetime

def get_synchronized_timestamps():
    """
        Function to return the closest timestamp for each camera to the first timestamp of the IMU measurements.
        NOTE: Measurement data must be present in temp directory! 
    """
    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")
    
    # TODO: 
    headCam_path = os.path.join(temp_path, "HeadCam", "*.jpg")
    
    headCam_files = glob.glob(headCam_path)
    test = headCam_files[0].split(os.sep)[-1]
    print(test)

def get_timestamp_from_picture(filename):
    """
        Function to convert the filename of a picture to it's timestamp.

        Parameters:
            - filename: The name of a picture from a measurement

        Returns:
            - (datetime.datetime): datetime object of the timestamp for further processing
    """
    timestamp_string = ""
    if filename[0] == "L":
        timestamp_string = filename[5:-4]
    elif filename[0] == "R":
        timestamp_string = filename[6:-4]
    else:
        raise Exception(f"Unexpected picture filename in timestamp evaluation!\n'{filename}' does not start with 'L' or 'R'!")

    return datetime.strptime(timestamp_string, "%H_%M_%S_%f")

if __name__ == "__main__":
    get_synchronized_timestamps()