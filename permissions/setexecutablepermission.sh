#!/bin/sh
if [ -z "$1" ]; then
    echo "usage: find . -type f -perm +111 -exec $0 {} \;"
    echo "Checks if file is executable, and if not, removes executable bit"
    exit 1;
fi
# usage: find . -type f -perm +111 -name -exec $0 {} \;
# only read first line to avoid multi-line information on files (e.g. for 'Mach-O universal binary with 3 architectures' 3 extra lines are printed)
ft=`file -b "$1" | head -1`
if ! echo "$ft" | grep -E "^(.*executable|.*(shell|perl|PHP|ruby|python) script.*|DOS batch file|Mach-O .*bundle|Mach-O universal binary)" > /dev/null 2>&1; then
    chmod a-x "$1"
    echo "$1: removed executable bit ($ft)"
fi
