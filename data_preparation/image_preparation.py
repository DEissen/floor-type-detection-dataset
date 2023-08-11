import os
import glob
from datetime import datetime, timedelta
import shutil

# differentiation needed to support execution of file directly and to allow function to be included by data_preparation_main.py
if __name__ == "__main__":
    from timestamp_evaluation import get_timestamp_from_picture, get_timestamp_string_from_timestamp
else:
    from data_preparation.timestamp_evaluation import get_timestamp_from_picture, get_timestamp_string_from_timestamp


def remove_obsolete_images_at_beginning(measurement_path, camera_name, earliest_timestamp):
    """
        Function to remove all images in the directory of camera_name in measurement_path before earliest_timestamp.
        If camera_name == "BellyCam", additionally the data will be downsampled, that it only contains images every ~200 ms
        instead of every ~100 ms, similar to the other cameras.
        NOTE: This is the only image preparation function that supports both stereo camera pictures to be stored in the same directory

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
            print(
                "Considered both stereo cameras in one dir during removal ob obsolete images")
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


def unify_image_timestamps(measurement_path, starting_timestamp):
    """
        Function to unify timestamps in filenames for all cameras.
        As a result all cameras will have images with the same timestamps starting at starting_timestamp incrementing by 200 ms.

        Parameters:
            - measurement_path (str): Path to the measurement
            - earliest_timestamp (datetime.datetime): Timestamp to use for first image name

        Returns:
            - earliest_last_image_timestamp (datetime.datetime): Timestamp of the earliest last image from all cameras
    """
    cameras_list = []
    camera_info_dict = {}

    # get list of all cameras
    for root, dirs, files in os.walk(measurement_path):
        for dir in dirs:
            if "Cam" in dir:
                cameras_list.append(dir)
                camera_info_dict[dir] = {}

    # initialize variables to search for camera with earliest last image (no camera should contain older images than this one)
    camera_earliest_last_image = ""
    # will definitely be later than any other timestamp
    earliest_last_image_timestamp = starting_timestamp + timedelta(days=10)

    # perform renaming of images for all cameras
    for camera in cameras_list:
        last_timestamp = rename_image_timestamps_for_single_camera(
            measurement_path, camera, starting_timestamp)

        if last_timestamp < earliest_last_image_timestamp:
            earliest_last_image_timestamp = last_timestamp
            camera_earliest_last_image = camera

    print(
        f"\nCamera with earliest last image is '{camera_earliest_last_image}' with timestamp {get_timestamp_string_from_timestamp(earliest_last_image_timestamp)}")

    return earliest_last_image_timestamp


def rename_image_timestamps_for_single_camera(measurement_path, camera_name, starting_timestamp):
    """
        Function to rename the timestamps in the image filenames for camera_name.
        As a result the the images will have filenames starting at starting_timestamp incrementing by 200 ms

        Prerequisites:
            - Images in dir camera_name were already prepared by function remove_obsolete_images()

        Parameters:
            - measurement_path (str): Path to the measurement
            - camera_name (str): Name of the camera to perform renaming for
            - earliest_timestamp (datetime.datetime): Timestamp to use for first image name

        Returns:
            - previous_timestamp_new_files (datetime.datetime): Timestamp of the last image
            - list_missing_timestamp_strings (list): List of all timestamp strings which are missing for this camera
    """
    # get all currently available files = with old timestamp
    glob_pattern = os.path.join(measurement_path, camera_name, "*.jpg")
    files_with_old_timestamp = glob.glob(glob_pattern)

    # check for each camera whether it contains both types of stereo camera images
    if files_with_old_timestamp[0].split(os.sep)[-1][0] != files_with_old_timestamp[-1].split(os.sep)[-1][0]:
        raise Exception(
            f"Images of both stereo cameras for '{camera_name}' are stored in the same directory! This is not supported!")

    # extract measurement date from starting timestamp for usage of get_timestamp_from_picture()
    measurement_date = datetime(year=starting_timestamp.year,
                                month=starting_timestamp.month, day=starting_timestamp.day)

    # initialize variables for loop
    # variable to store timestamp of previous file for the already present files
    previous_timestamp_present_files = None
    # variable to store timestamp of previous file for the new renamed files
    previous_timestamp_new_files = starting_timestamp
    # list to store strings of all timestamps that are missing
    list_missing_timestamp_strings = []

    # copy every file and name the new file with new timestamp
    for index, cam_file in enumerate(files_with_old_timestamp):
        new_filename = ""  # reset variable for new filename for each loop

        # get timestamp of current file
        current_filename = cam_file.split(os.sep)[-1]
        current_timestamp = get_timestamp_from_picture(
            current_filename, measurement_date)

        if index == 0:
            # for the first file previous_timestamp_present_files must be initialized
            previous_timestamp_present_files = current_timestamp

        # calculate number of passed capturing periods between this and the previous image (period = 200 ms)
        time_diff = current_timestamp - previous_timestamp_present_files
        passed_capturing_periods_between_images = int(
            time_diff.microseconds/180000)

        if passed_capturing_periods_between_images > 1:
            # in this case images are missing => log timestamp of missing images
            for i in range(1, passed_capturing_periods_between_images):
                missing_timestamp_string = get_timestamp_string_from_timestamp(previous_timestamp_new_files +
                                                                               i * timedelta(milliseconds=200))
                list_missing_timestamp_strings.append(missing_timestamp_string)
        elif passed_capturing_periods_between_images == 0:
            # in this case there is no period passed between the images
            if index == 0:
                # this is intended for the first image => do nothing in this case
                pass
            elif time_diff > timedelta(milliseconds=150):
                # if the time diff is smaller than 180 ms, but still bigger than 150 ms, the image shall be kept
                passed_capturing_periods_between_images = 1
            else:
                # otherwise passed_capturing_periods_between_images will stay 0 which leads to overwriting the previous images which shall be logged
                print(
                    f"For camera {camera_name} image with timestamp {get_timestamp_string_from_timestamp(current_timestamp)} is second images in this period! Only this file will be stored!")

        # get new filename based previous_timestamp_new_files
        timestamp_for_new_file = previous_timestamp_new_files + \
            passed_capturing_periods_between_images * \
            timedelta(milliseconds=200)
        new_filename = get_timestamp_string_from_timestamp(
            timestamp_for_new_file)

        # update previous timestamp for next image
        previous_timestamp_present_files = current_timestamp
        previous_timestamp_new_files = timestamp_for_new_file

        # copy image and name it with new timestamp
        path_new_file = os.path.join(
            measurement_path, camera_name, new_filename+".jpg")
        shutil.copy(cam_file, path_new_file)

        # remove old file
        os.remove(cam_file)

    # print(
    #     f"Images for camera '{camera_name}' are now renamed starting at timestamp {get_timestamp_string_from_timestamp(starting_timestamp)}")
    if list_missing_timestamp_strings != []:
        # TODO: maybe do something more with it than only logging (not needed yet as only obsolete images were missing in tests!
        print(
            f"The following timestamps are missing for camera {camera_name}: {list_missing_timestamp_strings}")

    return previous_timestamp_new_files


if __name__ == "__main__":
    # # create path to temp directory
    # file_dir = os.path.dirname(os.path.abspath(__file__))
    # temp_path = os.path.join(file_dir, os.pardir, "temp")

    # testdate1 = datetime(year=2023, month=7, day=25, hour=15,
    #                     minute=3, second=15, microsecond=671000)
    # testdate2 = datetime(year=2023, month=7, day=25, hour=15,
    #                     minute=3, second=16, microsecond=106000)
    # testdate3 = datetime(year=2023, month=7, day=25, hour=15,
    #                     minute=3, second=15, microsecond=256000)
    # remove_obsolete_images(temp_path, "BellyCam", testdate1)
    # remove_obsolete_images(temp_path, "ChinCam", testdate2)
    # remove_obsolete_images(temp_path, "HeadCam", testdate2)
    # remove_obsolete_images(temp_path, "LeftCam", testdate3)
    # remove_obsolete_images(temp_path, "RightCam", testdate3)

    # testdate = datetime(year=2023, month=7, day=26, hour=12,
    #                     minute=58, second=21, microsecond=671000)
    # unify_image_timestamps(temp_path, testdate)

    pass
