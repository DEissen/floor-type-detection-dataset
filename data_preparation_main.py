from custom_utils.utils import copy_measurement_to_temp, clean_temp_dir
from data_preparation.timestamp_evaluation import get_synchronized_timestamps


def main(measurement_path):
    # # clear the temp dir and copy the desired measurement to it afterwards
    # clean_temp_dir()
    # copy_measurement_to_temp(measurement_path)

    get_synchronized_timestamps()

if __name__ == "__main__":
    measurement_path = "./testdata/measurement_25_07__15_03"

    main(measurement_path)