import glob
import sys
import os
import numpy as np
import cv2
assert cv2.__version__[
    0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'


# TODO Add docstring and refactor code in case this should be implemented => currently only test code!

# You should replace these 3 lines with the output in calibration step
# HeadCamLeft whole image
# DIM=(928, 800)
# K=np.array([[247.95508394318423, 0.0, 462.9566518515127], [0.0, 256.54308683948966, 393.07518230660753], [0.0, 0.0, 1.0]])
# D=np.array([[0.09576528233462508], [-0.020156930484074145], [-0.004964827084375215], [-0.00016655924468938804]])

# # RightCamLeft whole image
# DIM=(928, 800)
# K=np.array([[242.23659793695919, 0.0, 428.44542204059513], [0.0, 249.47175949082202, 405.9547919630125], [0.0, 0.0, 1.0]])
# D=np.array([[0.11308861842390595], [-0.05004910833737109], [0.008228742033458988], [-0.0011866542458063706]])

# # RightCamLeft cropped
# DIM=(705, 800)
# K=np.array([[255.89685459330136, 0.0, 347.6153888785984], [0.0, 265.85067478875175, 412.0669274016698], [0.0, 0.0, 1.0]])
# D=np.array([[0.12777183167729392], [-0.09593219277958943], [0.03356959828630282], [-0.006163703154471481]])

DIM = (928, 800)
K = np.array([[245.3350690661852, 0.0, 388.7927615625203], [
             0.0, 253.3727062852535, 422.3413346440912], [0.0, 0.0, 1.0]])
D = np.array([[0.1151627542735223], [-0.06162285822482732],
             [0.0210637688141392], [-0.005514290367529182]])


def undistort(img_path):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    cv2.imshow("normal", img)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def balanced_undistort(img_path, balance=0.0, dim2=None, dim3=None):
    img = cv2.imread(img_path)
    # dim1 is the dimension of input image to un-distort
    dim1 = img.shape[:2][::-1]

    assert dim1[0]/dim1[1] == DIM[0] / \
        DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if not dim2:
        dim2 = dim1

    if not dim3:
        dim3 = dim1

    # The values of K is to scale with image dimension.
    scaled_K = K * dim1[0] / DIM[0]
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        scaled_K, D, dim2, np.eye(3), balance=balance)

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)

    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    cv2.imshow("normal", img)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    images = glob.glob('./fisheye_calibration/*.jpg')

    for fname in images:
        undistort(fname)
        # balanced_undistort(fname, balance=0)
        # break
