#!/usr/bin/python

import os
import sys
import xml.etree.ElementTree

# parse stdin into an XML tree
filespectree = xml.etree.ElementTree.parse(sys.stdin)

# setup the dictionary we'll use to sort the filenames
filesdict = dict()

# setup the list of hard links
hardlinks = []

# iterate through the XML elements
for element in filespectree.getroot():
    # if this is a hard link it needs special handling
    if element.tag == "lnk":
        hardlinks.append(element)
    else:
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

# iterate through the hard links
for element in hardlinks:
    # serialize this element
    text = xml.etree.ElementTree.tostring(element)
    # print the xml
    print '   ', text.rstrip()

# output the footer
print '</filespec>'
