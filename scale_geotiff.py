import sys
import os
from osgeo import gdal

from geotiff_manipulation import (
    get_geotiff_metadata,
    get_metadata_transform,
    )

# TODO: move to dedicaced package
def gen_part_path(prefix, geotiff, dest):
    prefix_path = os.path.join(
            dest,
            prefix,
            os.path.basename(os.path.dirname(geotiff)),
            )

    if not os.path.exists(prefix_path):
        os.makedirs(prefix_path)
    path = os.path.join(prefix_path, os.path.basename(geotiff))

    return path

def gdal_warp_geotiff(warp_ratio, geotiff, dest_path):
    warp_options = gdal.WarpOptions(
            xRes= warp_ratio,
            yRes = warp_ratio,
            resampleAlg = 'near'
            )
    gdal.Warp(dest_path, geotiff, options=warp_options)
    return

def scale_geotiff(ratio, geotiff, dest):

    dest_path = gen_part_path("input", geotiff, dest)
    if __debug__:
        print(f"{dest_path =}")

    gdal_warp_geotiff(ratio, geotiff, dest_path)

    return

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('missing parameter: <ratio> <geotiff_file> <destdir>')
        sys.exit(1)

    (_, ratio, geotiff) = sys.argv

    if __debug__:
        print(f"{ratio = }")
        print(f"{geotiff = }")
        print(f"{destdir = }")

    scale_geotiff(ratio, geotiff, destdir)

    sys.exit(0)



