#ifndef keyboardshortcut_H
#define keyboardshortcut_H

/* C header file for KeyboardShortcut
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

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct keyboardshortcut_object          keyboardshortcut_object;
typedef struct keyboardshortcut_list            keyboardshortcut_list;
typedef struct keyboardshortcut_list_base       keyboardshortcut_list_base;

/********************
 * Type definitions *
 ********************/
typedef bits keyboardshortcut_flags;

struct keyboardshortcut_object
   {  keyboardshortcut_flags flags;
      int c;
      bits action;
      char *name;
   };

struct keyboardshortcut_list
   {  keyboardshortcut_object objects [UNKNOWN];
   };

#define keyboardshortcut_LIST(N) \
   struct \
      {  keyboardshortcut_object objects [N]; \
      }

#define keyboardshortcut_SIZEOF_LIST(N) \
   ((N)*sizeof ((keyboardshortcut_list *) NULL)->objects)

/************************
 * Constant definitions *
 ************************/
#define keyboardshortcut_SHOW_AS_MENU           ((keyboardshortcut_flags) 0x1u)

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
