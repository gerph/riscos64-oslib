#ifndef types_H
#define types_H

/* C generic header file
 * written by Acorn Computers Ltd on 7th February 1995
 * Copyright � Acorn Computers Ltd, 1995
 */

/********************
 * Type definitions *
 ********************/
typedef unsigned int                            bits, bytes;
typedef int                                     bool;
typedef unsigned char                           byte;

/************************
 * Constant definitions *
 ************************/
#ifndef NULL
#define NULL                                    ((void *) 0)
#endif
#ifndef FALSE
#define FALSE                                   ((bool) 0)
#endif
#ifndef TRUE
#define TRUE                                    ((bool) 1)
#endif
#ifndef NONE
#define NONE                                    0u
#endif
#ifndef ALL
#define ALL                                     (~0u)
#endif
#ifndef SKIP
#define SKIP                                    0
#endif
#ifndef _V
#define _V                                      0x10000000u
#endif
#ifndef _C
#define _C                                      0x20000000u
#endif
#ifndef _Z
#define _Z                                      0x40000000u
#endif
#ifndef _N
#define _N                                      0x80000000u
#endif
#ifndef ERROR
#define ERROR                                   (-2)
#endif
#ifndef UNKNOWN
#define UNKNOWN                                 1
#endif

/*********************
 * Macro definitions *
 *********************/

/*Macros that "change the language"*/
#define AS    .
#define ASREF ->
#define _     ,
#ifdef  __swi
#undef  __swi
#define __swi(x) extern
#endif

/*Macros that suppress compiler warnings*/
#define NOT_USED(x) {x = x;}
#define UNSET(x) {(void) &x;}

#endif
