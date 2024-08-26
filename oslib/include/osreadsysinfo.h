#ifndef osreadsysinfo_H
#define osreadsysinfo_H

/* C header file for OSReadSysInfo
 * written by DefMod (Jun 13 2019) on Thu Jun 13 20:59:07 2019
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

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  OS_ReadSysInfo
#define OS_ReadSysInfo                          0x58
#undef  XOS_ReadSysInfo
#define XOS_ReadSysInfo                         0x20058
#undef  OSReadSysInfo_ScreenSize
#define OSReadSysInfo_ScreenSize                0x0
#undef  OSReadSysInfo_Mode
#define OSReadSysInfo_Mode                      0x1
#undef  OSReadSysInfo_MachineId
#define OSReadSysInfo_MachineId                 0x2
#undef  OSReadSysInfo_71XFeatures
#define OSReadSysInfo_71XFeatures               0x3

/********************
 * Type definitions *
 ********************/
typedef bits osreadsysinfo_flags0;

typedef bits osreadsysinfo_flags1;

typedef bits osreadsysinfo_flags2;

/************************
 * Constant definitions *
 ************************/
#define osreadsysinfo_SPECIAL_FUNCTION          ((osreadsysinfo_flags0) 0xFFu)
#define osreadsysinfo_SPECIAL_FUNCTION_SHIFT    0
#define osreadsysinfo_SPECIAL_FUNCTION_NONE     ((osreadsysinfo_flags0) 0x0u)
#define osreadsysinfo_SPECIAL_FUNCTION_IOEB     ((osreadsysinfo_flags0) 0x1u)
#define osreadsysinfo_IO_CONTROL                ((osreadsysinfo_flags0) 0xFF00u)
#define osreadsysinfo_IO_CONTROL_SHIFT          8
#define osreadsysinfo_IO_CONTROL_IOC            ((osreadsysinfo_flags0) 0x0u)
#define osreadsysinfo_IO_CONTROL_IOMD           ((osreadsysinfo_flags0) 0x1u)
#define osreadsysinfo_MEMORY_CONTROL            ((osreadsysinfo_flags0) 0xFF0000u)
#define osreadsysinfo_MEMORY_CONTROL_SHIFT      16
#define osreadsysinfo_MEMORY_CONTROL_MEMC1      ((osreadsysinfo_flags0) 0x0u)
#define osreadsysinfo_MEMORY_CONTROL_IOMD       ((osreadsysinfo_flags0) 0x1u)
#define osreadsysinfo_VIDEO_CONTROL             ((osreadsysinfo_flags0) 0xFF000000u)
#define osreadsysinfo_VIDEO_CONTROL_SHIFT       24
#define osreadsysinfo_VIDEO_CONTROL_VIDC_1A     ((osreadsysinfo_flags0) 0x0u)
#define osreadsysinfo_VIDEO_CONTROL_VIDC20      ((osreadsysinfo_flags0) 0x1u)
#define osreadsysinfo_IO                        ((osreadsysinfo_flags1) 0xFFu)
#define osreadsysinfo_IO_SHIFT                  0
#define osreadsysinfo_IO_NONE                   ((osreadsysinfo_flags1) 0x0u)
#define osreadsysinfo_IO82C710                  ((osreadsysinfo_flags1) 0x1u)
#define osreadsysinfo_LCD_CONTROL               ((osreadsysinfo_flags2) 0xFFu)
#define osreadsysinfo_LCD_CONTROL_SHIFT         0
#define osreadsysinfo_LCD_CONTROL_NONE          ((osreadsysinfo_flags2) 0x0u)
#define osreadsysinfo_LCD_CONTROL_TYPE1         ((osreadsysinfo_flags2) 0x1u)

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      osreadsysinfo_screen_size()
 *
 * Description:   Reads the configured screen size
 *
 * Output:        screen_size - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0x58 with R0 = 0x0.
 */

extern os_error *xosreadsysinfo_screen_size (int *screen_size);
extern int osreadsysinfo_screen_size (void);

/* ------------------------------------------------------------------------
 * Function:      osreadsysinfo_mode()
 *
 * Description:   Reads the configured Mode/WimpMode, MonitorType and Sync
 *
 * Output:        mode - value of R0 on exit (X version only)
 *                monitor_type - value of R1 on exit
 *                sync - value of R2 on exit
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0x58 with R0 = 0x1.
 */

extern os_error *xosreadsysinfo_mode (os_mode *mode,
      int *monitor_type,
      int *sync);
extern os_mode osreadsysinfo_mode (int *monitor_type,
      int *sync);

/* ------------------------------------------------------------------------
 * Function:      osreadsysinfo_machine_id()
 *
 * Description:   Reads the presence of various chips and unique machine id
 *
 * Output:        config0 - value of R0 on exit
 *                config1 - value of R1 on exit
 *                config2 - value of R2 on exit
 *                id_lo - value of R3 on exit
 *                id_hi - value of R4 on exit
 *
 * Other notes:   Calls SWI 0x58 with R0 = 0x2.
 */

extern os_error *xosreadsysinfo_machine_id (osreadsysinfo_flags0 *config0,
      osreadsysinfo_flags1 *config1,
      osreadsysinfo_flags2 *config2,
      bits *id_lo,
      bits *id_hi);
extern void osreadsysinfo_machine_id (osreadsysinfo_flags0 *config0,
      osreadsysinfo_flags1 *config1,
      osreadsysinfo_flags2 *config2,
      bits *id_lo,
      bits *id_hi);

/* ------------------------------------------------------------------------
 * Function:      osreadsysinfo_71x_features()
 *
 * Description:   Reads features mask for 82C710 chip family
 *
 * Output:        features - value of R0 on exit
 *                features_extended0 - value of R1 on exit
 *                features_extended1 - value of R2 on exit
 *                features_extended2 - value of R3 on exit
 *                features_extended3 - value of R4 on exit
 *
 * Other notes:   Calls SWI 0x58 with R0 = 0x3.
 */

extern os_error *xosreadsysinfo_71x_features (bits *features,
      bits *features_extended0,
      bits *features_extended1,
      bits *features_extended2,
      bits *features_extended3);
extern void osreadsysinfo_71x_features (bits *features,
      bits *features_extended0,
      bits *features_extended1,
      bits *features_extended2,
      bits *features_extended3);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
