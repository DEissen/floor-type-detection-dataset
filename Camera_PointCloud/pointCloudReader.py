import numpy as np
import open3d as o3d


def convert_to_pcd(filename_without_type, xyz_only=False):
    pcd_file_header = "# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH 251\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS 251\nDATA ascii"

    y = np.genfromtxt(f"data/{filename_without_type}.txt", delimiter=',', dtype=np.float32)

    # optionally transform to xyz only (without rgb)
    if xyz_only:
        y = y[:, :3]

    np.savetxt(f"data/{filename_without_type}.pcd", y, delimiter=" ",
               fmt="%1.5f", comments="", header=pcd_file_header)


if __name__ == "__main__":
    filename_without_type = "PointCloud_14-40-51"
    convert_to_pcd(filename_without_type)

    pcd = o3d.io.read_point_cloud(f"data/{filename_without_type}.pcd")

    print(pcd)

    o3d.visualization.draw_geometries([pcd])
