from debug import debugPrint, for_real
from subprocess import call


def urandom(device):
    if for_real:
        call(['dd', 'if=/dev/urandom', 'of=' + device.path])
    else:
        debugPrint("Filling {} with random data".format(device.path))
