#!/usr/bin/python

import argparse
import os
import guestfs
import ConfigParser
 
# parse the arguments
parser = argparse.ArgumentParser(description="create a bootable disk image for beaglebone black")
parser.add_argument('--output', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--tar', required=True)
parser.add_argument('--boot-file-path', required=True)
args = parser.parse_args()

# extract args    
output = args.output

# parse the config file
config = ConfigParser.RawConfigParser()
config.read(args.config)

# extract config params
sizeinmb = config.getint('disk', 'size_in_mb')
partition_1_start = config.getint('boot', 'start')
partition_1_end = config.getint('boot', 'end')
partition_2_start = config.getint('update', 'start')
partition_2_end = config.getint('update', 'end')
partition_3_start = config.getint('bank1', 'start')
partition_3_end = config.getint('bank1', 'end')
partition_4_start = config.getint('bank2', 'start')
partition_4_end = config.getint('bank2', 'end')

# look recursively for all files in the boot file path
bootpath = os.path.abspath(args.boot_file_path)
bootfiles = []
for root, subFolders, files in os.walk(bootpath):
    for file in files:
        bootfiles.append(root[len(bootpath):] + "/" + file)

# wrap in a try/catch so that we can clean up in case of errors
try:
    # create an instance of the libguestfs API binding
    g = guestfs.GuestFS()
 
    # Create a raw-format sparse disk image, 1024 MB in size.
    f = open (output, "w")
    f.truncate (sizeinmb * 1024 * 1024)
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
    # partition #1: FAT (type=12)
    # partition #2: LINUX
    # partition #3: LINUX
    g.part_init(device, "mbr")
    g.part_add(device, "primary", partition_1_start, partition_1_end)
    g.part_set_mbr_id(device, 1, 12)
    g.part_set_bootable(device, 1, 1)
    g.part_add(device, "primary", partition_2_start, partition_2_end)
    g.part_add(device, "primary", partition_3_start, partition_3_end)
    g.part_add(device, "primary", partition_4_start, partition_4_end)
 
    # get the list of partitions - we expect four
    partitions = g.list_partitions ()
    assert (len(partitions) == 4)

    # cache the actual partitions
    bootpartition = partitions[0]
    updatepartition = partitions[1]
    bank1partition = partitions[2]
    bank2partition = partitions[3]
 
    # create a VAT filesystem on the first partition
    g.mkfs("vfat", bootpartition)

    # create EXT4 filesystems on the rest 
    g.mkfs("ext4", updatepartition)
    g.mkfs("ext4", bank1partition)
    g.mkfs("ext4", bank2partition)

    # set the volume labels
    g.set_e2label(updatepartition, "update")
    g.set_e2label(bank1partition, "bank1")
    g.set_e2label(bank2partition, "bank2")

    # query the UUIDs for the bank partitions
    bank1uuid = g.vfs_uuid(bank1partition)
    bank2uuid = g.vfs_uuid(bank2partition)

    # mount the 1st linux partition
    g.mount(bank1partition, "/")

    # extract the tar
    g.tar_in(args.tar, "/")

    # open the fstab file and write in the uuid
    g.aug_init("/", 0)
    g.aug_load()
    g.aug_set("/files/etc/fstab/1/spec", "UUID=" + bank1uuid)
    g.aug_save()
    g.aug_close()
    
    # umount the 1st linux partition 
    g.umount("/")

    # mount the 2nd linux partition 
    g.mount(bank2partition, "/")

    # extract the tar
    g.tar_in(args.tar, "/")

    # open the fstab file and write in the uuid
    g.aug_init("/", 0)
    g.aug_load()
    g.aug_set("/files/etc/fstab/1/spec", "UUID=" + bank2uuid)
    g.aug_save()
    g.aug_close()

    # umount the 2nd linux partition
    g.umount("/")

    # now mount the boot partition
    g.mount(bootpartition, "/")

    # copy over the boot files
    for bootfile in bootfiles:
        # get the directory part of the bootfile
        directory = os.path.dirname(bootfile)
        # make sure the directory exists
        g.mkdir_p(directory)
        # upload the file into the file system
        g.upload(bootpath + bootfile, bootfile)

except:
    # remove the output file since it was no successful
    os.remove(output)
    # re-raise the exception
    raise
