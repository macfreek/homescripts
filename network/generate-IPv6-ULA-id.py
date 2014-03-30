#!/usr/bin/env python3.3
"""
Generate a 'Global ID' for Unique Local IPv6 Unicast Addresses.

The algorithm as decribed in RFC 4193:

1) Obtain the current time of day in 64-bit NTP format [NTP].
2) Obtain an EUI-64 identifier from the system running this
   algorithm.  If an EUI-64 does not exist, one can be created from
   a 48-bit MAC address as specified in [ADDARCH].  If an EUI-64
   cannot be obtained or created, a suitably unique identifier,
   local to the node, should be used (e.g. system serial number).
3) Concatenate the time of day with the system-specific identifier
   creating a key.
4) Compute an SHA-1 digest on the key as specified in [FIPS, SHA1];
   the resulting value is 160 bits.
5) Use the least significant 40 bits as the Global ID.
6) Concatenate FC00::/7, the L bit set to 1, and the 40 bit Global
   ID to create a Local IPv6 address prefix.
"""

__author__ = "Freek Dijkstra <software@macfreek.nl>"
__version__ = "1.0"
__licence__ = "public domain"

from time import time
from struct import pack
from hashlib import sha1
from uuid import getnode


def num_to_bytes(number, bytesize=2):
    """Return the packed byte representation of number."""
    if bytesize == 1:
        return bytes( pack("!B", number) )
    elif bytesize == 2:
        return bytes( pack("!H", number) )
    elif bytesize == 4:
        return bytes( pack("!I", number) )
    elif bytesize == 8:
        return bytes( pack("!Q", number) )
    else:
        raise NotImplemented("Unsupported number size (%d bytes) % bytesize")

def get_ntp_time():
    """Return the NTP time as a combination (era, seconds, fraction).
    each is a positive or zero integer, smaller than 2^32.
    (era * 2^32 + seconds) is the number of seconds since NTP epoch,
    which was at 1-1-1970 midnight. Era 1 starts in 2036.
    Note that this format is a hybrid between a NTP Timestamp (which does 
    not include an era) and a NTP Data (which has a 64-bit fraction).
    """
    epoch = time() # seconds since Unix epoch
    seconds = int(epoch)
    fraction = int((epoch - seconds) * 2**32)
    # There are 2208988800 seconds between 1-1-1900 (NTP epoch) and
    # 1-1-1970 (Unix epoch). See http://www.eecis.udel.edu/~mills/y2k.html
    era, seconds = divmod(seconds + 2208988800, 2**32)
    return (era, seconds, fraction)

def hexlify(data, prefixchar="", joinchar=":", case=None):
    """Similar to binascii.hexlify(). Return the hexadecimal representation of the binary data."""
    _hexdigits = '0123456789ABCDEF'
    def hex(num, octetlen=2):
        h,l = divmod(num,16)
        return _hexdigits[h] + _hexdigits[l]
    return joinchar.join([prefixchar+hex(item) for item in data])

def generate_ULU_ID(verbose=True):
    """Generate a 'Global ID' for Unique Local IPv6 Unicast Addresses.
    Return the 6-byte long IPv6 prefix. This is 15-bit 0xFC, L bit (set to 1), 
    followed by the 40-bit generated prefix."""
    if verbose:
        # print("Generate a 'Global ID' for Unique Local IPv6 Unicast Addresses.")
        # print()
        print(__doc__)
    
    era, seconds, fraction = get_ntp_time()
    ts = num_to_bytes(seconds, 4) + num_to_bytes(fraction, 4)
    if verbose:
        print("Current time is:")
        print("era:", era)
        print("seconds:", seconds)
        print("fraction:", fraction)
        print("In 64-bit format (without era): %s" % (hexlify(ts)))
        print()
    
    mac = num_to_bytes(getnode(), 8)
    if mac[:2] == b'\0\0':
        sysid = mac[2:5] + b'\xFF\xFE' + mac[5:8]
        if verbose:
            print("MAC (EUI-48) address is %s" % (hexlify(mac[2:])))
    else:
        sysid = mac
    if verbose:
        print("The 64-bit system identifier is: %s" % (hexlify(sysid)))
        print()
    
    s = sha1(ts + sysid).digest()
    unique_id = s[-5:]
    if verbose:
        print("SHA1(%s) = \n  = %s" % (hexlify(ts + sysid), hexlify(s)))
        print("The 40-bit unique ID is: %s" % hexlify(unique_id))
        print()
    prefix = b'\xFD' + unique_id
    
    if verbose:
        # print sexdects, groups of 16 bits:
        sexdects = [hexlify(prefix[i:i+2], joinchar="") for i in range(0, len(prefix), 2)]
        # remove leading 0 characters, but leave at least one. Add subnet designation.
        ipv6range = ":".join([sexdect[:-1].lstrip('0') + sexdect[-1:] for sexdect in sexdects]) + "::/48"
        print("The ULA IPv6 range is: %s" % ipv6range)
    
    if verbose:
        print()
        print("You can register your ULA at https://www.sixxs.net/tools/grh/ula/.")
        print("However, be aware that this not prevent anyone else from using this range,")
        print("so you are mostly fooling yourself.")
    
    return prefix

if __name__ == '__main__':
    generate_ULU_ID()
