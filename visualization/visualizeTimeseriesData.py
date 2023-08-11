import numpy as np
from matplotlib import pyplot as plt


def plot_IMU_data_from_file(measurement_path, sensor_name, filename, start_of_plot=None, end_of_plot=None):
    # load data
    y = np.genfromtxt(f'{measurement_path}/{sensor_name}/{filename}.csv', delimiter=';')

    # select wanted part of the measurement
    if start_of_plot != None and end_of_plot != None:
        y = y[start_of_plot:end_of_plot]

    x = np.arange(0, np.shape(y)[0])
    plt.title("Matplotlib demo")
    plt.plot(x, y)
    plt.show()

def plot_IMU_data(data, sensor_name, labels=None, start_of_plot=None, end_of_plot=None):

    # select wanted part of the measurement
    if start_of_plot != None and end_of_plot != None:
        data = data[start_of_plot:end_of_plot]

    x = np.arange(0, np.shape(data)[0])
    plt.title(sensor_name)
    if labels != None:
        for i in range(np.shape(data)[1]):
            plt.plot(x, data[:,i], label=labels[i])
        plt.legend()
    else:
        plt.plot(x, data)
    plt.show()

if __name__ == "__main__":
    measurement_path = r"D:\git_repos\FA_Dataset\temp"
    # different measurements names to copy: accelerometer, bodyHeight, footForce, footRaiseHeight, gyroscope, mode, rpy, temperature, velocity, yawSpeed
    sensor = "accelerometer"
    filename1 = "15_03_16_158"
    filename2 = "15_03_25_914"

    plot_IMU_data_from_file(measurement_path, sensor, filename1)
    plot_IMU_data_from_file(measurement_path, sensor, filename2)
