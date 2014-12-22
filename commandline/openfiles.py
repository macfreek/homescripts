#!/usr/bin/env python
# encoding: utf-8
"""
Get all open files in Python.

In Python, it is easy to find the maximum number of open fies:
  resource.getrlimit(resource.RLIMIT_NOFILE)

However, it seems impossible to get the number of open files.
Hence, LSOF <ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof> is used.
"""

__author__ = "Freek Dijkstra <software@macfreek.nl>"
__version__ = "1.0"
__licence__ = "public domain"

import os
import subprocess
import locale

def open_files(pid=None):
    """
    Return a dict of open files for the given process.
    The key of the dict is the file descriptor (a number).
    
    If PID is not specified, the PID of the current program is used.
    Only regular open files are returned.
    
    This program relies on the external lsof program.
    
    This function may raise an OSError.
    """
    if pid is None:
        pid = os.getpid()
    files = {}
    # lsof lists open files, including sockets, etc.
    # -n, -l, -P prevent DNS, user and port number lookups
    # -b avoid kernel-blocking functions
    # -w supresses warnings
    # -p specifies the PID
    # -F ftn specifies the output format (file descriptor, type and file name)
    command = ['lsof', '-nlP', '-b', '-w', '-p', str(pid), '-F', 'ftn']
    # set LC_ALL=UTF-8, so non-ASCII files are properly reported.
    env = dict(os.environ).copy()
    env['LC_ALL'] = 'UTF-8'
    # Open a subprocess, wait till it is done, and get the STDOUT result
    output = subprocess.Popen(command, stdout=subprocess.PIPE, env=env).communicate()[0]
    # decode the output and split in lines.
    output = output.decode('utf-8').split('\n')
    
    state = {'f': '', 't': ''}
    for line in output:
        try:
            linetype, line = line[0], line[1:]
        except IndexError:
            continue
        state[linetype] = line
        if linetype == 'n':
            if state['t'] == 'REG' and state['f'].isdigit():
                files[int(state['f'])] = line
                state = {'f': '', 't': ''}
    return files



if __name__ == '__main__':
    try:
        files = open_files()
    except OSError:
        print ("Failed to get open files")
        raise
    else:
        for fd, filename in files.items():
            print(fd, filename)
