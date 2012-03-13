## Process this file with automake to produce Makefile.in

EXTRA_DIST = config.rpath  INSTALL.generic THANKS NEWS
SUBDIRS = m4 doc src po
install-exec-hook:
	-$(RM) -f $(bindir)/mdecrypt
	$(LN_S) mcrypt $(bindir)/mdecrypt
uninstall-local:
	-$(RM) -f $(bindir)/mdecrypt

ChangeLog:
	cvs2cl --utc --fsf -t -S --prune
 
ACLOCAL_AMFLAGS = -I m4
