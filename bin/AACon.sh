#!/usr/bin/env bash

java -jar $SLIVKA_HOME/bin/compbio-conservation-1.1.jar $*
for arg in $*; do
    if [[ ${arg} == -o=* ]]; then
        outputFile=${arg:3}
        break
    fi
done
python $SLIVKA_HOME/scripts/parser.py aacon --input ${outputFile} --annot aacon.jvannot
