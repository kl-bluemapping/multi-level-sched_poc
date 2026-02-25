''' coordinates_conversion.py
functions to manipulate spatial and discrete index coordinates
'''

import numpy as np

def index_to_coordinates(coordinates, i, j):
    x, y = coordinates[i, j]
    return x, y

def coordinates_to_index(coordinates, x, y, tolerance = 1e-6):
    diff_x = np.abs(coordinates[:, :, 0] - x)
    diff_y = np.abs(coordinates[:, :, 1] - y)
    correspondances = np.logical_and(diff_x < tolerance, diff_y < tolerance)

    result = np.argwhere(correspondances)
    # squash result arr. dim.
    result = result[0]

    return result

def is_coordinate_valid(coordinates, x, y, tolerance=1e-6):
    diff_x = np.abs(coordinates[:, :, 0] - x)
    diff_y = np.abs(coordinates[:, :, 1] - y)
    correspondances = np.logical_and(diff_x < tolerance, diff_y < tolerance)
    result = np.any(correspondances)
    return result

def is_indexes_list_valid(coordinates, indexes_list):
    """
    for ea. index in list, check if index is valid when converted to coordinates
    referential
    """
    for indexes in indexes_list:
       for index in indexes:
           i = index[0]
           j = index[1]
           x, y = index_to_coordinates(coordinates, i, j)
           coords_vld = is_coordinate_valid(coordinates, x, y)
           if not coords_vld:
               print(f"Error: index({i},{j}) mapped to coords({x},{y}) invalid")
    return

def coordinates_list_to_indexes(coordinates, coordinates_list):
    """
    converts a list of coordinates to a list of indexes
    """
    result_list = []
    for coord in coordinates_list:
        x = coord[0]
        y = coord[1]
        index = coordinates_to_index(coordinates, x, y)
        result_list.append(index)
    return result_list
