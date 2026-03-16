# usage

## downscaled input
downscale a geotiff to a lower res. version (fixed 1/5 atm) w/ the same spatial extent
```sh
./downscale_geotiff.sh sim/input/topography/0.tif
```

```python
./downscale_geotiff.sh sim/input/topography/0.tif
```
## split input
split a geotiff horizontaly in the middle
```python
python3 split_geotiff.py horiz 0.5 file.geotiff
```

## source terms
generate source terms from a sim .poi geojson output, one of the sim. inputs (e.g. a DEM) & one of the target sim. input

```sh
LORES_GEOJSON=sim/output/poi/output.geojson
LORES_TIFF=low_res_sim/input/topography/0.tif
HIRES_TIFF=high_res_sim/input/topography/0.tif
```

```python
 python3 -O main.py $LORES_GEOJSON $LORES_TIFF $HIRES_TIFF
```

''' wrapper.py
compute docker entrypoint.
1. init. multi-level sim. env.
    1a. count gpus
    1b. set sims:gpu pairs
        - master sim:gpu 0
        - n split sims:gpu 1..n
    1c. set sub-sim "profiles"
        - target gpu
        - target inputs dir
        - target outpurs dir
    1d. set source terms dir
    1e. set outputs merge dir
2. create split info
    2a. get split ratio from input params
    2b. set split extent & coords from orig. inputs
    2c. gen. poi geojson following the borders
3. create master sim. files
    3a. get downscale ratio from input params.
    3b. create master sim. dirs.
    3c. downscale master sim. inputs
    3d. gen. master sim. ruleset from original ruleset w/ poi
4. create sub-sims. files
    4a. create sub-sims. dirs.
    4b. create split inputs from  orig. w/ split extent/coords
    4c. gen. sub-sims. ruleset w/ correct extents
5. run master (downscaled) sim.
    5a. spawn subprocess
    5b. @ end, collect poi res
6. gen. source terms
    6a. gen full src terms from master poi res & split extent
    6b. split src tersm files for sub-sims
7. run sub-sims
    7a. spawn subproc for ea. sub-sim
    7b. @ end, collect sub-sims res
8. gen. final output
    8a. stitch sub-sims res into orig. sim extent
    8b. mov gen. final. out. to output dir.
9. (bonus) run orig. sim.
    9a. run high-res full sim (for. ex. on master sim profile)
    9b. cmp res. vs stitched outputs
'''
