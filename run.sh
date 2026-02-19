#!/bin/sh

PWD=$(pwd)

if [ $# -ne  ]; then
    echo "not enough arguments"
    exit 1
fi

MODE=$1
if [ $MODE != "vertical" ] && [ $MODE != "horizontal" ]; then
    echo "$MODE unsupported."
    exit 2
fi

GEOJSON=$2
echo $GEOJSON

HIRES_TIFF=$3
echo $HIRES_TIFF

for d in source_terms_amp_106_synthetic_chevron_5m_to_1m_0*; do ./batch_split_geotiff_N_S.sh parts_source_terms_amp_106_synthetic_chevron_5m_to_1m_030min; done
python3 -O main.py synthetic_chevron_5m_full_poi/output/output=POI_water_depth_with_timeserie_scaled_measure_POI_on_water_depth_with_timeserie/1970-01-01T01-00-00Z.geojson synthetic_chevron_5m_full_poi/input/topography/0.tif synthetic_chevron_1m_full_poi/input/topography/0.tif && mkdir -p source_terms_amp_106_synthetic_chevron_5m_to_1m_030min && mv *.tif source_terms_amp_106_synthetic_chevron_5m_to_1m_030min
LORES_TIFF=synthetic_chevron_5m_full_poi/input/topography/0.tif
HIRES_TIFF=synthetic_chevron_1m_full_poi/input/topography/0.tif
LORES_GEOJSON=synthetic_chevron_5m_full_poi/output/output\=POI_water_depth_with_timeserie_scaled_measure_POI_on_water_depth_with_timeserie/1970-01-01T01-00-00Z.geojson
#python -O main.py $LORES_GEOJSON $LORES_TIFF $HIRES_TIFF
for d in parts_source_terms_amp_106_synthetic_chevron_5m_to_1m_0*; do cp -r synthetic_chevron_1m_high_part/ hi_parts_source_terms_amp_106_synthetic_chevron_5m_to_1m_030min ; cp -r parts_source_terms_amp_106_synthetic_chevron_5m_to_1m_030min/high/*/*.tif hi_parts_source_terms_amp_106_synthetic_chevron_5m_to_1m_030min/input/rains ; done
for d in minimalist_synthetic_chevron_1m_full_poi/input/*/; do for f in minimalist_synthetic_chevron_1m_full_poi/input/topography//*; do ../downscale_geotiff.sh minimalist_synthetic_chevron_1m_full_poi/input/topography//0.tif; done; done
