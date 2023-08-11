import os

# custom imports
from custom_utils.utils import copy_measurement_to_temp, clean_temp_dir, copy_prepared_dataset
from data_preparation.timestamp_evaluation import get_synchronized_timestamps, remove_obsolete_data_at_end, create_label_csv
from data_preparation.timeseries_preparation import TimeseriesDownsamplingForWholeMeasurement, remove_obsolete_values, load_complete_IMU_measurement, create_sliding_windows_and_save_them
from data_preparation.image_preparation import remove_obsolete_images_at_beginning, unify_image_timestamps
from visualization.visualizeTimeseriesData import plot_IMU_data
from visualization.visualizeImages import show_all_images_afterwards, show_all_images_afterwards_including_imu_data


def data_preparation_main(measurement_path, dataset_path=None):
    """
        Function to start the complete data preparation process for a new measurement.

        Parameters:
            - measurement_path (str): Path to dir where the measurement is stored (can also be a .zip file)
            - dataset_path (str): Path to dir where the prepared data shall be copied to.
                                  Default = None -> the dataset will be copied to results/ dir in the repository.
    """
    print("### Step 1: Copy measurements ###")
    # # clear the temp dir and copy the desired measurement to it afterwards
    clean_temp_dir()
    copy_measurement_to_temp(measurement_path)

    # uncomment to check how data looks before preparation step
    # visualize_result()

    print("\n\n### Step 2: Downsampling of IMU data ###")
    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, "temp")

    timeseries_downsampler = TimeseriesDownsamplingForWholeMeasurement(
        temp_path)
    timeseries_downsampler.start_downsampling()

    print("\n\n### Step 3: Get synchronized timestamps, create windows for IMU data and delete data previous to synchronized timestamp ###")
    timestamps = get_synchronized_timestamps(temp_path)

    for key, timestamp in timestamps.items():
        # print(f"Starting timestamp for {key} is {timestamp}")
        if "IMU" in key:
            for sensor in timeseries_downsampler.timeseries_sensors:
                remove_obsolete_values(temp_path, sensor, timestamp)

                # configuration values for sliding window TODO: better solution to configure it!
                window_size = 50
                stride = 10
                normalization = True 
                create_sliding_windows_and_save_them(temp_path, sensor, window_size, stride, normalization)
        elif "Cam" in key:
            remove_obsolete_images_at_beginning(temp_path, key, timestamp)

    print("\n\n### Step 4: Unify image timestamps ###")
    earliest_last_image_timestamp = unify_image_timestamps(temp_path, timestamps["IMU"])

    print("\n\n### Step 5: Deletion of data for timestamps that are not available for all sensors ###")
    remove_obsolete_data_at_end(temp_path, earliest_last_image_timestamp)
    
    print("\n\n### Step 6: Create labels csv file ###")
    create_label_csv(temp_path)

    print("\n\n### Step 7: Copy prepared dataset ###")
    copy_prepared_dataset(dataset_path)

    # uncomment to check how data looks after preparation step
    # visualize_result()


def visualize_result():
    """
        Helper function to load and visualize data from one IMU sensor and one picture of each stereo camera present in temp/ dir.
        Can be used the show e.g. intermediate results.
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, "temp")

    # determines which sensor is used for visualization
    data = load_complete_IMU_measurement(temp_path, "accelerometer")
    show_all_images_afterwards_including_imu_data(temp_path, data)

if __name__ == "__main__":
    measurement_path = "./testdata/measurement_25_07__15_03"
    # measurement_path = r"C:\Users\Dominik\Documents\Dokumente\Studium\Masterstudium\Semester_4\Forschungsarbeit\Messungen\dataset\measurement_25_07__12_58.zip"
    # measurement_path = r"C:\Users\Dominik\Downloads\updated_measurement_25_07__12_58.zip"

    data_preparation_main(measurement_path)
