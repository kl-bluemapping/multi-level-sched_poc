''' geotiff_manipulation.py
functions to extract and format data from a poi geojson
'''

import numpy as np
from osgeo import gdal, osr

def get_geotiff_metadata(geotiff):
    geotiff_metadata = {}
    gdal.UseExceptions()
    with gdal.Open(geotiff, gdal.GA_ReadOnly) as data:
        geotiff_metadata["projection"] = data.GetProjection()
        geotiff_metadata["geotransform"] = data.GetGeoTransform()
        geotiff_metadata["height"] = data.RasterYSize
        geotiff_metadata["width"] = data.RasterXSize
        geotiff_metadata["nb_bands"] = data.RasterCount
        geotiff_metadata["metadata"] = data.GetMetadata()
    return geotiff_metadata

def get_metadata_projection(metadata):
    projection = metadata.get("projection")
    return projection

def get_metadata_transform(metadata):
    transform = metadata.get("geotransform")
    return transform

def get_metadata_shape(metadata):
    height = metadata.get("height")
    width = metadata.get("width")
    return height, width

def get_metadata_metadata(metadata):
    metadata = metadata.get("metadata")
    return metadata

def geotiff_to_array(geotiff):
    gdal.UseExceptions()
    with gdal.Open(geotiff, gdal.GA_ReadOnly) as data:
        height = data.RasterYSize
        width = data.RasterXSize
        nb_bands = data.RasterCount
        if __debug__:
            print(f"{height = }")
            print(f"{width = }")
            print(f"{nb_bands = }")
        image_data = np.zeros((nb_bands, height, width), dtype=np.float32)
        if __debug__:
            print(f"{image_data.shape = }")
        for i in range(nb_bands):
            band = data.GetRasterBand(i+1)
            image_data[i,:,:] = band.ReadAsArray()
        return image_data

def array_to_geotiff(array, geotiff_metadata, filename):
    try:
        nb_bands, height, width = array.shape
    except Exception as e:
        raise ValueError(f"array shape {array.shape} is not 3D")

    driver = gdal.GetDriverByName('GTiff')
    datatype=gdal.GDT_Float32
    with driver.Create(filename, width, height, nb_bands, datatype) as data:
        projection = get_metadata_projection(geotiff_metadata)
        transform = get_metadata_transform(geotiff_metadata)
        metadata = get_metadata_metadata(geotiff_metadata)

        if __debug__:
            print(f"{projection = }")
            print(f"{transform = }")
            print(f"{metadata = }")

        data.SetProjection(projection)
        data.SetGeoTransform(transform)
        data.SetMetadata(metadata)

        for i in range(nb_bands):
            band = data.GetRasterBand(i+1)
            band.WriteArray(array[i,:,:])
            band.FlushCache()
    return

def transform_point(transform, x, y):
    origin_x = transform[0]
    pixel_width = transform[1]
    rotation_x = transform[2]
    origin_y = transform[3]
    rotation_y = transform[4]
    pixel_height = transform[5]

    X = origin_x + y * pixel_width + x * rotation_x + (pixel_width / 2)
    Y = origin_y + y * rotation_y + x * pixel_height + (pixel_height / 2)

    return X, Y

def transform_mesh(transform, rows, cols):
    nb_elems = rows * cols

    arr_x = np.zeros(nb_elems)
    arr_y = np.zeros(nb_elems)

    i = 0
    for row in range(rows):
        for col in range(cols):
            x, y = transform_point(transform, row, col)
            arr_x[i] = x
            arr_y[i] = y
            i += 1
    return arr_x, arr_y

def get_coordinates_2154(geotiff):
    gdal.UseExceptions()
    with gdal.Open(geotiff, gdal.GA_ReadOnly) as data:
        projection = data.GetProjection()

        srs = osr.SpatialReference()
        srs.ImportFromWkt(projection)
        epsg = srs.GetAttrValue('AUTHORITY', 1)

        if epsg != '2154':
            raise ValueError(f"{epsg} is not EPSG:2154")

        metadata = get_geotiff_metadata(geotiff)

        height, width = get_metadata_shape(metadata)
        transform = get_metadata_transform(metadata)

        # conv (row, col) to spatial coord (x, y)
        xs, ys = transform_mesh(transform, height, width)

        # reshape to 2D matrix after call to
        xs = xs.reshape((height, width))
        ys = ys.reshape((height, width))

        if __debug__:
            print(f"{xs.shape = }")
            print(f"{xs.ndim = }")

        # TOFIX: do stack properly
        coords = np.stack((xs, ys), axis=-1)

        return coords

# WARNING: transform encoding depends of the used lib.
#   rasterio: (x-width, x-height, x-base, y-width, y-height, y-base)
#   gdal: (x-base, x-width, x-height, y-base, y-width, y-height)
# gdal configuration
def format_transform(transform, lib='gdal'):
    res = []
    if lib == 'rasterio':
        res.append(transform[2])
        res.append(transform[0])
        res.append(transform[1])
        res.append(transform[5])
        res.append(transform[3])
        res.append(transform[4])
    elif lib == 'gdal':
        res = transform
    else:
        print(f"ERROR: unsupported geotiff manipulation library")
        sys.exit(1)
    return res

