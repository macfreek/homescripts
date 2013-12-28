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
    from dns.name import from_text as dns_from_text
    def dns_encode(domain):
        return str(dns_from_text(domain))[:-1]
except ImportError:
    def query(qname, rdtype):
        return []
    def dns_encode(domain):
        labels = []
        for label in domain.split('.'):
            try:
                labels.append(label)
            except UnicodeError:
                labels.append('xn--' + label.encode('punycode').decode('ascii'))
        return ".".join(labels)

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

def email_encode(emailaddress):
    """Given a Unicode email address, return a UTF-8/Punycode encoded byte"""
    user, domain = emailaddress.rsplit('@', 1)
    return user + '@' + dns_encode(domain)

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

# TODO: use US_ASCII encoding in the headers.
# Add the From: and To: headers at the start!
headers = ("From: %s\r\nTo: %s\r\nSubject: test mail %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs), time.strftime('%y%m%d %H:%M:%S')))
body = ("This is a test email.\r\n\r\nFrom: %s\r\nOriginating server: %s\r\nTo: %s\r\nServer: %s\r\n"
       % (fromaddr, thisserver, ", ".join(toaddrs), toserver))

msg = headers + body

print("Message length is %d" % len(msg))

try:
    print("connecting to %s" % toserver)
    server = smtplib.SMTP(toserver)
    print("sending EHLO message")
    server.set_debuglevel(1)
    server.ehlo(thisserver)
    # Optional: SASL authentication
    # server.login(user, password)

    esmtp_opts = []
    if server.has_extn('size'):
        esmtp_opts.append("SIZE=%d" % len(msg))
    if server.has_extn('8bitmime'):
        esmtp_opts.append('BODY=8BITMIME')
    if server.has_extn('smtputf8'):
        esmtp_opts.append('SMTPUTF8')
    (code, resp) = server.mail(fromaddr, esmtp_opts)
    if code != 250:
        raise SMTPSenderRefused(code, resp, fromaddr)

    for addr in toaddrs:
        # Note: only supports IDN (part after the @), not yet international email (part before the @)
        enc_addr = email_encode(addr)
        print("Adding recipient %s (as %s)" % (addr, enc_addr))
        (code, resp) = server.rcpt(enc_addr)
        if code not in (250, 251):
            raise SMTPRecipientsRefused(senderrs)
    
    (code, resp) = server.data(msg.encode('utf-8'))
    if code != 250:
        raise SMTPDataError(code, resp)
    
except smtplib.SMTPException as e:
    print(str(e))
finally:
    server.quit()


