#!/usr/bin/python

import os
import sys
import xml.etree.ElementTree

# validate args
if len(sys.argv) < 2:
    print >> sys.stderr, "usage: sort-filespec.py <filespec>"
    sys.exit("invalid arguments")

# extract args
filespec = sys.argv[1]

# parse stdin into an XML tree
filespectree = xml.etree.ElementTree.parse(filespec)

# setup the dictionary we'll use to sort the filenames
filesdict = dict()

# iterate through the XML elements
for element in filespectree.getroot():
    # get the name attribute
    name = element.get("name")
    # store the XML element using the name as the key
    filesdict[name] = element

# output the header
print '<filespec>'

# iterate through the sorted list
for name in sorted(filesdict.keys()):
    # get the element
    element = filesdict[name]
    # serialize this element
    text = xml.etree.ElementTree.tostring(element)
    # print the xml
    print '   ', text.rstrip()

# output the footer
print '</filespec>'
