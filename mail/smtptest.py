#!/usr/bin/env python
"""Small script that sends a test message to a specified SMTP server. It's primary use is to test a backup mail server."""

from __future__ import print_function

import sys
import smtplib
import time
import socket
import optparse
import email
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

class Email(object):
    has_utf8 = False
    def __init__(self, emailaddress):
        """Given a Unicode email address, return a UTF-8/Punycode encoded byte"""
        self.user, self.domain = emailaddress.rsplit('@', 1)
    def __str__(self):
        return self.user + '@' + self.domain
    def __repr__(self):
        return self.__class__.__name__ + "(" + self.__str__() + ")"
    def encoded_domain(self):
        return self.domain.encode('idna')
    def encoded_user(self):
        if self.has_utf8:
            return self.user.encode('utf-8')
        try:
            return self.user.encode('ascii')
        except UnicodeError:
            return email.quoprimime.header_encode(self.user.encode('utf-8'), 'utf-8').encode('ascii')
    def encoded(self):
        return self.encoded_user() + b'@' + self.encoded_domain()
    def encoded_str(self):
        return self.encoded().decode('ascii')
    def human_readable(self):
        utf = self.__str__()
        ascii = self.encoded_str()
        if utf == ascii:
            return utf
        else:
            return "%s (as %s)" % (utf, ascii)


def prompt(prompt):
    return input(prompt).strip()


def get_mx_server(domain):
    """Given an domain name, return the server specified by the MX record.
    May return None if no MX record is found or the dnspython library is not 
    installed."""
    try:
        mx_rr = query(domain, 'MX')
    except NoNameservers:
        return None
    if len(mx_rr) > 0:
        return str(mx_rr[0].exchange)
    return None


def send_mail(fromaddr, toaddrs, thisserver, toserver, usetls=False, username=None, password=None):
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
        if server.has_extn('smtputf8'):
            has_smtputf8 = True
            esmtp_opts.append('SMTPUTF8')
            Email.has_utf8 = True
        else:
            has_smtputf8 = False
            Email.has_utf8 = False
        
        headers = ("From: %s\r\nTo: %s\r\nSubject: test mail %s\r\nContent-Type: text/plain; charset=\"utf-8\"\r\n\r\n"
               % (fromaddr.encoded_str(), ", ".join([addr.encoded_str() for addr in toaddrs]), time.strftime('%y%m%d %H:%M:%S')))
        body = ("This is a test email.\r\n\r\nFrom: %s\r\nOriginating server: %s\r\nTo: %s\r\nServer: %s\r\n"
               % (fromaddr, thisserver, ", ".join([addr.human_readable() for addr in toaddrs]), toserver))
        
        msg = headers + body
        
        print("Message length is %d" % len(msg))
        if server.has_extn('size'):
            esmtp_opts.append("SIZE=%d" % len(msg))
        if server.has_extn('8bitmime'):
            esmtp_opts.append('BODY=8BITMIME')
        
        (code, resp) = server.mail(fromaddr.encoded_str(), esmtp_opts)
        if code != 250:
            raise smtplib.SMTPSenderRefused(code, resp, fromaddr)
        
        for addr in toaddrs:
            # Note: only supports IDN (part after the @), not yet international email (part before the @)
            print("Adding recipient %s" % (addr.human_readable()))
            (code, resp) = server.rcpt(addr.encoded_str())
            if code not in (250, 251):
                raise smtplib.SMTPRecipientsRefused(resp)
        
        (code, resp) = server.data(msg.encode('utf-8'))
        if code != 250:
            raise smtplib.SMTPDataError(code, resp)
    
    except smtplib.SMTPException as e:
        print(str(e))
    finally:
        server.quit()

# import email.utils
# print(email.utils.parseaddr('"Freek at π@√.eu" <√9@3.14π.eu>'))
# sys.exit(1)
if __name__ == "__main__":
    

    parser = optparse.OptionParser()
    parser.add_option("-f", "--from", dest="fromaddr", help="From mail address")
    parser.add_option("-t", "--to", dest="toaddrs", help="To mail address. May be used multiple times.", action="append", default=[])
    parser.add_option("-o", "--origin", dest="thisserver", help="Originating server")
    parser.add_option("-s", "--server", dest="toserver", help="Delivery server")
    parser.add_option("--tls", dest="usetls", default=False, action="store_true", help="Use TLS encryption")
    parser.add_option("-u", "--user", dest="username", help="Username for authentication")
    parser.add_option("-p", "--password", dest="password", help="Password for authentication")
    (options, args) = parser.parse_args()
    
    try:
        thisserver = options.thisserver or socket.getfqdn()

        if options.fromaddr is not None:
            fromaddr = options.fromaddr
        else:
            default_from = "postmaster@" + thisserver
            fromaddr = prompt("From [%s]: " % (default_from))
            if fromaddr == "":
                fromaddr = default_from
        fromaddr = Email(fromaddr)
        if len(options.toaddrs) > 0:
            toaddrs = options.toaddrs
        else:
            toaddrs = prompt("To (separate multiple to addresses with a space): ").split()
            if len(toaddrs) == 0:
                print("No addresses specified")
                raise KeyboardInterrupt
        toaddrs = [Email(addr) for addr in toaddrs]
        if options.toserver is not None:
            toserver = options.toserver
        else:
            mxserver = get_mx_server(toaddrs[0].domain)
            if options.username:
                mxserver += ":587"
            if mxserver is not None:
                toserver = prompt("Server [%s]: " % mxserver)
                if toserver == "":
                    toserver = mxserver
            else:
                toserver = prompt("Server: ")
        
        send_mail(fromaddr, toaddrs, thisserver, toserver, options.usetls, options.username, options.password)
        
        sys.exit(0)
    except KeyboardInterrupt:
        print("Aborted")
        sys.exit(1)
