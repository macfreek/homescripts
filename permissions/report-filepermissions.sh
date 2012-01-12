#!/bin/sh

# find world writable files
find /Users/freek /Users/caroline /Users/Shared -perm +002 ! -type l -exec echo '{}: world writable' \;
if [ -d "/Volumes/Media" ]; then
    find /Volumes/Media -perm +002 ! -type l -exec echo '{}: world writable' \;
fi

# find executable files, which are not really an executable
find /Users -type f -perm +111 -exec /usr/local/bin/reportexecutablepermission.sh {} \;

# find files with incorrect owner
find /Users/freek    ! -user freek    -exec echo '{}: not owned by freek' \;
find /Users/caroline ! -user caroline -exec echo '{}: not owned by caroline' \;
find /Users          ! -group staff   -exec echo '{}: not owned by group staff' \;
if [ -d "/Volumes/Media" ]; then
    find /Volumes/Media  ! -group staff -o ! -user freek  -exec echo '{}: not owned by freek:staff' \;
fi

# Check for dirs without any executable bit set