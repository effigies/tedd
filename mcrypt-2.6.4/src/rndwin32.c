/*
 *    Copyright (C) 2002 Nikos Mavroyanopoulos
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

/* $Id: rndwin32.c,v 1.4 2003/01/19 18:06:20 nmav Exp $ */

static char rcsid[] = "$Id: rndwin32.c,v 1.4 2003/01/19 18:06:20 nmav Exp $";


#ifdef WIN32

#include <errors.h>
#include <windows.h>
#include <wincrypt.h>

/* WARNING: These functions were not tested at ALL.
 */

static HCRYPTPROV hProv;

void init_random(void) {

	if(!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
		err_quit("Error calling CryptAcquireContext()");
	}
}

void deinit_random( void) {

	if(!CryptReleaseContext(hProv, 0)) {
		err_quit("Error calling CryptReleaseContext()");
	}

}

int gather_random( void* dest, size_t length, int level) {

	if(!CryptGenRandom(hProv, dest, length)) {
		err_quit("Error calling CryptGenRandom()");
	}

	return 0;
}

#endif
