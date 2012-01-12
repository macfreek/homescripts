#!/usr/bin/env perl

# http-request-filter
# Filters the output of tcpdump -A to show HTTP requests

# run as follows:
# tcpdump -i en0 -nn -A -s 574 dst port http | http-request-filter

use strict;

my $url;
my $host;
my $protocol = 'http';

while (<>) {
    if (/^\d\d?:\d\d?:\d\d?\.\d+ /) {
        if ($url) {
            print "$protocol://$host$url\n";
        }
        $url = "";
        $host = "";
    }
    if (/(GET|HEAD|POST|PUT|DELETE) (\/\S*) HTTP\/1\.\d/) {
        $url = $2;
    } elsif (/^Host: *([a-zA-Z0-9_\.]+)/) {
        $host = $1;
    } elsif (/^ IP6? \d[\d:\.]+\.\d+ > (\d[\d:\.]+)\.\d+: Flags/) {
        $host = $1;
    }
}
