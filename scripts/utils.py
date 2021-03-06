import os, random

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
