from debug import debugPrint, for_real
from disk import disk

import os

def urandom(device):
        if for_real:
            os.system("dd if=/dev/urandom of=%s" % device.path)
        else:
            debugPrint("Filling %s with random data"% device.path)
