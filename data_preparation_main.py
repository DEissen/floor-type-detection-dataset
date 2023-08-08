import os

# custom imports
from custom_utils.utils import copy_measurement_to_temp, clean_temp_dir
from data_preparation.timestamp_evaluation import get_synchronized_timestamps
from data_preparation.timeseries_preparation import TimeseriesDownsamplingForWholeMeasurement


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

    for key, value in timestamps.items():
        print(key, value)


if __name__ == "__main__":
    measurement_path = "./testdata/measurement_25_07__15_03"

    main(measurement_path)
