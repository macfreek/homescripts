#!/usr/bin/env python

import smtplib
import time
import socket
import optparse

parser = optparse.OptionParser()
parser.add_option("-f", "--from", dest="fromaddr", help="From mail address")
parser.add_option("-t", "--to", dest="toaddrs", help="To mail address. May be used multiple times.", action="append", default=[])
parser.add_option("-s", "--server", dest="toserver", help="Delivery server")
(options, args) = parser.parse_args()

def prompt(prompt):
    return raw_input(prompt).strip()

if options.fromaddr != None:
    fromaddr = options.fromaddr
else:
    fromaddr = prompt("From: ")
if len(options.toaddrs) > 0:
    toaddrs = options.toaddrs
else:
    toaddrs  = prompt("To: ").split()
if options.toserver != None:
    toserver = options.toserver
else:
    toserver = prompt("Server: ")
thisserver = socket.getfqdn()

# Add the From: and To: headers at the start!
headers = ("From: %s\r\nTo: %s\r\nSubject: test mail %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs), time.strftime('%y%m%d %H:%M:%S')))
body = ("This is a test email.\r\n\r\nFrom: %s\r\nOriginating server: %s\r\nTo: %s\r\nServer: %s\r\n"
       % (fromaddr, thisserver, ", ".join(toaddrs), toserver))

msg = headers + body

print "Message length is " + repr(len(msg))

try:
    print "connecting to",toserver
    server = smtplib.SMTP(toserver)
    print "sending EHLO message"
    server.set_debuglevel(1)
    server.ehlo(thisserver)
    # Optional: SASL authentication
    # server.login(user, password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
except smtplib.SMTPException as e:
    print str(e)

