#!/usr/bin/env python
#
#  getHostByName
#
#  Created by Freek Dijkstra on 2005-12-06.
#  Copyright (c) 2005. Distributed under 3-clause BSD license.
# 

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
def lookup(hostname):
    """lookup address with gethostbyname, using a 2 second timeout.
    Always returns an IPv4 address. No IPv6 support yet"""
    signal(SIGALRM, throw_timeout)
    try:
        # Don't wait too long for an answer.
        alarm(2)
        ipv4addr = socket.gethostbyname(hostname)
        alarm(0)
    except socket.error:
        # Lookup failed.  Reset alarm.
        alarm(0)
        ipv4addr = None
    except Timeout:
        # Lookup took too long.  Move on.
        ipv4addr = None
    return ipv4addr

def lookupBlocking(hostname):
    """lookup address with gethostbyname. No timeout, so can be blocking"""
    try:
        ipv4addr = socket.gethostbyname(hostname)
    except socket.error:
        ipv4addr = None
    return ipv4addr

def validHostname(hostname):
    """returns true if hostname is valid"""
    return (lookup(hostname) != None)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print lookupBlocking(sys.argv[1])
