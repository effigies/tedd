from debug import debugPrint, for_real
import os

class Filesystem(object):
    name = "Generic Filesystem"

    def __init__(self, partition):
        self.partition = partition

    def freeSpace(self):
        debugPrint("%s.freeSpace: Not written!" % self.name)

    def fillPartition(self):
        debugPrint("%s.fillPartition: Not written!" % self.name)

    def shrink(self, newSize):
        debugPrint("%s.shrink: Not Written!" % self.name)

    def format(self, journaling=True):
        debugPrint("%s.format: Not Written!" % self.name)

class TunableFS(Filesystem):
    name = "Tunable Filesystem"

    def __init__(self, partition, formatted=True):
        super(TunableFS, self).__init__(partition)
        if formatted:
            self.free_space, self.free_blocks, self.block_count = self.freeSpace()

# File-system functions for ext2/3
class ext(TunableFS):
    name = "ext"

    # Get the free_space, free_blocks, and block_count
    def freeSpace(self):
        fs_file = os.popen("tune2fs -l %s" % self.partition.path)
        for line in fs_file:
            if line.startswith("Block count:"):
                block_count = float(line.split()[2])
            elif line.startswith("Free blocks:"):
                free_blocks = float(line.split()[2])
            elif line.startswith("Filesystem UUID:"):
                self.uuid = line.split()[-1]
        return int((free_blocks/block_count)*self.partition.size), free_blocks, block_count

    # Shrink to the specified size
    def shrink(self, newSize):
        percent = float(newSize)/self.partition.size
        new_size = int(self.block_count * percent)
        if for_real:
            os.system("e2fsck -f %s" % self.partition.path)
            if os.popen("resize2fs %s %s" % (self.partition.path, new_size)):
                self.partition.size = newSize
                return True
        else:
            debugPrint("Resized %s to %s" % (self.partition.path, new_size))
            self.partition.size = newSize
            return True
        return False

    # Fill the file system to the size of the partition
    def fillPartition(self):
        if for_real:
            os.system("e2fsck -f %s" % self.partition.path)
            os.system("resize2fs %s" % (self.partition.path))
        else:
            debugPrint("Filled available space")

    def format(self, journaling=True):
        if for_real:
            if journaling:
                f = os.popen("mkfs.ext4 -q %s" % (self.partition.path))
            else:
                f = os.popen("mkfs.ext2 -q %s" % (self.partition.path))
            f.close()
            self.free_space, self.free_blocks, self.block_count = self.freeSpace()
        else:
            debugPrint("Formatted ext volume")

# File-system functions for reiserfs
class reiser(TunableFS):
    name = "reiser"

    # Get free space, blocks, and block count
    def freeSpace(self):
        fs_file = os.popen("df")
        for line in fs_file:
            if line.startswith(self.partition.path):
                free_blocks = float(line.split()[3])
                block_count = float(line.split()[1])
                fs_file.close()
                return int((free_blocks/block_count)*self.partition.size), free_blocks, block_count
        fs_file.close()
        fs_file = os.popen("reiserfstune %s" % self.partition.path)
        for line in fs_file:
            if line.startswith("Free blocks"):
                free_blocks = float(line.split()[-1])
            elif line.startswith("Count of blocks"):
                block_count = float(line.split()[-1])
            elif line.startswith("UUID:"):
                self.uuid = line.split()[-1]
        try:
            return int((free_blocks/block_count)*self.partition.size), free_blocks, block_count
        except NameError:
            return (0, 0, 0)

    # Shrink the file system to the specified size
    def shrink(self, newSize):
        print newSize
        if for_real:
            debugPrint("yes | resize_reiserfs -s %s %s" % (newSize, self.partition.path))
            if not os.system("yes | resize_reiserfs -s %s %s" % (newSize, self.partition.path)):
                self.partition.size = newSize
                return True
        else:
            debugPrint("Resized %s to %s" % (self.partition.path, new_size))
            self.partition.size = newSize
            return True
        return False

    # Grow the filesystem to fill the partition
    def fillPartition(self):
        if for_real:
            debugPrint("resize_reiserfs %s" % (self.partition.path))
            os.system("yes | resize_reiserfs %s" % (self.partition.path))
        else:
            debugPrint("Filled available space")

    def format(self):
        if for_real:
            os.system("mkfs.reiserfs -q %s" % (self.partition.path))
        else:
            debugPrint("Formatted reiser volume")
        self.free_space, self.free_blocks, self.block_count = self.freeSpace()

class jfs(Filesystem):
    name = "jfs"

    def format(self):
        if for_real:
            os.system("mkfs.jfs -q %s" % (self.partition.path))
        else:
            debugPrint("Formatted %s volume" % (self.name))

class xfs(Filesystem):
    name = "xfs"

    def format(self):
        if for_real:
            os.system("mkfs.xfs -qf %s" % (self.partition.path))
        else:
            debugPrint("Formatted %s volume" % (self.name))

class swap(Filesystem):
    name = "swap"

    def format(self):
        if for_real:
            os.system("mkswap %s" % (self.partition.path))
        else:
            debugPrint("Formatted %s volume" % (self.name))

