import sys
import os
import torch

from geotiff_manipulation import (
    get_geotiff_metadata,
    get_metadata_shape,
    )
from split_geotiff import (
        split_geotiff_ratio,
        get_line_coords,
        stitch_geotiffs,
        )
from scale_geotiff import (
        scale_geotiff,
        )
from gen_poi_line import (
        create_poi_geojson,
        )
from ruleset_creation import (
        create_downscaled_sim_ruleset,
        create_subsim_ruleset,
        )
from gen_src_terms import (
        generate_source_terms
        )

from osgeo import gdal

def is_geotiff(file):
    gdal.UseExceptions()
    res = False
    try:
        geotiff  = gdal.Open(file)
        res = True
    except Exception as e:
        if __debug__:
            print(f"{e}: gdal could not open {file} as a geotiff")
    return res

def copy_subdirs_tree(root_dir, copy_dir):
    root_dirs = next(os.walk(root_dir), (None, [], None))[1]
    #root_files = next(os.walk(root_dir), (None, None, []))[2]
    for d in root_dirs:
        try:
            os.mkdir(copy_dir + "/" + d + "/")
        except Exception as e:
            print(f"{e}")

class SimProfile:
    def __init__(self, gpu_id, root):
        self.gpu_id = gpu_id
        if not os.path.exists(root):
            os.mkdir(root)
        self.root_path = root
        in_path = root + "input/"
        if not os.path.exists(in_path):
            os.mkdir(in_path)
        self.input_path = in_path
        out_path = root + "output/"
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        self.output_path = out_path
        self.status = -1

    def copy_input_dirs(self, source):
        copy_subdirs_tree(source, self.input_path)

def create_dir(path, name):
    res = ""
    try:
        dir_path = path + name + "/"
        os.mkdir(dir_path)
        res = dir_path
    except Exception as e:
        print(f"{e}: could not create directory {dir_path}")
        res = dir_path
    return res

def setup_simulations_dirs(root_sim_dir, nb_devices, subsims_path):
    sims = []

    # log original sim.
    original_sim = SimProfile(-1, root_sim_dir)
    sims.append(original_sim)

    # log downscaled sim. & create dirs.
    downscaled_sim_path = root_sim_dir + "downscaled/"
    downscaled_sim = SimProfile(0, downscaled_sim_path)
    downscaled_sim.copy_input_dirs(original_sim.input_path)
    sims.append(downscaled_sim)

    # log sub-sims
    for i in range(nb_devices):
        sub_path = "part_" + str(i) + "/"
        subsim_path = os.path.join(subsims_path, sub_path)
        sim = SimProfile(i, subsim_path)
        #sim.copy_input_dirs(original_sim.input_path)
        sims.append(sim)

    return sims

def main(orig_sim_path, split_axis, split_ratio, scaling_ratio):
    # count gpus
    gpu_count = torch.cuda.device_count()
    if __debug__:
        print(f"{gpu_count} available gpu")
        for i in range(gpu_count):
            print(f"gpu{i}:{torch.cuda.get_device_properties(i)}")

    # sub-sims. nb. -- 2 or nb. of gpus
    #subsims_count = max(2, gpu_count)
    subsims_count = 2 # debug

    subsims_dir = create_dir(orig_sim_path, "subsims")

    # setup simulation profiles 
    sims_profiles = setup_simulations_dirs(orig_sim_path, subsims_count, subsims_dir)

    reference_sim = sims_profiles[0]
    downscaled_sim = sims_profiles[1]

    reference_ruleset = reference_sim.input_path + "ruleset.json5"
    reference_geotiff = reference_sim.input_path + "topography/" + "0.tif"

    ref_metadata = get_geotiff_metadata(reference_geotiff)
    ref_height, ref_width = get_metadata_shape(ref_metadata)

    # gen. src. terms
    # setup source terms dir
    downscaled_inputs_dir = downscaled_sim.root_path

    # gen. split & downscaled inputs
    for root, dirs, files in os.walk(reference_sim.input_path):
        for f in files:
            path_f = os.path.join(root, f)
            if is_geotiff(path_f):
                subsims_bounds = split_geotiff_ratio(split_axis, split_ratio, path_f, subsims_dir)
                scale_geotiff(scaling_ratio, path_f, downscaled_inputs_dir)

    # set downscaled sim. poi dir.
    downscaled_poi_dir = create_dir(downscaled_sim.input_path, "poi")

    # set target poi file
    poi_geojson = downscaled_poi_dir + "0.geojson"

    # get downscaled geotiff line of poi coords
    downscaled_ref_geotiff = downscaled_sim.input_path + "topography/" + "0.tif"
    poi_line = get_line_coords(
            split_axis,
            split_ratio,
            downscaled_ref_geotiff
            )

    if __debug__:
        print(f"{poi_line = }")

    # gen. poi line
    if not os.path.isfile(poi_geojson):
        create_poi_geojson(
                poi_line[0],
                split_axis,
                poi_line[1],
                poi_line[2],
                poi_line[3],
                poi_line[4],
                poi_geojson
                )

    create_downscaled_sim_ruleset(reference_ruleset, split_axis, downscaled_sim, poi_line)

    # collect downscaled results
    # TODO: subprocess run

    # gen. src. terms
    # setup source terms dir
    # TODO: directly in subsims ?
    src_terms_dir = create_dir(orig_sim_path, "springs_wells")
    downscaled_res_geojson_path = downscaled_sim.output_path + "output=POI_water_depth_scaled_measure_POI_on_water_depth_with_timeserie/"
    downscaled_res_geojson_file = os.listdir(downscaled_res_geojson_path)[0]
    downscaled_res_geojson = downscaled_res_geojson_path + downscaled_res_geojson_file

    if __debug__:
        print(f"{src_terms_dir = }")
        print(f"{split_axis = }")
        print(f"{downscaled_res_geojson_path = }")
        print(f"{downscaled_res_geojson_file = }")
        print(f"{downscaled_res_geojson = }")
        print(f"{downscaled_ref_geotiff = }")
        print(f"{reference_geotiff = }")

    generate_source_terms(split_axis, downscaled_res_geojson, downscaled_ref_geotiff, reference_geotiff, src_terms_dir)

    # feed src. terms to sub-sims.

    # setup split src_terms subsims dest dirs
    # split src_terms
    for root, dirs, files in os.walk(src_terms_dir):
        for f in files:
            path_f = os.path.join(root, f)
            if is_geotiff(path_f):
                src_terms_bounds = split_geotiff_ratio(split_axis, split_ratio, path_f, subsims_dir)

    # gen. sub-sims rulesets
    if __debug__:
        print(f"{subsims_bounds = }")

    subsims_rulesets = []
    for i in range(subsims_count):
        subsim = sims_profiles[i+2] # account for ref & downscaled
        subsim_geotiff = subsim.input_path + "topography/" + "0.tif"
        subsim_metadata = get_geotiff_metadata(subsim_geotiff)
        subsim_height, subsim_width = get_metadata_shape(subsim_metadata)
        idx = i*4
        profile = []
        profile.append(subsim_height)
        profile.append(subsim_width)
        profile.append(subsims_bounds[idx+0])
        profile.append(subsims_bounds[idx+1])
        profile.append(subsims_bounds[idx+2])
        profile.append(subsims_bounds[idx+3])

        if __debug__:
            print(f"subsim {i} {profile = }")

        subsim_ruleset = subsim.input_path + "ruleset.json5"
        if not os.path.isfile(subsim_ruleset):
            create_subsim_ruleset(reference_ruleset, subsim, profile)
        subsims_rulesets.append(subsim_ruleset)

    if __debug__:
        for ruleset in subsims_rulesets:
            print(f"subsim ruleset: {ruleset}")

    # stitch sub-sims results to reference sim extent

    # gdal merge list: list[list[geotiff_a, geotiff_b,...]]
    stitch_targets = []
    # iter over all part_0 res. that have a match
    subsim_0_output = sims_profiles[2].output_path
    for root, dirs, files in os.walk(subsim_0_output):
        for d in dirs:
            path_d = os.path.join(root, d)
            if os.path.isdir(path_d):
                #if __debug__:
                #    print(f"{path_d = }")
                #    print(f"{os.listdir(path_d) = }")
                for f in os.listdir(path_d):
                    if f.endswith('.tif'):
                        part_0_f = os.path.join(root, d, f)
                        if os.path.isfile(part_0_f):
                            stitch_target = [part_0_f]
                            if __debug__:
                                print(f"found: {part_0_f}")
                        for i in range    (1, subsims_count): # every subsim after part_0
                            subsim_output_path = sims_profiles[2+i].output_path
                            subsim_f = os.path.join(subsim_output_path, d, f)
                            if os.path.isfile(subsim_f):
                                stitch_target.append(subsim_f)
                                stitch_targets.append(stitch_target)
                                if __debug__:
                                    print(f"found: {subsim_f}")

    if __debug__:
        print(f"{stitch_targets = }")
        print(f"{len(stitch_targets) = }")

    # setup outputs merging dir
    final_res_dir = reference_sim.output_path
    if __debug__:
        print(f"{final_res_dir = }")

    for stitch_target in stitch_targets:
        target_name = os.path.basename(stitch_target[0])
        target_dir = os.path.basename(os.path.dirname(stitch_target[0]))
        final_target_dir = create_dir(final_res_dir, target_dir)
        final_target = final_target_dir + target_name
        stitch_geotiffs(stitch_target, final_target)
        if __debug__:
            print(f"{stitch_target = }")
            print(f"{final_target = }")

    return

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print('''missing parameter:
            <abs|ord (string)>
            <split ratio (float)>
            <scaling (integer)>
            <simulation (path)>
            <driver>
              ''')
        sys.exit(1)

    split_axis = sys.argv[1]
    split_ratio = sys.argv[2]
    scaling_ratio = sys.argv[3]
    orig_sim_path = sys.argv[4]
    driver = sys.argv[5]
    sim_args = sys.argv[5:]

    if __debug__:
        print(f"{split_axis = }")
        print(f"{split_ratio = }")
        print(f"{scaling_ratio = }")
        print(f"{orig_sim_path = }")
        print(f"{driver = }")
        print(f"{sim_args = }")

    # run downscaled sim. in sub-process
    # retrieve args
    args = sim_args

    # set entrypoint
    entrypoint = "./src/main.py"

    # create run command
    command = args
    command.insert(0, entrypoint)
    command.insert(0, '-O')
    command.insert(0, "python3")

    # set expected return val
    retcode = 0

    if __debug__:
        print(f"run {command = }")

    #sys.exit(0)

    #try:
    #    result = subprocess.run(command, capture_output=True, text=True)
    #    if result.returncode == retcode:
    #        print(f"subproc. returned {retcode}")
    #    else:
    #        print(f"subproc err. {result.returncode}")
    #except OSError as e:
    #    print("Execution failed:")

    # check if original sim. inputs exist -- debug mode ?
    orig_sim_inputs_path = orig_sim_path + "input"
    if not os.path.exists(orig_sim_inputs_path):
        print("error: no 'input' directory in simulation path")
        sys.exit(1)

    if __debug__:
        orig_input_dirs = next(os.walk(orig_sim_inputs_path), (None, [], None))[1]
        orig_input_files = next(os.walk(orig_sim_inputs_path), (None, None, []))[2]
        print(f"{orig_sim_inputs_path = }")
        print("contents:")
        print(f"{orig_input_dirs = }")
        print(f"{orig_input_files = }")

    main(orig_sim_path, split_axis, split_ratio, scaling_ratio)

    sys.exit(0)


