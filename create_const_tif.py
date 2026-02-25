''' create_const_tif.py
create geotiff initialized to 'x' from reference coordinates
'''

import sys
import numpy as np

from geotiff_manipulation import (
        array_to_geotiff,
        get_geotiff_metadata,
        get_coordinates_2154,
        get_metadata_shape,
        )

def create_const_geotiff(geotiff, constant_value):
    """
    create a new geotiff of the same shape & extent as the input geotiff
    new geotiff data is set to constant_value for the whole raster
    """
    # 0. read geotiff extent
    extent = get_coordinates_2154(geotiff)
    metadata = get_geotiff_metadata(geotiff)
    shape = get_metadata_shape(metadata)
    # 1. create empty array/tensor of geotiff size
    # TODO: use np fill func.
    constant_value_array = np.zeros(shape)
    # 2. write empty arr/tensor to new file
    geotiff_name = "const_" + str(constant_value) + ".tif"
    array_to_geotiff(constant_value_array, metadata, geotiff_name)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('missing parameter: <geotiff_file> <constant value>')
        sys.exit(1)

    (_, geotiff, constant_value) = sys.argv

    if __debug__:
        print(f"{geotiff = }")
        print(f"{constant_value = }")

    create_const_geotiff(geotiff, constant_value)

    sys.exit(0)
