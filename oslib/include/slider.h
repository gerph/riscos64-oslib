#ifndef slider_H
#define slider_H

/* C header file for Slider
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

#ifndef gadget_H
#include "gadget.h"
#endif

#if defined NAMESPACE_OSLIB
  namespace OSLib {
#endif

/**********************************
 * SWI names and SWI reason codes *
 **********************************/
#undef  Slider_SetValue
#define Slider_SetValue                         0x240
#undef  Slider_GetValue
#define Slider_GetValue                         0x241
#undef  Slider_SetBounds
#define Slider_SetBounds                        0x242
#undef  Slider_GetBounds
#define Slider_GetBounds                        0x243
#undef  Slider_SetColour
#define Slider_SetColour                        0x244
#undef  Slider_GetColour
#define Slider_GetColour                        0x245

/************************************
 * Structure and union declarations *
 ************************************/
typedef struct slider_object                    slider_object;
typedef struct slider_action_value_changed      slider_action_value_changed;

/********************
 * Type definitions *
 ********************/
struct slider_object
   {  int lower_bound;
      int upper_bound;
      int step_size;
      int initial_value;
   };

struct slider_action_value_changed
   {  int value;
   };

typedef bits slider_bounds_flags;

/************************
 * Constant definitions *
 ************************/
#define class_SLIDER                            ((toolbox_class) 0x240u)
#define slider_GENERATE_VALUE_CHANGED           ((gadget_flags) 0x1u)
#define slider_GENERATE_VALUE_CHANGED_BY_DRAGGING ((gadget_flags) 0x2u)
#define slider_GENERATE_SET_VALUE_CHANGED       ((gadget_flags) 0x4u)
#define slider_VERTICAL                         ((gadget_flags) 0x8u)
#define slider_DRAGGABLE                        ((gadget_flags) 0x10u)
#define slider_KNOB_COLOUR                      ((gadget_flags) 0xF000u)
#define slider_KNOB_COLOUR_SHIFT                12
#define slider_WELL_COLOUR                      ((gadget_flags) 0xF0000u)
#define slider_WELL_COLOUR_SHIFT                16
#define action_SLIDER_VALUE_CHANGED             0x82886u
#define slider_VALUE_CHANGING                   0x1u
#define slider_VALUE_CHANGED_BY_DRAGGING        0x2u
#define slider_VALUE_CHANGED                    0x4u
#define slider_BOUND_LOWER                      ((slider_bounds_flags) 0x1u)
#define slider_BOUND_UPPER                      ((slider_bounds_flags) 0x2u)
#define slider_BOUND_STEP                       ((slider_bounds_flags) 0x4u)

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      slider_set_value()
 *
 * Description:   Calls reason code 576 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                window - value of R1 on entry
 *                slider - value of R3 on entry
 *                colour - value of R4 on entry
 *
 * Other notes:   Before entry, R2 = 0x240.
 */

extern os_error *xslider_set_value (bits flags,
      toolbox_o window,
      toolbox_c slider,
      wimp_colour colour);
extern void slider_set_value (bits flags,
      toolbox_o window,
      toolbox_c slider,
      wimp_colour colour);

/* ------------------------------------------------------------------------
 * Function:      slider_get_value()
 *
 * Description:   Calls reason code 577 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                window - value of R1 on entry
 *                slider - value of R3 on entry
 *
 * Output:        value - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Before entry, R2 = 0x241.
 */

extern os_error *xslider_get_value (bits flags,
      toolbox_o window,
      toolbox_c slider,
      int *value);
extern int slider_get_value (bits flags,
      toolbox_o window,
      toolbox_c slider);

/* ------------------------------------------------------------------------
 * Function:      slider_set_bounds()
 *
 * Description:   Calls reason code 578 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                window - value of R1 on entry
 *                slider - value of R3 on entry
 *                upper_bound - value of R4 on entry
 *                lower_bound - value of R5 on entry
 *                step_size - value of R6 on entry
 *
 * Other notes:   Before entry, R2 = 0x242.
 */

extern os_error *xslider_set_bounds (slider_bounds_flags flags,
      toolbox_o window,
      toolbox_c slider,
      int upper_bound,
      int lower_bound,
      int step_size);
extern void slider_set_bounds (slider_bounds_flags flags,
      toolbox_o window,
      toolbox_c slider,
      int upper_bound,
      int lower_bound,
      int step_size);

/* ------------------------------------------------------------------------
 * Function:      slider_get_bounds()
 *
 * Description:   Calls reason code 579 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                window - value of R1 on entry
 *                slider - value of R3 on entry
 *
 * Output:        upper_bound - value of R4 on exit
 *                lower_bound - value of R5 on exit
 *                step_size - value of R6 on exit
 *
 * Other notes:   Before entry, R2 = 0x243.
 */

extern os_error *xslider_get_bounds (slider_bounds_flags flags,
      toolbox_o window,
      toolbox_c slider,
      int *upper_bound,
      int *lower_bound,
      int *step_size);
extern void slider_get_bounds (slider_bounds_flags flags,
      toolbox_o window,
      toolbox_c slider,
      int *upper_bound,
      int *lower_bound,
      int *step_size);

/* ------------------------------------------------------------------------
 * Function:      slider_set_colour()
 *
 * Description:   Calls reason code 580 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                window - value of R1 on entry
 *                slider - value of R3 on entry
 *                colour - value of R4 on entry
 *
 * Other notes:   Before entry, R2 = 0x244.
 */

extern os_error *xslider_set_colour (bits flags,
      toolbox_o window,
      toolbox_c slider,
      wimp_colour colour);
extern void slider_set_colour (bits flags,
      toolbox_o window,
      toolbox_c slider,
      wimp_colour colour);

/* ------------------------------------------------------------------------
 * Function:      slider_get_colour()
 *
 * Description:   Calls reason code 581 of SWI 0x44EC6
 *
 * Input:         flags - value of R0 on entry
 *                window - value of R1 on entry
 *                slider - value of R3 on entry
 *
 * Output:        colour - value of R0 on exit (X version only)
 *
 * Returns:       R0 (non-X version only)
 *
 * Other notes:   Before entry, R2 = 0x245.
 */

extern os_error *xslider_get_colour (bits flags,
      toolbox_o window,
      toolbox_c slider,
      wimp_colour *colour);
extern wimp_colour slider_get_colour (bits flags,
      toolbox_o window,
      toolbox_c slider);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
