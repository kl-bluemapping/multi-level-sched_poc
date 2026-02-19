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
                -dstnodata -999.0 \
                -tr 15.0 15.0 \
                -r near \
                -te 634091.0 6840006.0 652640.0 6847857.0 \
                -te_srs EPSG:2154 \
                -ot Float32 \
                -of GTiff \
                $SRCFILE \
                $DESTFILE
}
