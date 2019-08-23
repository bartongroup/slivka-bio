#!/usr/bin/env bash

python $HOME/slivka-bio/binaries/disembl/DisEMBL.py $* > output.txt
python $HOME/slivka-bio/scripts/parser.py disembl --input output.txt --annot disembl.jvannot --feat disembl.jvfeat