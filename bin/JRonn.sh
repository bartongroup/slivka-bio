#!/usr/bin/env bash

java -jar $SLIVKA_HOME/bin/bj3.0.4p-jronn.jar $*
for arg in $*; do
    if [[ ${arg} == -o=* ]]; then
        outputFile=${arg:3}
        break
    fi
done
python $SLIVKA_HOME/scripts/parser.py jronn --input ${outputFile} --annot jronn.jvannot
