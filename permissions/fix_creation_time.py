#!/usr/bin/env python3
"""Scan the given directory, and find files or directories (not aliases)
with missing or invalid inode creation date. Report or fix these by 
setting the inode creation date to the file modification date.

WARNING: consider this code flawed.
Right now, it reports the stat.st_birthtime, which works on BSD (including macOS).
However, on Windows, the creation time is stored in stat.ctime, and on Linux, it is stored in stat.cr_time, but that is not made available in the stat.h, so neither in Python.
See e.g. https://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
This difference between operating systems is likely why the creation time is messed up on my file system, what prompted me to write this code.
Unfortunately, there seems no good or easy way to change the creation time of a file, likely for good reasons.
Hence, I gave up on the idea of fixing this. :(
"""

import os
import sys
import argparse
from glob import glob
from os.path import join, normpath, exists, expanduser
import time

def check_inode_time(filename, args):
    """Check inode creation time"""
    try:
        statinfo = os.stat(filename, follow_symlinks=False)
        ctime = os.path.getctime(filename)
        if args.verbose:
            print("{}: {}".format(filename, statinfo.st_birthtime))
        if statinfo.st_birthtime < 1:
            print("{} has no inode creation time".format(filename))
        elif statinfo.st_birthtime > args.future:
            print("{} has inode creation time in the future".format(filename))
        if not args.dryrun:
            pass
    except Exception as e:
        print("{}: {}".format(filename, e))


def loop_directory(directory, args=None, file_func=check_inode_time):
    """Recursively loop the given directory.
    For files, call file_func(file, args)"""
    for root, dirs, files in os.walk(directory, followlinks=False):
        file_func(root, args)
        for name in files:
            file_func(normpath(join(root, name)), args)
        for name in dirs:
            file_func(normpath(join(root, name)), args)


def files_from_argv(args):
    parser = argparse.ArgumentParser(description='Fix invalid inode creation times.')
    parser.add_argument('files', type=str, nargs='+',
                        help='files or directories to recursively processs')
    parser.add_argument('-n', '--dry-run', dest='dryrun', action='store_true',
                        help='only invalid inode creation times')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='print inode of each file')
    args = parser.parse_args(args=args)
    # expand any glob pattern (*, ?) and user directories (~).
    # Note: pathlib is not used:
    # 1. Path.glob() does not support full paths, while
    #    glob.glob() both accepts absolute and relative paths.
    # 2. os.walk() requires Python 3.6 for use with pathlib.Path
    files = []
    here = normpath(os.getcwd())
    for path in args.files:
        has_files = False
        for filename in glob(expanduser(path)):
            filename = normpath(join(here, filename))
            if not exists(filename):
                continue
            has_files = True
            files.append(filename)
        if not has_files:
            sys.stderr.write('No such file: {path}\n'.format(path=path))
    return files, args


def main(args):
    dirs, options = files_from_argv(args)
    options.future = time.time() + 100
    for directory in dirs:
        loop_directory(directory, options, file_func=check_inode_time)

if __name__ == '__main__':
    # main(args=sys.argv[1:])
    # main(['/Users/freek/Work', '/Users/freek/nosuchfile', '/Users/freek/Downloads/r*', '*.sh'])
    main(['/Users/freek/Work/Literature/MooC/Cloud Applications/storm-tutorial'])
