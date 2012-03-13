all: utils pythonscripts
	cat tedd.sh tedd.tar.gz > tedd.bundle
	chmod +x tedd.bundle

pythonscripts:
	tar -czf tedd.tar.gz scripts/*.py scripts/distros/*.py tedd-utils.tar.gz

utils: mcrypt mkfs getpass
	tar -czf tedd-utils.tar.gz -C tedd-utils/ getpass mcrypt mkfs.xfs

getpass:
	gcc -static getpass.c -o tedd-utils/getpass

libmcrypt:
	make -C libmcrypt-2.5.7/

mhash:
	make -C mhash-0.9.9/

mcrypt: libmcrypt mhash
	make -C mcrypt-2.6.4/
	gcc -static -fno-stack-protector -I /usr/local/include -Wall -o \
tedd-utils/mcrypt mcrypt-2.6.4/src/extra.o mcrypt-2.6.4/src/mcrypt.o mcrypt-2.6.4/src/keys.o mcrypt-2.6.4/src/random.o \
mcrypt-2.6.4/src/rndunix.o mcrypt-2.6.4/src/xmalloc.o mcrypt-2.6.4/src/functions.o mcrypt-2.6.4/src/errors.o \
mcrypt-2.6.4/src/bits.o mcrypt-2.6.4/src/openpgp.o mcrypt-2.6.4/src/rndwin32.o mcrypt-2.6.4/src/environ.o \
mcrypt-2.6.4/src/getpass.o mcrypt-2.6.4/src/ufc_crypt.o mcrypt-2.6.4/src/popen.o mcrypt-2.6.4/src/classic.o \
mcrypt-2.6.4/src/rfc2440.o mcrypt-2.6.4/src/gaaout.o -lz libmcrypt-2.5.7/lib/.libs/libmcrypt.a \
-L/usr/local/lib mhash-0.9.9/lib/.libs/libmhash.a

mkfs:
	make -C xfsprogs-2.9.8/ DEBUG="-DNDEBUG"
	gcc -static -o tedd-utils/mkfs.xfs  xfsprogs-2.9.8/mkfs/maxtrres.o \
xfsprogs-2.9.8/mkfs/proto.o xfsprogs-2.9.8/mkfs/xfs_mkfs.o \
xfsprogs-2.9.8/libxfs/.libs/libxfs.a -luuid \
xfsprogs-2.9.8/libdisk/.libs/libdisk.a -lrt -lpthread

clean:
	rm -rf *.tar.gz *.pyc *.bundle *~
	make -C mhash-0.9.9/ distclean
	make -C mcrypt-2.6.4/ distclean
	make -C libmcrypt-2.5.7/ distclean
	make -C xfsprogs-2.9.8/ distclean
	rm tedd-utils/*
