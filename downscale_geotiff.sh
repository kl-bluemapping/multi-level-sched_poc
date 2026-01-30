#!/bin/sh

SRCFILE=$1
DEST=$(pwd)

SRCFILENAME=$(basename $SRCFILE)
SRCDIRNAME=$(basename $(dirname $SRCFILE))

DESTDIR=$DEST/$SRCDIRNAME
mkdir -p $DESTDIR
DESTFILE="$DESTDIR/$SRCFILENAME"

{
        gdalwarp \
                -overwrite \
                -s_srs EPSG:2154 \
                -t_srs EPSG:2154 \
                -dstnodata -9999.0 \
                -tr 5.0 5.0 \
                -r near \
                -te 1037856.0 6868608.0 1038856.0 6870608.0 \
                -te_srs EPSG:2154 \
                -ot Float32 \
                -of GTiff \
                $SRCFILE \
                $DESTFILE
}
