#!/usr/bin/env python
import os, shutil, tarfile

duress_script_template = """#!/bin/sh

# Example invocation: /scripts/duress "$PASS" /dev/sda2 sda2_crypt
PASS="$1"
cryptsource="$2"
crypttarget="$3"

# This is the most convenient way to access LVM functionality
ln -s /sbin/lvm /bin/pvcreate
ln -s /sbin/lvm /bin/vgcreate
ln -s /sbin/lvm /bin/vgchange
ln -s /sbin/lvm /bin/lvcreate

# Make sure the headers are trashed, not just partially overwritten
HEADERSIZE=`cryptsetup luksDump $cryptsource | grep Payload`
set -- $HEADERSIZE
dd of=$cryptsource if=/dev/urandom count=$3

# These next two commands are going to be most of the heavy lifting involved
# here.
echo -n "$PASS" | cryptsetup luksFormat $cryptsource
echo -n "$PASS" | cryptsetup luksOpen $cryptsource $crypttarget

# Set up LVM
pvcreate /dev/mapper/$crypttarget
vgcreate {volgroupname} /dev/mapper/$crypttarget
vgchange -a y {volgroupname}
lvcreate -Cy -L{swapsize} -nswap {volgroupname}
lvcreate -Cy -l +100%%FREE -noverlay {volgroupname}

# Create your swap. We want this system to look credible.
mkswap {swappath}

# XFS seems to be the fastest filesystem to create
mkfs.{overlay.type} -q {overlay.path}

# Replace this initramfs
# Using noatime prevents a record of the swap
mkdir -p /boot
mount -t {base.type} -o rw,noatime {base.path} /boot

# Rather than deleting the old initrd, we're going to swap them around
# So your current access password becomes your new duress password

mv /boot/boot/access.nc /boot/boot/tmp.nc
mv /boot/boot/duress.nc /boot/boot/access.nc
mv /boot/boot/tmp.nc /boot/boot/duress.nc
mv /boot/boot/initrd.img-`uname -r` /boot/boot/initrd.tmp
mv /boot/boot/{secondinitrd} /boot/boot/initrd.img-`uname -r`
mv /boot/boot/initrd.tmp /boot/boot/{secondinitrd}

# Finish up and leave us in the state the normal script expects
umount /boot
rm -rf /boot
vgchange -a n {volgroupname}
cryptsetup luksClose $crypttarget"""

class initrd:
    def __init__(self, path, working_dir, base_dir, cwd=os.getcwd()):
        self.install_mod = None
        boot_dir = os.path.dirname(path)
        for item in os.listdir(os.path.join(cwd,"scripts","distros")):
            if item.endswith(".py"):
                module = __import__(os.path.join("distros",item[:-3]))
                if module.predicate(base_dir):
                    self.install_mod = module
                    break
        assert self.install_mod != None, "No matching distributions."
        self.path,self.working_dir,initrd_dir = map(os.path.realpath,
            (path,working_dir,initrd_dir))
#        self.path = os.path.realpath(path)
#        self.working_dir = os.path.realpath(working_dir)
        os.mkdir(self.working_dir)
#        initrd_dir = os.path.realpath(os.path.join(self.working_dir, "initrd"))
        os.mkdir(initrd_dir)
        os.system('cd "%s" ; zcat "%s" | cpio -i -H newc' % (initrd_dir, self.path))
        util_archive = tarfile.open(os.path.join(cwd, "tedd-utils.tar.gz"), "r:gz")
        util_archive.extractall(os.path.join(initrd_dir, "bin"))
        util_archive.close()
        self.installer = self.install_mod.installer(initrd_dir, working_dir, base_dir, boot_dir, path)

    def createDuress(self, lvg, base, password, this_initrd, second_initrd, permname):
        duress_script = open(os.path.join(self.working_dir, "initrd","scripts","duress"), "w")
        script_text = duress_script_template.format(
            volgroupname=lvg.group_name,
            swapsize=lvg.logical_volumes["swap"].size / (2 ** 20),
            swappath=lvg.logical_volumes["swap"].path,
            overlay=lvg.logical_volumes["overlay"],
            base=base, second_initrd=second_initrd)
        duress_script.write(script_text)
        duress_script.close()
        if os.path.exists(os.path.join(self.working_dir, "initrd","scripts","duress.nc")):
            os.remove(os.path.join(self.working_dir, "initrd","scripts","duress.nc"))
        os.system('cd "%s" && mcrypt -q -u -k "%s" -a blowfish duress' % (os.path.join(self.working_dir, "initrd","scripts"),password))
        shutil.copy(os.path.join(self.working_dir, "initrd", "scripts", "duress.nc"), os.path.join(os.path.dirname(self.path), permname))

    def guestPass(self, password):
        guest_nc = open(os.path.join(self.working_dir, "initrd", "scripts", "clean"), "w")
        guest_nc.write("Hello world.")
        guest_nc.close()
        os.system('cd "%s" && mcrypt -q -u -k "%s" -a blowfish clean' % (os.path.join(self.working_dir, "initrd","scripts"),password))
        shutil.copy(os.path.join(self.working_dir, "initrd", "scripts", "clean.nc"), os.path.join(os.path.dirname(self.path), "clean.nc"))

    def packageInitrd(self, dest_name=False):
        if not dest_name:
            dest_name = os.path.realpath(self.path)
        if os.path.exists(dest_name):
            os.rename(dest_name, "%s.bak" % dest_name)
        os.system('cd "%s" && find . -print | cpio -o -H newc > "%s.tmp"' % (os.path.join(self.working_dir,"initrd"), dest_name))
        os.system('cd "%s" && gzip --best "%s.tmp" -c > "%s" ' % (os.path.join(self.working_dir,"initrd"), dest_name, dest_name))
        os.remove("%s.tmp" % dest_name)

