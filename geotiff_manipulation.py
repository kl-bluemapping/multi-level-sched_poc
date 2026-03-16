''' geotiff_manipulation.py
functions to extract and format data from a poi geojson
'''

import rasterio
import numpy as np

def geotiff_to_array(geotiff):
    with rasterio.open(geotiff) as data:
        image_data = data.read()  # read all bands
    return image_data

def array_to_geotiff(array, geotiff_metadata, filename):
    with rasterio.open(filename, 'w', **geotiff_metadata) as geotiff:
        geotiff.write(array, 1)

def get_geotiff_metadata(geotiff):
    with rasterio.open(geotiff) as data:
        metadata = data.meta
    return metadata

def get_metadata_transform(metadata):
    transform = metadata.get("transform")
    return transform

def get_metadata_shape(metadata):
    height = metadata.get("height")
    width = metadata.get("width")
    return height ,width

def get_coordinates_2154(geotiff):
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


''' gdal equivalent:
from osgeo import gdal

data = gdal.Open(orig_topo_geotiff, gdal.GA_ReadOnly)
geoTransform = data.GetGeoTransform()
'''
