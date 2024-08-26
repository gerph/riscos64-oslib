#ifndef filter_H
#define filter_H

/* C header file for Filter
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

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  Filter_RegisterPreFilter
#define Filter_RegisterPreFilter                0x42640
#undef  XFilter_RegisterPreFilter
#define XFilter_RegisterPreFilter               0x62640
#undef  Filter_RegisterPostFilter
#define Filter_RegisterPostFilter               0x42641
#undef  XFilter_RegisterPostFilter
#define XFilter_RegisterPostFilter              0x62641
#undef  Filter_DeRegisterPreFilter
#define Filter_DeRegisterPreFilter              0x42642
#undef  XFilter_DeRegisterPreFilter
#define XFilter_DeRegisterPreFilter             0x62642
#undef  Filter_DeRegisterPostFilter
#define Filter_DeRegisterPostFilter             0x42643
#undef  XFilter_DeRegisterPostFilter
#define XFilter_DeRegisterPostFilter            0x62643
#undef  Service_FilterManagerInstalled
#define Service_FilterManagerInstalled          0x87
#undef  Service_FilterManagerDying
#define Service_FilterManagerDying              0x88

/************************
 * Constant definitions *
 ************************/
#define filter_NAME_LIMIT                       40
#define filter_ALL_TASKS                        ((wimp_t) 0x0u)

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      filter_register_pre_filter()
 *
 * Description:   Adds a new pre-filter to the list of pre-filters
 *
 * Input:         filter_name - value of R0 on entry
 *                code - value of R1 on entry
 *                handle - value of R2 on entry
 *                task - value of R3 on entry
 *
 * Other notes:   Calls SWI 0x42640.
 */

extern os_error *xfilter_register_pre_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task);
__swi (0x42640) void filter_register_pre_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task);

/* ------------------------------------------------------------------------
 * Function:      filter_register_post_filter()
 *
 * Description:   Adds a new post-filter to the list of post-filters
 *
 * Input:         filter_name - value of R0 on entry
 *                code - value of R1 on entry
 *                handle - value of R2 on entry
 *                task - value of R3 on entry
 *                mask - value of R4 on entry
 *
 * Other notes:   Calls SWI 0x42641.
 */

extern os_error *xfilter_register_post_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task,
      wimp_poll_flags mask);
extern void filter_register_post_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task,
      wimp_poll_flags mask);

/* ------------------------------------------------------------------------
 * Function:      filter_de_register_pre_filter()
 *
 * Description:   Removes a pre-filter from the list of pre-filters
 *
 * Input:         filter_name - value of R0 on entry
 *                code - value of R1 on entry
 *                handle - value of R2 on entry
 *                task - value of R3 on entry
 *
 * Other notes:   Calls SWI 0x42642.
 */

extern os_error *xfilter_de_register_pre_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task);
__swi (0x42642) void filter_de_register_pre_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task);

/* ------------------------------------------------------------------------
 * Function:      filter_de_register_post_filter()
 *
 * Description:   Removes a post-filter from the list of post-filters
 *
 * Input:         filter_name - value of R0 on entry
 *                code - value of R1 on entry
 *                handle - value of R2 on entry
 *                task - value of R3 on entry
 *                mask - value of R4 on entry
 *
 * Other notes:   Calls SWI 0x42643.
 */

extern os_error *xfilter_de_register_post_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task,
      wimp_poll_flags mask);
extern void filter_de_register_post_filter (char const *filter_name,
      void const *code,
      byte *handle,
      wimp_t task,
      wimp_poll_flags mask);

/* ------------------------------------------------------------------------
 * Function:      service_filter_manager_installed()
 *
 * Description:   Filter Manager starting up
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x87.
 */

extern os_error *xservice_filter_manager_installed (void);
extern void service_filter_manager_installed (void);

/* ------------------------------------------------------------------------
 * Function:      service_filter_manager_dying()
 *
 * Description:   Filter Manager dying
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x88.
 */

extern os_error *xservice_filter_manager_dying (void);
extern void service_filter_manager_dying (void);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
