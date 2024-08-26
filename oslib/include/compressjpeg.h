#ifndef compressjpeg_H
#define compressjpeg_H

/* C header file for CompressJPEG
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

#ifndef jpeg_H
#include "jpeg.h"
#endif

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  CompressJPEG_Start
#define CompressJPEG_Start                      0x4A500
#undef  XCompressJPEG_Start
#define XCompressJPEG_Start                     0x6A500
#undef  CompressJPEG_WriteLine
#define CompressJPEG_WriteLine                  0x4A501
#undef  XCompressJPEG_WriteLine
#define XCompressJPEG_WriteLine                 0x6A501
#undef  CompressJPEG_Finish
#define CompressJPEG_Finish                     0x4A502
#undef  XCompressJPEG_Finish
#define XCompressJPEG_Finish                    0x6A502

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct compressjpeg_tag_                *compressjpeg_tag;
typedef struct compressjpeg_parameters          compressjpeg_parameters;

/********************
 * Type definitions *
 ********************/
struct compressjpeg_parameters
   {  int width;
      int height;
      int quality;
      int bytes_per_pixel;
      int xdpi;
      int ydpi;
   };

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      compressjpeg_start()
 *
 * Description:   Starts the JPEG compression process and sets up various
 *                parameters
 *
 * Input:         image - value of R0 on entry
 *                image_size - value of R1 on entry
 *                parameters - value of R2 on entry
 *                workspace - value of R3 on entry
 *                workspace_size - value of R4 on entry
 *
 * Output:        tag - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0x4A500.
 */

extern os_error *xcompressjpeg_start (jpeg_image const *image,
      int image_size,
      compressjpeg_parameters const *parameters,
      void *workspace,
      int workspace_size,
      compressjpeg_tag *tag);
extern compressjpeg_tag compressjpeg_start (jpeg_image const *image,
      int image_size,
      compressjpeg_parameters const *parameters,
      void *workspace,
      int workspace_size);

/* ------------------------------------------------------------------------
 * Function:      compressjpeg_write_line()
 *
 * Description:   Compresses one row of source pixels into the JPEG buffer
 *
 * Input:         tag - value of R0 on entry
 *                pixels - value of R1 on entry
 *
 * Other notes:   Calls SWI 0x4A501.
 */

extern os_error *xcompressjpeg_write_line (compressjpeg_tag tag,
      byte *pixels);
__swi (0x4A501) void compressjpeg_write_line (compressjpeg_tag tag,
      byte *pixels);

/* ------------------------------------------------------------------------
 * Function:      compressjpeg_finish()
 *
 * Description:   Tidies up JPEG buffer
 *
 * Input:         tag - value of R0 on entry
 *
 * Output:        image_size - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0x4A502.
 */

extern os_error *xcompressjpeg_finish (compressjpeg_tag tag,
      int *image_size);
__swi (0x4A502) int compressjpeg_finish (compressjpeg_tag tag);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
