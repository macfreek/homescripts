#!/bin/sh
# Compares the list of installed files as reported by dpkg and apt-get to the list
# of actually installed files, and reports if any file is missing
# Created 2012-01-01 Freek Dijkstra. Contributed to public domain.

# Set the item separator to newline only (to support package names with spaces)
OIFS="$IFS"
IFS='
'
# Loop through the installed packages
for pkg in `dpkg --get-selections | grep -v "\bdeinstall" | awk '{ print $1 }'`
do
    # Find the list of installed files for each package
    for f in `dpkg -L "${pkg}"`
    do
        f=`echo "$f" | sed 's/diverted by [a-z0-9\.\-\+]* to: //'`
        f=${f#package diverts others to: }
        if ! [ -e "$f" ]; then
            echo "$f is a missing file in the $pkg package."
        fi
    done
done
IFS="$OIFS"
