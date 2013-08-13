#!/usr/bin/python

import argparse
import os
import guestfs
 
# parse the arguments
parser = argparse.ArgumentParser(description="create a bootable disk image for leveling-glass")
parser.add_argument('--output', required=True)
parser.add_argument('--tar', required=True)
parser.add_argument('--boot-files', nargs="+", required=True)
args = parser.parse_args()

# extract args    
output = args.output

# wrap in a try/catch so that we can clean up in case of errors
try:
    # create an instance of the libguestfs API binding
    g = guestfs.GuestFS()
 
    # Create a raw-format sparse disk image, 1024 MB in size.
    f = open (output, "w")
    f.truncate (1152 * 1024 * 1024)
    f.close ()
 
    # Set the trace flag so that we can see each libguestfs call.
    g.set_trace (1)
 
    # Attach the disk image to libguestfs.
    g.add_drive_opts (output, format = "raw", readonly = 0)
 
    # Run the libguestfs back-end.
    g.launch ()
 
    # Get the list of devices.  Because we only added one drive
    # above, we expect that this list should contain a single
    # element.
    devices = g.list_devices ()
    assert (len (devices) == 1)

    # cache the actual device
    device = devices[0]
 
    # Partition the disk as follows
    # partition #1: FAT, size=16MB, type=12
    # partition #2: LINUX, size=2022 MB
    g.part_init(device, "mbr")
    g.part_add(device, "primary", 32, 32799)
    g.part_set_mbr_id(device, 1, 12)
    g.part_set_bootable(device, 1, 1)
    g.part_add(device, "primary", 32800, 2359295)
 
    # get the list of partitions - we expect two
    partitions = g.list_partitions ()
    assert (len(partitions) == 2)

    # cache the actual partitions
    bootpartition = partitions[0]
    rootfspartition = partitions[1]
 
    # create a VAT filesystem on the first partition
    g.mkfs("vfat", bootpartition)

    # create a EXT3 filesystem on the second partition
    g.mkfs("ext3", rootfspartition)

    # set the volume label
    g.set_e2label(rootfspartition, "rootfs")

    # mount the linux partition
    g.mount(rootfspartition, "/")

    # extract the tar
    g.tar_in(args.tar, "/")

    # umount the linux partition and mount the dos partition
    g.umount("/")
    g.mount(bootpartition, "/")

    # copy over the boot files
    for bootfile in args.boot_files:
        g.upload(os.path.abspath(bootfile), "/" + os.path.basename(bootfile))

except:
    # remove the output file since it was no successful
    os.remove(output)
    # re-raise the exception
    raise
