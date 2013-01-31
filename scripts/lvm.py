from debug import debugPrint, for_real
from filesystems import ext, reiser, xfs, jfs, swap
from partition import fsMap
import os

class lvg:
    def __init__(self, group_name, device_list):
        self.group_name = group_name
        self.device_list = device_list
        self.logical_volumes = {}

    def pvcreate(self):
        for device in self.device_list:
            if for_real:
                os.system("pvcreate %s" % (device.path))
            else:
                print "Creating physical volume %s" % (device.path)

    def vgcreate(self):
        comm_string = "vgcreate %s" % self.group_name
        for device in self.device_list:
            comm_string += " %s" % device.path
        if for_real:
            os.system(comm_string)
        else:
            print "Creating volume group"

    def vgactivate(self):
        if for_real:
            os.system("vgchange -a y %s" % self.group_name)
        else:
            print "Activating volume group"

    def lvcreate(self, size, name, fs):
        self.logical_volumes[name] = logicalVolume(self,size,name,fs)
        self.logical_volumes[name].create()

    def extents(self):
        f = os.popen("vgdisplay %s" % self.group_name)
        for line in f:
            if line.strip().startswith("Free"):
                free_extents = int(line.split()[4])
            elif line.strip().startswith("Total"):
                total_extents = int(line.split()[2])
            elif line.strip().startswith("VG Size"):
                total_size = int(float(line.split()[-2]))
                if line.split()[-1] == "TB":
                    total_size *= 1099511627776
                elif line.split()[-1] == "GB":
                    total_size *= 1073741842
                elif line.split()[-1] == "MB":
                    total_size *= 1048576
                elif line.split()[-1] == "KB":
                    total_size *= 1024
        return free_extents, total_extents, total_size

class logicalVolume:
    def __init__(self, vg, size, name,fs):
        self.volume_group = vg
        self.size = int(size)
        self.name = name
        self.path = "/dev/mapper/%s-%s" % (vg.group_name, name)
        self.type = fs
        self.fs = self.fileSystem()

    def fileSystem(self):
        return fsMap.get(self.type, lambda x: None)(self)

    def create(self):
        free, total, size = self.volume_group.extents()
        lv_extents = int(min((float(self.size) / size)*total, free))
        if for_real:
            os.system("lvcreate %s -l %s -n %s" % (self.volume_group.group_name, lv_extents, self.name))
        else:
            debugPrint("Creating logical volume")
