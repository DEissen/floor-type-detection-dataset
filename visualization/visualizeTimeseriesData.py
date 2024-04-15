import numpy as np
from matplotlib import pyplot as plt


def plot_IMU_data_from_file(measurement_path, sensor_name, filename_without_extension, start_of_plot=None, end_of_plot=None):
    """
        Function to plot IMU data file at path measurement_path/sensor_name/filename_without_extension.csv.
        If start_of_plot and end_of_plot are given, only data points between these two values will be plotted.

        Parameters:
            - measurement_path (str): Path to the measurement
            - sensor_name (str): Name of the sensor dir in measurement_path
            - filename_without_extension (str): Filename to plot from sensor dir without file extension
            - start_of_plot (int): Optional starting position of plot.
            - end_of_plot (int): Optional end position of plot.
    """
    # load data
    y = np.genfromtxt(
        f'{measurement_path}/{sensor_name}/{filename_without_extension}.csv', delimiter=';')

    # select wanted part of the measurement
    if start_of_plot != None and end_of_plot != None:
        y = y[start_of_plot:end_of_plot]

    x = np.arange(0, np.shape(y)[0])
    plt.title("Matplotlib demo")
    plt.plot(x, y)
    plt.show()


def plot_IMU_data(data, sensor_name, labels=None, start_of_plot=None, end_of_plot=None):
    """
        Function to plot already loaded IMU data. sensor_name will be used as plot title and labels can be added to plot.
        If start_of_plot and end_of_plot are given, only data points between these two values will be plotted.

        Parameters:
            - data (np.array): Data to plot
            - sensor_name (str): Name of the sensor for plot title
            - labels (list): List with labels. Must fit to dimension of data, otherwise execution will fail.
            - start_of_plot (int): Optional starting position of plot.
            - end_of_plot (int): Optional end position of plot.
    """
    # select wanted part of the measurement
    if start_of_plot != None and end_of_plot != None:
        data = data[start_of_plot:end_of_plot]

    x = np.arange(0, np.shape(data)[0])
    plt.title(sensor_name)
    if labels != None:
        for i in range(np.shape(data)[1]):
            plt.plot(x, data[:, i], label=labels[i])
        plt.legend()
    else:
        plt.plot(x, data)
    plt.show()


if __name__ == "__main__":
    # measurement_path = r"update_with_path_to_measurement"
    # # different measurements names to copy: accelerometer, bodyHeight, footForce, footRaiseHeight, gyroscope, mode, rpy, temperature, velocity, yawSpeed
    # sensor = "accelerometer"
    # filename1 = "15_03_16_158"
    # filename2 = "15_03_25_914"

    # plot_IMU_data_from_file(measurement_path, sensor, filename1)
    # plot_IMU_data_from_file(measurement_path, sensor, filename2)

    pass
