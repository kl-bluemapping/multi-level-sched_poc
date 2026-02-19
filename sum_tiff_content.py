''' sum_tiff_content.py
compute sum of all pixel values in geotiff
'''

import sys
import numpy as np

from geotiff_manipulation import (
        geotiff_to_array,
        get_geotiff_metadata,
        get_coordinates_2154,
        get_metadata_shape,
        )

def sum_all_pixels(geotiff):
    # 0. get geotiff data
    data = geotiff_to_array(geotiff)
    data = data.flatten()
    if __debug__:
        print(f"{data.shape = }")
    # 1. sum all array values
    summed_data = sum(data)

    return summed_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        #print('missing parameter: <geotiff_file>')
        print(0)
        sys.exit(1)

    (_, geotiff) = sys.argv

    if __debug__:
        print(f"{geotiff = }")

    summed_pixels = sum_all_pixels(geotiff)

    print(summed_pixels)
    sys.exit(summed_pixels)


