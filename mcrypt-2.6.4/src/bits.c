/*
 *    Copyright (C) 1998,1999,2000 Nikos Mavroyanopoulos
 *
 *    This program is free software; you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation; either version 2 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program; if not, write to the Free Software
 *    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

/* $Id: bits.c,v 1.1.1.1 2000/05/22 13:09:26 nmav Exp $ */

#ifndef DEFINES_H
#define DEFINES_H
#include <defines.h>
#endif
#include "bits.h"
#include <extra.h>		/* for MAX_KEY_LEN */



unsigned int m_setbit(unsigned int which, unsigned int fullnum, unsigned int what)
{
	if (what == 1) {
		return i_setbit(which, fullnum);
	} else {
		return i_unsetbit(which, fullnum);
	}
}


