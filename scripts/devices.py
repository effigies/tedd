from debug import debugPrint, for_real
from disk import disk

import os

# Look for a disk. Probably ought to be improved.
def guessDisk():
    for i in ["a","b","c", "d", "e", "f"]:
        for j in ["/dev/sd", "/dev/hd"]:
            path = j+i
            if os.path.exists(path):
                return disk(path)
    return None

def urandom(device):
        if for_real:
            os.system("dd if=/dev/urandom of=%s" % device.path)
        else:
            debugPrint("Filling %s with random data"% device.path)

def zeroFill(device):
        if for_real:
            os.system("dd if=/dev/zero of=%s" % device.path)
        else:
            debugPrint("Filling %s zeroes"% device.path)

