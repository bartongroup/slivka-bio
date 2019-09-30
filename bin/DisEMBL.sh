#!/usr/bin/env bash

python $SLIVKA_HOME/bin/disembl/DisEMBL.py $* > output.txt
returncode=$?
if [ $returncode -ne 0 ]; then
    exit $returncode
fi
python $SLIVKA_HOME/scripts/parser.py disembl --input output.txt --annot disembl.jvannot --feat disembl.jvfeat
