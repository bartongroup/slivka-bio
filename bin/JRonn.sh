#!/usr/bin/env bash

java -jar $SLIVKA_HOME/bin/bj3.0.4p-jronn.jar $*
returncode=$?
if [ $returncode -ne 0 ]; then
    exit $returncode
fi
for arg in $*; do
    if [[ ${arg} == -o=* ]]; then
        outputFile=${arg:3}
        break
    fi
done
python $SLIVKA_HOME/scripts/jalview_parser.py jronn --input ${outputFile} --annot jronn.jvannot
