#ifndef osfind_H
#define osfind_H

/* C header file for OSFind
 * written by DefMod (Jun 13 2019) on Thu Jun 13 20:58:39 2019
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

#ifndef os_H
#include "os.h"
#endif

#ifndef fileswitch_H
#include "fileswitch.h"
#endif

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  OS_Find
#define OS_Find                                 0xD
#undef  XOS_Find
#define XOS_Find                                0x2000D
#undef  OSFind_Openin
#define OSFind_Openin                           0x40
#undef  OSFind_Openout
#define OSFind_Openout                          0x80
#undef  OSFind_Openup
#define OSFind_Openup                           0xC0
#undef  OSFind_Close
#define OSFind_Close                            0x0
#undef  FindV
#define FindV                                   0xD
#undef  UpCallFind_CreateOpenup
#define UpCallFind_CreateOpenup                 0x101
#undef  UpCallFind_Openup
#define UpCallFind_Openup                       0x102
#undef  UpCallFind_Close
#define UpCallFind_Close                        0x103

/********************
 * Type definitions *
 ********************/
typedef bits osfind_flags;

/************************
 * Constant definitions *
 ************************/
#define osfind_PATH                             ((osfind_flags) 0x1u)
#define osfind_PATH_VAR                         ((osfind_flags) 0x2u)
#define osfind_NO_PATH                          ((osfind_flags) 0x3u)
#define osfind_ERROR_IF_ABSENT                  ((osfind_flags) 0x8u)
#define osfind_ERROR_IF_DIR                     ((osfind_flags) 0x4u)

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      osfind_openin()
 *
 * Description:   Opens an existing file with read access only
 *
 * Input:         flags - value of R0 on entry
 *                file_name - value of R1 on entry
 *                path - value of R2 on entry
 *
 * Output:        file - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0xD with R0 |= 0x40.
 */

extern os_error *xosfind_openin (osfind_flags flags,
      char const *file_name,
      char const *path,
      os_f *file);
extern os_f osfind_openin (osfind_flags flags,
      char const *file_name,
      char const *path);

/* ------------------------------------------------------------------------
 * Function:      osfind_openout()
 *
 * Description:   Creates a new file with read/write access
 *
 * Input:         flags - value of R0 on entry
 *                file_name - value of R1 on entry
 *                path - value of R2 on entry
 *
 * Output:        file - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0xD with R0 |= 0x80.
 */

extern os_error *xosfind_openout (osfind_flags flags,
      char const *file_name,
      char const *path,
      os_f *file);
extern os_f osfind_openout (osfind_flags flags,
      char const *file_name,
      char const *path);

/* ------------------------------------------------------------------------
 * Function:      osfind_openup()
 *
 * Description:   Opens an existing file with read/write access
 *
 * Input:         flags - value of R0 on entry
 *                file_name - value of R1 on entry
 *                path - value of R2 on entry
 *
 * Output:        file - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0xD with R0 |= 0xC0.
 */

extern os_error *xosfind_openup (osfind_flags flags,
      char const *file_name,
      char const *path,
      os_f *file);
extern os_f osfind_openup (osfind_flags flags,
      char const *file_name,
      char const *path);

/* ------------------------------------------------------------------------
 * Function:      osfind_close()
 *
 * Description:   Closes a file or files
 *
 * Input:         file - value of R1 on entry
 *
 * Other notes:   Calls SWI 0xD with R0 = 0x0.
 */

extern os_error *xosfind_close (os_f file);
extern void osfind_close (os_f file);

/* ------------------------------------------------------------------------
 * Function:      upcallfind_create_openup()
 *
 * Description:   Warns your program that a file is being created and
 *                opened for update
 *
 * Input:         file_name - value of R1 on entry
 *                file - value of R2 on entry
 *                special - value of R6 on entry
 *                fs_info - value of R8 on entry
 *
 * Other notes:   Calls SWI 0x33 with R0 = 0x3, R9 = 0x101.
 */

extern os_error *xupcallfind_create_openup (char const *file_name,
      os_f file,
      char const *special,
      fileswitch_fs_info fs_info);
extern void upcallfind_create_openup (char const *file_name,
      os_f file,
      char const *special,
      fileswitch_fs_info fs_info);

/* ------------------------------------------------------------------------
 * Function:      upcallfind_openup()
 *
 * Description:   Warns your program that a file is being opened for update
 *
 * Input:         file_name - value of R1 on entry
 *                file - value of R2 on entry
 *                special - value of R6 on entry
 *                fs_info - value of R8 on entry
 *
 * Other notes:   Calls SWI 0x33 with R0 = 0x3, R9 = 0x102.
 */

extern os_error *xupcallfind_openup (char const *file_name,
      os_f file,
      char const *special,
      fileswitch_fs_info fs_info);
extern void upcallfind_openup (char const *file_name,
      os_f file,
      char const *special,
      fileswitch_fs_info fs_info);

/* ------------------------------------------------------------------------
 * Function:      upcallfind_close()
 *
 * Description:   Warns your program that a file is being closed
 *
 * Input:         file - value of R1 on entry
 *                fs_info - value of R8 on entry
 *
 * Other notes:   Calls SWI 0x33 with R0 = 0x3, R9 = 0x103.
 */

extern os_error *xupcallfind_close (os_f file,
      fileswitch_fs_info fs_info);
extern void upcallfind_close (os_f file,
      fileswitch_fs_info fs_info);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
