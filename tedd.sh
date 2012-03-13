#!/bin/bash

SKIP=`awk '/^__BEGIN_GZIP__/ { print NR +1; exit 0; }' 	$0`
tail -n +$SKIP $0 | gzip -dc | tar x

sudo python scripts/install.py

exit 0;

__BEGIN_GZIP__
