#ifndef jpeg_H
#define jpeg_H

/* C header file for JPEG
 * written by DefMod (Jun 13 2019) on Thu Jun 13 20:58:57 2019
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

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  JPEG_Info
#define JPEG_Info                               0x49980
#undef  XJPEG_Info
#define XJPEG_Info                              0x69980
#undef  JPEGInfo_Dimensions
#define JPEGInfo_Dimensions                     0x1
#undef  JPEG_FileInfo
#define JPEG_FileInfo                           0x49981
#undef  XJPEG_FileInfo
#define XJPEG_FileInfo                          0x69981
#undef  JPEGFileInfo_Dimensions
#define JPEGFileInfo_Dimensions                 0x1
#undef  JPEG_PlotScaled
#define JPEG_PlotScaled                         0x49982
#undef  XJPEG_PlotScaled
#define XJPEG_PlotScaled                        0x69982
#undef  JPEG_PlotScaledColourMap
#define JPEG_PlotScaledColourMap                0x49982
#undef  XJPEG_PlotScaledColourMap
#define XJPEG_PlotScaledColourMap               0x69982
#undef  JPEG_PlotFileScaled
#define JPEG_PlotFileScaled                     0x49983
#undef  XJPEG_PlotFileScaled
#define XJPEG_PlotFileScaled                    0x69983
#undef  JPEG_PlotFileScaledColourMap
#define JPEG_PlotFileScaledColourMap            0x49983
#undef  XJPEG_PlotFileScaledColourMap
#define XJPEG_PlotFileScaledColourMap           0x69983
#undef  JPEG_PlotTransformed
#define JPEG_PlotTransformed                    0x49984
#undef  XJPEG_PlotTransformed
#define XJPEG_PlotTransformed                   0x69984
#undef  JPEG_PlotTransformedColourMap
#define JPEG_PlotTransformedColourMap           0x49984
#undef  XJPEG_PlotTransformedColourMap
#define XJPEG_PlotTransformedColourMap          0x69984
#undef  JPEG_PlotFileTransformed
#define JPEG_PlotFileTransformed                0x49985
#undef  XJPEG_PlotFileTransformed
#define XJPEG_PlotFileTransformed               0x69985
#undef  JPEG_PlotFileTransformedColourMap
#define JPEG_PlotFileTransformedColourMap       0x49985
#undef  XJPEG_PlotFileTransformedColourMap
#define XJPEG_PlotFileTransformedColourMap      0x69985
#undef  JPEG_PDriverIntercept
#define JPEG_PDriverIntercept                   0x49986
#undef  XJPEG_PDriverIntercept
#define XJPEG_PDriverIntercept                  0x69986

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct jpeg_image                       jpeg_image;
typedef struct jpeg_image_base                  jpeg_image_base;

/********************
 * Type definitions *
 ********************/
typedef bits jpeg_info_flags;

typedef bits jpeg_scale_flags;

typedef bits jpeg_transform_flags;

struct jpeg_image
   {  byte i [UNKNOWN];
   };

#define jpeg_IMAGE(N) \
   struct \
      {  byte i [N]; \
      }

#define jpeg_SIZEOF_IMAGE(N) \
   ((N)*sizeof ((jpeg_image *) NULL)->i)

/************************
 * Constant definitions *
 ************************/
#define jpeg_INFO_MONOCHROME                    ((jpeg_info_flags) 0x1u)
#define jpeg_INFO_NO_TRFM                       ((jpeg_info_flags) 0x2u)
#define jpeg_INFO_DPI_UNKNOWN                   ((jpeg_info_flags) 0x4u)
#define jpeg_SCALE_DITHERED                     ((jpeg_scale_flags) 0x1u)
#define jpeg_SCALE_ERROR_DIFFUSED               ((jpeg_scale_flags) 0x2u)
#define jpeg_SCALE_COLOUR_MAP                   ((jpeg_scale_flags) 0x8u)
#define jpeg_DESTINATION_COORDS                 ((jpeg_transform_flags) 0x1u)
#define jpeg_TRANSFORM_DITHERED                 ((jpeg_transform_flags) 0x2u)
#define jpeg_TRANSFORM_ERROR_DIFFUSED           ((jpeg_transform_flags) 0x4u)
#define jpeg_TRANSFORM_COLOUR_MAP               ((jpeg_transform_flags) 0x10u)
#define jpeg_FILE_TYPE                          0xC85u

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      jpeginfo_dimensions()
 *
 * Description:   Returns the dimensions of a JPEG image in memory
 *
 * Input:         image - value of R1 on entry
 *                size - value of R2 on entry
 *
 * Output:        info_flags - value of R0 on exit (X version only)
 *                width - value of R2 on exit
 *                height - value of R3 on exit
 *                xdpi - value of R4 on exit
 *                ydpi - value of R5 on exit
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0x49980 with R0 = 0x1.
 */

extern os_error *xjpeginfo_dimensions (jpeg_image const *image,
      int size,
      jpeg_info_flags *info_flags,
      int *width,
      int *height,
      int *xdpi,
      int *ydpi);
extern jpeg_info_flags jpeginfo_dimensions (jpeg_image const *image,
      int size,
      int *width,
      int *height,
      int *xdpi,
      int *ydpi);

/* ------------------------------------------------------------------------
 * Function:      jpegfileinfo_dimensions()
 *
 * Description:   Returns the dimensions of a JPEG image in a file
 *
 * Input:         file_name - value of R1 on entry
 *
 * Output:        info_flags - value of R0 on exit (X version only)
 *                width - value of R2 on exit
 *                height - value of R3 on exit
 *                xdpi - value of R4 on exit
 *                ydpi - value of R5 on exit
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Calls SWI 0x49981 with R0 = 0x1.
 */

extern os_error *xjpegfileinfo_dimensions (char const *file_name,
      jpeg_info_flags *info_flags,
      int *width,
      int *height,
      int *xdpi,
      int *ydpi);
extern jpeg_info_flags jpegfileinfo_dimensions (char const *file_name,
      int *width,
      int *height,
      int *xdpi,
      int *ydpi);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_scaled()
 *
 * Description:   Plots a JPEG image from memory
 *
 * Input:         image - value of R0 on entry
 *                x - value of R1 on entry
 *                y - value of R2 on entry
 *                factors - value of R3 on entry
 *                size - value of R4 on entry
 *                flags - value of R5 on entry
 *
 * Other notes:   Calls SWI 0x49982.
 */

extern os_error *xjpeg_plot_scaled (jpeg_image const *image,
      int x,
      int y,
      os_factors const *factors,
      int size,
      jpeg_scale_flags flags);
extern void jpeg_plot_scaled (jpeg_image const *image,
      int x,
      int y,
      os_factors const *factors,
      int size,
      jpeg_scale_flags flags);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_scaled_colour_map()
 *
 * Description:   Plots a JPEG image from memory through a colour map
 *
 * Input:         image - value of R0 on entry
 *                x - value of R1 on entry
 *                y - value of R2 on entry
 *                factors - value of R3 on entry
 *                size - value of R4 on entry
 *                flags - value of R5 on entry
 *                colourmap - value of R6 on entry
 *
 * Other notes:   Calls SWI 0x49982.
 */

extern os_error *xjpeg_plot_scaled_colour_map (jpeg_image const *image,
      int x,
      int y,
      os_factors const *factors,
      int size,
      jpeg_scale_flags flags,
      os_colour_map const *colourmap);
extern void jpeg_plot_scaled_colour_map (jpeg_image const *image,
      int x,
      int y,
      os_factors const *factors,
      int size,
      jpeg_scale_flags flags,
      os_colour_map const *colourmap);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_file_scaled()
 *
 * Description:   Plots a JPEG image from a file
 *
 * Input:         file_name - value of R0 on entry
 *                x - value of R1 on entry
 *                y - value of R2 on entry
 *                factors - value of R3 on entry
 *                flags - value of R4 on entry
 *
 * Other notes:   Calls SWI 0x49983.
 */

extern os_error *xjpeg_plot_file_scaled (char const *file_name,
      int x,
      int y,
      os_factors const *factors,
      jpeg_scale_flags flags);
extern void jpeg_plot_file_scaled (char const *file_name,
      int x,
      int y,
      os_factors const *factors,
      jpeg_scale_flags flags);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_file_scaled_colour_map()
 *
 * Description:   Plots a JPEG image from a file through a colour map
 *
 * Input:         file_name - value of R0 on entry
 *                x - value of R1 on entry
 *                y - value of R2 on entry
 *                factors - value of R3 on entry
 *                flags - value of R4 on entry
 *                colourmap - value of R5 on entry
 *
 * Other notes:   Calls SWI 0x49983.
 */

extern os_error *xjpeg_plot_file_scaled_colour_map (char const *file_name,
      int x,
      int y,
      os_factors const *factors,
      jpeg_scale_flags flags,
      os_colour_map const *colourmap);
extern void jpeg_plot_file_scaled_colour_map (char const *file_name,
      int x,
      int y,
      os_factors const *factors,
      jpeg_scale_flags flags,
      os_colour_map const *colourmap);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_transformed()
 *
 * Description:   Plots a JPEG image from memory using a transformation
 *                matrix
 *
 * Input:         image - value of R0 on entry
 *                flags - value of R1 on entry
 *                trfm_or_rect - value of R2 on entry
 *                size - value of R3 on entry
 *
 * Other notes:   Calls SWI 0x49984.
 */

extern os_error *xjpeg_plot_transformed (jpeg_image const *image,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect,
      int size);
__swi (0x49984) void jpeg_plot_transformed (jpeg_image const *image,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect,
      int size);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_transformed_colour_map()
 *
 * Description:   Plots a JPEG image from memory using a transformation
 *                matrix though a colour map
 *
 * Input:         image - value of R0 on entry
 *                flags - value of R1 on entry
 *                trfm_or_rect - value of R2 on entry
 *                size - value of R3 on entry
 *                colourmap - value of R4 on entry
 *
 * Other notes:   Calls SWI 0x49984.
 */

extern os_error *xjpeg_plot_transformed_colour_map (jpeg_image const *image,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect,
      int size,
      os_colour_map const *colourmap);
extern void jpeg_plot_transformed_colour_map (jpeg_image const *image,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect,
      int size,
      os_colour_map const *colourmap);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_file_transformed()
 *
 * Description:   Plots a JPEG image from a file using a transformation
 *                matrix
 *
 * Input:         file_name - value of R0 on entry
 *                flags - value of R1 on entry
 *                trfm_or_rect - value of R2 on entry
 *
 * Other notes:   Calls SWI 0x49985.
 */

extern os_error *xjpeg_plot_file_transformed (char const *file_name,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect);
__swi (0x49985) void jpeg_plot_file_transformed (char const *file_name,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect);

/* ------------------------------------------------------------------------
 * Function:      jpeg_plot_file_transformed_colour_map()
 *
 * Description:   Plots a JPEG image from a file using a transformation
 *                matrix through a colour map
 *
 * Input:         file_name - value of R0 on entry
 *                flags - value of R1 on entry
 *                trfm_or_rect - value of R2 on entry
 *                colourmap - value of R3 on entry
 *
 * Other notes:   Calls SWI 0x49985.
 */

extern os_error *xjpeg_plot_file_transformed_colour_map (char const *file_name,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect,
      os_colour_map const *colourmap);
__swi (0x49985) void jpeg_plot_file_transformed_colour_map (char const *file_name,
      jpeg_transform_flags flags,
      os_trfm const *trfm_or_rect,
      os_colour_map const *colourmap);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
