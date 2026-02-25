import sys
import os
from osgeo import gdal

from geotiff_manipulation import (
    get_geotiff_metadata,
    get_metadata_shape,
    get_metadata_transform,
    )

def compute_part_corners(min_A, min_B, max_A, max_B):
    results = []

    split =  min_A + round((max_A - min_A) * float(ratio))

    part_A_min_A = min_A
    part_A_max_A = split
    part_A_min_B = min_B
    part_A_max_B = max_B

    part_B_min_A = split
    part_B_max_A = max_A
    part_B_min_B = min_B
    part_B_max_B = max_B

    results.append(part_A_min_A)
    results.append(part_A_max_A)
    results.append(part_A_min_B)
    results.append(part_A_max_B)
    results.append(part_B_min_A)
    results.append(part_B_max_A)
    results.append(part_B_min_B)
    results.append(part_B_max_B)

    return results

def compute_orientation_part_corners(orientation, min_A, min_B, max_A, max_B):
    results = []

    if orientation == "vert": # split over X
        results = compute_part_corners(min_A, min_B, max_A, max_Y)
    elif orientation == "horiz": # split over Y
        results = compute_part_corners(min_B, min_A, max_B, max_A)
    else:
        print(f"ERROR: unsupported split orientation {orientation}")

    return results

def gen_part_path(prefix, geotiff):
    prefix_path = os.path.join(
            prefix,
            os.path.basename(os.path.dirname(geotiff)))

    if not os.path.exists(prefix_path):
        os.makedirs(prefix_path)
    path = os.path.join(prefix_path, os.path.basename(geotiff))

    return path

def gdal_split_geotiff(res_path, original_geotiff, min_X, min_Y, max_X, max_Y):
    #gdal transform
    gdal.UseExceptions() # cf. doc gdal

    gdal.Translate(
            res_path,
            original_geotiff,
            projWin=(min_X, min_Y, max_X, max_Y),
            format='GTiff'
            )
    return

def split_geotiff_ratio(orientation, ratio, geotiff):
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

    corners = compute_orientation_part_corners(
            orientation,
            extent_X_min,
            extent_X_max,
            extent_Y_min,
            extent_Y_max
            )

    part_A_min_X = corners[0]
    part_A_max_X = corners[1]
    part_A_min_Y = corners[2]
    part_A_max_Y = corners[3]
    
    part_B_min_X = corners[4]
    part_B_max_X = corners[5]
    part_B_min_Y = corners[6]
    part_B_max_Y = corners[7]

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


    part_A = gen_part_path("part_A")
    if __debug__:
        print(f"{part_A =}")

    part_B = gen_part_path("part_B")
    if __debug__:
        print(f"{part_B =}")

    # part_A
    gdal_split_geotiff(
            part_A,
            geotiff,
            part_A_min_X,
            part_A_min_Y,
            part_A_max_X,
            part_A_max_Y
            )

    # part_B
    gdal_split_geotiff(
            part_B,
            geotiff,
            part_B_min_X,
            part_B_min_Y,
            part_B_max_X,
            part_B_max_Y
            )
    return

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('missing parameter: <horiz|vert> <ratio> <geotiff_file>')
        sys.exit(1)

    (_, orientation, ratio, geotiff) = sys.argv

    if __debug__:
        print(f"{orientation = }")
        print(f"{ratio = }")
        print(f"{geotiff = }")

    split_geotiff_ratio(orientation, ratio, geotiff)

    sys.exit(0)



