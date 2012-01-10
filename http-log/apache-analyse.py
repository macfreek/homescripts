#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys, os, string
import optparse
import re

import getHostByAddr

def analyseAgent(useragent):
    return useragent

apachere = re.compile('(.*) \- \- \[(.*)\] "(\w+) (/.*) (HTTP/[\d\.]+)" (\d+) (\d+|\-) "(.*)" "(.*)"\n')
#apachere = re.compile('(.*)')
fileobject = open("koalas.log", 'r')
for dataline in fileobject.readlines():
    data = apachere.match(dataline)
    if data == None:
        print "Can't analyse line:",dataline
    else:
        ipaddress   = data.group(1)
        time        = data.group(2)
        requesttype = data.group(3)
        path        = data.group(4)
        version     = data.group(5)
        resultcode  = data.group(6)
        size        = data.group(7)
        referrer    = data.group(8)
        useragent   = data.group(9)
        isbot   = (re.search('bot', useragent) != None)
        isownIP = (re.search('145.99.148.', ipaddress) != None)
        useragent = analyseAgent(useragent)
        #print ipaddress,
        dnsname   = getHostByAddr.lookup(ipaddress)
        if not (isownIP or isbot or (path != '/')):
            print dnsname,path,useragent
        else:
            pass
            #print ''
fileobject.close()


