import numpy as np
import matplotlib.pyplot as plt
import cv2
import glob
import os


def show_camera_images_in_parallel(cam1_image_path, cam2_image_path, cam3_image_path, cam4_image_path, cam5_image_path, imu_data=None, imu_position=None):
    """
        Function to show five camera images in parallel in on plot and optionally IMU data with red vertical line in 6th subplot.

        Parameters:
            - cam1_image_path: Path to image for "Belly Cam"
            - cam2_image_path: Path to image for "Chin Cam"
            - cam3_image_path: Path to image for "Head Cam"
            - cam4_image_path: Path to image for "Left Cam"
            - cam5_image_path: Path to image for "Right Cam"
            - imu_data (np.array): Optional IMU data to add in 6th subplot
            - imu_position (int): Optional position of vertical red line in IMU data subplot
    """
    # initialize figure and related variables
    columns = 3
    rows = 2
    fig = plt.figure(figsize=(20, 13))
    ax = []

    # load images
    img1 = cv2.imread(cam1_image_path)
    img2 = cv2.imread(cam2_image_path)
    img3 = cv2.imread(cam3_image_path)
    img4 = cv2.imread(cam4_image_path)
    img5 = cv2.imread(cam5_image_path)

    ax.append(fig.add_subplot(rows, columns, 1))
    ax[-1].set_title("Belly Cam")
    plt.imshow(img1)

    ax.append(fig.add_subplot(rows, columns, 2))
    ax[-1].set_title("Chin Cam")
    plt.imshow(img2)

    ax.append(fig.add_subplot(rows, columns, 3))
    ax[-1].set_title("Head Cam")
    plt.imshow(img3)

    ax.append(fig.add_subplot(rows, columns, 4))
    ax[-1].set_title("Left Cam")
    plt.imshow(img4)

    ax.append(fig.add_subplot(rows, columns, 5))
    ax[-1].set_title("Right Cam")
    plt.imshow(img5)

    if imu_position != None:
        ax.append(fig.add_subplot(rows, columns, 6))
        ax[-1].set_title("IMU data")
        x = np.arange(0, np.shape(imu_data)[0])
        plt.plot(x, imu_data)
        plt.vlines(imu_position, ymin=np.min(imu_data),
                   ymax=np.max(imu_data), color="red")

    plt.show(block=False)
    plt.pause(1)
    plt.close("all")


def show_all_images_afterwards(measurement_path):
    """
        Function to show all images for all cameras from measurement_path in one figure after another.

        Parameter:
            - measurement_path (str): Path to the measurement
    """
    cameras = ["BellyCam", "ChinCam", "HeadCam", "LeftCam", "RightCam"]
    filename_list = []

    # get filenames of all images and add them to filename_list
    for camera in cameras:
        files_glob_pattern = os.path.join(measurement_path, camera, "*.jpg")
        files = glob.glob(files_glob_pattern)
        files.sort()
        filename_list.append(files)

    for i in range(len(filename_list[0])):
        try:
            # show i-th image of every camera
            show_camera_images_in_parallel(
                filename_list[0][i], filename_list[1][i], filename_list[2][i], filename_list[3][i], filename_list[4][i])
        except IndexError:
            # stop in case of IndexError, which can happen if BellyCam has more images then the other cameras
            break


def show_all_images_afterwards_including_imu_data(measurement_path, imu_data, imu_offset=0):
    """
        Function to show all images for all cameras from measurement_path in one figure after another.

        Parameter:
            - measurement_path (str): Path to the measurement
            - imu_data (np.array): IMU data for plot
            - imu_offset (int): Offset for vertical line in IMU plot (needed if sliding windows were already created)
    """
    cameras = ["BellyCamLeft", "ChinCamLeft",
               "HeadCamLeft", "LeftCamLeft", "RightCamLeft"]
    filename_list = []

    # get filenames of all images and add them to filename_list
    for camera in cameras:
        files_glob_pattern = os.path.join(measurement_path, camera, "*.jpg")
        files = glob.glob(files_glob_pattern)
        files.sort()
        filename_list.append(files)

    for i in range(len(filename_list[0])):
        # images are available every 200 ms => IMU data has values every 20 ms => next image fits to timestamp 10 measurements later
        imu_position = 10 * i + imu_offset
        try:
            # show i-th image of every camera
            show_camera_images_in_parallel(
                filename_list[0][i], filename_list[1][i], filename_list[2][i], filename_list[3][i], filename_list[4][i], imu_data, imu_position)
        except IndexError:
            # stop in case of IndexError, which can happen if BellyCam has more images then the other cameras
            break


def show_image_comparison(old_image, new_image, title):
    """
        Function to show two images next to each other (e.g. to visualize image preprocessing).

        Parameter:
            - old_image (PIL.Image): First image to show
            - new_image (PIL.Image): Second image to show (on the right side)
            - title (str): String with the title for the plot
    """
    columns = 2
    rows = 1
    fig = plt.figure(figsize=(20, 13))
    ax = []

    plt.title(title)

    ax.append(fig.add_subplot(rows, columns, 1))
    ax[-1].set_title("old image")
    plt.imshow(old_image)

    ax.append(fig.add_subplot(rows, columns, 2))
    ax[-1].set_title("preprocessed image")
    plt.imshow(new_image)
    plt.show()


if __name__ == "__main__":
    # file_dir = os.path.dirname(os.path.abspath(__file__))
    # temp_path = os.path.join(file_dir, os.pardir, "temp")

    # show_all_images_afterwards(temp_path)

    pass
