#ifndef labelledbox_H
#define labelledbox_H

/* C header file for LabelledBox
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
typedef struct labelledbox_object               labelledbox_object;

/********************
 * Type definitions *
 ********************/
struct labelledbox_object
   {  char *label;
   };

/************************
 * Constant definitions *
 ************************/
#define class_LABELLED_BOX                      ((toolbox_class) 0x100u)
#define labelledbox_SPRITE                      ((gadget_flags) 0x1u)
#define labelledbox_SPRITE_IS_FILLED            ((gadget_flags) 0x2u)

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
