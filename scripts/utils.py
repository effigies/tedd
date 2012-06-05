import os, random, time
from tempfile import mkdtemp

def random_string(length):
    alphabet = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string = ""
    for i in range(0,length):
        string += random.choice(alphabet)
    return string

def mount_partition(part):
    f = open('/proc/mounts')
    mounts = [mount.split() for mount in f if mount]
    f.close()

    existing = [mount for mount in mounts if mount[0] == part.path]
    if existing:
        return existing[0][1], False

    mountpoint = mkdtemp()
    if os.system("mount -t %s -o ro %s %s" %
                (part.fileSystem.type, part.path, mountpoint)
                ) == 0:
        return mountpoint, True
    return None

def unmount_partition(mountpoint, flag):
    if flag:
        time.sleep(1)
        if not os.system("umount %s" % mountpoint):
            os.rmdir(mountpoint)
        else:
            time.sleep(2)
            if not os.system("umount %s" % mountpoint):
                os.rmdir(mountpoint)
            else:
                debugPrint("WARNING: Could not unmount %s" % mountpoint)
