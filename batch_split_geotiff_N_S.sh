#!/bin/sh

CURRDIR=$(pwd)
RUNSCRIPT=split_geotiff_N_S.sh

TRGTDIR=$1

DESTDIR="${CURRDIR}/parts_$(basename $TRGTDIR)"
mkdir -p $DESTDIR

for file in $TRGTDIR/*; do
        echo "Split geotiff: $(basename $file)"
        $CURRDIR/$RUNSCRIPT $file
done

mv $CURRDIR/high/ $DESTDIR
mv $CURRDIR/low/ $DESTDIR

