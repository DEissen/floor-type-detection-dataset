import os
import numpy as np
import glob
from PIL import Image
from torch.utils.data import Dataset

class FloorTypeDetectionDataset(Dataset):
    """
        Dataset class for FTDD (Floor Type Detection Dataset).
    """
    def __init__(self, root_dir, sensors):
        self.root_dir = root_dir
        self.sensors = sensors

        # get list of all files from labels
        self.filenames = []

    def __getitem__(self, index):
        data = None
        return data