#!/usr/bin/python

import os
import tarfile
import sys

# validate args
if len(sys.argv) < 2:
    print >> sys.stderr, "usage: tar-to-fileset.py <tar>"
    sys.exit("invalid arguments")

# extract args
input = sys.argv[1]

# open the tar file
if input.endswith('.gz'):
    tar = tarfile.open(input, "r:gz")
else:
    tar = tarfile.open(input, "r")

print '<filespec>'

# read each file in the tar 
for tarinfo in tar:
    #print "base => " + tarinfo.name, "user=" + tarinfo.uid, "uid=" + str(tarinfo.uid), "group=" + tarinfo.gid, "gid=" + str(tarinfo.gid), "type=" + tarinfo.type, "mode=" + str(oct(tarinfo.mode))
    # see what kind of element this is
    if tarinfo.isfile():
        print '  <file name="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    elif tarinfo.isdir():
        print '  <dir name="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    elif tarinfo.issym():
        print '  <sym name="%s" link="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.linkname, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    elif tarinfo.islnk():    
        print '  <lnk name="%s" link="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.linkname, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    elif tarinfo.ischr():
        print '  <chr name="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    elif tarinfo.isblk():
        print '  <blk name="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    elif tarinfo.isfifo():
        print '  <fifo name="%s" uid="%s" gid="%s" mode="%s" timestamp="%s"/>' % (tarinfo.name, tarinfo.uid, tarinfo.gid, str(oct(tarinfo.mode)), tarinfo.mtime)
    else:
        raise BaseException 

print '</filespec>'
