#!/bin/bash

TRGTDIR=$1
RUNSCRIPT=sum_tiff_content.py
VAR=0
RES=0
TIME1=0
NAME1=""
FILE1=""

for tif in `ls $TRGTDIR/*.tif | sort -V`; do
        FILE2=$FILE1
        NAME2=$NAME1
        TIME2=$TIME1
        FILE1=$tif
        NAME1=$(basename $FILE1)
        TIME1=${NAME1%%.*}
        DIFF=$((TIME1 - TIME2))
        echo "curr. tif $FILE2"
        echo "over $TIME1 - $TIME2 = $DIFF s"
        VAR=$(python -O $RUNSCRIPT $FILE2)
        echo "compounded sum = $VAR"
        RES=$(python -c "print($RES+$VAR)")
done
echo "res = $RES"

