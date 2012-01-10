#!/usr/bin/env python
#
#  getHostByAddr
#
#  Created by Jeroen van der Ham on 2005-09-26.
#  Copyright (c) 2005. Distributed under 3-clause BSD license.

import socket
import sys
from signal import signal, alarm, SIGALRM
import time

# Register our timeout signal handler.
class Timeout(Exception):
    pass

def throw_timeout(sig, frame):
    pass

# <some code snipped>

# Return the resolved address if it exists, otherwise, just give back
# the IP version.
def lookup(addr):
    signal(SIGALRM, throw_timeout)
    try:
        # Don't wait too long for an answer.
        alarm(2)
        (hostname, more, ip) = socket.gethostbyaddr(addr)
        alarm(0)
    except socket.error:
        # Lookup failed.  Reset alarm.
        alarm(0)
        hostname = None
    except Timeout:
        # Lookup took too long.  Move on.
        hostname = None
    return hostname
    
def lookupBlocking(addr):
    try:
        (hostname, more, ip) = socket.gethostbyaddr(addr)
    except socket.error:
        hostname = None
    return hostname
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        print lookupBlocking(sys.argv[1])