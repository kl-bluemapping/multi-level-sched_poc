import sys
import os
from osgeo import gdal
from geotiff_manipulation import (
    get_geotiff_metadata,
    get_metadata_shape,
    get_metadata_transform,
    )

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('missing parameter: <horiz|vert> <ratio> <geotiff_file>')
        sys.exit(1)

    (_, orientation, ratio, geotiff) = sys.argv

    if __debug__:
        print(f"{orientation = }")
        print(f"{ratio = }")
        print(f"{geotiff = }")

    # get geotiff metadata
    metadata = get_geotiff_metadata(geotiff)
    # get geotiff shape
    height, width = get_metadata_shape(metadata)
    # get geotiff transform
    transform = get_metadata_transform(metadata)

    scale_X = transform[0]
    extent_X_min = transform[2]
    extent_X_max = extent_X_min + (scale_X * width)

    scale_Y = transform[4]
    extent_Y_min = transform[5]
    extent_Y_max = extent_Y_min + (scale_Y * height)

    if __debug__:
        print(f"(height,width) = ({height},{width})")
        print(f"{transform = }")
        print(f"{extent_X_min = }")
        print(f"{extent_X_max = }")
        print(f"{extent_Y_min = }")
        print(f"{extent_Y_max = }")

    # compute split geotif new extents
    if orientation == "vert": # split over X
        split =  extent_X_min + round((extent_X_max - extent_X_min) * float(ratio))

        part_A_min_X = extent_X_min
        part_A_max_X = split
        part_A_min_Y = extent_Y_min
        part_A_max_Y = extent_Y_max

        part_B_max_X = split
        part_B_min_X = extent_X_max
        part_B_min_Y = extent_Y_min
        part_B_max_Y = extent_Y_max
    elif orientation == "horiz": # split over Y
        split =  extent_Y_min + round((extent_Y_max - extent_Y_min) * float(ratio))

        part_A_min_X = extent_X_min
        part_A_max_X = extent_X_max
        part_A_min_Y = extent_Y_min
        part_A_max_Y = split

        part_B_min_X = extent_X_min
        part_B_max_X = extent_X_max
        part_B_min_Y = split
        part_B_max_Y = extent_Y_max
    else:
        print(f"ERROR: unsupported split orientation {orientation}")
        sys.exit(-1)

    if __debug__:
        print(f"{split = }")

        print(f"{part_A_min_X = }")
        print(f"{part_A_max_X = }")
        print(f"{part_A_min_Y = }")
        print(f"{part_A_max_Y = }")

        print(f"{part_B_min_X = }")
        print(f"{part_B_max_X = }")
        print(f"{part_B_min_Y = }")
        print(f"{part_B_max_Y = }")

    # dest dirs
    part_A_dir = "part_A"
    part_A_path = os.path.join(
            part_A_dir,
            os.path.basename(os.path.dirname(geotiff)))

    if not os.path.exists(part_A_path):
        os.makedirs(part_A_path)
    part_A = os.path.join(part_A_path, os.path.basename(geotiff))

    if __debug__:
        print(f"{part_A =}")

    part_B_dir = "part_B"
    part_B_path = os.path.join(
            part_B_dir,
            os.path.basename(os.path.dirname(geotiff)))

    if not os.path.exists(part_B_path):
        os.makedirs(part_B_path)
    part_B = os.path.join(part_B_path,os.path.basename(geotiff))

    if __debug__:
        print(f"{part_B =}")

    #gdal transform
    gdal.UseExceptions() # cf. doc gdal
    # part_A
    gdal.Translate(
            part_A,
            geotiff,
            projWin=(part_A_min_X,
                     part_A_min_Y,
                     part_A_max_X,
                     part_A_max_Y),
            format='GTiff'
            )
    # part_B
    gdal.Translate(
            part_B,
            geotiff,
            projWin=(part_B_min_X,
                     part_B_min_Y,
                     part_B_max_X,
                     part_B_max_Y),
            format='GTiff'
            )

    sys.exit(0)



