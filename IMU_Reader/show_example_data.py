import numpy as np
from matplotlib import pyplot as plt


def plot_IMU_data(measurement_name, sensor_name, start_of_plot=None, end_of_plot=None):
    # load data
    y = np.genfromtxt(f'{measurement_name}/{sensor_name}.csv', delimiter=';')

    # select wanted part of the measurement
    if start_of_plot != None and end_of_plot != None:
        y = y[start_of_plot:end_of_plot]

    x = np.arange(0, np.shape(y)[0])
    plt.title("Matplotlib demo")
    plt.plot(x, y)
    plt.show()


if __name__ == "__main__":
    measurement_name = "first_dance"
    # different measurements names to copy: accelerometer, bodyHeight, footForce, footRaiseHeight, gyroscope, mode, rpy, temperature, velocity, yawSpeed
    sensor = "footForce"

    plot_IMU_data(measurement_name, sensor)
