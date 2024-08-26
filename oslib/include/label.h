#ifndef label_H
#define label_H

/* C header file for Label
 * written by DefMod (Jun 13 2019) on Thu Jun 13 20:58:49 2019
 * Anon
 */

/*OSLib---efficient, type-safe, transparent, extensible,
   register-safe A P I coverage of RISC O S*/
/*Copyright © 1994 Jonathan Coxhead*/

/*
      OSLib is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 1, or (at your option)
   any later version.

      OSLib is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

      You should have received a copy of the GNU General Public License
   along with this programme; if not, write to the Free Software
   Foundation, Inc, 675 Mass Ave, Cambridge, MA 02139, U S A.
*/

#ifndef types_H
#include "types.h"
#endif

#ifndef toolbox_H
#include "toolbox.h"
#endif

#ifndef gadget_H
#include "gadget.h"
#endif

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct label_object                     label_object;

/********************
 * Type definitions *
 ********************/
struct label_object
   {  char *label;
   };

/************************
 * Constant definitions *
 ************************/
#define class_LABEL                             ((toolbox_class) 0x140u)
#define label_NO_BOX                            0x1u
#define label_RJUSTIFIED                        0x2u
#define label_HCENTRED                          0x4u

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
