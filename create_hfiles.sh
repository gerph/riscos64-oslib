#!/bin/bash
##
# Create all the .h files in the include directory

set -e

if [[ "$(uname -s)" == 'Darwin' ]] ; then
    echo "This won't work on Darwin/BSD systems due to the difference in behaviour for 'i' in sed" >&2
    exit 1
fi

for i in oslib/include/*.h oslib/Macros/header oslib/Types/header ; do
    name=$(basename "$i")
    if [[ "$i" == 'oslib/Macros/header' ]] ; then
        name="macros.h"
    elif [[ "$i" == 'oslib/Types/header' ]] ; then
        name="types.h"
    fi
    env LC_ALL=C sed -E -e 's/^#ifdef  *__swi/#if defined(__swi) || defined(__riscos64)/' \
                        -e 's/([ (])int /\1int32_t /' \
                        -e 's/unsigned int32_t/uint32_t/' \
                        -e 's/typedef int32_t *bool;/#include <stdbool.h>/' \
                        -e '3i #include <stdint.h>' \
                        < "$i" \
                        > "include/$name"
done
