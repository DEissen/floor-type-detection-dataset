import gin

# custom modules
from visualization.visualizePointCloud import convert_txt_to_pcd, open_point_cloud


if __name__ == "__main__":
    # get and use gin config
    gin_config_path = "./configs/config.gin"
    variant_specific_bindings = []
    gin.parse_config_files_and_bindings(
        [gin_config_path], variant_specific_bindings)
