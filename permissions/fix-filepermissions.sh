#!/bin/sh

# PRE=false
# PRE=echo
PRE=
#DIRS=/Users/freek/Documents /Users/freek/Work /Volumes/Media
DIRS="/Users/freek/Documents /Users/freek/Downloads"
OWNER=freek
GROUP=staff

# Remove junk files
find $DIRS -name "SyncTemp*" -exec echo '{}: junk file' \; -exec $PRE rm -f {} \;
find $DIRS -name ".AppleDouble" -exec echo '{}: junk file' \; -exec $PRE rm -rf {} \;
find $DIRS -name "~\$*" -exec echo '{}: junk file' \; -exec $PRE rm -rf {} \;

# find non-executable folders
find $DIRS -type d ! -perm -500 -exec echo '{}: missing browsable or readable bit' \; -exec $PRE chmod u+rx {} \;

# find world writable files
find $DIRS -perm +002 ! -type l -exec echo "{}: world writable" \; -exec $PRE chmod o-w {} \;

# find executable files, which are not really an executable
executablepermissionscript=`dirname "$0"`/setexecutablepermission.sh
find $DIRS -type f -perm +111 -exec $PRE $executablepermissionscript {} \;

# find files with incorrect owner
# find /Users/freek    ! -user freek    -exec echo '{}: changed to owner freek' \; -exec $PRE chown -h freek {} \;
# find /Users/caroline ! -user caroline -exec echo '{}: changed to owner caroline' \; -exec $PRE chown -h caroline {} \;
# find /Users          ! -group staff   -exec echo '{}: changed to group staff' \; -exec $PRE chgrp -h staff {} \;
find $DIRS  ! -group $GROUP -o ! -user $OWNER -exec echo "{}: not owned by $OWNER:$GROUP" \; -exec $PRE chown -h $OWNER:$GROUP {} \;

