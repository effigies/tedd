from debug import debugPrint, for_real
from partition import partition
import os
from subprocess import Popen, call, PIPE


class disk:
    def __init__(self, path):
        self.path = path
        self.partitions = {}
        for i in self.__getPartitions():
            self.partitions[i] = partition(self, i)

    def __repr__(self):
        return "<Disk: {} ({})>".format(
            self.path, ','.join(sorted(self.partitions.keys())))

    def __getPartitions(self):
        for i in os.listdir(os.path.dirname(self.path)):
            if i.startswith(os.path.basename(self.path)) and \
                    i != os.path.basename(self.path):
                yield os.path.join(os.path.dirname(self.path), i)

    def getSwap(self):
        self.swap_list = [part for part in self.partitions
                          if part.type == 'linux-swap']
        return self.swap_list

    def disableSwap(self):
        with open('/proc/swaps') as swap_file:
            for line in swap_file:
                for part in self.swap_list:
                    if line.find(part.path) != -1:
                        if for_real:
                            call(['swapoff', part.path])
                        debugPrint("Disabling %s as swap" % part.path)

    def guessPartition(self):
        for i in self.partitions:
            if self.partitions[i].linux_verified is not None:
                return self.partitions[i]
        return False

    def hasBoot(self):
        return any(part.is_boot for part in self.partitions)

    def createPartition(self, size=""):
        num_list = range(1, 5)
        for i in self.partitions:
            num_list.remove(self.partitions[i].number)

        pipe = Popen(['fdisk', self.path], stdin=PIPE)
        pipe.stdin.write('n\np\n{}\n\n{}w'.format(num_list[0], size))
        pipe.stdin.close()
        pipe.wait()

        label = self.path + num_list[0]
        self.partitions[label] = partition(self, label)
        return self.partitions[label]

    # Deletes any partitions in the list
    def deletePart(self, part_list):
        for part in part_list:
            if for_real:
                call(['parted', part.disk.path, 'rm', part.number])
            debugPrint("Deleting partition " + part.disk.path + part.number)
            if part.path in self.partitions:
                del self.partitions[part.path]
