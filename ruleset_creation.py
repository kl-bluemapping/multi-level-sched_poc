import os

from ruleset_manipulation import (
        insert_value,
        insert_pair,
        )

def copy_file_contents(file_a, file_b):
    with open(file_a, "r") as in_file, open(file_b, "a") as out_file:
        for line in in_file:
            out_file.write(line)
    return

def create_downscaled_sim_ruleset(reference_ruleset, split_axis, downscaled_sim, poi_line):
    # gen. downscaled sim. ruleset
    downscaled_ruleset = downscaled_sim.input_path + "ruleset.json5"

    # TODO: if ruleset already exist, skip
    if not os.path.isfile(downscaled_ruleset):

        # copy contents of reference_ruleset into downscaled_ruleset
        copy_file_contents(reference_ruleset, downscaled_ruleset)

        insert_value(downscaled_ruleset, "measure_metrics", "get_point_of_interest_metrics")

        insert_value(downscaled_ruleset, "last_pass", "append_final_poi_persistence")

        insert_pair(downscaled_ruleset,
                    "operations",
                    "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option",
                    "get_matrix_value_at_coordinates_grouped_by_dimension_with_scaling_option",
                    )

        insert_pair(downscaled_ruleset,
                    "operations",
                    "append_final_poi_persistence",
                    "append_final_persistence_poi_geojson_with_statistics",
                    )

        downscaled_cell_size = abs(poi_line[3])

        insert_pair(downscaled_ruleset,
                    "properties",
                    "cell_size",
                    downscaled_cell_size
                    )

        poi_dataset_entry = {
                "key": "points_of_interest",
                "input": {
                    "slice": {
                        "path": "poi",
                        },
                    "timestamps": {
                        "fixed": [
                            "0",
                            ],
                        },
                    "bytes_mapper": "json_bytes_to_poi_dict",
                    "type": "v2",
                    "transforms": [],
                    "initialization": "point_of_interest_model_initialization",
                    }
                    }
        insert_value(downscaled_ruleset, "datasets", poi_dataset_entry)

        downscaled_height = poi_line[5]

        insert_pair(downscaled_ruleset,
                    "profile",
                    "height",
                    downscaled_height
                    )

        downscaled_width = poi_line[6]

        insert_pair(downscaled_ruleset,
                    "profile",
                    "width",
                    downscaled_width
                    )

        if split_axis == "abs":
            downscaled_scale_x = poi_line[4]
        else:
            downscaled_scale_x = poi_line[3]

        insert_pair(downscaled_ruleset,
                    "transform",
                    "scale_x",
                    downscaled_scale_x
                    )

        if split_axis == "abs":
            downscaled_scale_y = poi_line[3]
        else:
            downscaled_scale_y = poi_line[4]

        insert_pair(downscaled_ruleset,
                    "transform",
                    "scale_y",
                    downscaled_scale_y
                    )

        outputs_poi_wo_timeserie = {
                "output_type": "eoi",
                "path": "output=POI_water_depth_scaled_measure_POI_on_water_depth_without_timeserie",
                "processors": {},
                "variable": "POI_water_depth_scaled_measure_POI_on_water_depth_without_timeserie",
                }
        insert_pair(downscaled_ruleset,
                    "outputs",
                    "POI_water_depth_scaled_measure_POI_on_water_depth_without_timeserie",
                    outputs_poi_wo_timeserie,
                    )

        outputs_poi_w_timeserie = {
            "output_type": "eoi",
            "path": "output=POI_water_depth_scaled_measure_POI_on_water_depth_with_timeserie",
            "processors": {},
            "variable": "POI_water_depth_scaled_measure_POI_on_water_depth_with_timeserie",
            }
        insert_pair(downscaled_ruleset,
                    "outputs",
                    "POI_water_depth_scaled_measure_POI_on_water_depth_with_timeserie",
                    outputs_poi_w_timeserie,
                    )
    return

def create_subsim_ruleset(reference_ruleset, subsim, profile):

    # gen. downscaled sim. ruleset
    subsim_ruleset = subsim.input_path + "ruleset.json5"

    # copy contents of reference_ruleset into subsim_ruleset
    copy_file_contents(reference_ruleset, subsim_ruleset)

    subsim_height = profile[0]
    subsim_width = profile[1]
    subsim_left = profile[2]
    subsim_top = profile[3]
    subsim_right = profile[4]
    subsim_bottom = profile[5]

    insert_pair(subsim_ruleset,
                "profile",
                "height",
                subsim_height
                )

    insert_pair(subsim_ruleset,
                "profile",
                "width",
                subsim_width
                )

    insert_pair(subsim_ruleset,
                "bounds",
                "left",
                subsim_left
                )

    insert_pair(subsim_ruleset,
                "bounds",
                "top",
                subsim_top
                )

    insert_pair(subsim_ruleset,
                "bounds",
                "right",
                subsim_right
                )

    insert_pair(subsim_ruleset,
                "bounds",
                "bottom",
                subsim_bottom
                )

    return
