import json

features_header = """{
    "type": "FeatureCollection",
    "name": "borders_poi_lines",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:EPSG::2154"
            }
        },
    "features": ["""

def gen_poi_features_header():
    return features_header

def gen_poi_feature(x, y):
    feature = {
            "type": "Feature",
            "properties": {
                "VALUE": 1.0,
                "operations": {
                    "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option": "water_depth_matrix"
                    },
                "display_key": "water_depth_matrix_get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option"
                },
            "geometry": {
                "type": "Point",
                "coordinates": [x, y]
                }
            }
    return feature

features_metadata = """"features_metadata": {
        "layer_name": "POI_water_depth",
        "measure_every_N_iterations": 10,
        "save_timeserie": "yes",
        "modify_units": {
            "action": "no",
            "variable": "water_depth_matrix",
            "operation": "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option",
            "new_unit": ""
        },
        "data_scaling": {
            "variable": "water_depth_matrix",
            "operation": "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option",
            "scaling_factor": {
                "value": 1.0,
                "type": "constant",
                "expr": 1.0
            }
        },
        "persistence_properties": {
            "persistence_mode": "normal",
            "variable": "water_depth_matrix",
            "operation": "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option"
        },
        "display": {
            "water_depth_matrix_get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option": {
                "variable": "water_depth_matrix",
                "operation": "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option",
                "attribut_for_dynamic_display": "max",
                "color_name": "LOW_HEIGHT_COLORMAP",
                "color_mode": "default",
                "color_levels": [
                    0.1,
                    0.5,
                    0.8,
                    0.9,
                    0.99
                ],
                "color_extrema": {
                    "max": 1.0
                },
                "fill_type": "dynamic",
                "fill_value": "rgba(249, 202, 50, 1)",
                "hide_null_values": "yes",
                "legend_prefix": "",
                "legend_tick": ".2f",
                "legend_unit": "",
                "legend_variable_display_name": "",
                "show_as_legend": "yes",
                "radius_type": "dynamic",
                "radius_adaptative_display": "dynamic",
                "radius_min_adaptative_display": 5,
                "radius_max_adaptative_display": 40,
                "stroke_type": "constant",
                "stroke_width": 1,
                "text_type": "dynamic",
                "text_adaptative_display": "dynamic",
                "text_hide_threshold": 10,
                "text_value": "text"
            }
        }
    }"""

def gen_poi_features_metadata():
    return features_metadata

