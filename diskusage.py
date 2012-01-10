#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys, os, string
import UserDict
import operator # python 2.4 and up
import optparse
import re

def humanReadable(size):
    if size < 1000:
        return "%3dB " % size
    elif size < 9950:
        return "%3.1fkB" % (size / 1000.0)
    elif size < 999500:
        return "%3.0fkB" % (size / 1000.0)
    elif size < 9950000:
        return "%3.1fMB" % (size / 1000000.0)
    elif size < 999500000:
        return "%3.0fMB" % (size / 1000000.0)
    elif size < 9950000000:
        return "%3.1fGB" % (size / 1000000000.0)
    elif size < 999500000000:
        return "%3.0fGB" % (size / 1000000000.0)
    elif size < 9950000000000:
        return "%3.1fTB" % (size / 1000000000000.0)
    else:
        return "%3.0fTB" % (size / 1000000000000.0)

class FileSizeList(UserDict.UserDict):
    def appendfile(self, dirname, basename, filesize):
        if not self.data.has_key(dirname):
            self.data[dirname] = {};
        self.data[dirname][basename] = filesize
    
    def setParent(self, parentdir):
        self.parent = parentdir
    
    def setMaxDepth(self, maxdepth):
        self.maxdepth = maxdepth
    
    def getParent(self):
        try:
            return self.parent
        except :
            print "PLEASE SET PARENT"
            dirs = self.data.keys()
            dirs.sort()
            topdir = dirs[0]
            topdir = self.data[topdir]
            (parent, size) = topdir.popitem()
            print "parent + size = ",parent,size
            return parent
    
    def getDirSize(self, dir):
        parent = os.path.dirname(dir)
        filelist = self.data[parent]
        return filelist[os.path.basename(dir)]
    
    def printList(self):
        parent = self.getParent()
        size = self.getDirSize(parent)
        self.printDir(parent, size)
    
    def printDir(self, dir, dirsize, nest=0):
        if dir == '': path = '/'
        else: path = dir
        if self.data.has_key(path):
            print (nest*"    ")+humanReadable(dirsize)+"    "+dir+"/"
            if nest < self.maxdepth:
                filelist = self.data[path]
                # Sort list by value
                # Python >= 2.4:
                sortedfiles = filelist.items()
                sortedfiles.sort(key = operator.itemgetter(1), reverse=True)
                for subdir in sortedfiles:
                    self.printDir(os.path.join(path,subdir[0]), subdir[1], nest+1)
            else :
                print (nest*"    ")+"         (max depth reached)"
        else:
            if os.path.isdir(path):
                dir = dir + '/'
            print (nest*"    ")+humanReadable(dirsize)+"    "+dir
    

def main(argv=None):
    """
    main() function. Parse command line arguments, before calling rundaemon(), runclient() or runstandalone()
    """
    if argv is None:
        # allow user to override argv in interactive python interpreter
        argv = sys.argv
    parser = optparse.OptionParser(usage="diskusage PATH", version="diskusage 1.1", conflict_handler="resolve")
    parser.add_option("-t", "--threshold", dest="threshold", action="store", default="20000000", 
                      help="Threshold for file sizes. Recognizes kb, Mb, Gb and Tb units (all base-1000)")
    parser.add_option("-d", "--depth", dest="maxdepth", action="store", default=20, 
                      help="Display an entry for all files and directories depth directories deep.")
    parser.add_option("-b", "--nobundle", dest="skipbundle", action="count", 
                      help="Do not display files in bundles (e.g. in .app, .localized, .dict, etc.)")
    parser.add_option("-x", dest="onemount", action="count", 
                      help="File system mount points are not traversed.")
    parser.add_option("-I", dest="mask", action="store", 
                      help="Ignore files and directories matching the specified mask.")
    parser.add_option("-L", dest="symlink", action="store_const", const='L', 
                      help="Symbolic links on the command line and in file hierarchies are followed..")
    parser.add_option("-P", dest="symlink", action="store_const", const='P', 
                      help="No symbolic links are followed.  This is the default.")
    parser.add_option("-H", dest="symlink", action="store_const", const='H', 
                      help=" Symbolic links on the command line are followed, symbolic links in file hierarchies are not followed.")
    parser.add_option("-v", "--verbose", dest="verbose", action="count", 
                      help="Verbose output (for debugging)")
    parser.add_option("-f", "--file", dest="filename", action="store", default=None, 
                      help="Debugging. Read from file rather then invoking 'du'.")
    (options, args) = parser.parse_args(args=argv[1:])
    if len(args) > 0:
        path = args[0]
    else:
        path = '.'
    if path[-1:] == "/": # remove trainling slash (/). warning. may result in '/' -> ''. This is intentional.
        path = path [:-1]
    # logger = logging.getLogger('getlocalhosts')
    # logger = setLogVerbosity(logger, options.verbosity)
    # logger.info("Log information from main()")
    # logger.warning("Log warning from main()")
    # logger.error("Log error from main()")
    # dosomething()
    
    data_list = FileSizeList()
    data_list.setParent(path)
    data_list.setMaxDepth(options.maxdepth)
    
    #Extra du options:
    # -x      File system mount points are not traversed.
    # -H      Symbolic links on the command line are followed, symbolic links
    #         in file hierarchies are not followed.
    # -L      Symbolic links on the command line and in file hierarchies are
    #         followed.
    # -I mask
    #         Ignore files and directories matching the specified mask.
    # -P      No symbolic links are followed.  This is the default.
    
    if path == '':
        path = '/'  # special case.
    duoptions = [];
    if options.onemount:
        duoptions.append('-x');
    if options.symlink:
        duoptions.append('-'+options.symlink);
    if options.mask:
        duoptions.append('-I '+options.mask);
    if options.maxdepth:
        # depends on du version
        duoptions.append('-d '+str(options.maxdepth));
        # duoptions.append('--max-depth='+str(options.maxdepth));
    if options.threshold:
        options.threshold = str(options.threshold)
        threshold = re.match('(.*\d)([TGMKk])?([Bb])?', options.threshold)
        if threshold == None:
            print >>sys.stderr, "Invalid treshold %s ignored\n" % (repr(options.threshold
            ))
            options.threshold = 0
        else:
            options.threshold = float(threshold.group(1))
            if threshold.group(2):
                magnitude = string.upper(threshold.group(2))
            else:
                magnitude = ""
            if magnitude == 'T':
                options.threshold = int(1000000000000*options.threshold)
            if magnitude == 'G':
                options.threshold = int(1000000000*options.threshold)
            if magnitude == 'M':
                options.threshold = int(1000000*options.threshold)
            if magnitude == 'K':
                options.threshold = int(1000*options.threshold)
            else:
                options.threshold = int(options.threshold)
    command = "/usr/bin/du -k %s '%s'" % (string.join(duoptions, " "), path)
    if options.verbose:
        print "command:",command
    if options.filename:
        fileobject = open(options.filename, 'r')
    else:
        fileobject = os.popen(command)
    for dataline in fileobject.readlines():
        data = dataline[:-1].split("\t")
        try:
            filesize = int(data[0])*1024
            path = data[1]
        except ValueError, e:
            print >>sys.stderr, "ValueError: %s" % str(e)
            print >>sys.stderr, "data = %s\n" % (repr(data))
            continue
        except IndexError, e:
            print >>sys.stderr, "IndexError: %s" % str(e)
            print >>sys.stderr, "data = %s\n" % (repr(data))
            continue
        if path[-1:] == "/":
            path = path [:-1]
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        data = [dirname,filesize,basename]
        if filesize < options.threshold:
            pass # skip: file too small
        elif options.skipbundle and inBundle(path):
            pass # skip: inside a bundle (application, etc.)
        else:
            data_list.appendfile(dirname, basename, filesize)
    fileobject.close()
    
    data_list.printList()
    
    # print data_list

def inBundle(path):
    # return True if one of the parent dirs ends in .app, .localized, .dict, etc.
    return (re.search('\w\.[a-z]+\/.', path) != None)

if __name__ == "__main__":
    main()
