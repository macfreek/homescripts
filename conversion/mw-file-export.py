#!/usr/bin/env python

"""
Parse a XML as downloaded from the Special:Export page of your wiki,
and export the individual pages as files.

Does not support downloading Images.
"""

import sys
import re
import xml.etree.ElementTree as ET
import os

if len(sys.argv) <= 1:
    sys.stderr.write("Usage: %s MEDIAWIKI-XML-FILE [EXPORT-FOLDER]\n" % (sys.argv[0]))
    sys.stderr.write("   MEDIAWIKI-XML-FILE: XML retrieved from the Special:Export page of a Mediawiki.\n")
    sys.exit(1)

filename = sys.argv[1]
extension = '.mediawiki'

if len(sys.argv) >= 3:
    exportpath = sys.argv[2]
    if not os.path.exists(exportpath):
        os.mkdir(exportpath)

else:
    exportpath = os.path.dirname(filename)

tree = ET.parse(filename)
root = tree.getroot()
# Find namespace
if root.tag[0] == '{':
    try:
        ns, tag = root.tag[1:].split('}')
        ns = '{'+ns+'}'
    except IndexError:
        ns = ''
        tag = root.tag
else:
    ns = ''
    tag = root.tag
if tag != 'mediawiki':
    sys.stderr.write("File is not a Mediawiki XML export (root element is %r instead of 'mediawiki')\n" % (tag))
    sys.exit(1)

for child in root.findall(ns+'page'):
    try:
        title = child.find(ns+'title').text
    except AttributeError:
        continue
    try:
        contents = child.findtext(ns+'revision/'+ns+'text')
    except AttributeError:
        sys.stderr.write("Can not find contents for lemma %r" % (title))
        continue
    filename = os.path.join(exportpath, re.sub('[^\w]+', '_', title).strip("_") + extension)
    print(title, filename, len(contents))
    
    file = open(filename, 'wb')
    file.write(contents.encode("utf-8"))
    file.close()

