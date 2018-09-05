#!/usr/bin/env bash

java -jar $HOME/slivka-bio/binaries/compbio-conservation-1.1.jar $*
for arg in $*; do
    if [[ ${arg} == -o=* ]]; then
        outputFile=${arg:3}
        break
    fi
done
python $HOME/slivka-bio/scripts/parser.py aacon --input ${outputFile} --annot aacon.jvannot
