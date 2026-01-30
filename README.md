# usage

## downscaled input
downscale a geotiff to a lower res. version (fixed 1/5 atm) w/ the same spatial extent
```sh
./downscale_geotiff.sh sim/input/topography/0.tif
```

## split input
split a geotiff in 2 part north/south in the middle through their extent
```sh
./split_geotiff_N_W.sh sim/input/catchment/0.tif
```

## source terms
generate source terms from a sim .poi geojson output, one of the sim. inputs (e.g. a DEM) & one of the target sim. input
```python
python3 extract_geojson_data.py example_output.geojson example_low_res_dem.tif example_hi_res_dem.tif
``
