import numpy as np
import os
import glob
from datetime import datetime, timedelta

# differentiation needed to support execution of file directly and to allow function to be included by data_preparation_main.py
if __name__ == "__main__":
    from timestamp_evaluation import get_timestamp_from_timestamp_string
else:
    from data_preparation.timestamp_evaluation import get_timestamp_from_timestamp_string

class TimeseriesDownsamplingForWholeMeasurement():
    """
        Class for downsampling of all timeseries/ IMU data present in a measurement directory.

        Background:
            Downsampling of the timeseries/ IMU data is necessary, as the data is polled in parallel for all sensors with ~100 Hz from the Unitree Go1. 
            The IMU in the Unitree Go1 itself provides the data with 50 Hz. As the polling frequency is implemented by using time.sleep(1/100),
            the real polling frequency < 100 Hz as the data capturing itself also needs some time. In order prevent missing any value of the 50 Hz signal,
            it's polled with the double frequency. As a result roughly every 7th value is only captured once instead of two times.
            As a result, the captured data shall be downsampled to a 50 Hz signal by keeping single occurring values and reducing double occurring values to a single value.

        Usage:
            Provide the path to the measurement dir as a parameter when creating the object.
            Call the method TimeseriesDownsamplingForWholeMeasurement.start_downsampling() afterwards to start the downsampling process.
            As a result all timeseries/ IMU data in the measurement dir will be overwritten with the downsampled data.
    """
    def __init__(self, measurement_path):
        """
            Init method stores measurement_path in a member an creates member list of sensors usable for downsampling.

            Parameters:
                - measurement_path (str): Path to the measurement to which downsampling shall be applied
        """
        self.measurement_path = measurement_path

        # checking about how to downsample must only be done for one array with noisy measurement and can be applied to all others
        # list of sensors which are ok for this check (determined by checking max counter for a measurement)
        self.sensors_for_downsampling = ["accelerometer",
                                         "bodyHeight", "gyroscope", "velocity", "yawSpeed"]

    def start_downsampling(self):
        """
            Public method to start downsampling process for all timeseries data in self.measurement_path.
            Execution will be aborted by a Exception in case no timeseries data could be found in self.measurement_path.
        """
        self.timeseries_sensors = []
        # check for present timeseries measurement dirs in measurement directory
        for root, dirs, files in os.walk(self.measurement_path):
            for dir in dirs:
                if not "Cam" in dir:
                    self.timeseries_sensors.append(dir)

        if self.timeseries_sensors == []:
            raise Exception(
                f"No timeseries sensor found for measurement '{self.measurement_path}'")
        else:
            print(
                f"downsampling will be done for the following sensors: {self.timeseries_sensors}")

        # execute downsampling for all files
        for root, dirs, files in os.walk(os.path.join(self.measurement_path, self.timeseries_sensors[0])):
            for file in files:
                print(f"\nStart downsampling for file '{file}'")
                self.__start_downsampling_for_all_sensors_by_filename(file)

    def __start_downsampling_for_all_sensors_by_filename(self, filename):
        """
            Private method to start downsampling process for the file "filename" in all timeseries sensors dirs in self.measurement_path.

            NOTE: Filenames are identical for all timeseries sensors with identical sampling for all these files, thus only one filename must be provided!

            Parameters:
                - filename (str): Name of the file which the downsampling shall be applied to
        """
        # clear self.data_struct and self.downsampling_array for new downsampling
        self.data_struct = {}
        self.downsampling_array = None

        # create new empty list in downsampled_data_struct for each sensor for new downsampling
        self.downsampled_data_struct = {}
        for sensor in self.timeseries_sensors:
            self.downsampled_data_struct[sensor] = []

        self.__load_data_to_data_struct_and_downsampling_array(filename)

        self.__perform_downsampling_for_all_sensors()

        self.__overwriting_measurement_data_with_downsampled_data(filename)

    def __load_data_to_data_struct_and_downsampling_array(self, filename):
        """
            Private method to load the data of all sensors in self.timeseries_sensors present in in self.mesarument_path.
            Additionally loads data of one fitting sensor listed in self.sensors_for_downsampling to self.downsampling_array which is used as a basis for the downsampling process.
            If no measurement of a fitting sensor is fount, execution will be aborted with an Exception.

            Parameters:
                - filename (str): Name of the file which shall be loaded for all sensors
        """
        sensor_for_downsampling_found = False

        # load data to data_struct
        for sensor in self.timeseries_sensors:
            if sensor in self.sensors_for_downsampling and not sensor_for_downsampling_found:
                # load data for first sensor from sensors_for_downsampling list also in downsampling_array
                self.downsampling_array = np.genfromtxt(os.path.join(
                    self.measurement_path, sensor, filename), delimiter=';')
                self.data_struct[sensor] = self.downsampling_array
                sensor_for_downsampling_found = True
                print(
                    f"Using '{sensor}' for downsampling of file '{filename}'")
            else:
                self.data_struct[sensor] = np.genfromtxt(os.path.join(
                    self.measurement_path, sensor, filename), delimiter=';')

        # stop execution if no proper sensor for downsampling is present in measurement
        if not sensor_for_downsampling_found:
            raise Exception(
                f"No fitting sensor for proper downsampling found for measurement '{self.measurement_path}' with sensors '{self.timeseries_sensors}'")

    def __perform_downsampling_for_all_sensors(self):
        """
            Private method to perform the downsampling process for the data present in self.data_struct based on the data present in self.downsampling_array.
            Methods also prints some details about the downsampling process after it's finished.
        """
        # initialize local variables
        last_checked_value = None
        max_occurrences = 0
        self.even_counter = 0
        self.odd_counter = 0

        array_length = np.shape(self.downsampling_array)[0]

        for index in range(array_length):
            # store value to check next (try catch to support all kinds of arrays (1D, 2D, ...))
            try:
                # only one value needed for comparison for 2D or higher
                current_value = self.downsampling_array[index][0]
            except IndexError:
                current_value = self.downsampling_array[index]

            if last_checked_value == current_value:
                # if the last checked value is equal to the current value, the value was already counted and no further action for this iteration needed
                pass
            else:
                # else the value was no checked yet
                num_subsequent_occurrences = self.__count_subsequent_occurrences(
                    array_length, index, current_value)

                self.__perform_downsampling_step_for_all_sensors(
                    index, num_subsequent_occurrences)

                # store last checked value to prevent counting same value multiple times
                last_checked_value = current_value
                if num_subsequent_occurrences > max_occurrences:
                    max_occurrences = num_subsequent_occurrences

        # print info about max occurrences for plausibility check of downsampling
        print(f"Max occurrence of single value was '{max_occurrences}'")
        print(f"Amount of odd occurrences is {self.odd_counter} which corresponds to {(self.odd_counter*100)/(self.odd_counter+self.even_counter):.2f} %")

    def __count_subsequent_occurrences(self, array_length, current_index, value_to_check):
        """
            Private method to count the number of subsequent occurrences of value_to_check in self.downsampling_array starting at current_index.

            Parameters:
                - array_length (int): Info about length of self.downsampling_array to calculate maximum number of values to check
                - current_index (int): Index where counting shall start in self.downsampling_array
                - value_to_check (int): Value whose number of occurrence shall determined

            Returns:
                - occurrence_counter (int): Number of subsequent occurrences of value_to_check
        """
        occurrence_counter = 0
        # inner loop to count count how often value occurs
        for counting_index in range(array_length - current_index):
            # get next value for comparison (try catch to support all kinds of arrays (1D, 2D, ...))
            try:
                comparison_value = self.downsampling_array[current_index +
                                                           counting_index][0]  # only one value needed for comparison for 2D or higher
            except IndexError:
                comparison_value = self.downsampling_array[current_index +
                                                           counting_index]

            # count subsequent occurrences of value to check
            if value_to_check == comparison_value:
                occurrence_counter += 1
            else:
                # stop counting when if statement is not met for the first time
                break

        return occurrence_counter

    def __perform_downsampling_step_for_all_sensors(self, raw_data_index, num_subsequent_occurrences):
        """
            Private method to perform downsampling step for all sensors at raw_data_index based on value of num_subsequent_occurrences.

            Parameters:
                - raw_data_index (int): Index where downsampling shall be performed for all arrays in self.data_struct
                - num_subsequent_occurrences (int): Number of occurrences of the value at raw_data_index which determines number of occurrences for downsampled data
        """
        num_downsampled_occurrences = 0
        # calculate number of downsampled occurences
        if (num_subsequent_occurrences % 2) == 0:
            num_downsampled_occurrences = int(num_subsequent_occurrences / 2)
            self.even_counter += 1
        else:
            num_downsampled_occurrences = int(
                num_subsequent_occurrences / 2) + (num_subsequent_occurrences % 2)
            self.odd_counter += 1

        # append value for downsampled amount of times for each sensor
        for _ in range(num_downsampled_occurrences):
            for sensor in self.timeseries_sensors:
                self.downsampled_data_struct[sensor].append(
                    self.data_struct[sensor][raw_data_index])

    def __overwriting_measurement_data_with_downsampled_data(self, filename):
        """
            Private method to overwrite the files with filename for every sensor in self.timeseries_sensors with the downsampled data from self.downsampled_data_struct

            Parameters:
                - filename (str): Name of the file to overwrite with the downsampled data for every sensor
        """
        for sensor in self.timeseries_sensors:
            array_for_storing = np.asarray(
                self.downsampled_data_struct[sensor])
            np.savetxt(os.path.join(
                self.measurement_path, sensor, filename), array_for_storing, delimiter=";")

def remove_obsolete_values(measurement_path, sensor_name, reference_timestamp):
    """
        Function to remove data points in the first measurement of sensor_name in measurement_path which are before reference_timestamp.
        NOTE: Must be called after downsampling was performed!!!
        Execution will be aborted if reference_timestamp is before the earliest available data point or when reference_timestamp is not
        located in the first measurement file.

        Parameters:
            - measurement_path (str): Path to the measurement
            - sensor_name (str): Name of the sensor to perform the function for
            - reference_timestamp (datetime.datetime): Timestamp to use as reference for data removal
    """
    # extract measurement date from reference_timestamp for get_timestamp_from_timestamp_string()
    measurement_date = datetime(year=reference_timestamp.year,
                                month=reference_timestamp.month, day=reference_timestamp.day)
    
    # get filename of first file in the dir
    glob_pattern = os.path.join(measurement_path, sensor_name, "*.csv")
    files = glob.glob(glob_pattern)
    first_filename = files[0].split(os.sep)[-1]

    # extract timestamp string from filename and convert it to datetime object
    earliest_timestamp_string = first_filename[:-4]
    earliest_timestamp = get_timestamp_from_timestamp_string(earliest_timestamp_string, measurement_date)

    if earliest_timestamp > reference_timestamp:
        raise Exception(f"Reference timestamp is before earliest available timestamp. Thus execution will be aborted.")

    # load data from earliest measurement
    filename = os.path.join(measurement_path, sensor_name, first_filename)
    data = np.genfromtxt(filename, delimiter=';')

    # get time diff between timestamps
    time_diff = reference_timestamp - earliest_timestamp
    # calculate needed shift in file
    shift = int(time_diff.microseconds / 20000)

    if shift > np.shape(data)[0]:
        # shift is not within earliest measurement file, thus execution is aborted with an Exception
        raise Exception(f"The needed shift of {shift} is not within the earliest measurement. Thus execution will be aborted.")
    elif shift > 0:
        # drop obsolete data when mandatory 
        print(f"Obsolete data for sensor '{sensor_name}' will be removed (first {shift} data points will be removed).")
        data = data[shift:]

        # store data corrected timestamp as name
        np.savetxt(os.path.join(measurement_path, sensor_name, datetime.strftime(reference_timestamp, "%H_%M_%S_%f")[:-3] + ".csv"),
                    data, delimiter=";")
        
        # delete old file
        os.remove(os.path.join(measurement_path, sensor_name, first_filename))
    else:
        print(f"No update needed for sensor '{sensor_name}'")

if __name__ == "__main__":
    # create path to temp directory
    file_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(file_dir, os.pardir, "temp")

    timeseries_downsampler = TimeseriesDownsamplingForWholeMeasurement(
        temp_path)
    timeseries_downsampler.start_downsampling()

    testdate = datetime(year=2023, month=7, day=25, hour=15,
                        minute=3, second=16, microsecond=958000)
    remove_obsolete_values(temp_path, "bodyHeight", testdate)
