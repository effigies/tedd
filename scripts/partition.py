from debug import debugPrint, for_real
from filesystems import ext, reiser, xfs, jfs, swap
import os, math, subprocess, time, sys

from utils import mount_partition, unmount_partition

fsMap = {'ext2':     ext,
         'ext3':     ext,
         'ext4':     ext,
         'reiserfs': reiser,
         'xfs':      xfs,
         'jfs':      jfs,
         'swap':     swap}

class partition:
    # Get the partition path, disk, number and size
    def __init__(self, disk, path):
        print "Creating %s " % path
        self.path = path
        self.logical = False
        self.disk = disk
        self.is_boot = 0
        self.number = int(self.path[len(self.disk.path):])
        self.linux_verified = None
        print "parted %s print" % self.disk.path
        proc = subprocess.Popen("parted %s print" % self.disk.path, shell=True,stdout=subprocess.PIPE, stdin=None)
        x = proc.wait()
        part_file = proc.stdout
        part_info = part_file.readlines()
        if not x:
            found = False
            for line in part_info:
                if line.strip().startswith(str(self.number)):
                    part_info = line.split()
                    found = True
                    break
            if not found:
                self.size = 0
                self.type = None
                self.fs = None
                return
#            part_info = part_info[6].split()
            if part_info[4] == "extended":
                self.size = 0
                self.type = "extended"
            else:
                if part_info[4] == "logical":
                    self.logical = True
                part_size = part_info[3]
                if part_size.lower().endswith("tb"):
                    self.size = float(part_size[:-2])*(1 << 40)
                elif part_size.lower().endswith("gb"):
                    self.size = float(part_size[:-2])*(1 << 30)
                elif part_size.lower().endswith("mb"):
                    self.size = float(part_size[:-2])*(1 << 20)
                elif part_size.lower().endswith("kb"):
                    self.size = float(part_size[:-2])*(1 << 10)
                else:
                    self.size = int(part_size)
                if len(part_info) > 5:
                    self.type = part_info[5]
                else:
                    self.type = None
                self.fs = self.fileSystem()
                
                if self.type in fsMap:
                    self.verifyLinux()
        else:
            self.size = 0
            self.type = None

    def __repr__(self):
	return "<Part: %s>" % self.path

    # Get the file-system specific object
    def fileSystem(self):
        fs = fsMap.get(self.type)
        if fs is not None:
            return fs(self)
        else:
            return None
   
    # Resize the file system, then the partition, then the file system
    def resize(self):
        new_size = int(math.ceil((self.size - self.fs.free_space)*1.1))
        # I've had rounding issues. This *should* take care of them.
        percent = new_size/self.size
        percent *= 100
        percent = math.ceil(percent)/100
        debugPrint(new_size)
        self.fs.shrink(new_size)
        self.getSectors()
        # new_end_sectors = int(self.start_sector + math.ceil(self.num_sectors * percent))
        debugPrint(percent)
        if for_real:
            # This is ugly, but I haven't found a better way to do this
            # Using fdisk -u, it deletes the specified partition, creates a new, primary partition
            # at the same partition number and the same start sector. The new end sector is chosen
            # to make the total partition size slightly larger than the filesystem on board.
            # Then, a new primary partition is created in the empty space following the partition
            # that we just created. Changes are written.
            debugPrint("fdisk -u %s << EOF\nd\n%s\nn\np\n%s\n%s\n+%sK\nw" % (self.disk.path, self.number,self.number,self.start_sector, int(math.ceil(new_size/1024.0))))
            os.system("fdisk -u %s << EOF\nd\n%s\nn\np\n%s\n%s\n+%sK\nw" % (self.disk.path, self.number,self.number,self.start_sector, int(math.ceil(new_size/1024.0))))
        self.fs.fillPartition()

    # Get the number of sectors used by a partition
    def getSectors(self):
        part_file = os.popen("fdisk -l %s" % self.disk.path)
        for line in part_file:
            if line.strip().startswith(self.path):
                debugPrint(line)
                star_offset = 0
                if line.split()[1] == '*':
                    star_offset = 1
                self.start_sector = int(line.split()[1+star_offset])
                self.end_sector = int(line.split()[2+star_offset])    
                self.num_sectors = self.end_sector - self.start_sector
        part_file.close()

    # Determine whether or not Linux is installed on this partition
    def verifyLinux(self,cwd=os.getcwd()):
        if self.linux_verified != None:
            return self.linux_verified
        path, flag = mount_partition(self)
        distrodir = os.path.join(cwd,"scripts","distros")
        if distrodir not in sys.path:
            sys.path.append(distrodir)
        for item in os.listdir(os.path.join(cwd,"scripts","distros")):
            if item.endswith(".py"):
                module = __import__(item[:-3])
                if module.predicate(path):
                    self.linux_verified = module
                    unmount_partition(path, flag)
                    return True
        unmount_partition(path, flag)
        return False
