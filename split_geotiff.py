import sys
import os
from osgeo import gdal

from geotiff_manipulation import (
    get_geotiff_metadata,
    get_metadata_shape,
    get_metadata_transform,
    )

def compute_orientation_border(orientation, ratio, min_A, min_B, max_A, max_B):
    results = []

    if orientation == "abs": # split over X
        split = min_A + round((max_A - min_A) * float(ratio))
        start = min(min_B, max_B)
        end = max(min_B, max_B)
    elif orientation == "ord": # split over Y
        split = min_B + round((max_B - min_B) * float(ratio))
        start = min(min_A, max_A)
        end = max(min_A, max_A)
    else:
        print(f"ERROR: unsupported split orientation {orientation}")

    results.append(split)
    results.append(start)
    results.append(end)
    results.append(0)
    results.append(0)

    return results

def compute_part_corners(ratio, min_A, min_B, max_A, max_B):
    results = []

    if __debug__:
        print(f"{min_A = }")
        print(f"{max_A = }")
        print(f"{min_B = }")
        print(f"{max_B = }")

        len_A = max_A - min_A
        len_B = max_B - min_B
        print(f"{len_A = }")
        print(f"{len_B = }")

    split = min_A + round((max_A - min_A) * float(ratio))

    if __debug__:
        print(f"{split = }")

    part_0_min_A = min_A
    part_0_max_A = split
    part_0_min_B = min_B
    part_0_max_B = max_B

    part_1_min_A = split
    part_1_max_A = max_A
    part_1_min_B = min_B
    part_1_max_B = max_B

    results.append(part_0_min_A)
    results.append(part_0_max_A)
    results.append(part_0_min_B)
    results.append(part_0_max_B)
    results.append(part_1_min_A)
    results.append(part_1_max_A)
    results.append(part_1_min_B)
    results.append(part_1_max_B)

    return results

def compute_orientation_part_corners(orientation, ratio, min_A, min_B, max_A, max_B):
    results = [None] * 8
    shuffled_results = []

    if orientation == "abs": # split over X
        results = compute_part_corners(ratio, min_A, min_B, max_A, max_B)
    elif orientation == "ord": # split over Y
        shuffled_results = compute_part_corners(ratio, min_B, min_A, max_B, max_A)
        # shuffle back corners list
        for i in range(0, 8, 4):
            results[i] = shuffled_results[i+2]
            results[i+1] = shuffled_results[i+3]
            results[i+2] = shuffled_results[i]
            results[i+3] = shuffled_results[i+1]
    else:
        print(f"ERROR: unsupported split orientation {orientation}")

    return results

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

def gdal_split_geotiff(res_path, original_geotiff, min_X, min_Y, max_X, max_Y):
    #gdal transform
    gdal.UseExceptions() # cf. doc gdal

    if __debug__:
        print(f"{res_path = }")
        print(f"{original_geotiff = }")
        print(f"{min_X = }")
        print(f"{min_Y = }")
        print(f"{max_X = }")
        print(f"{max_Y = }")


    gdal.Translate(
            res_path,
            original_geotiff,
            projWin=(min_X, min_Y, max_X, max_Y),
            format='GTiff'
            )
    return

def get_line_coords(orientation, ratio, geotiff):
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

    border = compute_orientation_border(
            orientation,
            ratio,
            extent_X_min,
            extent_Y_min,
            extent_X_max,
            extent_Y_max,
            )

    if orientation == 'abs':
        border[3] = scale_Y
        border[4] = scale_X
    else:
        border[3] = scale_X
        border[4] = scale_Y

    if __debug__:
        print(f"{border = }")

    return border


def split_geotiff_ratio(orientation, ratio, geotiff, destination):
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
            ratio,
            extent_X_min,
            extent_Y_min,
            extent_X_max,
            extent_Y_max,
            )

    part_0_min_X = corners[0]
    part_0_max_X = corners[1]
    part_0_min_Y = corners[2]
    part_0_max_Y = corners[3]
    
    part_1_min_X = corners[4]
    part_1_max_X = corners[5]
    part_1_min_Y = corners[6]
    part_1_max_Y = corners[7]

    if __debug__:
        print(f"{part_0_min_X = }")
        print(f"{part_0_max_X = }")
        print(f"{part_0_min_Y = }")
        print(f"{part_0_max_Y = }")

        print(f"{part_1_min_X = }")
        print(f"{part_1_max_X = }")
        print(f"{part_1_min_Y = }")
        print(f"{part_1_max_Y = }")


    part_0 = gen_part_path("part_0/input", geotiff, destination)
    if __debug__:
        print(f"{part_0 =}")

    # part_0
    gdal_split_geotiff(
            part_0,
            geotiff,
            part_0_min_X,
            part_0_min_Y,
            part_0_max_X,
            part_0_max_Y,
            )

    part_1 = gen_part_path("part_1/input", geotiff, destination)
    if __debug__:
        print(f"{part_1 =}")

    # part_1
    gdal_split_geotiff(
            part_1,
            geotiff,
            part_1_min_X,
            part_1_min_Y,
            part_1_max_X,
            part_1_max_Y
            )
    return

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print('missing parameter: <ord|abs> <ratio> <geotiff_file> <destdir>9')
        sys.exit(1)

    (_, orientation, ratio, geotiff, dest) = sys.argv

    if __debug__:
        print(f"{orientation = }")
        print(f"{ratio = }")
        print(f"{geotiff = }")
        print(f"{dest = }")

    split_geotiff_ratio(orientation, ratio, geotiff, dest)

    sys.exit(0)



