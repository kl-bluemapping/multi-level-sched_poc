import sys
import os
from osgeo import gdal

from geotiff_manipulation import (
    get_geotiff_metadata,
    get_metadata_transform,
    )

# TODO: move to dedicaced package
def gen_part_path(prefix, geotiff):
    prefix_path = os.path.join(
            prefix,
            os.path.basename(os.path.dirname(geotiff)))

    if not os.path.exists(prefix_path):
        os.makedirs(prefix_path)
    path = os.path.join(prefix_path, os.path.basename(geotiff))

    return path

def gdal_warp_geotiff(metadata, warp_ratio, geotiff, dest_path):

    # TODO: parse metadata

    warp_options = gdal.WarpOptions(
        srcSRS=s_srs,
        dstSRS=t_srs,
        dstNodata=dstnodata,
        xRes=tr[0],
        yRes=tr[1],
        resampleAlg=resampling,
        outputBounds=te,
        outputBoundsSRS=te_srs,
        outputType=output_type
    )
    gdal.Warp(dest_path, geotiff, options=warp_options)

    return

def scale_geotiff(ratio, geotiff):
    # get geotiff metadata
    metadata = get_geotiff_metadata(geotiff)
    dest_path = gen_part_path("scaled_", geotiff)

    gdal_warp_geotiff(metadata, ratio, geotiff, dest_path)

    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('missing parameter: <ratio> <geotiff_file>')
        sys.exit(1)

    (_, ratio, geotiff) = sys.argv

    if __debug__:
        print(f"{ratio = }")
        print(f"{geotiff = }")

    scale_geotiff(ratio, geotiff)

    sys.exit(0)



