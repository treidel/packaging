#!/usr/bin/python

import argparse
import os
import tarfile
import tempfile
import sys
import re
import xml.etree.ElementTree
import subprocess
import glob
 
# parse the arguments
parser = argparse.ArgumentParser(description="build script for leveling-glass images")
parser.add_argument('--output', required=True)
parser.add_argument('--base', required=True)
parser.add_argument('--filespec', required=True)
args = parser.parse_args()

# figure out the path to the staging
staging = os.path.abspath(os.path.dirname(sys.argv[0])) + "/staging"

# create a temporary tar file
tmpfile = tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False)
print >> sys.stderr, "created temporary tar " + tmpfile.name

# open the base tar file
print >> sys.stderr, "opening base tar " + args.base
basetar = tarfile.open(args.base, "r:gz")

# open the filespec
print >> sys.stderr, "opening filespec " + args.filespec
filespectree = xml.etree.ElementTree.parse(args.filespec)

# wrap the temp file as a tar
tmptar = tarfile.open(fileobj=tmpfile, mode="w:gz")

# read each file in the base tar and add it to the temporary tar
for tarinfo in basetar:
    print "base => " + tarinfo.name, "user=" + tarinfo.uname, "group=" + tarinfo.gname, "type=" + tarinfo.type, "mode=" + str(oct(tarinfo.mode))
    # only extract regular files
    if tarinfo.isfile():
        tmptar.addfile(tarinfo, basetar.extractfile(tarinfo))
    else:
        tmptar.addfile(tarinfo)

# wrap this in an exception handler so that we can remove the tar file in exception rases
try:
    # iterate thru the filespec 
    for element in filespectree.getroot():
        # get the attributes we need
        name = element.get("name")
        user = element.get("user")
        group = element.get("group")
        mode = int(element.get("mode"), 8)
        print >> sys.stderr, "fileset => " + name, "user=" + user, "group=" + group, "type=" + tarfile.REGTYPE, "mode=" + str(oct(mode))
        # open the file for this entry
        file = open(staging + "/" + name, 'r')
        # create a tarinfo object for this file
        tarinfo = tmptar.gettarinfo(fileobj=file)
        # populate the file properties
        tarinfo.name = name
        tarinfo.uname = user
        tarinfo.gname = group
        tarinfo.mode = mode
        # add the file to the tar
        tmptar.addfile(tarinfo, file)
        # close the file
        file.close()
except:
    # close + remove the temporary tar
    tmptar.close()
    os.remove(tmpfile.name)
    # re-raise the exception
    raise

# close the temporary tar
tmptar.close()
tmpfile.close()

# figure out the list of boot files 
bootfiles = glob.glob(os.path.abspath(os.path.dirname(sys.argv[0])) + "/boot/*")

# generate the image
subprocess.call(["./mk-disk.py", "--output", args.output, "--tar", tmpfile.name, "--boot-files"] + bootfiles) 

# remove the temporary tar
print >> sys.stderr, "removing temporary tar ", tmpfile.name
os.remove(tmpfile.name)
