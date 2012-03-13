#!/usr/bin/env python

import os, shutil
from debug import debugPrint

class distro:
    def __init__(self, base, boot, working_dir):
        self.base = base
        self.boot = boot
        self.workingdir = working_dir

    # Source comes from base, destination goes to working_dir
    def copy_file(self, source, destination=None, base_dest=False):
        if not destination:
            destination = source
        if not base_dest:
            try:
                shutil.copy(os.path.join(self.base, source), os.path.join(self.workingdir, "initrd", destination))
            except IOError:
                debugPrint("Error copying %s to %s" % (os.path.join(self.base, source), os.path.join(self.workingdir, "initrd", destination)))
        else:
            try:
                shutil.copy(os.path.join(self.base, source), os.path.join(self.base, destination))
            except IOError:
                debugPrint("Error copying %s to %s" % (os.path.join(self.base, source), os.path.join(self.base, destination)))

    def copy_tree(self, source, destination=None):
        if not destination:
            destination = source
        try:
            shutil.copytree(os.path.join(self.base, source), os.path.join(self.workingdir, "initrd", destination))
        except OSError, exc:
            if exc[0] == 2:
                raise
            elif exc[0] == 17:
                debugPrint("File %s already exists" % (os.path.join(self.workingdir, "initrd", destination)))

    def patch_file(self, patch):
        # Apply Patches
        patchfile = open(os.path.join(self.workingdir, "file.patch"), "w")
        patchfile.write(patch)
        patchfile.close()
        os.system("cd %s && patch -p0 < file.patch" % self.workingdir)
#        os.remove(os.path.join(self.workingdir, "file.patch"))

    def new_directory(self, dirname, base=False):
        if base:
            b = self.base
        else:
            b = os.path.join(self.workingdir,"initrd")
        try:
            os.mkdir(os.path.join(b, dirname))
        except OSError:
            #Already exists
            pass

    def write_file(self, filename, content, append=False, base=False):
        def appendChar(app):
            if app:
                return "a"
            else:
                return "w"
        if base:
            newfile = open(os.path.join(self.base, filename), appendChar(append))
        else:
            newfile = open(os.path.join(self.workingdir, "initrd", filename), appendChar(append))
        newfile.write(content)
        newfile.close()

    def prep_chroot(self):
        os.system("mount --bind /proc %s/proc" % self.base)
        os.system("mount --bind /dev %s/dev" % self.base)
        os.system("mount --bind %s %s/boot" % (self.boot, self.base))
        os.rename(os.path.join(self.base, "etc", "resolv.conf"),os.path.join(self.base, "etc", "resolv.conf.bak-tedd"))
        shutil.copy(os.path.join("/etc", "resolv.conf"), os.path.join(self.base, "etc", "resolv.conf"))

    def run_chroot(self, action):
        os.system("chroot %s %s" % (self.base, action))

    def close_chroot(self):
        os.system("umount %s/proc" % self.base)
        os.system("umount %s/dev" % self.base)
        os.system("umount %s/boot" % self.base)
        os.rename(os.path.join(self.base, "etc", "resolv.conf.bak-tedd"),os.path.join(self.base, "etc", "resolv.conf"))

