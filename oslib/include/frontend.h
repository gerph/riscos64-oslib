#ifndef frontend_H
#define frontend_H

/* C header file for FrontEnd
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

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  FrontEnd_ExtendedCmdLine
#define FrontEnd_ExtendedCmdLine                0x81400
#undef  XFrontEnd_ExtendedCmdLine
#define XFrontEnd_ExtendedCmdLine               0xA1400
#undef  FrontEnd_FreeCmdLine
#define FrontEnd_FreeCmdLine                    0x81401
#undef  XFrontEnd_FreeCmdLine
#define XFrontEnd_FreeCmdLine                   0xA1401

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      frontend_extended_cmd_line()
 *
 * Description:   Calls SWI 0x81400
 */

extern os_error *xfrontend_extended_cmd_line (void);
__swi (0x81400) void frontend_extended_cmd_line (void);

/* ------------------------------------------------------------------------
 * Function:      frontend_free_cmd_line()
 *
 * Description:   Calls SWI 0x81401
 */

extern os_error *xfrontend_free_cmd_line (void);
__swi (0x81401) void frontend_free_cmd_line (void);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
