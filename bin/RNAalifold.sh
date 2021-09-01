#!/usr/bin/env bash

set -e
RNAalifold "$@" | tee output.txt
PARSER="python $SLIVKA_HOME/scripts/jalview_parser.py rnaalifold"
if [ -f alifold.out ]; then
  $PARSER -a alifold.out output.txt rnaalifold.jvannot
else
  $PARSER output.txt rnaalifold.jvannot
fi
