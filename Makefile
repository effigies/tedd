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
	make -C libmcrypt-2.5.8/

mhash:
	make -C mhash-0.9.9/

mcrypt: libmcrypt mhash
	make -C mcrypt-2.6.8/
	gcc -static -fno-stack-protector -I /usr/local/include -Wall -o \
tedd-utils/mcrypt mcrypt-2.6.8/src/extra.o mcrypt-2.6.8/src/mcrypt.o mcrypt-2.6.8/src/keys.o mcrypt-2.6.8/src/random.o \
mcrypt-2.6.8/src/rndunix.o mcrypt-2.6.8/src/xmalloc.o mcrypt-2.6.8/src/functions.o mcrypt-2.6.8/src/errors.o \
mcrypt-2.6.8/src/bits.o mcrypt-2.6.8/src/openpgp.o mcrypt-2.6.8/src/rndwin32.o mcrypt-2.6.8/src/environ.o \
mcrypt-2.6.8/src/getpass.o mcrypt-2.6.8/src/ufc_crypt.o mcrypt-2.6.8/src/popen.o mcrypt-2.6.8/src/classic.o \
mcrypt-2.6.8/src/rfc2440.o mcrypt-2.6.8/src/gaaout.o -lz libmcrypt-2.5.8/lib/.libs/libmcrypt.a \
-L/usr/local/lib mhash-0.9.9/lib/.libs/libmhash.a

mkfs:
	make -C xfsprogs-3.1.7/ DEBUG="-DNDEBUG"
	gcc -static -o tedd-utils/mkfs.xfs  xfsprogs-3.1.7/mkfs/maxtrres.o \
xfsprogs-3.1.7/mkfs/proto.o xfsprogs-3.1.7/mkfs/xfs_mkfs.o \
xfsprogs-3.1.7/libxfs/.libs/libxfs.a -luuid \
xfsprogs-3.1.7/libdisk/.libs/libdisk.a -lrt -lpthread

clean:
	rm -rf *.tar.gz *.pyc *.bundle *~
	make -C mhash-0.9.9/ distclean
	make -C mcrypt-2.6.8/ distclean
	make -C xfsprogs-3.1.7/ distclean
	rm tedd-utils/*
	make -C libmcrypt-2.5.8/ distclean
