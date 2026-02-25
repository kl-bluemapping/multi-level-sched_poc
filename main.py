''' main.py
sim. input up/down-scaling caller
'''

import sys
import copy
import numpy as np

from poi_data_extraction import (
        extract_values
        )
from geotiff_manipulation import (
        geotiff_to_array,
        array_to_geotiff,
        get_geotiff_metadata,
        get_coordinates_2154,
        get_metadata_shape,
        )
from coordinates_conversion import (
        index_to_coordinates,
        coordinates_to_index,
        is_coordinate_valid,
        is_indexes_list_valid,
        coordinates_list_to_indexes,
        )

SOURCE_TERMS_TIMING = 300 # in seconds

DEBUG_AMP = 1e0

INIT_TOTAL_METRIC_ACC = 0
TEST_TOTAL_METRIC_ACC = 0
TEST_SRC_TERMS_METRIC_ACC = 0

def get_intervals_indexes(times_list, interval):
    '''
    get the list of indexes of the times_list values spaced by interval
    e.g. list = [0, 10, 20, 30, 60, 100, 150, 200] ; interval = 60
        will return [4, 6, 7]
    '''
    result_list = []
    clock = interval
    for t, time in enumerate(times_list):
        #print(f"{t = } ; {time = }")
        if time >= clock:
            result_list.append(t)
            clock += interval
    return result_list

def get_total_accumulated_data(data_lists):
    result = 0
    for lst in data_lists:
        for d, data in enumerate(lst):
            result += data
    return result

def aggregate_data_by_interval(data_lists, indexes_list):
    '''
    for ea. list in the data_list, aggregate the datapoints into nb. intervals
    datapoints
    returns a list of the aggregated (compressed) lists
    '''
    result_lists = []
    for lst in data_lists:
        aggregated_list = []
        aggregated_data = 0
        interval_index = 0
        target_index = indexes_list[interval_index]
        for d, data in enumerate(lst):
            aggregated_data += data
            if d == target_index:
                aggregated_list.append(aggregated_data)
                aggregated_data = 0
                interval_index += 1
                if interval_index < len(indexes_list):
                    target_index = indexes_list[interval_index]
        # manage last interval
        if target_index < len(lst)-1:
            aggregated_list.append(aggregated_data)
        result_lists.append(aggregated_list)
    return result_lists


def get_intervals_start_time(times, times_indexes):
    '''
    get the start time for ea. interval
    err if first interval ends at t0
    '''
    result_list = []
    for i, index in enumerate(times_indexes):
        result_list.append(times[index])
    result_list.insert(0, times[0]);
    return result_list

def get_interval_average(data_lists, interval_length):
    '''
    average ea. datapoint by interval_length
    '''
    result_lists = []
    if __debug__:
        TOTAL_DATA = 0
        TOTAL_AVG = 0
    for lst in data_lists:
        averaged_list = []
        for data in lst:
            averaged_data = data / interval_length
            averaged_list.append(averaged_data)
            if __debug__:
                print(f" {averaged_data = } = {data = } / {interval_length = }")
        result_lists.append(averaged_list)
        if __debug__:
            TOTAL_DATA = TOTAL_DATA + sum(lst)
            TOTAL_AVG = TOTAL_AVG + sum(averaged_list)
    if __debug__:
        print(f"{TOTAL_DATA = } {TOTAL_AVG = }")
    return result_lists


def indexes_cardinal_split(indexes, split='vertical'):
    '''
    splits indexes list into two lists N/S or W/E
    '''
    part_A = []
    part_B = []
    if split == 'vertical':
        axis = 0
    elif split == 'horizontal':
        axis = 1
    else:
        raise ValueError(f"split '{split}' is not supported")

    ref_poi = indexes[0][axis]
    for index in indexes:
        if index[0] == ref_poi:
            part_A.append(index)
        else:
            part_B.append(index)

    # always return partitions in order high -> low
    if part_B[0][axis] > part_A[0][axis]:
        return part_B, part_A
    else:
        return part_A, part_B

def sursample_indexes(indexes, offset, ratio):
    result_list = []
    nb_new_indexes = (ratio - 1) // 2 # nb of new indexes on ea. side of ea. index
    for index in indexes:
        new_indexes = []
        for k in range(-nb_new_indexes, nb_new_indexes + 1):
            for o, offst in enumerate(offset):
                if offst != 0:
                    no = (index[o] + offst) * ratio
                    p = (o + 1) % 2
                    np = (index[p] + offset[p]) * ratio + k
                    if o < p:
                        new_indexes.append([no, np])
                    else:
                        new_indexes.append([np, no])
        if (ratio - 1) % 2 != 0:
            k = 1
            for o, offst in enumerate(offset):
                if offst != 0:
                    no = (index[o] + offst) * ratio
                    p = (o + 1) % 2
                    np = (index[p] + offset[p]) * ratio + k
                    if o < p:
                        new_indexes.append([no, np])
                    else:
                        new_indexes.append([np, no])
        result_list.append(new_indexes)
    return result_list

def remove_duplicated_indexes(indexes_list):
    '''
    remove duplicated entries in sublist from a list of lists
    '''
    counter = 0
    result_list = []
    for lst in indexes_list:
        clean_list = []
        for index in lst:
            if index not in clean_list:
                clean_list.append(index)
            else:
                counter += 1
                #print(f"removed {index} duplicate")
        result_list.append(clean_list)
    if counter > 0:
        print(f"removed {counter} duplicated indexes")
    return result_list

def remove_out_of_bound_indexes(indexes_list, i_bound, j_bound,
                                i_bound_low = 0,
                                j_bound_low = 0):
    '''
    remove out of bounds entries in sublist from a list of lists
    '''
    counter = 0
    result_list = []
    for lst in indexes_list:
        clean_list = []
        for index in lst:
            if index[0] in range(i_bound_low, i_bound) and index[1] in range(j_bound_low, j_bound):
                clean_list.append(index)
            else:
                counter += 1
                #print(f"removed {index} out of bounds {i_bound} {j_bound}")
        result_list.append(clean_list)
    if counter > 0:
        print(f"removed {counter} out-of-bounds indexes")
    return result_list

def generate_source_terms_list(nb_intervals, source_terms, target_shape,
                               partition_A, partition_B):
    source_terms_list = []
    for t in range(nb_intervals):
        source_terms_array = np.zeros(target_shape)
        for n, indexes in enumerate(partition_A):
            for index in indexes:
                source_terms_array[index[0]][index[1]] = source_terms[n][t] / len(indexes) * DEBUG_AMP
        n += 1
        for s, indexes in enumerate(partition_B):
            for index in indexes:
                source_terms_array[index[0]][index[1]] = source_terms[n+s][t] / len(indexes) * DEBUG_AMP

        source_terms_list.append(source_terms_array)
    return source_terms_list


def write_source_terms(source_terms_list, metadata, source_terms_start_times):
    for t, time in enumerate(source_terms_start_times):
        rounded_time = round(time)
        geotiff_name = str(rounded_time) + ".tif"

        print(f"writing {geotiff_name}")
        array_to_geotiff(source_terms_list[t], metadata, geotiff_name)
    return

def generate_source_terms(split, geojson, lo_geotiff, hi_geotiff):
    # 0. init.

    # get poi data from geojson
    timeseries = extract_values(geojson, 'timeserie')

    if __debug__:
        INIT_TOTAL_METRIC_ACC = get_total_accumulated_data(timeseries)
        print(f"{INIT_TOTAL_METRIC_ACC = }")

    # get poi sampling time from geosjon
    timevector = extract_values(geojson, 'time_vector')
    # squash timevector arr. dim.
    if len(timevector) == 1:
        timevector = timevector[0]
    else:
        print(f"ERROR: problem w/ the geojson sampling times")
        sys.exit(1)

    # get spatial coordinates baseline from low-res geotiff
    lo_coords_2154 = get_coordinates_2154(lo_geotiff)
    # test coodinate <-> index conversions
    if __debug__:
        i, j = 0, 0
        x, y = index_to_coordinates(lo_coords_2154, i, j)
        idx = coordinates_to_index(lo_coords_2154, x, y)
        print(f"TEST: pixel_coords({i},{j}): x={x}, y={y} index={idx}")
        coords_vld = is_coordinate_valid(lo_coords_2154, x, y)
        print(f"TEST: coordinates({x},{y}) valid ? {coords_vld}")

    # get poi spatial coordinates from geojson
    poi_coordinates = extract_values(geojson, 'coordinates')
    # squash timevector arr. dim.
    if len(poi_coordinates) >= 1:
        poi_coordinates = poi_coordinates[0]
    else:
        print(f"ERROR: no poi coordinates found in geojson")
        sys.exit(1)
    # test poi coordinates validity
    if __debug__:
        for coord in poi_coordinates:
            x = coord[0]
            y = coord[1]
            coord_valid = is_coordinate_valid(lo_coords_2154, x, y)
            if not coord_valid:
                print(f"ERROR: invalid coordinates: ({x},{y})")

    # get low-res geotiff metadata
    lo_metadata = get_geotiff_metadata(lo_geotiff)
    # get low-res geotiff shape
    lo_shape = get_metadata_shape(lo_metadata)

    # convert poi coordinates to array indexes
    poi_indexes = coordinates_list_to_indexes(lo_coords_2154, poi_coordinates)
    # test poi converterd indexes validity
    if __debug__:
        bi = lo_shape[0]
        bj = lo_shape[1]
        for index in poi_indexes:
            i = index[0]
            j = index[1]
            index_valid = (i in range(0, bi)) and (j in range(0, bj))
            if not index_valid:
                print(f"ERROR: index: ({i},{j}) out of range: ({bi},{bj})")

    # 1. lo-res. sim histogram 

    # select target times for source term generation
    selected_intervals_indexes = get_intervals_indexes(timevector, SOURCE_TERMS_TIMING)
    # test selected nb. of times, ie nb. of intervals
    if __debug__:
        print(f"selected {len(selected_intervals_indexes)} intervals")
        if len(selected_intervals_indexes) < 1:
            print(f"Error: not enough times, check the interval var.")
            sys.exit(1)

    # 1a. aggregate poi data by time interval
    aggregated_data = aggregate_data_by_interval(timeseries, selected_intervals_indexes)

    if __debug__:
        TEST_TOTAL_METRIC_ACC = get_total_accumulated_data(aggregated_data)
        print(f"{TEST_TOTAL_METRIC_ACC = }")

    if __debug__:
        print(f"datapoint {0} is of length {len(aggregated_data[0])}")
        for d, data in enumerate(aggregated_data):
            if len(data) < len(selected_intervals_indexes):
                print(f"Error: datapoint {d} is of {len(data)=} but should be at least {len(selected_intervals_indexes)}")

    # 1b. average interval data by interval length 
    #lo_source_terms = get_interval_average(aggregated_data, SOURCE_TERMS_TIMING)
    lo_source_terms = get_interval_average(aggregated_data, 1)

    if __debug__:
        TEST_SRC_TERMS_METRIC_ACC = get_total_accumulated_data(lo_source_terms)
        print(f"{TEST_SRC_TERMS_METRIC_ACC = }")

    # 2. create higher resolution points for the source term to target

    # 2a. divide poi by spatial section
    # A/B partition
    A_poi, B_poi = indexes_cardinal_split(poi_indexes, 'vertical')

    # 2b. compute scaling ratio between hih and low res/
    # get high-res geotiff metadata
    hi_metadata = get_geotiff_metadata(hi_geotiff)
    # get high-res geotiff shape
    hi_shape = get_metadata_shape(hi_metadata)

    # check ratios w/ round to neareset instead of div. rest
    height_ratio = round(hi_shape[0] / lo_shape[0])
    width_ratio = round(hi_shape[1] / lo_shape[1])
    # input test
    if height_ratio != width_ratio:
        print(f"{hi_shape = }")
        print(f"{lo_shape = }")
        print(f"{height_ratio = }")
        print(f"{width_ratio = }")
        raise ValueError("incompatible raster shapes")
    else:
        ratio = height_ratio

    # 2c. for ea. partition, create new hi-res indexes
    if split == "horiz":
        # north
        A_B_mv = [1, 0] # north part to south part movement
        new_B_indexes = sursample_indexes(A_poi, A_B_mv, ratio)
        # cleanup (optional)
        new_B_indexes = remove_duplicated_indexes(new_B_indexes)
        new_B_indexes = remove_out_of_bound_indexes(new_B_indexes,
                                                        hi_shape[0],
                                                        hi_shape[1])
        # south
        B_A_mv = [-1, 0] # north part to south part movement
        new_A_indexes = sursample_indexes(B_poi, B_A_mv, ratio)
        # cleanup (optional)
        new_A_indexes = remove_duplicated_indexes(new_A_indexes)
        new_A_indexes = remove_out_of_bound_indexes(new_A_indexes,
                                                        hi_shape[0],
                                                        hi_shape[1])
    elif split == "vert":
        # west
        A_B_mv = [0, 1] # west part to east part movement
        new_B_indexes = sursample_indexes(A_poi, A_B_mv, ratio)
        # cleanup (optional)
        new_B_indexes = remove_duplicated_indexes(new_B_indexes)
        new_B_indexes = remove_out_of_bound_indexes(new_B_indexes,
                                                        hi_shape[0],
                                                        hi_shape[1])
        # est
        B_A_mv = [0, -1] # east part to west part movement
        new_A_indexes = sursample_indexes(B_poi, B_A_mv, ratio)
        # cleanup (optional)
        new_A_indexes = remove_duplicated_indexes(new_A_indexes)
        new_A_indexes = remove_out_of_bound_indexes(new_A_indexes,
                                                        hi_shape[0],
                                                        hi_shape[1])
    else:
        print(f"ERROR: unsupported split operation: {split}")

    # test if new indexes map to valid coordinates
    if __debug__:
        # get spatial coordinates baseline from high-res geotiff
        hi_coords_2154 = get_coordinates_2154(hi_geotiff)
        is_indexes_list_valid(hi_coords_2154, new_B_indexes)
        is_indexes_list_valid(hi_coords_2154, new_A_indexes)


    # 3. create & assign source terms to high-res indexes

    # 3a. get source terms start time
    source_terms_start_times = get_intervals_start_time(timevector, selected_intervals_indexes)

    # 3b. create list of arrays of high-res source terms from low-res source terms
    hi_source_terms_list = generate_source_terms_list(len(source_terms_start_times),
                                                      lo_source_terms,
                                                      hi_shape,
                                                      new_A_indexes,
                                                      new_B_indexes,
                                                      )

    # 4. write geotiff files
    write_source_terms(hi_source_terms_list, hi_metadata, source_terms_start_times)



if __name__ == "__main__":
    if len(sys.argv) != 5:
        print('missing parameter: <horiz|vert> <geojson_file> <lo-res_geotiff_file> <hi-res_geotiff_file>')
        sys.exit(1)

    (_, split, geojson, lo_geotiff, hi_geotiff) = sys.argv

    if __debug__:
        print(f"{split = }")
        print(f"{geojson = }")
        print(f"{lo_geotiff = }")
        print(f"{hi_geotiff = }")

    generate_source_terms(_, split, geojson, lo_geotiff, hi_geotiff)

    sys.exit(0)
