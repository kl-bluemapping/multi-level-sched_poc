import os
import sys
import json
#from mlsp_utils import geotiff_to_tensor
from mlsp_utils import *



# hi-res
LO_BOUND_X = 0
HI_BOUND_X = 1000 
LO_BOUND_Y = 0
HI_BOUND_Y = 2000 
'''
# lo-res
LO_BOUND_X = 0
HI_BOUND_X = 200 
LO_BOUND_Y = 0
HI_BOUND_Y = 400 
'''
DEBUG_AMP=1
TEMPORAL_SAMPLING = 10

RESOLUTION_RATIO = 5 # ex: res*i 2 == 1 pixel -> 2 pixels

# synthetic water movement data ; 1 entry per poi
# for poc, 1 dir. per poi : N->S; S->N
movement = (
        [1, 0],
        [-1, 0]
        ) # for poc, 1 dir. per poi : N->S; S->N

def extract_list_from_dict(obj, key, res_list):
    # check if obj is a dict
    if isinstance(obj, dict):
        # check if key is in dict
        for k, v in obj.items():
            if k == key:
                # append key value to results list
                res_list.append(v)
            else:
                # recurse
                extract_list_from_dict(v, key, res_list)
    # run over obj list by elem
    elif isinstance(obj, list):
        for item in obj:
            extract_list_from_dict(item, key, res_list)

def extract_key_from_geojson(geojson_path, key):
    # Charger le fichier GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    res_list = []
    extract_list_from_dict(data, key, res_list)

    return res_list

def convert_poi_spatial_coords_to_indexes(spatial_coords_sys, poi_coords):
    """
    converts a list of poi spatial coordinates to a list 
    raster indexes tuples
    """
    res_list = []
    for pc in range(len(poi_coords)):
        poi_coord = poi_coords[pc]
        poi_x = poi_coord[0]
        poi_y = poi_coord[1]
        poi_index = spatial_to_index_coords(spatial_coords, poi_x, poi_y)
        res_list.append((poi_index[0, 0], poi_index[0, 1]))
    return res_list

def aggregate_list(lists, limit):
    aggregated_lists = []
    nb_lists = len(lists)
    for l in range(nb_lists):
        list_data = lists[l]
        aggregated_list = []
        aggreg_val = 0
        aggreg_counter = 0
        for data in range(len(list_data)):
            aggreg_val += list_data[data]
            aggreg_counter += 1
            if aggreg_counter == limit:
                aggregated_list.append(aggreg_val)
                aggreg_val = 0
                aggreg_counter = 0
        aggregated_lists.append(aggregated_list)
    return aggregated_lists

def sample_list(lists, frequency):
    sample_lists = []
    nb_lists = len(lists)
    for l in range(nb_lists):
        list_data = lists[l]
        sample_list = []
        aggreg_counter = 0
        for data in range(len(list_data)):
            aggreg_counter += 1
            if aggreg_counter == frequency:
                sample_list.append(list_data[data])
                aggreg_counter = 0
        sample_lists.append(sample_list)
    return sample_lists

def gen_new_poi_indexes(poi_indexes, movements, ratio):
    new_poi_list = []
    nb_new_poi = (ratio - 1) // 2
    for p in range(len(poi_indexes)):
        poi = poi_indexes[p]
        movmt = None
        # manage lines of poi
        if p < len(poi_indexes):
            movmt = movements[0] # S->N movement
        else:
            movmt = movements[1] # N->S movement
        print(f"{movmt = }")
        i = poi[0]
        j = poi[1]
        print(f"poi({i},{j})")
        poi_neighbors = []
        for k in range(1, nb_new_poi + 1):
            if movmt[1] != 0:
                if (i+k) < HI_BOUND_Y:
                    poi_neighbors.append((i+k, j))
                poi_neighbors.append((i, j))
                if (i-k) >= LO_BOUND_Y:
                    poi_neighbors.append((i-k, j))
            elif movmt[0] != 0:
                if (j+k) < HI_BOUND_X:
                    poi_neighbors.append((i, j+k))
                poi_neighbors.append((i, j))
                if (j-k) >= LO_BOUND_X:
                    poi_neighbors.append((i, j-k))
        # manage odd nb_new_poi by adding one more
        if (ratio - 1) % 2 != 0:
            k = nb_new_poi + 1
            if movmt[1] != 0:
                if (i+k) < HI_BOUND_X:
                    poi_neighbors.append((i+k, j))
            elif movmt[0] != 0:
                if (j+k) < HI_BOUND_Y:
                    poi_neighbors.append((i, j+k))
            poi_neighbors.append((i, j))
        new_poi_list.append(poi_neighbors)
    return new_poi_list

def gen_new_poi_indexes_2(poi_indexes, movements, ratio):
    new_poi_list = []
    nb_new_poi = (ratio - 1) // 2
    for p in range(len(poi_indexes)):
        poi = poi_indexes[p]
        movmt = None
        # manage lines of poi
        if p < len(poi_indexes):
            movmt = movements[0] # S->N movement
        else:
            movmt = movements[1] # N->S movement
        print(f"{movmt = }")
        i = poi[0] * ratio
        j = poi[1] * ratio
        print(f"poi({i},{j})")
        poi_neighbors = []
        for k in range(1, nb_new_poi + 1):
            if movmt[1] != 0:
                if (i+k) < HI_BOUND_Y:
                    poi_neighbors.append((i+k, j))
                poi_neighbors.append((i, j))
                if (i-k) >= LO_BOUND_Y:
                    poi_neighbors.append((i-k, j))
            elif movmt[0] != 0:
                if (j+k) < HI_BOUND_X:
                    poi_neighbors.append((i, j+k))
                poi_neighbors.append((i, j))
                if (j-k) >= LO_BOUND_X:
                    poi_neighbors.append((i, j-k))
        # manage odd nb_new_poi by adding one more
        if (ratio - 1) % 2 != 0:
            k = nb_new_poi + 1
            if movmt[1] != 0:
                if (i+k) < HI_BOUND_X:
                    poi_neighbors.append((i+k, j))
            elif movmt[0] != 0:
                if (j+k) < HI_BOUND_Y:
                    poi_neighbors.append((i, j+k))
            poi_neighbors.append((i, j))
        new_poi_list.append(poi_neighbors)
    return new_poi_list

def gen_new_source_terms(ref_tensor_shape,
                         timestep,
                         new_poi_idx,
                         aggregated_timeseries,
                         aggregated_time_vectors,
                         ref_metadata,
                         original_transform):
    ns_tensor_n = torch.zeros(ref_tensor_shape)
    # 3b. load data in tensor @ new_poi_idfor poi in range(len(new_poi_idx)):
    for ps in range(len(new_poi_idx)):
        poi_set = new_poi_idx[ps]
        data = aggregated_timeseries[ps]
        split_data = data[timestep] / RESOLUTION_RATIO * DEBUG_AMP
        #print(f"{split_data = }")
        for poi_i, poi_j in poi_set:
            ns_tensor_n[0, poi_i, poi_j] = split_data

    #print(f"{ns_tensor_n = }")

    # 4. generate geotiffs (1 per time compr)
    # 4a. filename
    time = round(aggregated_time_vectors[0][timestep])
    #print(f"{time = }")
    filename = str(time) + ".tif"
    print(f"{filename = }")
    # 4b. writetensor to new filename
    tensor_to_geotiff(ns_tensor_n, ref_metadata, filename, original_transform)

def gen_new_source_terms_2(trgt_tensor_shape,
                           timestep,
                           new_poi_idx,
                           aggregated_timeseries,
                           aggregated_time_vectors,
                           trgt_metadata,
                           trgt_transform):
    ns_tensor_n = torch.zeros(trgt_tensor_shape)
    # 3b. load data in tensor @ new_poi_idfor poi in range(len(new_poi_idx)):
    for ps in range(len(new_poi_idx)):
        poi_set = new_poi_idx[ps]
        data = aggregated_timeseries[ps]
        split_data = data[timestep] / RESOLUTION_RATIO * DEBUG_AMP
        #print(f"{split_data = }")
        for poi_i, poi_j in poi_set:
            ns_tensor_n[0, poi_i, poi_j] = split_data

    #print(f"{ns_tensor_n = }")

    # 4. generate geotiffs (1 per time compr)
    # 4a. filename
    time = round(aggregated_time_vectors[0][timestep])
    #print(f"{time = }")
    filename = str(time) + ".tif"
    print(f"{filename = }")
    # 4b. writetensor to new filename
    tensor_to_geotiff(ns_tensor_n, trgt_metadata, filename, trgt_transform)

if len(sys.argv) != 4:
    print('missing parameter: <geojson_file> <geotiff_file> <geotiff_file>')
    sys.exit(1)

(_, geojson_file, geotiff_file, geotiff_file_2) = sys.argv

timeseries = extract_key_from_geojson(geojson_file, 'timeserie')
for ts in range(len(timeseries)):
    timeserie = timeseries[ts]
    print(f"{type(timeserie) = } {type(timeserie) =}")
    print(f"{len(timeserie) = }")

time_vectors = extract_key_from_geojson(geojson_file, 'time_vector')
for ts in range(len(time_vectors)):
    time_vector = time_vectors[ts]
    print(f"{type(time_vector) = }")
    print(f"{len(time_vector) = }")

reference_tensor = geotiff_to_tensor(geotiff_file)

print_tensor_info(reference_tensor)
print(f"{torch.max(reference_tensor) = }")

trgt_metadata = get_geotiff_metadata(geotiff_file_2)
print(f"{trgt_metadata = }")
target_tensor = geotiff_to_tensor(geotiff_file_2)
trgt_tensor_shape = target_tensor.shape
print(f"{trgt_tensor_shape = }")
trgt_transform = get_geotiff_transform(geotiff_file_2)
print(f"{trgt_transform = }")

ref_metadata = get_geotiff_metadata(geotiff_file)
print(f"{ref_metadata = }")

ref_tensor_shape = reference_tensor.shape

reference_tensor = reshape_qgis_input(reference_tensor)

original_transform = get_geotiff_transform(geotiff_file)

spatial_coords = extract_2154_coords(geotiff_file)

print(f"{type(spatial_coords) = }")
print(f"{spatial_coords.shape = }")

i = 0
j = 0
x, y = spatial_coords[i, j]
print(f"test pixel coords ({i},{j}): x={x}, y={y}")

tx = 1038046.5
ty = 6869606.5
test_idx = spatial_to_index_coords(spatial_coords, tx, ty)

print(f"{test_idx = }")

if check_spatial_coords_validity(spatial_coords, tx, ty):
    print("valid")
else:
    print("invalid")

points_coordinates = extract_key_from_geojson(geojson_file, 'coordinates')
if len(points_coordinates) < 1:
    print(f"no feature found ?")
else:
    points_coordinates = points_coordinates[0]

print(f"{points_coordinates = }")

for pc in range(len(points_coordinates)):
    point_coordinates = points_coordinates[pc]
    print(f"{type(point_coordinates) = }")
    print(f"{len(point_coordinates) = }")
    print(f"{point_coordinates = }")

# 0.convert poi spatial coords
poi_indexes = convert_poi_spatial_coords_to_indexes(spatial_coords, points_coordinates)
print(f"{points_coordinates = }")
print(f"{poi_indexes = }")

# 1. temporal compression
# 1a. for each point, aggregate timeseries data
aggregated_timeseries = aggregate_list(timeseries, TEMPORAL_SAMPLING)
# 1b. sample time_vector @ same freq. as point aggreg.
aggregated_time_vectors = sample_list(time_vectors, TEMPORAL_SAMPLING)
# 2. for each time data, dispatch to target (higher) resolution
# 2a. find poi neighbors in higher res
# we are missing the water movement direction - TODO: extend compute
#new_poi_idx = gen_new_poi_indexes(poi_indexes, movement, RESOLUTION_RATIO)
new_poi_idx = gen_new_poi_indexes_2(poi_indexes, movement, RESOLUTION_RATIO)
#print(f"{new_poi_idx = }")
# 3. create new source term for target resolution
# 3a. create empty tensor of dim src term

for t in range(len(aggregated_time_vectors[0])):
               #gen_new_source_terms(ref_tensor_shape,
               #                     t,
               #                     new_poi_idx,
               #                     aggregated_timeseries,
               #                     aggregated_time_vectors,
               #                     ref_metadata,
               #                     original_transform)
               gen_new_source_terms(trgt_tensor_shape,
                                    t,
                                    new_poi_idx,
                                    aggregated_timeseries,
                                    aggregated_time_vectors,
                                    trgt_metadata,
                                    trgt_transform)

