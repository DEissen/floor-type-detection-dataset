import numpy as np
import matplotlib.pyplot as plt
import cv2
import glob
import os


def show_camera_images_in_parallel(cam1_image_path, cam2_image_path, cam3_image_path, cam4_image_path, cam5_image_path, imu_data=None, imu_position=None):
    """
        Function to show five camera images in parallel in on plot.

        Parameters:
            - cam1_image_path: Path to image for "Belly Cam"
            - cam2_image_path: Path to image for "Chin Cam"
            - cam3_image_path: Path to image for "Head Cam"
            - cam4_image_path: Path to image for "Left Cam"
            - cam5_image_path: Path to image for "Right Cam"
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
        plt.vlines(imu_position, ymin=np.min(imu_data), ymax=np.max(imu_data), color = "red")

    plt.show()


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
        filename_list.append(glob.glob(files_glob_pattern))

    for i in range(len(filename_list[0])):
        try:
            # show i-th image of every camera
            show_camera_images_in_parallel(
                filename_list[0][i], filename_list[1][i], filename_list[2][i], filename_list[3][i], filename_list[4][i])
        except IndexError:
            # stop in case of IndexError, which can happen if BellyCam has more images then the other cameras
            break

def show_all_images_afterwards_including_imu_data(measurement_path, imu_data):
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
        filename_list.append(glob.glob(files_glob_pattern))

    for i in range(len(filename_list[0])):
        # images return every 200 ms => IMU data has values every 20 ms => next image fits to timestamp 10 measurements later
        imu_position = 10 * i
        try:
            # show i-th image of every camera
            show_camera_images_in_parallel(
                filename_list[0][i], filename_list[1][i], filename_list[2][i], filename_list[3][i], filename_list[4][i], imu_data, imu_position)
        except IndexError:
            # stop in case of IndexError, which can happen if BellyCam has more images then the other cameras
            break

if __name__ == "__main__":
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    show_all_images_afterwards(temp_path)
