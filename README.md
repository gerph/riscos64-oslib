# RISC OS 64 version of OSLib

## Introduction

This is a 64 bit version of OSLib. It builds the interfaces for the bulk of the
OSLib headers for RISC OS interfaces. It is built using the Python OSLib header
parser, and assembled using the GNU assembler.

## Caveats

Some of the interfaces may not be correct due to calling convention errors -
in particular the flags are not processed, and if there are more than 8 input
registers the generated code will not work.

## Building

You require:

* Python
* Docker

To build, use:

    make

A library `liboslib.a` should be created, together with headers in the
`include` directory.
