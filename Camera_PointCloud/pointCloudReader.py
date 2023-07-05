import numpy as np
import open3d as o3d

def convert_to_pcd(filename):
    y = np.genfromtxt(filename, delimiter=',', dtype=np.float32)
    # transform to xyz only (without rgb)
    #y = y[:, :3]
    np.savetxt("PointCloudTest.pcd", y, delimiter=" ", fmt="%1.5f", comments="", header="# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH 251\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS 251\nDATA ascii")
   
if __name__ == "__main__":
    # convert_to_pcd("PointCloud_14-40-52.txt")
    pcd = o3d.io.read_point_cloud("PointCloudTest.pcd")
    print(pcd)
    #o3d.io.write_point_cloud("copy_of_fragment.pcd", pcd)
    o3d.visualization.draw_geometries([pcd])
    #o3d.visualization.draw_geometries(pcd)
