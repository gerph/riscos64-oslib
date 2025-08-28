# RISC OS 64 version of OSLib

## Introduction

This is a 64-bit version of OSLib. It builds the interfaces for the bulk of the
OSLib headers for RISC OS interfaces. It is built using the Python OSLib header
parser, and assembled using the GNU assembler.

## Downloading

The releases of the 64-bit version of OSLib can be found in the GitHub Release
in the side bar. The header files are a modified version of those supplied with
OSLib, replacing `int32_t`/`uint32_t` in the parameters as appropriate.

## Building

You require a POSIX system which has:

* Python
* Docker

To build, use:

    make

A library `liboslib.a` should be created, together with headers in the
`include` directory.
