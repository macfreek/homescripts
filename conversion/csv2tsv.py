#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CVS to TSV converter.

Convert a CSV formatted file (comma separated values) to a TSV formatted file (tab separated values).

Usage:
   cvs2tsv.py < comma-delimited-file.txt > tab-delimited-file.txt

The CSV format is described in RFC 4180 <https://tools.ietf.org/html/rfc4180>.
The TSV format is described in e.g. <http://www.iana.org/assignments/media-types/text/tab-separated-values> or <http://www.cs.tut.fi/~jkorpela/TSV.html>

Author:
Freek Dijkstra <software@macfreek.nl>

License:
Contributed to public domain.
"""

import sys
import os
import optparse
import csv

reader = csv.reader(sys.stdin, 'excel')
writer = csv.writer(sys.stdout, 'excel-tab')
try:
    for row in reader:
        writer.writerow(row)
except csv.Error as e:
    sys.exit('line %d: %s' % (reader.line_num, e))

