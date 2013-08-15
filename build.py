#!/usr/bin/python

import argparse
import os
import tarfile
import tempfile
import sys
import xml.etree.ElementTree
import subprocess
import glob
 
# parse the arguments
parser = argparse.ArgumentParser(description="build script for leveling-glass images")
parser.add_argument('--output', required=True)
parser.add_argument('--boot-files', required=True)
parser.add_argument('--filespec', nargs="+", required=True)
args = parser.parse_args()

# figure out the path to the staging
staging = os.path.abspath(os.path.dirname(sys.argv[0])) + "/staging"

# create a temporary tar file
tmpfileinfo = tempfile.mkstemp(suffix=".tar")
tmpfile = os.fdopen(tmpfileinfo[0], 'wb')
tmpfilename = tmpfileinfo[1]
print >> sys.stderr, "created temporary tar " + tmpfilename

# wrap the temp file as a tar
tar = tarfile.open(fileobj=tmpfile, mode='w')

# wrap this in an exception handler so that we can remove the tar file in exception cases 
try:

    # open each filespec
    for filespec in args.filespec:
        # open the filespec
        print >> sys.stderr, "opening filespec " + filespec
        filespectree = xml.etree.ElementTree.parse(filespec)

        # iterate thru the filespec 
        for element in filespectree.getroot():
            # get the common attributes
            name = element.get("name")
            user = element.get("user")
            group = element.get("group")
            mode = int(element.get("mode"), 8)
            time = int(element.get("time"))
            print >> sys.stderr, "fileset => " + name, "user=" + user, "group=" + group, "type=" + element.tag, "mode=" + str(oct(mode))
            # setup the tarinfo object
            tarinfo = tarfile.TarInfo(name)
            tarinfo.mtime = time
            tarinfo.uname = user
            tarinfo.gname = group
            tarinfo.mode = mode

            # do different things depending on the type of entry we found
            if element.tag == "file":
                tarinfo.type = tarfile.REGTYPE
                # open the file for this entry
                file = open(staging + "/" + name, 'r')
                # populate the size
                tarinfo.size = file.size()
                # add the file to the tar
                tar.addfile(tarinfo, file)
                # close the file
                file.close()
            elif element.tag == "dir":
                tarinfo.type = tarfile.DIRTYPE
                tar.addfile(tarinfo)
            elif element.tag == "sym":
                tarinfo.type = tarfile.SYMTYPE
                tarinfo.linkname = element.get("link")
                tar.addfile(tarinfo)
            elif element.tar == "lnk":
                tarinfo.type = tarfile.LNKTYPE
                tarinfo.linkname = element.get("link")
                tar.addfile(tarinfo)
            elif element.tar == "chr":
                tarinfo.type = tarfile.CHRTYPE
                tar.addfile(tarinfo)
            elif element.tar == "blk":
                tarinfo.type = tarfile.BLKTYPE
                tar.addfile(tarinfo)
            elif element.tar == "fifo":
                tarinfo.type = tarfile.FIFOTYPE
                tar.addfile(tarinfo)
            else:
                raise BaseException("invalid tag=" + element.tag)

    # close the temporary tar
    tar.close()

    # figure out the list of boot files 
    bootfiles = glob.glob(args.boot_files + "/*")

    # generate the image
    subprocess.call(["./mk-disk.py", "--output", args.output, "--tar", tmpfilename, "--boot-files"] + bootfiles) 

except:
    # close + remove the temporary tar
    tar.close()
    os.remove(tmpfilename)
    # re-raise the exception
    raise

# remove the temporary tar
print >> sys.stderr, "removing temporary tar ", tmpfilename
os.remove(tmpfilename)

print >> sys.stderr, "finished creating", args.output
