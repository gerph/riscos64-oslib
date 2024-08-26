#ifndef serviceinternational_H
#define serviceinternational_H

/* C header file for ServiceInternational
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
#undef  Service_International
#define Service_International                   0x43
#undef  ServiceInternational_CountryNameToCountryNumber
#define ServiceInternational_CountryNameToCountryNumber 0x0
#undef  ServiceInternational_AlphabetNameToAlphabetNumber
#define ServiceInternational_AlphabetNameToAlphabetNumber 0x1
#undef  ServiceInternational_CountryNumberToCountryName
#define ServiceInternational_CountryNumberToCountryName 0x2
#undef  ServiceInternational_AlphabetNumberToAlphabetName
#define ServiceInternational_AlphabetNumberToAlphabetName 0x3
#undef  ServiceInternational_CountryNumberToAlphabetNumber
#define ServiceInternational_CountryNumberToAlphabetNumber 0x4
#undef  ServiceInternational_DefineChars
#define ServiceInternational_DefineChars        0x5
#undef  ServiceInternational_NewKeyboard
#define ServiceInternational_NewKeyboard        0x6

/************************
 * Constant definitions *
 ************************/
#define error_UNKNOWN_ALPHABET                  0x640u
      /*Unknown alphabet*/
#define error_UNKNOWN_COUNTRY                   0x641u
      /*Unknown country*/
#define error_UNKNOWN_KEYBOARD                  0x642u
      /*Unknown keyboard*/

/*************************
 * Function declarations *
 *************************/

#ifdef __cplusplus
   extern "C" {
#endif

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_country_name_to_country_number()
 *
 * Description:   Converts country name to country number
 *
 * Input:         country_name - value of R3 on entry
 *
 * Output:        unclaimed - value of R1 on exit (X version only)
 *                country_no - value of R4 on exit
 *
 * Returns:       R1 (non-X version only)
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x0.
 */

extern os_error *xserviceinternational_country_name_to_country_number (char const *country_name,
      bool *unclaimed,
      int *country_no);
extern bool serviceinternational_country_name_to_country_number (char const *country_name,
      int *country_no);

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_alphabet_name_to_alphabet_number()
 *
 * Description:   Converts alphabet name to alphabet number
 *
 * Input:         alphabet_name - value of R3 on entry
 *
 * Output:        unclaimed - value of R1 on exit (X version only)
 *                alphabet_no - value of R4 on exit
 *
 * Returns:       R1 (non-X version only)
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x1.
 */

extern os_error *xserviceinternational_alphabet_name_to_alphabet_number (char const *alphabet_name,
      bool *unclaimed,
      int *alphabet_no);
extern bool serviceinternational_alphabet_name_to_alphabet_number (char const *alphabet_name,
      int *alphabet_no);

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_country_number_to_country_name()
 *
 * Description:   Converts country number to country name
 *
 * Input:         country_no - value of R3 on entry
 *                buffer - value of R4 on entry
 *                size - value of R5 on entry
 *
 * Output:        unclaimed - value of R1 on exit (X version only)
 *                used - value of R5 on exit
 *
 * Returns:       R1 (non-X version only)
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x2.
 */

extern os_error *xserviceinternational_country_number_to_country_name (int country_no,
      char *buffer,
      int size,
      bool *unclaimed,
      int *used);
extern bool serviceinternational_country_number_to_country_name (int country_no,
      char *buffer,
      int size,
      int *used);

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_alphabet_number_to_alphabet_name()
 *
 * Description:   Converts alphabet number to alphabet name
 *
 * Input:         alphabet_no - value of R3 on entry
 *                buffer - value of R4 on entry
 *                size - value of R5 on entry
 *
 * Output:        unclaimed - value of R1 on exit (X version only)
 *                used - value of R5 on exit
 *
 * Returns:       R1 (non-X version only)
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x3.
 */

extern os_error *xserviceinternational_alphabet_number_to_alphabet_name (int alphabet_no,
      char *buffer,
      int size,
      bool *unclaimed,
      int *used);
extern bool serviceinternational_alphabet_number_to_alphabet_name (int alphabet_no,
      char *buffer,
      int size,
      int *used);

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_country_number_to_alphabet_number()
 *
 * Description:   Converts country number to alphabet number
 *
 * Input:         country_no - value of R3 on entry
 *
 * Output:        unclaimed - value of R1 on exit (X version only)
 *                alphabet_no - value of R4 on exit
 *
 * Returns:       R1 (non-X version only)
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x4.
 */

extern os_error *xserviceinternational_country_number_to_alphabet_number (int country_no,
      bool *unclaimed,
      int *alphabet_no);
extern bool serviceinternational_country_number_to_alphabet_number (int country_no,
      int *alphabet_no);

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_define_chars()
 *
 * Description:   Defines a range of characters from a given alphabet
 *                number
 *
 * Input:         alphabet_no - value of R3 on entry
 *                first - value of R4 on entry
 *                last - value of R5 on entry
 *
 * Output:        unclaimed - value of R1 on exit (X version only)
 *
 * Returns:       R1 (non-X version only)
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x5.
 */

extern os_error *xserviceinternational_define_chars (int alphabet_no,
      byte first,
      byte last,
      bool *unclaimed);
extern bool serviceinternational_define_chars (int alphabet_no,
      byte first,
      byte last);

/* ------------------------------------------------------------------------
 * Function:      serviceinternational_new_keyboard()
 *
 * Description:   Notification of a new keyboard selection
 *
 * Input:         keyboard_no - value of R3 on entry
 *                alphabet_no - value of R4 on entry
 *
 * Other notes:   Calls SWI 0x30 with R1 = 0x43, R2 = 0x6.
 */

extern os_error *xserviceinternational_new_keyboard (int keyboard_no,
      int alphabet_no);
extern void serviceinternational_new_keyboard (int keyboard_no,
      int alphabet_no);

#ifdef __cplusplus
   }
#endif

#if defined NAMESPACE_OSLIB
  } 
#endif

#endif
