#!/usr/bin/env python

import os
import shutil
from debug import debugPrint
from subprocess import Popen, call, PIPE


class distro:
    def __init__(self, base, boot, working_dir):
        self.base = base
        self.boot = boot
        self.workingdir = working_dir

    # Source comes from base, destination goes to working_dir
    def copy_file(self, source, destination=None, base_dest=False):
        src = os.path.join(self.base, source)

        if not destination:
            destination = source

        if not base_dest:
            dst = os.path.join(self.workingdir, "initrd", destination)
        else:
            dst = os.path.join(self.base, destination)

        try:
            shutil.copy(src, dst)
        except IOError:
            debugPrint("Error copying {} to {}".format(src, dst))

    def copy_tree(self, source, destination=None):
        if not destination:
            destination = source

        dst = os.path.join(self.workingdir, "initrd", destination)
        try:
            shutil.copytree(os.path.join(self.base, source), dst)
        except OSError, exc:
            if exc[0] == 2:
                raise
            elif exc[0] == 17:
                debugPrint("File {} already exists".format(dst))

    def patch_file(self, patch):
        # Apply Patches
        pipe = Popen(['patch', '-p0'], stdin=PIPE, cwd=self.workingdir)
        pipe.stdin.write(patch)
        pipe.stdin.close()
        pipe.wait()

    def new_directory(self, dirname, base=False):
        if base:
            b = self.base
        else:
            b = os.path.join(self.workingdir, "initrd")

        path = os.path.join(b, dirname)

        if not os.path.isdir(path):
            os.mkdir(os.path.join(b, dirname))

    def write_file(self, filename, content, append=False, base=False):
        if base:
            fname = os.path.join(self.base, filename)
        else:
            fname = os.path.join(self.workingdir, "initrd", filename)

        with open(fname, 'a' if append else 'w') as newfile:
            newfile.write(content)

    def prep_chroot(self):
        call(['mount', '--bind', '/proc', os.path.join(self.base, 'proc')])
        call(['mount', '--bind', '/dev', os.path.join(self.base, 'dev')])
        call(['mount', '--bind', self.boot, os.path.join(self.base, 'boot')])
        os.rename(os.path.join(self.base, "etc", "resolv.conf"),
                  os.path.join(self.base, "etc", "resolv.conf.bak-tedd"))
        shutil.copy(os.path.join("/etc", "resolv.conf"),
                    os.path.join(self.base, "etc", "resolv.conf"))

    def run_chroot(self, action):
        call(['chroot', self.base, action])

    def close_chroot(self):
        call(['umount', os.path.join(self.base, 'proc')])
        call(['umount', os.path.join(self.base, 'dev')])
        call(['umount', os.path.join(self.base, 'boot')])
        os.rename(os.path.join(self.base, "etc", "resolv.conf.bak-tedd"),
                  os.path.join(self.base, "etc", "resolv.conf"))
