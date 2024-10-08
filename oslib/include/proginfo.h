#ifndef proginfo_H
#define proginfo_H

/* C header file for ProgInfo
 * written by DefMod (Jun 13 2019) on Thu Jun 13 20:58:49 2019
 * Anon
 */

/*OSLib---efficient, type-safe, transparent, extensible,
   register-safe A P I coverage of RISC O S*/
/*Copyright � 1994 Jonathan Coxhead*/

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

#ifndef window_H
#include "window.h"
#endif

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  ProgInfo_ClassSWI
#define ProgInfo_ClassSWI                       0x82B40
#undef  XProgInfo_ClassSWI
#define XProgInfo_ClassSWI                      0xA2B40
#undef  ProgInfo_PostFilter
#define ProgInfo_PostFilter                     0x82B41
#undef  XProgInfo_PostFilter
#define XProgInfo_PostFilter                    0xA2B41
#undef  ProgInfo_PreFilter
#define ProgInfo_PreFilter                      0x82B42
#undef  XProgInfo_PreFilter
#define XProgInfo_PreFilter                     0xA2B42
#undef  ProgInfo_GetWindowID
#define ProgInfo_GetWindowID                    0x0
#undef  ProgInfo_SetVersion
#define ProgInfo_SetVersion                     0x1
#undef  ProgInfo_GetVersion
#define ProgInfo_GetVersion                     0x2
#undef  ProgInfo_SetLicenceType
#define ProgInfo_SetLicenceType                 0x3
#undef  ProgInfo_GetLicenceType
#define ProgInfo_GetLicenceType                 0x4
#undef  ProgInfo_SetTitle
#define ProgInfo_SetTitle                       0x5
#undef  ProgInfo_GetTitle
#define ProgInfo_GetTitle                       0x6

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct proginfo_object                  proginfo_object;
typedef struct proginfo_action_about_to_be_shown proginfo_action_about_to_be_shown;

/********************
 * Type definitions *
 ********************/
typedef bits proginfo_flags;

struct proginfo_object
   {  proginfo_flags flags;
      char *title;
      int title_limit;
      char *purpose;
      char *author;
      int licence_type;
      char *version;
      char *alternative_window_name;
   };

typedef toolbox_full proginfo_full;

struct proginfo_action_about_to_be_shown
   {  toolbox_position_tag tag;
      union
      {  proginfo_full full;
         os_coord top_left;
      }
      position;
   };

/************************
 * Constant definitions *
 ************************/
#define class_PROG_INFO                         ((toolbox_class) 0x82B40u)
#define proginfo_GENERATE_ABOUT_TO_BE_SHOWN     ((proginfo_flags) 0x1u)
#define proginfo_GENERATE_DIALOGUE_COMPLETED    ((proginfo_flags) 0x2u)
#define proginfo_INCLUDE_LICENCE_TYPE           ((proginfo_flags) 0x4u)
#define proginfo_NAME                           ((toolbox_c) 0x82B400u)
#define proginfo_PURPOSE                        ((toolbox_c) 0x82B401u)
#define proginfo_AUTHOR                         ((toolbox_c) 0x82B402u)
#define proginfo_LICENCE_TYPE                   ((toolbox_c) 0x82B403u)
#define proginfo_VERSION                        ((toolbox_c) 0x82B404u)
#define proginfo_NAME_LABEL                     ((toolbox_c) 0x82B405u)
#define proginfo_PURPOSE_LABEL                  ((toolbox_c) 0x82B406u)
#define proginfo_AUTHOR_LABEL                   ((toolbox_c) 0x82B407u)
#define proginfo_LICENCE_LABEL                  ((toolbox_c) 0x82B408u)
#define proginfo_VERSION_LABEL                  ((toolbox_c) 0x82B409u)
#define proginfo_LICENCE_PUBLIC_DOMAIN          0
#define proginfo_LICENCE_SINGLE_USER            1
#define proginfo_LICENCE_SINGLE_MACHINE         2
#define proginfo_LICENCE_SITE                   3
#define proginfo_LICENCE_NETWORK                4
#define proginfo_LICENCE_AUTHORITY              5
#define action_PROG_INFO_ABOUT_TO_BE_SHOWN      0x82B40u
#define action_PROG_INFO_DIALOGUE_COMPLETED     0x82B41u
#define error_PROG_INFO_TASKS_ACTIVE            0x80B400u
#define error_PROG_INFO_ALLOC_FAILED            0x80B401u
#define error_PROG_INFO_SHORT_BUFFER            0x80B402u
#define error_PROG_INFO_NO_SUCH_TASK            0x80B411u
#define error_PROG_INFO_NO_SUCH_METHOD          0x80B412u
#define error_PROG_INFO_NO_SUCH_MISC_OP_METHOD  0x80B413u

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      proginfo_get_window_id()
 *
 * Description:   Calls reason code 0 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *
 * Output:        window - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Before entry, R2 = 0x0.
 */

extern os_error *xproginfo_get_window_id (bits flags,
      toolbox_o prog_info,
      toolbox_o *window);
extern toolbox_o proginfo_get_window_id (bits flags,
      toolbox_o prog_info);

/* ------------------------------------------------------------------------
 * Function:      proginfo_set_version()
 *
 * Description:   Calls reason code 1 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *                version - value of R3 on entry
 *
 * Other notes:   Before entry, R2 = 0x1.
 */

extern os_error *xproginfo_set_version (bits flags,
      toolbox_o prog_info,
      char const *version);
extern void proginfo_set_version (bits flags,
      toolbox_o prog_info,
      char const *version);

/* ------------------------------------------------------------------------
 * Function:      proginfo_get_version()
 *
 * Description:   Calls reason code 2 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *                buffer - value of R3 on entry
 *                size - value of R4 on entry
 *
 * Output:        used - value of R4 on exit (X version only)
 *
 * Returns:       R4 (non-X version only)
 *
 * Other notes:   Before entry, R2 = 0x2.
 */

extern os_error *xproginfo_get_version (bits flags,
      toolbox_o prog_info,
      char *buffer,
      int size,
      int *used);
extern int proginfo_get_version (bits flags,
      toolbox_o prog_info,
      char *buffer,
      int size);

/* ------------------------------------------------------------------------
 * Function:      proginfo_set_licence_type()
 *
 * Description:   Calls reason code 3 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *                licence_type - value of R3 on entry
 *
 * Other notes:   Before entry, R2 = 0x3.
 */

extern os_error *xproginfo_set_licence_type (bits flags,
      toolbox_o prog_info,
      int licence_type);
extern void proginfo_set_licence_type (bits flags,
      toolbox_o prog_info,
      int licence_type);

/* ------------------------------------------------------------------------
 * Function:      proginfo_get_licence_type()
 *
 * Description:   Calls reason code 4 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *
 * Output:        licence_type - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Before entry, R2 = 0x4.
 */

extern os_error *xproginfo_get_licence_type (bits flags,
      toolbox_o prog_info,
      int *licence_type);
extern int proginfo_get_licence_type (bits flags,
      toolbox_o prog_info);

/* ------------------------------------------------------------------------
 * Function:      proginfo_set_title()
 *
 * Description:   Calls reason code 5 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *                title - value of R3 on entry
 *
 * Other notes:   Before entry, R2 = 0x5.
 */

extern os_error *xproginfo_set_title (bits flags,
      toolbox_o prog_info,
      char const *title);
extern void proginfo_set_title (bits flags,
      toolbox_o prog_info,
      char const *title);

/* ------------------------------------------------------------------------
 * Function:      proginfo_get_title()
 *
 * Description:   Calls reason code 6 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                prog_info - value of R1 on entry
 *                buffer - value of R3 on entry
 *                size - value of R4 on entry
 *
 * Output:        used - value of R4 on exit (X version only)
 *
 * Returns:       R4 (non-X version only)
 *
 * Other notes:   Before entry, R2 = 0x6.
 */

extern os_error *xproginfo_get_title (bits flags,
      toolbox_o prog_info,
      char *buffer,
      int size,
      int *used);
extern int proginfo_get_title (bits flags,
      toolbox_o prog_info,
      char *buffer,
      int size);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
