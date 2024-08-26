#!/bin/bash
##
# Create all the .h files in the include directory

set -e

for i in oslib/include/*.h ; do
    env LC_ALL=C sed -E -e '/__swi[^;]*$/,/;/ s/^/\/\//' \
                        -e '/__swi.*;$/ s/^/\/\//' \
                        -e 's/([ (])int /\1int32_t /' \
                        -e 's/unsigned int32_t/uint32_t/' \
                        -e 's/typedef int32_t *bool;/#include <stdbool.h>/' \
                        -e '3i #include <stdint.h>' \
                        < "$i" \
                        > "include/$(basename "$i")"
done
