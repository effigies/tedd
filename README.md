# Transparent Emergency Data Destruction

## Original Author's Note
This is the source for a project I wrote in college. I published a paper
regarding this process enttiled Transparent Emergency Data Destruction in the
proceedings of the 5th International Conference on Information Warfare and 
security. I subsequently requested permission to publish the source, and the
University's Intellectual Property Committee never gave me an answer. Upon 
reviewing the University's Intellectual Property Policy, I have concluded that
I, as the author of this software, own copyright and thus the right to 
distribute the software under a license I see fit. If anyone from the 
University disagrees with this assessment, please contact me to resolve the 
issue.

The components I developed (in the scripts/ folder) are licensed under the BSD 
license. `mcrypt`, and `mkfs.xfs` are licensed under the GNU GPL (these are
invoked as separate processes and are not linked with the installer).

While I am making this source available, I am unable to support or maintain it 
further. I will not accept any maintenance patches, but would invite interested
parties to create their own forks.

## Compilation

To build TEDD the following dependnecies must be met.

* build-essential
* libtool
* automake1.4
* automake1.7
* libmcrypt-dev
* libmhash-dev
* gettext
* uuid-dev
* zlib1g-dev

Run `./configure`, then run `make`.

This will compile static binaries for `xfs.mkfs`, `mcrypt`, and `getpass`.
Then, it will create a `.tar.gz` containing all files necessary for installing
TEDD. Finally, it will combine the `.tar.gz` file with `tedd.sh`, creating a
self-unpacking installer, `tedd.bundle`. The only file that needs to be
distributed to end users is tedd.bundle.

At the time of this writing, TEDD supports Ubuntu 8.10, both 32-bit and 64-bit 
architectures. If the `tedd.bundle` package is built on a 32-bit system, the
same package can be used on 32-bit or 64-bit systems. If the `tedd.bundle`
package is built on a 64-bit system, it will only work on 64-bit systems.

## Installation

Before installing TEDD, the user should do a fresh installation of Linux. The 
user may choose to run system updates and configure the base installation. Any 
changes made before installing TEDD will persist after the duress password has 
been used.

Once the base system has been configured to your satisfaction, reboot to a Live
CD. Download `tedd.bundle` to the system running the Live CD. Open a terminal
and navigate to the folder containing tedd.bundle. Run

    $ sh tedd.bundle

The installer will start up.

First it will ask you which disk contains your Linux installation. Type in the
full path to the disk (not the partition) containing your device.

Next, it will look at the partitions on the disk and identify any that have
Linux installed. Unless you know otherwise, accept the default value.

Next it will prompt you to delete any swap partitions. This is very important.
If you allow your system to swap, your encryption key may be written to the hard
disk. If your swap is not encrypted, your key may be written in plain-text, 
allowing a competent investigator to unlock your encrypted drive without your
passphrase. If your swap partition was in an extended partition, you will also 
be prompted to delete the now empty extended partition.

Next, TEDD will shrink your Linux installation. TEDD prevents changes from 
being written to the base operating system. There is no reason to keep extra
space on the base partition, and we want plenty of room to store changes. Unless
you left empty space during the initial installation, allow TEDD to shrink this
partition. This will take some time.

You will be prompted to random-fill your encrypted partition. If you do not do
this, it may be possible for an adversary to determine that you have used your
duress password. Unless you have done this in the past, select option 1. This 
will take approximately 4.5 minutes per gigabyte, depending on your system.

When the drive has been filled with random data, you will be asked for your 
access password. This will be the password that encrypts your hard drive, and it
is the one you will use to boot your computer. You should make the password very
strong. The internet has numerous guides on choosing a good password.

Now you will be prompted to choose a size for your encrypted swap. By default,
the swap will be the same size as the swap you deleted early on.

Next, you will be prompted to choose a size for your encrypted overlay. The 
default value will be the difference between the size of the encrypted partition
and the space already allocated to swap. You cannot choose a number bigger than
the default, but if you want to create other volumes later, you may make this 
number smaller.

You will then be prompted to choose a file system for the encrypted overlay.
This requires a static binary, and at this the only available option is XFS.
Select option 1 to continue.

You will be asked which `initrd` file you use. This will look in the `/boot`
folder, and select the one with the highest kernel version. If this is not the
correct image, type the file name, otherwise just hit enter.

Now you must choose your duress password. This is the password you will enter
when you want to discreetly destroy your private information. This should be a
convincingly strong password. It must be something you can remember an
emergency, but should be something you would never type by accident.

Finally you will be prompted to enter a guest password.
