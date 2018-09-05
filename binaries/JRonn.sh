#!/usr/bin/env bash

java -jar $HOME/slivka-bio/binaries/bj3.0.4p-jronn.jar $*
for arg in $*; do
    if [[ ${arg} == -o=* ]]; then
        outputFile=${arg:3}
        break
    fi
done
python $HOME/slivka-bio/scripts/parser.py jronn --input ${outputFile} --annot jronn.jvannot