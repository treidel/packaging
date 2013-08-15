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
tar = tarfile.open(input, "r:gz")

print '<filespec>'

# read each file in the tar 
for tarinfo in tar:
    #print "base => " + tarinfo.name, "user=" + tarinfo.uname, "uid=" + str(tarinfo.uid), "group=" + tarinfo.gname, "gid=" + str(tarinfo.gid), "type=" + tarinfo.type, "mode=" + str(oct(tarinfo.mode))
    # see what kind of element this is
    if tarinfo.isfile():
        print '  <file name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    elif tarinfo.isdir():
        print '  <dir name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    elif tarinfo.issym():
        print '  <sym name="%s" link="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.linkname, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    elif tarinfo.islnk():    
        print '  <lnk name="%s" link="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.linkname, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    elif tarinfo.ischr():
        print '  <chr name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    elif tarinfo.isblk():
        print '  <blk name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    elif tarinfo.isfifo():
        print '  <fifo name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
    else:
        raise BaseException 

print '</filespec>'
