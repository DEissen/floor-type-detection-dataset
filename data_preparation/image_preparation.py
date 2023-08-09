import os
import glob
from datetime import datetime, timedelta

# differentiation needed to support execution of file directly and to allow function to be included by data_preparation_main.py
if __name__ == "__main__":
    from timestamp_evaluation import get_timestamp_from_picture
else:
    from data_preparation.timestamp_evaluation import get_timestamp_from_picture


def remove_obsolete_images_at_beginning(measurement_path, camera_name, earliest_timestamp):
    """
        Function to remove all images in the directory of camera_name in measurement_path before earliest_timestamp.
        If camera_name == "BellyCam", additionally the data will be downsampled, that it only contains images every ~200 ms
        instead of every ~100 ms, similar to the other cameras.

        Parameters:
            - measurement_path (str): Path to the measurement
            - camera_name (str): Name of the camera to perform the function for
            - earliest_timestamp (datetime.datetime): Timestamp to use for further calculations
    """
    # local variables
    reference_timestamp = earliest_timestamp
    restarted_for_right_camera_image_flag = True


    # extract measurement date from earliest timestamp for get_timestamp_from_picture()
    measurement_date = datetime(year=earliest_timestamp.year,
                                month=earliest_timestamp.month, day=earliest_timestamp.day)

    # extract list of all files from camera directory
    files_glob_pattern = os.path.join(measurement_path, camera_name, "*.jpg")
    cam_files = glob.glob(files_glob_pattern)

    # Check whether camera contains images of both stereo cameras
    if cam_files[0].split(os.sep)[-1][0] != cam_files[-1].split(os.sep)[-1][0]:
        print(f"Camera {camera_name} contains two picture Types!")
        restarted_for_right_camera_image_flag = False


    # iterate over all files and check if file has to be removed
    for index, cam_file in enumerate(cam_files):
        # stop for loop when index + 1 would be out of index range for cam_files 
        if (index + 1) > (len(cam_files) - 1):
            break

        # get timestamp of file
        current_filename = cam_file.split(os.sep)[-1]
        current_timestamp = get_timestamp_from_picture(
            current_filename, measurement_date)

        # reference_timestamp must be set to earliest_timestamp again when "Right_xxx" images start in the list
        if not restarted_for_right_camera_image_flag and current_filename[0] == "R":
            print("Considered both stereo cameras in one dir during removal ob obsolete images")
            reference_timestamp = earliest_timestamp
            restarted_for_right_camera_image_flag = True

        if current_timestamp < earliest_timestamp:
            # remove all files before the earliest timestamp
            os.remove(cam_file)
        elif (current_timestamp > earliest_timestamp) and ("BellyCam" in camera_name):
            # BellyCam images are captured every 100 ms instead of 200 ms, thus every second image shall be removed
            if timedelta() < (current_timestamp - reference_timestamp) < timedelta(milliseconds=190):
                # remove a file, if the timedelta to the reference_timestamp is > 0 ms and < 190 ms
                os.remove(cam_file)

                # update reference_timestamp with timestamp of the next file 
                next_filename = cam_files[index + 1].split(os.sep)[-1]
                next_timestamp = get_timestamp_from_picture(
                    next_filename, measurement_date)
                reference_timestamp = next_timestamp

def unify_timestamps(measurement_path):
    pass

def remove_obsolete_images_at_end(measurement_path):
    """
        Function to remove all obsolete images at the end of the measurement with the target that all cameras in measurement_path have
        an equal amount of images.

        Parameters:
            - measurement_path (str): Path to the measurement
    """
    # get the camera with the least images
    pass


if __name__ == "__main__":
    # # create path to temp directory
    # file_dir = os.path.dirname(os.path.abspath(__file__))
    # temp_path = os.path.join(file_dir, os.pardir, "temp")

    # testdate = datetime(year=2023, month=7, day=25, hour=15,
    #                     minute=3, second=15, microsecond=671000)
    # testdate2 = datetime(year=2023, month=7, day=25, hour=15,
    #                     minute=3, second=16, microsecond=106000)
    # testdate3 = datetime(year=2023, month=7, day=25, hour=15,
    #                     minute=3, second=15, microsecond=256000)

    # remove_obsolete_images(temp_path, "BellyCam", testdate)
    # remove_obsolete_images(temp_path, "ChinCam", testdate2)
    # remove_obsolete_images(temp_path, "HeadCam", testdate2)
    # remove_obsolete_images(temp_path, "LeftCam", testdate3)
    # remove_obsolete_images(temp_path, "RightCam", testdate3)
    pass
