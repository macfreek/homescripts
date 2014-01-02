#!/usr/bin/env python
"""Small script that sends a test message to a specified SMTP server. It's primary use is to test a backup mail server."""

from __future__ import print_function

import sys
import smtplib
import time
import socket
import optparse

try:
    from dns.resolver import query, NoNameservers
except ImportError:
    def query(qname, rdtype):
        return []

try:
    input = raw_input  # Python 2.x compatibility
except NameError:
    pass

class SMTP(smtplib.SMTP):
    """Override of smtplib.SMTP to support international email addresses according to RFC 6531."""
    def send(self, s):
        """Send `s' to the server."""
        if self.debuglevel > 0:
            print('send:', repr(s), file=sys.stderr)
        if hasattr(self, 'sock') and self.sock:
            if isinstance(s, str):
                s = s.encode("utf-8")
            try:
                self.sock.sendall(s)
            except socket.error:
                self.close()
                raise smtplib.SMTPServerDisconnected('Server not connected')
        else:
            raise smtplib.SMTPServerDisconnected('please run connect() first')


def prompt(prompt):
    return input(prompt).strip()

thisserver = socket.getfqdn()

def get_mx_server(email):
    """Given an email address, return the server specified by the MX record.
    May return None if no MX record is found or the dnspython library is not 
    installed."""
    domain = email.rsplit('@', 1)[-1]
    try:
        mx_rr = query(domain, 'MX')
    except NoNameservers:
        return None
    if len(mx_rr) > 0:
        return str(mx_rr[0].exchange)
    return None

def email_encode(emailaddress, has_smtputf8=False):
    """Given a Unicode email address, return a UTF-8/Punycode encoded byte"""
    user, domain = emailaddress.rsplit('@', 1)
    if has_smtputf8:
        return user + '@' + domain.encode('idna').decode('ascii')
    else:
        return user + '@' + domain.encode('idna').decode('ascii')

def send_mail(fromaddr, toaddrs, toserver, usetls=False, username=None, password=None):
    # TODO: use US_ASCII encoding in the headers.
    # Add the From: and To: headers at the start!
    headers = ("From: %s\r\nTo: %s\r\nSubject: test mail %s\r\nContent-Type: text/plain; charset=\"utf-8\"\r\n\r\n"
           % (fromaddr, ", ".join(toaddrs), time.strftime('%y%m%d %H:%M:%S')))
    body = ("This is a test email.\r\n\r\nFrom: %s\r\nOriginating server: %s\r\nTo: %s\r\nServer: %s\r\n"
           % (fromaddr, thisserver, ", ".join(toaddrs), toserver))

    msg = headers + body

    print("Message length is %d" % len(msg))

    try:
        print("connecting to %s" % toserver)
        server = SMTP(toserver)
        print("sending EHLO message")
        server.set_debuglevel(1)
        if usetls:
            server.starttls()
        server.ehlo(thisserver)
        if username:
            # Optional: SASL authentication
            server.login(username, password)
        esmtp_opts = []
        if server.has_extn('size'):
            esmtp_opts.append("SIZE=%d" % len(msg))
        if server.has_extn('8bitmime'):
            esmtp_opts.append('BODY=8BITMIME')
        if server.has_extn('smtputf8'):
            has_smtputf8 = True
            esmtp_opts.append('SMTPUTF8')
        else:
            has_smtputf8 = False
        enc_fromaddr = email_encode(fromaddr, has_smtputf8)
        (code, resp) = server.mail(fromaddr, esmtp_opts)
        if code != 250:
            raise smtplib.SMTPSenderRefused(code, resp, fromaddr)
    
        for addr in toaddrs:
            # Note: only supports IDN (part after the @), not yet international email (part before the @)
            enc_addr = email_encode(addr, has_smtputf8)
            if addr == enc_addr:
                print("Adding recipient %s" % (enc_addr))
            else:
                print("Adding recipient %s (as %s)" % (addr, enc_addr))
            (code, resp) = server.rcpt(enc_addr)
            if code not in (250, 251):
                raise smtplib.SMTPRecipientsRefused(resp)
    
        (code, resp) = server.data(msg.encode('utf-8'))
        if code != 250:
            raise smtplib.SMTPDataError(code, resp)
    
    except smtplib.SMTPException as e:
        print(str(e))
    finally:
        server.quit()

if __name__ == "__main__":
    default_from = None

    parser = optparse.OptionParser()
    parser.add_option("-f", "--from", dest="fromaddr", help="From mail address")
    parser.add_option("-t", "--to", dest="toaddrs", help="To mail address. May be used multiple times.", action="append", default=[])
    parser.add_option("-s", "--server", dest="toserver", help="Delivery server")
    parser.add_option("--tls", dest="usetls", default=False, action="store_true", help="Use TLS encryption")
    parser.add_option("-u", "--user", dest="username", help="Username for authentication")
    parser.add_option("-p", "--password", dest="password", help="Password for authentication")
    (options, args) = parser.parse_args()
    
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
            if options.username:
                mxserver += ":587"
            if mxserver is not None:
                toserver = prompt("Server [%s]: " % mxserver)
                if toserver == "":
                    toserver = mxserver
            else:
                toserver = prompt("Server: ")
        
        send_mail(fromaddr, toaddrs, toserver, options.usetls, options.username, options.password)
        
        sys.exit(0)
    except KeyboardInterrupt:
        print("Aborted")
        sys.exit(1)
