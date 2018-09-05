#!/usr/bin/env bash

python $HOME/slivka-bio/binaries/globplot/GlobPlot.py $* > output.txt
python $HOME/slivka-bio/scripts/parser.py globplot --input output.txt --annot globplot.jvannot --feat globplot.jvfeat
