from debug import debugPrint, for_real
import os

class luksVolume:
    def __init__(self, device, password, mapper_name):
        self.device = device
        self.password = password
        self.mapper_name = mapper_name
        self.path = "/dev/mapper/%s" % mapper_name

    def luksFormat(self):
        if for_real:
            os.system("echo -n %s | cryptsetup luksFormat -q %s " % (self.password, self.device.path))
        else:
            debugPrint("Creating a luks partition")

    def luksOpen(self):
        if for_real:
            os.system("echo -n %s | cryptsetup luksOpen %s %s" % (self.password, self.device.path, self.mapper_name))
        else:
            debugPrint("Creating luks device")

    def luksClose(self):
        if for_real:
            os.system("cryptsetup luksClose %s" % (mapper_name))
        else:
            debugPrint("Closing luks partition")
