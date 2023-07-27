from custom_utils.utils import copy_measurement_to_temp


def main(measurement_path):
    copy_measurement_to_temp(measurement_path)

if __name__ == "__main__":
    measurement_path = "./testdata/measurement_25_07__15_03"

    main(measurement_path)