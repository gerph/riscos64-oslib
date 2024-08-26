#ifndef help_H
#define help_H

/* C header file for Help
 * written by DefMod (Jun 13 2019) on Thu Jun 13 20:58:57 2019
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

#ifndef os_H
#include "os.h"
#endif

#ifndef wimp_H
#include "wimp.h"
#endif

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct help_message_request             help_message_request;
typedef struct help_message_reply               help_message_reply;

/********************
 * Type definitions *
 ********************/
/* ------------------------------------------------------------------------
 * Type:          help_message_request
 *
 * Description:   message type to request help from an application
 *
 * Fields:        pos - mouse coordinates
 *                buttons - mouse button state
 *                w - window handle
 *                i - icon handle
 */

struct help_message_request
   {  os_coord pos;
      wimp_mouse_state buttons;
      wimp_w w;
      wimp_i i;
   };

/* ------------------------------------------------------------------------
 * Type:          help_message_reply
 *
 * Description:   message type to reply with help text
 *
 * Fields:        reply - help message, 0-terminated
 */

struct help_message_reply
   {  char reply [236];
   };

/************************
 * Constant definitions *
 ************************/
#define message_HELP_REQUEST                    0x502u
#define message_HELP_REPLY                      0x503u

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
