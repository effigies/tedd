from debug import debugPrint, for_real
from partition import partition
import os

class disk:
    def __init__(self, path):
        self.path = path
        self.partitions = {}
        for i in self.__getPartitions():
            self.partitions[i] = partition(self, i)

    def __repr__(self):
	return "<Disk: %s (%s)>" % (self.path, ','.join(sorted(self.partitions.keys())))

    def __getPartitions(self):
        for i in os.listdir(os.path.dirname(self.path)):
            if i.startswith(os.path.basename(self.path)) and i != os.path.basename(self.path):
                yield os.path.join(os.path.dirname(self.path), i)

    def getSwap(self):
        self.swap_list = []
        for i in self.partitions:
            if self.partitions[i].type == "linux-swap":
                self.swap_list.append(self.partitions[i])
        return self.swap_list

    def disableSwap(self):
        swap_file = open("/proc/swaps")
        for line in swap_file:
            for part in self.swap_list:
                if line.find(part.path) != -1:
                    if for_real:
                        os.system("swapoff %s" % part.path)
                    debugPrint("Disabling %s as swap" % part.path)

    def guessPartition(self):
        for i in self.partitions:
            if self.partitions[i].linux_verified != None:
                return self.partitions[i]
        return False

    def hasBoot(self):
        for i in self.partitions:
            if self.partitions[i].is_boot:
                return i
        return False

    def createPartition(self,size=""):
        num_list = range(1,5)
        for i in self.partitions:
            num_list.remove(self.partitions[i].number)
        os.system("fdisk %s << EOF\nn\np\n%s\n\n%s\nw" % (self.path, num_list[0],size))
        self.partitions["%s%s" % (self.path,num_list[0])] = partition(self, "%s%s" % (self.path,num_list[0]))
        return self.partitions["%s%s" % (self.path,num_list[0])]

    # Deletes any partitions in the list
    def deletePart(self, part_list):
        for part in part_list:
            if for_real:
                os.system("parted %s rm %s" % (part.disk.path, part.number))
            debugPrint("Deleting partition %s%s" % (part.disk.path, part.number))
            if part.path in self.partitions:
                del self.partitions[part.path]
