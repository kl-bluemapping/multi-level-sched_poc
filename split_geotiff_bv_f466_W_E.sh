#!/bin/sh

PWD=$(pwd)
SRCFILE=$1

SRCFILENAME=$(basename $SRCFILE)
SRCDIRNAME=$(basename $(dirname $SRCFILE))

DESTDIREAST="$PWD/east/$SRCDIRNAME"
mkdir -p $DESTDIREAST
DESTFILEEAST="$DESTDIREAST/$SRCFILENAME"

DESTDIRWEST="$PWD/west/$SRCDIRNAME"
mkdir -p $DESTDIRWEST
DESTFILEWEST="$DESTDIRWEST/$SRCFILENAME"

echo $DESTFILEEAST
echo $DESTFILEWEST

{ # west
        gdal_translate \
                -projwin 634091.0 6847857.0 643365.5 6840012.0 \
                -of GTiff \
                $SRCFILE \
                $DESTFILEWEST
}

{ # east
        gdal_translate \
                -projwin 643365.5 6847857.0 652640.0 6840012.0 \
                -of GTiff \
                $SRCFILE \
                $DESTFILEEAST
}
