#!/bin/bash
##
# Create all the .s files in the src directory

set -e

for n in oslib/*/def/* ; do
    nb=$(basename "$n")
    # Exclude non-working files (everything seems to be working now!)
    #if [[ "$nb" = 'nothing' ]] ; then
    #    continue
    #fi
    python oslib_parser.py --oslib-dir oslib/ \
                           "$n" \
                           --create-aarch64-api "src/$nb.s"
done
