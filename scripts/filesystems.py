from debug import debugPrint, for_real
import os
from subprocess import Popen, call, PIPE


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

    def format(self):
        if for_real:
            call(self.formatter + [self.partition.path])
        else:
            debugPrint("Formatted %s volume" % (self.name))


class TunableFS(Filesystem):
    name = "Tunable Filesystem"

    def __init__(self, partition, formatted=True):
        super(TunableFS, self).__init__(partition)
        if formatted:
            self.free_space, self.free_blocks, self.block_count = \
                self.freeSpace()

    def format(self):
        super(TunableFS, self).format()
        self.free_space, self.free_blocks, self.block_count = self.freeSpace()


# File-system functions for ext2/3
class ext(TunableFS):
    name = "ext"

    # Get the free_space, free_blocks, and block_count
    def freeSpace(self):
        tune2fs = Popen(['tune2fs', '-l', self.partition.path], stdout=PIPE)
        fs_file = tune2fs.stdout
        for line in fs_file:
            if line.startswith("Block count:"):
                block_count = float(line.split()[2])
            elif line.startswith("Free blocks:"):
                free_blocks = float(line.split()[2])
            elif line.startswith("Filesystem UUID:"):
                self.uuid = line.split()[-1]
        return int((free_blocks / block_count) * self.partition.size), \
            free_blocks, block_count

    # Shrink to the specified size
    def shrink(self, newSize):
        percent = float(newSize)/self.partition.size
        new_size = int(self.block_count * percent)
        if for_real:
            call(['e2fsck', '-f', self.partition.path])
            if call(['resize2fs', self.partition.path, new_size]) == 0:
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
            call(['e2fsck', '-f', self.partition.path])
            call(['resize2fs', self.partition.path])
        else:
            debugPrint("Filled available space")

    def format(self, journaling=True):
        if for_real:
            cmd = 'mkfs.ext4' if journaling else 'mkfs.ext2'
            call([cmd, '-q', self.partition.path])
            self.free_space, self.free_blocks, self.block_count = \
                self.freeSpace()
        else:
            debugPrint("Formatted ext volume")


# File-system functions for reiserfs
class reiser(TunableFS):
    name = "reiser"
    formatter = ['mkfs.reiserfs', '-q']

    # Get free space, blocks, and block count
    def freeSpace(self):
        df = Popen('df', stdout=PIPE)
        for line in df.stdout:
            if line.startswith(self.partition.path):
                free_blocks = float(line.split()[3])
                block_count = float(line.split()[1])
                fs_file.close()
                space = int(free_blocks * self.partition.size / block_count)
                return space, free_blocks, block_count
        df.wait()

        reiserfstune = Popen(['reiserfstune', self.partition.path],
                             stdout=PIPE)
        for line in reiserfstune.stdout:
            if line.startswith("Free blocks"):
                free_blocks = float(line.split()[-1])
            elif line.startswith("Count of blocks"):
                block_count = float(line.split()[-1])
            elif line.startswith("UUID:"):
                self.uuid = line.split()[-1]
        reiserfstune.wait()
        try:
            return int(free_blocks * self.partition.size / block_count), \
                free_blocks, block_count
        except NameError:
            return 0, 0, 0

    # Shrink the file system to the specified size
    def shrink(self, newSize):
        print newSize
        if for_real:
            debugPrint("yes | resize_reiserfs -s {} {}".format(
                newSize, self.partition.path))
            yes = Popen('yes', stdout=PIPE)
            if call(['resize_reiserfs', '-s', newSize, self.partition.path],
                    stdin=yes.stdout) == 0:
                self.partition.size = newSize
                return True
        else:
            debugPrint("Resized {} to {}%s".format(self.partition.path,
                                                   newSize))
            self.partition.size = newSize
            return True
        return False

    # Grow the filesystem to fill the partition
    def fillPartition(self):
        if for_real:
            debugPrint('resize_reiserfs ' + self.partition.path)
            yes = Popen('yes', stdout=PIPE)
            call(['resize_reiserfs', self.partition.path], stdin=yes.stdout)
        else:
            debugPrint("Filled available space")


class jfs(Filesystem):
    name = "jfs"
    formatter = ['mkfs.jfs', '-q']


class xfs(Filesystem):
    name = "xfs"
    formatter = ['mkfs.xfs', '-qf']


class swap(Filesystem):
    name = "swap"
    formatter = ['mkswap']
