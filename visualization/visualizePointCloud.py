import numpy as np
import open3d as o3d

# not needed for new measurement anymore, as data is stored directly in correct format in the meantime


def convert_txt_to_pcd(measurement_path, filename_without_type, xyz_only=False, add_direction_points=False):
    y = np.genfromtxt(f"{measurement_path}/{filename_without_type}.txt",
                      delimiter=',', dtype=np.float32)

    # optionally transform to xyz only (without rgb)
    if xyz_only:
        y = y[:, :3]

    # remove nan values if some are present
    y = y[~np.isnan(y).any(axis=1)]

    # add points to indicate directions by adding the following four points to the point cloud:
    # 0 0 0 4.2108e+01      => reference point in origin in darkblue
    # 0.1 0 0 4.2108e+01    => reference point at x = 0.1 in darkblue
    # 0 0.1 0 4.2108e+024   => reference point at y = 0.1 in lightblue
    # 0 0 0.1 0             => reference point at z = 0.1 in black
    if add_direction_points:
        darkblue = 4.2108e+01
        lightblue = 4.2108e+024
        black = 0
        y = np.append(y, [[0, 0, 0, darkblue], [0.1, 0, 0, darkblue], [
                      0, 0.1, 0, lightblue], [0, 0, 0.1, black]], axis=0)

    # prepare pcd header with content type (with or without rgb) and length
    length = np.shape(y)[0]
    rgb = " rgb"  # with rgb is not working yet
    rgb_size = " 4"
    rgb_type = " F"
    rgb_count = " 1"
    if xyz_only:
        rgb = "" 
        rgb_size = ""
        rgb_type = ""
        rgb_count = ""

    pcd_file_header = f"# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z{rgb}\nSIZE 4 4 4{rgb_size}\nTYPE F F F{rgb_type}\nCOUNT 1 1 1{rgb_count}\nWIDTH {length}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {length}\nDATA ascii"

    np.savetxt(f"{measurement_path}/{filename_without_type}.pcd", y, delimiter=" ",
               fmt=["%.10f", "%.10f", "%.10f", "%.10e"], comments="", header=pcd_file_header)


def open_point_cloud(measurement_path, filename_without_type, print_details=False):
    # load point cloud
    pcd = o3d.io.read_point_cloud(
        f"{measurement_path}/{filename_without_type}.pcd")

    # optionally print details about the loaded point cloud
    if print_details:
        print(pcd)

    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    # measurement_path = r"C:\Users\Dominik\Documents\Dokumente\Studium\Masterstudium\Semester_4\Forschungsarbeit\Messungen\Point_Clouds\kurz_vor_Heizung"
    # filename_without_type = "PointCloud_16-36-55"

    # convert_txt_to_pcd(measurement_path, filename_without_type,
    #                add_direction_points=True)

    # open_point_cloud(measurement_path, filename_without_type, True)
    pass
