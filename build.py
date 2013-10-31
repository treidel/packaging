#!/usr/bin/python

import argparse
import os
import tarfile
import tempfile
import sys
import xml.etree.ElementTree
import subprocess
import glob
import time
import ConfigParser

# parse the arguments
parser = argparse.ArgumentParser(description="build script for leveling-glass images")
parser.add_argument('--output', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--staging', nargs="+", required=True)
args = parser.parse_args()

# figure out the path(s) to the staging
if (1 >= len(args.staging)): 
    stagings = glob.glob(args.staging[0])
else:
    stagings = args.staging

# parse the config file
config = ConfigParser.RawConfigParser()
config.read(args.config)

# extract the config file params
bootpath = os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + config.get('disk', 'boot_path');
filespecs = config.get('disk', 'filespecs').split(" ");

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
    for filespec in filespecs:
        # open the filespec
        filespecpath =  os.path.abspath(os.path.dirname(sys.argv[0])) + "/filespecs/" + filespec
        print >> sys.stderr, "reading filespec " + filespecpath
        filespectree = xml.etree.ElementTree.parse(filespecpath)

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
            print >> sys.stderr, filespec, "=>", name.encode("utf-8"), "uid=" + str(uid), "gid=" + str(gid), "type=" + str(element.tag), "mode=" + str(oct(mode)), "timestamp=" + str(timestamp)
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

    # close the temporary tar
    tar.close()

    # figure out the list of boot files 
    bootfiles = glob.glob(boot + "/*")

    # generate the image
    cmd = ["./mk-disk.py", "--output", args.output, "--tar", tmpfilename, "--boot-files"] + bootfiles
    print >> sys.stderr, "executing:", ' '.join(cmd)
    subprocess.call(cmd) 

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
