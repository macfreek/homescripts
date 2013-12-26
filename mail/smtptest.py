#!/usr/bin/env python
"""Small script that sends a test message to a specified SMTP server. It's primary use is to test a backup mail server."""

from __future__ import print_function

import sys
import smtplib
import time
import socket
import optparse

try:
    from dns.resolver import query
except ImportError:
    def query(qname, rdtype):
        return []

try:
    input = raw_input  # Python 2.x compatibility
except NameError:
    pass

default_from = None

parser = optparse.OptionParser()
parser.add_option("-f", "--from", dest="fromaddr", help="From mail address")
parser.add_option("-t", "--to", dest="toaddrs", help="To mail address. May be used multiple times.", action="append", default=[])
parser.add_option("-s", "--server", dest="toserver", help="Delivery server")
(options, args) = parser.parse_args()

def prompt(prompt):
    return input(prompt).strip()

thisserver = socket.getfqdn()

def get_mx_server(email):
    """Given an email address, return the server specified by the MX record.
    May return None if no MX record is found or the dnspython library is not 
    installed."""
    domain = email.rsplit('@', 1)[-1]
    mx_rr = query(domain, 'MX')
    if len(mx_rr) > 0:
        return str(mx_rr[0].exchange)
    return None


try:
    if options.fromaddr != None:
        fromaddr = options.fromaddr
    else:
        if default_from == None:
            default_from = "postmaster@" + thisserver
        fromaddr = prompt("From [%s]: " % (default_from))
        if fromaddr == "":
            fromaddr = default_from
    if len(options.toaddrs) > 0:
        toaddrs = options.toaddrs
    else:
        toaddrs  = prompt("To (separate multiple to addresses with a space): ").split()
        if len(toaddrs) == 0:
            print("No addresses specified")
            raise KeyboardInterrupt
    if options.toserver != None:
        toserver = options.toserver
    else:
        mxserver = get_mx_server(toaddrs[0])
        if mxserver is not None:
            toserver = prompt("Server [%s]: " % mxserver)
            if toserver == "":
                toserver = mxserver
        else:
            toserver = prompt("Server: ")
except KeyboardInterrupt:
    print("Aborted")
    sys.exit(1)

# Add the From: and To: headers at the start!
headers = ("From: %s\r\nTo: %s\r\nSubject: test mail %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs), time.strftime('%y%m%d %H:%M:%S')))
body = ("This is a test email.\r\n\r\nFrom: %s\r\nOriginating server: %s\r\nTo: %s\r\nServer: %s\r\n"
       % (fromaddr, thisserver, ", ".join(toaddrs), toserver))

msg = headers + body

print("Message length is " + repr(len(msg)))

try:
    print("connecting to %s" % toserver)
    server = smtplib.SMTP(toserver)
    print("sending EHLO message")
    server.set_debuglevel(1)
    server.ehlo(thisserver)
    # Optional: SASL authentication
    # server.login(user, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
except smtplib.SMTPException as e:
    print(str(e))

