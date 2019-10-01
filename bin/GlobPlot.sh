#!/usr/bin/env bash

python $SLIVKA_HOME/bin/globplot/GlobPlot.py $* > output.txt
returncode=$?
if [ $returncode -ne 0 ]; then
    exit $returncode
fi
python $SLIVKA_HOME/scripts/jalview_parser.py globplot --input output.txt --annot globplot.jvannot --feat globplot.jvfeat
