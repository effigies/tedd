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

/* Functions for that may not exist in some unices */

/* $Id: functions.c,v 1.1.1.1 2000/05/22 13:09:26 nmav Exp $ */

#ifndef DEFINES_H
#define DEFINES_H
#include <defines.h>
#endif

#ifndef FUNCTIONS_H
#define FUNCTIONS_H
#include "functions.h"
#endif

Sigfunc *
 Signal(int signo, Sigfunc * func)
{
#ifdef HAVE_SIGACTION

	struct sigaction act, oact;

	act.sa_handler = func;
	sigemptyset(&act.sa_mask);
	act.sa_flags = 0;
	if (signo == SIGALRM) {
#ifdef SA_INTERRUPT
		act.sa_flags |= SA_INTERRUPT;	/* SunOs 4.x */
#endif
	} else {
#ifdef SA_RESTART
		act.sa_flags |= SA_RESTART;	/* SVR4, 4.4BSD */
#endif
	}

	if (sigaction(signo, &act, &oact) < 0)
		return (SIG_ERR);
	return (oact.sa_handler);

#else
#ifdef HAVE_SIGNAL
	return signal(signo, func);
#else
	return (Sigfunc *) 0;	/* Do nothing */
#endif
#endif
}
