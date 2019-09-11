#!/usr/bin/env bash

python $SLIVKA_HOME/bin/disembl/DisEMBL.py $* > output.txt
python $SLIVKA_HOME/scripts/parser.py disembl --input output.txt --annot disembl.jvannot --feat disembl.jvfeat
