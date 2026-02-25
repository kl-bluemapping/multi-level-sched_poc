# usage

## downscaled input
downscale a geotiff to a lower res. version (fixed 1/5 atm) w/ the same spatial extent
```sh
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

