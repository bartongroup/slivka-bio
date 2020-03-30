#!/usr/bin/env bash

DisEMBL $* > output.txt
returncode=$?
if [ $returncode -ne 0 ]; then
    exit $returncode
fi
python $SLIVKA_HOME/scripts/jalview_parser.py disembl --input output.txt --annot disembl.jvannot --feat disembl.jvfeat
