import os
import json


def load_json_from_configs(run_path, json_filename):
    """
        Helper function to load any JSON file from the configs/ dir of the repo.

        Parameters:
            - run_path (str): Run path to previous run from where config can be loaded. If run_path == "" the default config from the repo will be used.
            - json_filename (str): Name of the JSON file in the configs/ dir

        Returns:
            - json_as_dict (dict): Dict containing the data from the file json_filename
    """
    if run_path == "":
        file_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(file_dir, os.pardir, "configs", json_filename)
    else:
        json_path = os.path.join(run_path, "config", json_filename)

    with open(json_path, "r") as f:
        json_as_dict = json.load(f)

    return json_as_dict
