#!/usr/bin/env python

# This file is primarily a wrapper for functionality in other python libraries.
# Someday this should be replaced with a similar wrapper that offers a GUI

import parted as ped
from devices import urandom
from disk import disk
from partition import fsMap, mount_partition
from getpass import getpass
from luks import luksVolume
from lvm import lvg
from initrd import initrd as mkInitrd
import copy
import os
import random

swap_size = 0


# Determine which disk contains the Linux installation
def getDisk():
    devs = ped.getAllDevices()
    if len(devs) > 0:
        prompt = '\n'.join("[%d]\t%s" % (i, x.path)
                           for i, x in enumerate(devs))
        disk_prompt = raw_input("\nThe following disk drives were detected:\n"
                                "\n{}\n\nWhich contains your Linux "
                                "installation? [0]:".format(prompt))
        if disk_prompt == '':
            dev = devs[0]
        else:
            dev = devs[int(disk_prompt)]
    else:
        disk_prompt = raw_input("\nNo disks were detected.\nWhat is the path "
                                "of the disk containing your Linux "
                                "installation? ")
        if os.path.exists(disk_prompt):
            dev = ped.device.Device(disk_prompt)
        else:
            print "This doesn't seem to be working. Sorry."
            raise Exception("Cannot figure out installation location.")

    return ped.disk.Disk(dev)


# Determine which partition contains the Linux installation
def getPartition(disk):
    # Filter for partitions with filesystems we know how to handle
    parts = [part for part in disk.partitions if part.fileSystem.type in fsMap]

    if len(parts) == 0:
        print "No recognized Linux partitions on %s" % disk.device.path
        print "Following filesystems found:"
        print "\n".join("%s\t%s" % (part.path, part.fileSystem.type)
                        for part in disk.partitions)
        raise Exception("Cannot figure out installation location.")

    elif len(parts) == 1:
        part_prompt = raw_input("\nFound a Linux partition on {}. Is this "
                                "correct? [Y/n] ".format(parts[0].path))
        if part_prompt != '' and not part_prompt.lower().startswith('y'):
            print "Sorry. We only recognize the following filesystems:"
            print ", ".join(fsMap.keys())
            raise Exception("Cannot figure out installation location.")
        else:
            part = parts[0]

    else:
        prompt = '\n'.join("[{:d}]\t{}\t{}".format(i, part.path,
                                                   part.fileSystem.type)
                           for i, x in enumerate(parts))
        part_prompt = raw_input("\nThe following partitions were detected:\n"
                                "\n{}\n\nWhich contains your Linux "
                                "installation? [0]:".format(prompt))
        if part_prompt == '':
            part = parts[0]
        else:
            part = parts[int(part_prompt)]

    return part


# Delete the swap partitions
def deleteSwap(our_disk):
    global swap_size
    swap_list = our_disk.getSwap()
    if len(swap_list) > 0:
        print "\nIt is *highly* recommended that you encrypt your swap " \
            "partition.\nMay we delete the following swap partitions?"
        swap_size = 0
        for i in swap_list:
            swap_size += int(i.size)
            print "    %s " % i.path
        swap_prompt = raw_input("    [Y/n]: ")
        if not swap_prompt.lower().startswith("n"):
            our_disk.disableSwap()
            our_disk.deletePart(swap_list)
        else:
            swap_size = 0


# Delete any empty extended partitions
def deleteEmptyExtended(our_disk):
    has_logical = False
    for i in our_disk.partitions:
        if our_disk.partitions[i].logical:
            has_logical = True
    if not has_logical:
        for i in copy.copy(our_disk.partitions):
            if our_disk.partitions[i].type == "extended":
                print "\nDeleting the swap partition has left the following " \
                    "extended partition empty."
                print i
                delete_extended_prompt = raw_input("May we delete it? [Y/n]")
                if not delete_extended_prompt.startswith("n"):
                    our_disk.deletePart((our_disk.partitions[i],))
                break


def shrinkLinux(our_disk, our_part):
    print "\nTEDD will now shrink your Linux partition to make room for the " \
        "encrypted overlay."
    shrink_prompt = raw_input("May we proceed? [Y/n]: ")
    if not shrink_prompt.lower().startswith("n"):
        print "This may take a while depending on your file system and " \
            "partition size. Please be patient."
        our_part.resize()
        our_disk = disk(our_disk.path)
        our_part = our_disk.partitions[our_part.path]


def random_string(length):
    alphabet = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [random.choice(alphabet) for _ in range(length)]


def createEncrypted(our_disk):
    print "\nTEDD is creating the encrypted overlay."
    print "It is *highly* recommended that you random-fill your encrypted " \
        "partion."
    print "Which method would you like to use?"

    methods = ["None", "/dev/urandom"]
    for i in range(0, len(methods)):
        print "%s. %s" % (i, methods[i])
    try:
        method_prompt = int(raw_input("Choice? "))
    except:
        method_prompt = -1
        print "Expecting integer"
    while method_prompt != "" and method_prompt not in range(0, len(methods)):
        try:
            method_prompt = int(raw_input("Choice? "))
        except:
            print "Expecting integer"
            method_prompt = -1

    encrypted_part = our_disk.createPartition()
    if methods[method_prompt] == "/dev/urandom":
        print "Random wiping %s, this will take a while." % encrypted_part.path
        urandom(encrypted_part)

    while True:
        print "Enter a password. This is the password you will use to " \
            "*access* your data, not to destroy it."
        password_prompt = None
        while not password_prompt:
            password_prompt = getpass()
        if password_prompt != getpass("Verify: "):
            print "Passwords did not match"
        else:
            break
    luks = luksVolume(encrypted_part, password_prompt,
                      "%s_crypt" % os.path.basename(encrypted_part.path))
    luks.luksFormat()
    luks.luksOpen()
    return luks


def createLogicalVolumes(encrypted_part):
    global swap_size
    print "Creating logical volume"
    luks_lvg = lvg("luks", (encrypted_part,))
    luks_lvg.pvcreate()
    luks_lvg.vgcreate()
    luks_lvg.vgactivate()
    enc_swap_prompt = raw_input("\nHow big do you want your encrypted swap "
                                "(in bytes)? [%s] " % swap_size)
    try:
        enc_swap = int(enc_swap_prompt)
    except:
        enc_swap = swap_size

    luks_lvg.lvcreate(enc_swap, "swap", "swap")
    luks_lvg.logical_volumes["swap"].fs.format()
    vg_free, vg_total, vg_size = luks_lvg.extents()
    enc_size = int((float(vg_free)/vg_total)*vg_size)
    enc_overlay_prompt = raw_input("\nHow big do you want your encrypted "
                                   "overlay (in bytes)? [%s] " % enc_size)
    if enc_overlay_prompt != "":
        enc_size = int(enc_overlay_prompt)

    fs_list = ["xfs"]
    print "\nWhat filesystem would you like to use for your encrypted overlay?"
    for num in range(0, len(fs_list)):
        print "%s. %s" % ((num+1), fs_list[num])
    fs_prompt = -1
    while not int(fs_prompt) in range(1, len(fs_list) + 1):
        fs_prompt = raw_input("Choice: ")
        fs_type = fs_list[int(fs_prompt) - 1]
    luks_lvg.lvcreate(enc_size, "overlay", fs_type)
    luks_lvg.logical_volumes["overlay"].fs.format()
    return luks_lvg


def unpackInitrd(base):
    base_path, base_flag = mount_partition(base)
    boot_path = os.path.join(base_path, "boot")
    working_dir = "working_%s" % random_string(3)
    initrd_file = None
    max_version = 0
    max_subversion = 0
    for item in os.listdir(boot_path):
        if item.startswith("initrd.img"):
            version = int(item[15:17])
            subversion = int(item[18:].split('-')[0])
            if version > max_version:
                max_version = version
                max_subversion = 0
                initrd_file = item
            if subversion > max_subversion:
                max_subversion = subversion
                initrd_file = item
    initrd_prompt = raw_input("Which initrd file do you use? [%s]" %
                              initrd_file)
    if initrd_prompt != "":
        initrd_file = initrd_prompt

    return mkInitrd(os.path.join(boot_path, initrd_file), working_dir,
                    base_path), base_path, base_flag


def duress(vg, base, initrd, password=False):
    fallback_dir = os.path.dirname(initrd.path)
    fallback_file = os.path.basename(initrd.path)
    fallback_initrd = fallback_file[:18]
    fallback_initrd += str((int(fallback_file[18:].split('-')[0])-1))
    for item in fallback_file[18:].split('-')[1:]:
        fallback_initrd += "-%s" % item
    if not password:
        print "Type in your duress password. Remember this password, but " \
            "beware: authenticating with this password will destroy all of " \
            "your data."
        while True:
            duress_prompt = getpass()
            if duress_prompt != getpass("Verify: "):
                print "Passwords did not match. Try again."
            else:
                break
        permname = "duress.nc"
    else:
        duress_prompt = password
        permname = "access.nc"
    initrd.createDuress(vg, base, duress_prompt,
                        os.path.basename(initrd.path), fallback_initrd,
                        permname)
    return os.path.join(fallback_dir, fallback_initrd)


def guest(initrd):
    print "Do you want a guest login? This will be a password that will " \
        "boot the system, hiding sensitive data, and prohibiting changes."
    print "Enter a password, or leave blank for no guest login."
    guest_pass = getpass()
    if guest_pass != "":
        initrd.guestPass(guest_pass)

if __name__ == "__main__":

#    enable_universe()

#    install_dependencies()
# Determine disk
    print "MAIN: Get Disk..."
    our_disk = getDisk()
# Determine Linux partition
    print "MAIN: Get Partition..."
    our_part = getPartition(our_disk)
    print "MAIN: Prepare Partition..."
    our_part.linux_verified.prepare()

# Delete swap
    print "MAIN: Delete SWAP..."
    deleteSwap(our_disk)

# Delete empty extended partition
    print "MAIN: Delete EmptyExtended..."
    deleteEmptyExtended(our_disk)

# Shrink Linux partition
    print "MAIN: Shrink Linux Partition..."
    shrinkLinux(our_disk, our_part)

# Create encrypted partition
# Random fill encrypted partition
    print "MAIN: Create Encrypted Partition..."
    encrypted_part = createEncrypted(our_disk)

# Create Logical Volume Group
# Create Logical Volume: Swap
# Create Logical Volume: Root
# Format Logical Volume Root
    print "MAIN: Create Logical Volume..."
    vg = createLogicalVolumes(encrypted_part)

# Unpack initrd
    print "MAIN: Unpack initrd..."
    initrd, base_path, base_flag = unpackInitrd(our_part)

    fallback_initrd = duress(vg, our_part, initrd)

    initrd.installer.install_tedd(our_part, vg.logical_volumes["overlay"],
                                  vg.logical_volumes["swap"], encrypted_part,
                                  fallback_initrd)

# Create duress script

    print "MAIN: Create Duress Script..."
    guest(initrd)

# Package initrd
    initrd.packageInitrd()
# Create duress script
    duress(vg, our_part, initrd, encrypted_part.password)
# Package fallback initrd
    initrd.packageInitrd(fallback_initrd)
