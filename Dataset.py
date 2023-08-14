import os
import numpy as np
import pandas as pd
import glob
import json
from PIL import Image
from torch.utils.data import Dataset

# for testing
import matplotlib.pyplot as plt

class FloorTypeDetectionDataset(Dataset):
    """
        Dataset class for FTDD (Floor Type Detection Dataset).
    """
    def __init__(self, root_dir, sensors, mapping_filename):
        self.root_dir = root_dir
        self.sensors = sensors

        # get label mapping from configs/ dir
        self.label_mapping_struct = load_label_mapping(mapping_filename)

        # get list of all files from labels
        self.filenames_labels_array = pd.read_csv(os.path.join(root_dir, "labels.csv"), sep=";", header=0).to_numpy()

    def __getitem__(self, index):
        # get data for all sensors in self.sensors for the index
        data = []
        for sensor in self.sensors:
            if "Cam" in sensor:
                # data is stored as .jpg file for all cameras
                file_path = os.path.join(self.root_dir, sensor, self.filenames_labels_array[index, 0]+".jpg")
                data.append(Image.open(file_path))
            else:
                # data is stored as .csv file for all other sensors
                file_path = os.path.join(self.root_dir, sensor, self.filenames_labels_array[index, 0]+".csv")
                data.append(np.loadtxt(file_path, delimiter=";"))

        # get the label for the index
        label = self.filenames_labels_array[index, 1]
        return (data, self.label_mapping_struct[label])
    
def load_label_mapping(mapping_filename):
    """
        Helper function to load the label mapping from the mapping_filename file in the configs/ dir of the repo.

        Parameters:
            - mapping_filename (str): Name of the JSON file in the configs/ dir

        Returns:
            - label_mapping_struct (struct): Struct containing the label name as key and the label number as value.
    """
    file_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(file_dir, "configs", mapping_filename)

    with open(json_path, "r") as f:
        label_mapping_struct = json.load(f)

    return label_mapping_struct

if __name__ == "__main__":
    mapping_filename = "label_mapping_binary.json"
    test = FloorTypeDetectionDataset(r"C:\Users\Dominik\Downloads\FTDD_0.1", ["accelerometer", "BellyCamRight"], mapping_filename)
    
    for index, (sample, label) in enumerate(test):
        if index == 100: # should be 12_50_16_797
            print(sample[0], sample[1], label)
            sample[1].show()
