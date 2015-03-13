from debug import debugPrint, for_real
from partition import fsMap
from subprocess import call, Popen, PIPE


FACTOR = {'KiB': 2 ** 10,
          'GiB': 2 ** 20,
          'MiB': 2 ** 30,
          'TiB': 2 ** 40}


class lvg:
    def __init__(self, group_name, device_list):
        self.group_name = group_name
        self.device_list = device_list
        self.logical_volumes = {}

    def pvcreate(self):
        for device in self.device_list:
            args = ['pvcreate', device.path]
            if for_real:
                call(args)
            else:
                print 'Creating physical volume: ' + ' '.join(args)

    def vgcreate(self):
        if for_real:
            call(['vgcreate', self.group_name] +
                 [device.path for device in self.device_list])
        else:
            print "Creating volume group"

    def vgactivate(self):
        if for_real:
            call(['vgchange', '-a', 'y', self.group_name])
        else:
            print "Activating volume group"

    def lvcreate(self, size, name, fs):
        self.logical_volumes[name] = logicalVolume(self, size, name, fs)
        self.logical_volumes[name].create()

    def extents(self):
        pipe = Popen(['vgdisplay', self.group_name], stdout=PIPE)
        for line in pipe.stdout:
            if line.strip().startswith("Free"):
                free_extents = int(line.split()[4])
            elif line.strip().startswith("Total"):
                total_extents = int(line.split()[2])
            elif line.strip().startswith("VG Size"):
                base, unit = line.split()[-2:]
                total_size = int(float(base)) * FACTOR[unit]
        return free_extents, total_extents, total_size


class logicalVolume:
    def __init__(self, vg, size, name, fs):
        self.volume_group = vg
        self.size = int(size)
        self.name = name
        self.type = fs
        self.fs = self.fileSystem()

    def fileSystem(self):
        return fsMap.get(self.type, lambda x: None)(self)

    def create(self):
        free, total, size = self.volume_group.extents()
        lv_extents = int(min((float(self.size) / size)*total, free))
        if for_real:
            call(['lvcreate', self.volume_group.group_name, '-l', lv_extents,
                  '-n', self.name])
        else:
            debugPrint("Creating logical volume")

    @property
    def path(self):
        return "/dev/mapper/{}-{}".format(self.volume_group.group_name,
                                          self.name)
