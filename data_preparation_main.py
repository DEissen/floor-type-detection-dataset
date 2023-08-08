import os

# custom imports
from custom_utils.utils import copy_measurement_to_temp, clean_temp_dir, load_complete_IMU_measurement
from data_preparation.timestamp_evaluation import get_synchronized_timestamps
from data_preparation.timeseries_preparation import TimeseriesDownsamplingForWholeMeasurement, remove_obsolete_values
from data_preparation.image_preparation import remove_obsolete_images
from visualization.visualizeTimeseriesData import plot_IMU_data
from visualization.visualizeImages import show_all_images_afterwards, show_all_images_afterwards_including_imu_data


def main(measurement_path):
    # # clear the temp dir and copy the desired measurement to it afterwards
    clean_temp_dir()
    copy_measurement_to_temp(measurement_path)

    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, "temp")

    timeseries_downsampler = TimeseriesDownsamplingForWholeMeasurement(
        temp_path)
    timeseries_downsampler.start_downsampling()

    timestamps = get_synchronized_timestamps(temp_path)

    for key, timestamp in timestamps.items():
        print(f"Starting timestamp for {key} is {timestamp}")
        if "IMU" in key:
            for sensor in timeseries_downsampler.timeseries_sensors:
                remove_obsolete_values(temp_path, sensor, timestamp)
        elif "Cam" in key:
            remove_obsolete_images(temp_path, key, timestamp)

def visualize_intermediate_result():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, "temp")

    data = load_complete_IMU_measurement(temp_path, "accelerometer") # determines which sensor is used for visualization
    show_all_images_afterwards_including_imu_data(temp_path, data)
    plot_IMU_data(data)


if __name__ == "__main__":
    measurement_path = "./testdata/measurement_25_07__15_03"

    main(measurement_path)

    visualize_intermediate_result()