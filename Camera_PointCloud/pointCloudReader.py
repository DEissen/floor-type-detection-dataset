import numpy as np
import open3d as o3d


def convert_to_pcd(filename_without_type, xyz_only=False):
    y = np.genfromtxt(f"kurz_vor_Heizung/{filename_without_type}.txt",
                      delimiter=',', dtype=np.float32)

    # optionally transform to xyz only (without rgb)
    if xyz_only:
        y = y[:, :3]

    # remove nan
    y = y[~np.isnan(y).any(axis=1)]

    # prepare pcd header with content type (with or without rgb) and length
    length = np.shape(y)[0]
    # rgb = " rgb" # with rgb is not working yet
    # if xyz_only:
    #     rgb = ""
    pcd_file_header = f"# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH {length}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {length}\nDATA ascii"

    np.savetxt(f"data/{filename_without_type}.pcd", y, delimiter=" ",
               fmt=["%1.7f", "%1.7f", "%1.7f", "%d"], comments="", header=pcd_file_header)


def open_point_cloud(filename_without_type, print_details=False):
    # load point cloud
    pcd = o3d.io.read_point_cloud(f"data/{filename_without_type}.pcd")

    # optionally print details about the loaded point cloud
    if print_details:
        print(pcd)

    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    filename_without_type = "PointCloud_16-36-58"

    convert_to_pcd(filename_without_type)

    open_point_cloud(filename_without_type, True)
