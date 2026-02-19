#!/bin/sh

PWD=$(pwd)
SRCFILE=$1

SRCFILENAME=$(basename $SRCFILE)
SRCDIRNAME=$(basename $(dirname $SRCFILE))

DESTDIRLOW="$PWD/low/$SRCDIRNAME"
mkdir -p $DESTDIRLOW
DESTFILELOW="$DESTDIRLOW/$SRCFILENAME"

DESTDIRHIGH="$PWD/high/$SRCDIRNAME"
mkdir -p $DESTDIRHIGH
DESTFILEHIGH="$DESTDIRHIGH/$SRCFILENAME"

echo $DESTFILELOW
echo $DESTFILEHIGH

{ # high
        gdal_translate \
                -projwin 1037856.0 6870608.0 1038856.0 6869608.0 \
                -of GTiff \
                $SRCFILE \
                $DESTFILEHIGH
}

{ # low
        gdal_translate \
                -projwin 1037856.0 6869608.0 1038856.0 6868608.0 \
                -of GTiff \
                $SRCFILE \
                $DESTFILELOW
}
