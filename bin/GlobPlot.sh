#!/usr/bin/env bash

python $SLIVKA_HOME/bin/globplot/GlobPlot.py $* > output.txt
python $SLIVKA_HOME/scripts/parser.py globplot --input output.txt --annot globplot.jvannot --feat globplot.jvfeat
