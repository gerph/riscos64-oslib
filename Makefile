# Makefile for building bin for aarch64
#
# Code compiles with:
#
#   __riscos
#   __riscos64
#   __aarch64__
#
# Norcroft defines not set:
#   __acorn
#   __arm

TARGET ?= oslib

USE_FUNC_SIGNATURE ?= 1

CROSS_ROOT = ${shell echo $$CROSS_ROOT}

ALL_TARGETS = liboslib.a


# Remove the flags that might make code think it's compiling for linux system.
CFLAGS = -U__linux -U__linux__ -U__unix__ -U__unix -Ulinux -Uunix -U__gnu_linux__

# Add the definitions to indicate that we're compiling for RISC OS
CFLAGS += -D__riscos -D__riscos64

# Allow us to build without assuming the standard library is present
CFLAGS += -nostdlib -ffreestanding -march=armv8-a
#CFLAGS += -nostdlib -ffreestanding -march=armv8-a+nofp

# Add the exports directory to those things we'll build with
CFLAGS += -I${CLIBDIR}/riscos_headers/C -I${CLIBDIR}/riscos_headers/Lib/ -I${CLIBDIR}/riscos_headers/Lib/CLib/

# Options to allow function signatures to appear RISC OS-like
ifeq (${USE_FUNC_SIGNATURE},1)
CFLAGS += -fpatchable-function-entry=20,20
endif

# Optimisation options
CFLAGS += -O1

# Options for this build
CFLAGS += -I/ro64

# Assembler flags
AFLAGS = -march=armv8-a

# Flags for the linker
LDFLAGS = -T link.lnk -e _aif64_entry

targetted:
	make liboslib.a

all:
	make liboslib.a

shell: dockcross-linux-arm64
	./dockcross-linux-arm64 bash

dockcross-linux-arm64:
	docker run --rm dockcross/linux-arm64:latest > dockcross-linux-arm64
	chmod +x dockcross-linux-arm64

clean:
	-rm -f src/*.s src/*.o *.a

.PHONY: srcs
srcs: src/os.s
src/os.s: oslib_parser.py templates/aarch64-api.s.j2 oslib/Core/def/os
	mkdir -p src
	./create_sfiles.sh

ifeq (${CROSS_ROOT},)
# If we're outside the docker container, re-run ourselves inside the container

ifneq ($(filter-out all shell dockcross-linux-arm64 srcs clean,${MAKECMDGOALS}),)
# The command wasn't one of our invocation commands above
.PHONY: ${MAKECMDGOALS}
${MAKECMDGOALS}: dockcross-linux-arm64 srcs
	./dockcross-linux-arm64 -- bash -c "cd . && make ${MAKECMDGOALS} TARGET=${TARGET}"
else
.PHONY: ${DEFAULT_GOAL}
${DEFAULT_GOAL}: dockcross-linux-arm64 srcs
	./dockcross-linux-arm64 -- bash -c "cd . && make ${MAKECMDGOALS} TARGET=${TARGET}"
endif

${CLIBDIR}/libcrt.a:
	cd ${CLIBDIR}; make

else
# We are within the docker container

CLIBDIR = /ro64/clib


CC = aarch64-unknown-linux-gnu-gcc
AS = aarch64-unknown-linux-gnu-as
LD = aarch64-unknown-linux-gnu-ld
OBJCOPY = aarch64-unknown-linux-gnu-objcopy

SRCS = $(wildcard src/*.s)
OBJS = ${SRCS:%.s=%.o}

headers: include/os.h
include/os.h: oslib/include/os.h create_hfiles
	mkdir -p include
	./create_hfiles.sh

VPATH = src

liboslib.a: ${OBJS} headers
	aarch64-unknown-linux-gnu-ar -rc $@ ${OBJS}

%.o: %.c
	${CC} ${CFLAGS} -c -o $@ $?

%.o: %.s
	${AS} ${AFLAGS} -o $@ $?

endif
