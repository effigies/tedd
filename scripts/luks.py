from debug import debugPrint, for_real
from subprocess import Popen, call, PIPE


class luksVolume:
    def __init__(self, device, password, mapper_name):
        self.device = device
        self.password = password
        self.mapper_name = mapper_name
        self.path = "/dev/mapper/%s" % mapper_name

    def luksFormat(self):
        if for_real:
            cryptsetup = Popen(['cryptsetup', 'luksFormat', '-q',
                                self.device.path], stdin=PIPE)
            cryptsetup.stdin.write(self.password)
            cryptsetup.stdin.close()
            cryptsetup.wait()
        else:
            debugPrint("Creating a luks partition")

    def luksOpen(self):
        if for_real:
            cryptsetup = Popen(['cryptsetup', 'luksOpen', self.device.path,
                                self.mapper_name], stdin=PIPE)
            cryptsetup.stdin.write(self.password)
            cryptsetup.stdin.close()
            cryptsetup.wait()
        else:
            debugPrint("Creating luks device")

    def luksClose(self):
        if for_real:
            call(['cryptsetup', 'luksClose', self.mapper_name])
        else:
            debugPrint("Closing luks partition")
