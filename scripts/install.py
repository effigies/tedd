#!/usr/bin/env python

# This file is primarily a wrapper for functionality in other python libraries.
# Someday this should be replaced with a similar wrapper that offers a GUI

from devices import guessDisk, urandom, zeroFill
from disk import disk
from partition import partition
from getpass import getpass
from filesystems import ext
from luks import luksVolume
from lvm import lvg
from initrd import initrd
import copy, os, random, shutil

swap_size = 0

# Determine which disk contains the Linux installation
def getDisk():
    our_disk = guessDisk()
    disk_prompt = raw_input("\nWhat disk contains your Linux Installation? [%s]: " % our_disk.path)
    while disk_prompt != "" and not os.path.exists(disk_prompt):
        print "Disk not found."
        disk_prompt = raw_input("\nWhat disk contains your Linux Installation? [%s]: " % our_disk.path)
    if disk_prompt != "":
        our_disk = disk(disk_prompt)
    return our_disk

# Determine which partition contains the Linux installation
def getPartition(our_disk):
    our_part = our_disk.guessPartition()
    part_prompt = raw_input("\nWhat partition contains your Linux Installation? [%s]: " % our_part.path)
    while part_prompt != "" and not os.path.exists(part_prompt):
        print "Partition not found."
        part_prompt = raw_input("What partition contains your Linux Installation? [%s]: " % our_part.path)
    if part_prompt != "":
        our_part = our_disk.partitions[part_prompt]
    if not our_part.verifyLinux():
        print "No known Linux distribution on %s." % part_prompt
        return getPartition(our_disk)
    return our_part

# Delete the swap partitions
def deleteSwap(our_disk):
    global swap_size
    swap_list = our_disk.getSwap()
    if len(swap_list) > 0:
        print "\nIt is *highly* recommended that you encrypt your swap partition."
        print "May we delete the following swap partitions? "    
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
                print "\nDeleting the swap partition has left the following extended partition empty."
                print i
                delete_extended_prompt = raw_input("May we delete it? [Y/n]")
                if not delete_extended_prompt.startswith("n"):
                    our_disk.deletePart((our_disk.partitions[i],))
                break

def shrinkLinux(our_disk, our_part):
    print "\nTEDD will now shrink your Linux partition to make room for the encrypted overlay."
    shrink_prompt = raw_input("May we proceed? [Y/n]: ")
    if not shrink_prompt.lower().startswith("n"):
        print "This may take a while depending on your file system and partition size. Please be patient."
        our_part.resize()
        our_disk = disk(our_disk.path)
        our_part = our_disk.partitions[our_part.path]

def random_string(length):
    alphabet = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string = ""
    for i in range(0,length):
        string += random.choice(alphabet)
    return string

def mount_partition(part):
        fs = os.popen("mount")
        for line in fs:
            line_split = line.split()
            if line_split[0] == part.path:
                return line_split[2], False
        randstring = random_string(8)
        os.mkdir(randstring)
        if not os.system("mount %s %s" % (part.path, randstring)):
            return randstring, True
        return None

def unmount_partition(path, flag):
    if flag:
        if not os.system("umount %s" % path):
            os.removedirs(path)
        else:
            time.sleep(2)
            if not os.system("umount %s" % path):
                os.removedirs(path)
            else:
                debugPrint("WARNING: Could not unmount %s" % path)
        
    
def createEncrypted(our_disk):
    print "\nTEDD is creating the encrypted overlay."
    print "It is *highly* recommended that you random-fill your encrypted partion."
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
        print "Enter a password. This is the password you will use to *access* your data, not to destroy it."
        password_prompt = None
        while not password_prompt:
            password_prompt = getpass()
        if password_prompt != getpass("Verify: "):
            print "Passwords did not match"
        else: break
    luks = luksVolume(encrypted_part, password_prompt, "%s_crypt" % os.path.basename(encrypted_part.path))
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
    enc_swap_prompt = raw_input("\nHow big do you want your encrypted swap (in bytes)? [%s] " % swap_size)
    try:
        enc_swap = int(enc_swap_prompt)
    except:
        enc_swap = swap_size

    luks_lvg.lvcreate(enc_swap, "swap", "swap")
    luks_lvg.logical_volumes["swap"].fs.format()
    vg_free, vg_total, vg_size = luks_lvg.extents()
    enc_size = int((float(vg_free)/vg_total)*vg_size)
    enc_overlay_prompt = raw_input("\nHow big do you want your encrypted overlay (in bytes)? [%s] " % enc_size)
    if enc_overlay_prompt != "":
        enc_size = int(enc_overlay_prompt)

    fs_list = ["xfs"]
    print "\nWhat filesystem would you like to use for your encrypted overlay?"
    for num in range(0, len(fs_list)):
        print "%s. %s" % ((num+1), fs_list[num])
    fs_prompt = -1
    while not int(fs_prompt) in range(1,len(fs_list)+1):
        fs_prompt = raw_input("Choice: ")
        fs_type = fs_list[int(fs_prompt)-1]
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
    initrd_prompt = raw_input("Which initrd file do you use? [%s]" % initrd_file)
    if initrd_prompt != "":
        initrd_file = initrd_prompt

    return initrd(os.path.join(boot_path,initrd_file), working_dir, base_path), base_path, base_flag

def duress(lvg, base, initrd, password=False):
    fallback_dir = os.path.dirname(initrd.path)
    fallback_file = os.path.basename(initrd.path)
    fallback_initrd = fallback_file[:18]
    fallback_initrd += str((int(fallback_file[18:].split('-')[0])-1))
    for item in fallback_file[18:].split('-')[1:]:
        fallback_initrd += "-%s" % item
    if not password:
        print "Type in your duress password. Remember this password, but beware: authenticating with this password will destroy all of your data."
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
    initrd.createDuress(lvg,base, duress_prompt, os.path.basename(initrd.path),fallback_initrd, permname)
    return os.path.join(fallback_dir, fallback_initrd)

def guest(initrd):
    print "Do you want a guest login? This will be a password that will boot the system, hiding sensitive data, and prohibiting changes."
    print "Enter a password, or leave blank for no guest login."
    guest_pass = getpass()
    if guest_pass != "":
        initrd.guestPass(guest_pass)

if __name__ == "__main__":

#    enable_universe()

#    install_dependencies()
# Determine disk
    our_disk = getDisk()
# Determine Linux partition
    our_part = getPartition(our_disk)
    our_part.linux_verified.prepare()

# Delete swap
    deleteSwap(our_disk)

# Delete empty extended partition
    deleteEmptyExtended(our_disk)

# Shrink Linux partition
    shrinkLinux(our_disk, our_part)

# Create encrypted partition
# Random fill encrypted partition
    encrypted_part = createEncrypted(our_disk)

# Create Logical Volume Group
# Create Logical Volume: Swap
# Create Logical Volume: Root
# Format Logical Volume Root
    lvg = createLogicalVolumes(encrypted_part)

# Unpack initrd
    initrd, base_path, base_flag = unpackInitrd(our_part)

    fallback_initrd = duress(lvg, our_part, initrd)

    initrd.installer.install_tedd(our_part, lvg.logical_volumes["overlay"], lvg.logical_volumes["swap"], encrypted_part, fallback_initrd)

# Create duress script

    guest(initrd)

# Package initrd
    initrd.packageInitrd()
# Create duress script
    duress(lvg, our_part, initrd, encrypted_part.password)
# Package fallback initrd
    initrd.packageInitrd(fallback_initrd)
