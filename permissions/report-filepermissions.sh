#!/bin/sh

# find world writable files
find /Users/freek /Users/caroline /Users/Shared -perm +002 ! -type l -exec echo '{}: world writable' \;
if [ -d "/Volumes/Media" ]; then
    find /Volumes/Media -perm +002 ! -type l -exec echo '{}: world writable' \;
fi

# find group writable files
# find /Users/freek /Users/caroline -perm +020 ! -type l -exec echo '{}: group writable' \;

# find non-executable folders
find /Users -type d ! -perm -500 -exec echo '{}: not browsable or readable' \;

# find executable files, which are not really an executable
executablepermissionscript=`dirname "$0"`/reportexecutablepermission.sh
find /Users -type f -perm +111 -exec $executablepermissionscript {} \;

# find files with incorrect owner
find /Users/freek    ! -user freek    -exec echo '{}: not owned by freek' \;
find /Users/caroline ! -user caroline -exec echo '{}: not owned by caroline' \;
find /Users          ! -group staff   -exec echo '{}: not owned by group staff' \;
if [ -d "/Volumes/Media" ]; then
    find /Volumes/Media  ! -group staff -o ! -user freek  -exec echo '{}: not owned by freek:staff' \;
fi

# Check for files with inode creation time near epoch
find . ! -newerBt '1971-01-01' ! -type l -exec echo '{}: inode creation near epoch' \;

# Check for files with inode creation time in the future
find . -Btime -1 -exec echo '{}: inode creation time in future' \;
