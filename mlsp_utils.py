import sys
import torch
import rasterio
import numpy as np

def geotiff_to_tensor(geotiff):
    with rasterio.open(geotiff) as data:
        image_data = data.read()  # read all bands
    tensor = torch.tensor(image_data, dtype=torch.float32)
    return tensor

def get_geotiff_transform(geotiff):
    with rasterio.open(geotiff) as src:
        transform = src.transform
    return transform

def get_geotiff_metadata(geotiff):
    with rasterio.open(geotiff) as data:
        metadata = data.meta
    return metadata

def tensor_to_geotiff(tensor, filename, transform=None):
    np_arr = tensor.numpy()
    print(f"{np_arr.shape = }")
    print(f"{np_arr[0, 1001, 190] = }")
    with rasterio.open(filename, 'w', driver='GTiff',
                       height=np_arr.shape[1], width=np_arr.shape[2],
                       count=1, dtype=np_arr.dtype,
                       crs='EPSG:2154',
                       transform=transform) as geotiff:
        geotiff.write(np_arr, 1)


def tensor_to_geotiff(tensor, filename, transform=None):

    print(f"{torch.max(tensor) = }")

    np_arr = tensor.squeeze(0).cpu().numpy()
    height, width = np_arr.shape

    print(f"{np_arr.shape = }")
    print(f"{np_arr[1001, 190] = }")

    meta_data = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": np_arr.dtype,
        "crs": "EPSG:2154",
        "transform": transform
    }

    with rasterio.open(filename, 'w', **meta_data) as geotiff:
        geotiff.write(np_arr, 1)

def tensor_to_geotiff(tensor, meta_data, filename, transform=None):

    print(f"{torch.max(tensor) = }")

    np_arr = tensor.squeeze(0).cpu().numpy()
    height, width = np_arr.shape

    print(f"{np_arr.shape = }")
    #print(f"{np_arr[1001, 190] = }")

    with rasterio.open(filename, 'w', **meta_data) as geotiff:
        geotiff.write(np_arr, 1)

def print_tensor_info(tensor):
    print(f"{tensor.size() = }")
    print(f"{tensor.dim() = }")

#/!\ on qgis tensors dim(0) is 1 - why ? -> ask T. /!\
# fix: reshape the tensor to drop the dim(0) before splitting
def reshape_qgis_input(tensor):
    print(f"old shape: {tensor.size()}")
    if tensor.dim() == 3 and tensor.size(0) == 1:
        tensor = tensor.reshape(tensor.size(1), tensor.size(2))
    print(f"new shape: {tensor.size()}")
    return tensor

def extract_2154_coords(geotiff):
    with rasterio.open(geotiff) as src:
        # check for epsg:2154
        crs = src.crs
        if crs.to_epsg() != 2154:
            raise ValueError(f"{crs} is not EPSG:2154")

        # ignore dim[0] - because it at 1 -> ask T. ?
        band1 = src.read(1)
        height = band1.shape[0]
        width = band1.shape[1]

        transform = src.transform

        # create grid - directly to tensor ?
        rows = np.arange(height)
        cols = np.arange(width)

        mesh_cols, mesh_rows = np.meshgrid(cols, rows)

        # conv (row, col) to spatial coord (x, y)
        xs, ys = rasterio.transform.xy(transform, mesh_rows, mesh_cols)

        xs = np.array(xs)
        ys = np.array(ys)

        # must reshape to 2D matrix after call to xy()
        #   rasterio.transform.xy() takes 1D vectors as input
        #   if given 2D matrices, it will flatten them
        #   as such, they must be reshaped afterwards
        xs = xs.reshape(mesh_rows.shape)
        ys = ys.reshape(mesh_rows.shape)

        coords = np.stack((xs, ys), axis=-1)

        return coords

def check_spatial_coords_validity(spatial_coords_sys, x, y, tol=1e-6):
    diff_x = np.abs(spatial_coords_sys[:, :, 0] - x)
    diff_y = np.abs(spatial_coords_sys[:, :, 1] - y)
    correspondances = np.logical_and(diff_x < tol, diff_y < tol)
    return np.any(correspondances)

def index_to_spatial_coords(spatial_coords_sys, i, j):
    x, y = spatial_coords_sys[i, j]
    return x, y

def spatial_to_index_coords(spatial_coords_sys, x, y, tol=1e-6):
    diff_x = np.abs(spatial_coords_sys[:, :, 0] - x)
    diff_y = np.abs(spatial_coords_sys[:, :, 1] - y)
    correspondances = np.logical_and(diff_x < tol, diff_y < tol)
    return np.argwhere(correspondances)
