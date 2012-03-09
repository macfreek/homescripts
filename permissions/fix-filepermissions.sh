#!/bin/sh

# Remove junk files
find /Users -name "SyncTemp*" -exec rm -f {} \; -exec echo '{}: deleted' \;
find /Users -name ".AppleDouble" -exec rm -rf {} \; -exec echo '{}: deleted' \;

# find world writable files
find /Users/freek /Users/caroline /Users/Shared -perm +002 ! -type l -exec chmod o-w {} \; -exec echo '{}: removed world writable bit' \;
if [ -d "/Volumes/Media" ]; then
    find /Volumes/Media -perm +002 ! -type l -exec chmod o-w {} \;
fi

# find executable files, which are not really an executable
executablepermissionscript=`dirname "$0"`/setexecutablepermission.sh
find /Users -type f -perm +111 -exec $executablepermissionscript {} \;

# find files with incorrect owner
find /Users/freek    ! -user freek    -exec chown -h freek {} \;    -exec echo '{}: changed to owner freek' \;
find /Users/caroline ! -user caroline -exec chown -h caroline {} \; -exec echo '{}: changed to owner caroline' \;
find /Users          ! -group staff   -exec chgrp -h staff {} \;    -exec echo '{}: changed to group staff' \;
if [ -d "/Volumes/Media" ]; then
    find /Volumes/Media  ! -group staff -o ! -user freek -exec chown -h freek:staff {} \;
fi
