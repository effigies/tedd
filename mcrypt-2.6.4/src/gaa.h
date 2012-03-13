
#line 104 "gaa.skel"
/* GAA HEADER */
#ifndef GAA_HEADER_POKY
#define GAA_HEADER_POKY

typedef struct _gaainfo gaainfo;

struct _gaainfo
{
#line 111 "mcrypt.gaa"
	char **input;
#line 110 "mcrypt.gaa"
	int size;
#line 100 "mcrypt.gaa"
	int quiet;
#line 92 "mcrypt.gaa"
	int real_random_flag;
#line 89 "mcrypt.gaa"
	int noecho;
#line 86 "mcrypt.gaa"
	int force;
#line 83 "mcrypt.gaa"
	int timer;
#line 79 "mcrypt.gaa"
	int nodelete;
#line 76 "mcrypt.gaa"
	int unlink_flag;
#line 73 "mcrypt.gaa"
	int double_check;
#line 70 "mcrypt.gaa"
	int flush;
#line 66 "mcrypt.gaa"
	int bzipflag;
#line 63 "mcrypt.gaa"
	int gzipflag;
#line 61 "mcrypt.gaa"
	int bare_flag;
#line 58 "mcrypt.gaa"
	int noiv;
#line 54 "mcrypt.gaa"
	char **keys;
#line 53 "mcrypt.gaa"
	int keylen;
#line 50 "mcrypt.gaa"
	char *hash;
#line 47 "mcrypt.gaa"
	char *modes_directory;
#line 44 "mcrypt.gaa"
	char *mode;
#line 41 "mcrypt.gaa"
	char *algorithms_directory;
#line 38 "mcrypt.gaa"
	char *algorithm;
#line 35 "mcrypt.gaa"
	char *config_file;
#line 34 "mcrypt.gaa"
	int config;
#line 31 "mcrypt.gaa"
	char *keyfile;
#line 28 "mcrypt.gaa"
	char *kmode;
#line 25 "mcrypt.gaa"
	int keysize;
#line 22 "mcrypt.gaa"
	int ed_specified;
#line 21 "mcrypt.gaa"
	int ein;
#line 20 "mcrypt.gaa"
	int din;
#line 16 "mcrypt.gaa"
	int openpgp_z;
#line 13 "mcrypt.gaa"
	int openpgp;

#line 114 "gaa.skel"
};

#ifdef __cplusplus
extern "C"
{
#endif

    int gaa(int argc, char *argv[], gaainfo *gaaval);

    void gaa_help(void);
    
    int gaa_file(char *name, gaainfo *gaaval);
    
#ifdef __cplusplus
}
#endif


#endif
