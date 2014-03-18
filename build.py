#!/usr/bin/python

import argparse
import os
import tarfile
import sys
import xml.etree.ElementTree
import subprocess
import glob
import time

# parse the arguments
parser = argparse.ArgumentParser(description="build script to create tar-based OS image")
parser.add_argument('--output', required=True)
parser.add_argument('--file-specs', nargs="+", required=True)
parser.add_argument('--staging', nargs="+", required=True)
args = parser.parse_args()

# figure out the path(s) to the staging
if (1 >= len(args.staging)): 
    stagings = glob.glob(args.staging[0])
else:
    stagings = args.staging

# extract the args
filespecs = args.file_specs
output = args.output

# open the tar file 
tar = tarfile.open(output, mode='w')

# wrap this in an exception handler so that we can remove the tar file in exception cases 
try:
    # open each filespec
    for filespec in filespecs:
        print >> sys.stderr, "reading filespec " + filespec
        filespectree = xml.etree.ElementTree.parse(filespec)

        # iterate thru the filespec 
        for element in filespectree.getroot():
            # get the common attributes
            name = element.get("name")
            uid = int(element.get("uid"))
            gid = int(element.get("gid"))
            mode = int(element.get("mode"), 8)
            # if there isn't a timestamp choose 'now'
            if element.get("timestamp") is None:
                timestamp = time.time()
            else:
                timestamp = int(element.get("timestamp"))
            # output a log for this element
            print >> sys.stdout, filespec, "=>", name.encode("utf-8"), "uid=" + str(uid), "gid=" + str(gid), "type=" + str(element.tag), "mode=" + str(oct(mode)), "timestamp=" + str(timestamp)
            # setup the tarinfo object
            tarinfo = tarfile.TarInfo(name)
            tarinfo.uid = uid
            tarinfo.gid = gid
            tarinfo.mode = mode
            tarinfo.mtime = timestamp

            # do different things depending on the type of entry we found
            if element.tag == "file":
                tarinfo.type = tarfile.REGTYPE
                # flag if we found the file
                found = False
                for staging in stagings:
                    # create the full file path 
                    filepath = staging + "/" + name     
                    try:
                        # open the file for this entry
                        file = open(filepath, 'r')
                        # we found the file
                        found = True
                        # populate the size based on the file system contents
                        tarinfo.size = os.path.getsize(filepath)
                        # add the file to the tar
                        tar.addfile(tarinfo, file)
                        # close the file
                        file.close()
                        # bail out of loop
                        break
                    except:
                        # just continue on to try the next staging path
                        continue
                # if the file isn't found abort
                if found == False:
                    raise BaseException("can not find in staging file=" + name)
            elif element.tag == "dir":
                tarinfo.type = tarfile.DIRTYPE
                tar.addfile(tarinfo)
            elif element.tag == "sym":
                tarinfo.type = tarfile.SYMTYPE
                tarinfo.linkname = element.get("link")
                tar.addfile(tarinfo)
            elif element.tag == "lnk":
                tarinfo.type = tarfile.LNKTYPE
                tarinfo.linkname = element.get("link")
                tar.addfile(tarinfo)
            elif element.tag == "chr":
                tarinfo.type = tarfile.CHRTYPE
                tar.addfile(tarinfo)
            elif element.tag == "blk":
                tarinfo.type = tarfile.BLKTYPE
                tar.addfile(tarinfo)
            elif element.tag == "fifo":
                tarinfo.type = tarfile.FIFOTYPE
                tar.addfile(tarinfo)
            else:
                raise BaseException("invalid tag=" + element.tag)

    # close the tar
    tar.close()

except:
    # close + remove the temporary tar
    tar.close()
    os.remove(output)
    # re-raise the exception
    raise

print >> sys.stderr, "finished creating", output 
