import sys
import os
import json
import numpy as np

from poi_geojson_stub import (
        gen_poi_features_header,
        gen_poi_feature,
        gen_poi_features_metadata,
        )

def create_poi_geojson(const, axis, start, end, stride, offset, dest):

    if __debug__:
        print(f"{const = }")
        print(f"{axis = }")
        print(f"{start = }")
        print(f"{end = }")
        print(f"{stride = }")
        print(f"{offset = }")
        print(f"{dest = }")

    with open(dest, 'a', encoding="utf-8") as file:
        file.write(gen_poi_features_header())
        file.write("\n")

        line_offset = const - abs(offset)

        for i in np.arange(start, end, stride):
            if axis == 'abs':
                feature = gen_poi_feature(line_offset, i)
            else:
                feature = gen_poi_feature(i, line_offset)
            json.dump(feature, file, indent=4)
            if i+stride < end: # manage last feature comma
                file.write(",\n")
            else:
                file.write("\n")

        file.write(",")
        line_offset = const + abs(offset)

        for i in np.arange(start, end, stride):
            if axis == 'abs':
                feature = gen_poi_feature(line_offset, i)
            else:
                feature = gen_poi_feature(i, line_offset)
            json.dump(feature, file, indent=4)
            if i+stride < end: # manage last feature comma
                file.write(",\n")
            else:
                file.write("\n")

        file.write("],\n")
        file.write(gen_poi_features_metadata())
        file.write("\n}")
        file.close()

    return

if __name__ == "__main__":
    if len(sys.argv) != 8:
        print('missing parameter: <const> <axis> <start> <end> <stride> <offset> <dest>')
        sys.exit(1)

    (_, const, axis, start, end, stride, offset, dest) = sys.argv

    if __debug__:
        print(f"{const = }")
        print(f"{axis = }")
        print(f"{start = }")
        print(f"{end = }")
        print(f"{stride = }")
        print(f"{offset = }")
        print(f"{dest = }")

    create_poi_geojson(
            int(const),
            axis,
            int(start),
            int(end),
            int(stride),
            int(offset),
            dest)

    sys.exit(0)

