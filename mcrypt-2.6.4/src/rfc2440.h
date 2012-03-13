/* rfc2440.h - OpenPGP message format
 *   Copyright (C) 2002 Timo Schulz <twoaday@freakmail.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef RFC2440_H
#define RFC2440_H

#define fail_if_nomem(p) \
do { \
    if ( !(p) ) { \
        fprintf( stderr, "OUT OF CORE: Could not allocate memory!!" ); \
        exit( 0 ); \
    } \
} while ( 0 )

enum {
    PGP_SUCCESS = 0,
    PGP_ERR_PKT = 1,
    PGP_ERR_GENERAL = 2,
    PGP_ERR_FILE = 3
};  

enum {
    PKT_SYMKEY_ENC = 3,
    PKT_ONEPASS_SIG = 4,
    PKT_COMPRESSED = 8,
    PKT_ENCRYPTED = 9,
    PKT_PLAINTEXT = 11,
};

enum {
    OPENPGP_S2K_SIMPLE = 0,
    OPENPGP_S2K_SALTED = 1,
    OPENPGP_S2K_ISALTED = 3
};
enum {
    OPENPGP_MD_MD5 = 1,
    OPENPGP_MD_SHA1 = 2,
    OPENPGP_MD_RMD160 = 3
};

enum {
    OPENPGP_ENC_3DES = 2,
    OPENPGP_ENC_CAST5 = 3,
    OPENPGP_ENC_BLOWFISH = 4,
    OPENPGP_ENC_AES128 = 7,
    OPENPGP_ENC_AES192 = 8,
    OPENPGP_ENC_AES256 = 9,
    OPENPGP_ENC_TWOFISH = 10
};

typedef unsigned char uchar;
typedef unsigned int uint32;

typedef struct packet_s {
    unsigned block:1;
    unsigned old:1;
} PACKET; 

typedef struct ustring_s {
    size_t len;
    unsigned char d[1];
} *USTRING;

typedef struct {
    struct {
        int mode;
        uchar algo;
        uchar salt[8];
        uint32 count;
    } s2k;
    MCRYPT hd;
    uchar key[32];
    int keylen;
    int blocklen;
    char* algo;
} DEK;

void *m_alloc( size_t size );

/*-- low level interface --*/
void dek_free( DEK *d );
DEK* dek_create( char *algo, char *pass  );
void dek_load( DEK *d, char *pass );

USTRING proc_packets( const char *file, char *pass );

USTRING plaintext_encode( const USTRING dat );
int     plaintext_decode( const USTRING pt, USTRING *result );

USTRING encrypted_encode( const USTRING pt, const DEK *dek );
int     encrypted_decode( const DEK *dek, const USTRING dat, USTRING *result );

USTRING compressed_encode( const USTRING dat, int algo );
int     compressed_decode( const USTRING zip, USTRING *result );

USTRING symkey_enc_encode( const DEK *dek );
int     symkey_enc_decode( const USTRING dat, DEK **dek );

/*-- high level interface --*/
int pgp_encrypt_file( const char *infile, const char *outfile, char *pass );
int pgp_decrypt_file( const char *infile, const char *outfile, char *pass );

#endif /*RFC2440_H*/





