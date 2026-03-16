import sys
import os
import torch

from split_geotiff import (
        split_geotiff_ratio,
        get_line_coords,
        )
from scale_geotiff import (
        scale_geotiff,
        )
from gen_poi_line import (
        create_poi_geojson,
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
        os.mkdir(copy_dir + "/" + d + "/")

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

def main(orig_sim_path, split_ratio, scaling_ratio):
    # count gpus
    gpu_count = torch.cuda.device_count()
    if __debug__:
        print(f"{gpu_count} available gpu")
        for i in range(gpu_count):
            print(f"gpu{i}:{torch.cuda.get_device_properties(i)}")

    # sub-sims. nb. -- 2 or nb. of gpus
    subsims_count = max(2, gpu_count)

    subsims_dir = create_dir(orig_sim_path, "subsims")

    # setup simulation profiles 
    sims_profiles = setup_simulations_dirs(orig_sim_path, subsims_count, subsims_dir)

    reference_sim = sims_profiles[0]
    downscaled_sim = sims_profiles[1]

    # gen. src. terms
    # setup source terms dir
    downscaled_inputs_dir = downscaled_sim.root_path
    #downscaled_inputs_dir = create_dir(orig_sim_path, "downscaled_inputs")

    # TODO: merge split & scale loops (same dir. walk pattern)
    for root, dirs, files in os.walk(reference_sim.input_path):
        for f in files:
            path_f = os.path.join(root, f)
            if is_geotiff(path_f):
                split_geotiff_ratio(split_axis, split_ratio, path_f, subsims_dir)
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

    # gen. poi line
    create_poi_geojson(
            poi_line[0],
            split_axis,
            poi_line[1],
            poi_line[2],
            poi_line[3],
            poi_line[4],
            poi_geojson
            )

    # gen. downscaled sim. ruleset
    downscaled_ruleset = downscaled_sim.input_path + "ruleset.json5"

    sys.exit(0)

    # run downscaled sim. in sub-process

    # collect downscaled results

    # gen. sub-sims rulesets

    # gen. src. terms
    # setup source terms dir
    # TODO: directly in subsims ?
    src_terms_dir = create_dir(orig_sim_path, "src_terms")

    # feed src. terms to sub-sims.

    # run sub-sims -- in parallel if gpus >= 2 ; else in seq.
    subsim_0_ruleset = sim_profiles[2].input_path + "ruleset.json5"
    subsim_1_ruleset = sim_profiles[2].input_path + "ruleset.json5"

    # collect sub-sims results

    # stitch sub-sims results to reference sim extent
    # setup outputs merging dir
    split_output_dir = create_dir(orig_sim_path, "split_output")

    return

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print('''missing parameter:
            <horiz|vert (string)>
            <split ratio (float)>
            <scaling (integer)>
            <simulation (path)>
              ''')
        sys.exit(1)

    (_,
     split_axis,
     split_ratio,
     scaling_ratio,
     orig_sim_path,
     ) = sys.argv

    if __debug__:
        print(f"{split_axis = }")
        print(f"{split_ratio = }")
        print(f"{scaling_ratio = }")
        print(f"{orig_sim_path = }")

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

    main(orig_sim_path, split_ratio, scaling_ratio)

    sys.exit(0)


#sim_entry = "test_program.py"
#sim_args = " 1.1 2.2"

#command = sim_args.split()
#command.insert(0, sim_entry)
#command.insert(0, "python3")
#
#retcode = 31
#
#try:
#    result = subprocess.run(command, capture_output=True, text=True)
#    if result.returncode == retcode:
#        print(f"subproc. returned {retcode}")
#    else:
#        print(f"subproc err. {result.returncode}")
#except OSError as e:
#    print("Execution failed:")
