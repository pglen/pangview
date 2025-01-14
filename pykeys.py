#!/usr/bin/env python

import sys, os, re
import string

fname = "/usr/lib/python2.6/site-packages/gtk-2.0/gtk/keysyms.py"

if __name__ == '__main__':

    try:
        strx = sys.argv[1]
    except:
        print "usage: ", sys.argv[0], "keyname"; sys.exit(1)

    #print "Hello", fname
    
    try:
        f = open(fname)
    except:        
        print "Cannot open keysyms", fname
        sys.exit(1)
    
    try:
        buf = f.read();
    except:
        strerr2 =  "Cannot read keysyms"
        sys.exit(1)
    
    f.close()

    for aa in string.split(buf, "\n"):
        #print aa
        if len(aa) == 0: 
            continue
        if aa[0] == "#":
            continue

        if re.findall(strx, aa, re.IGNORECASE):
            bb = string.split(aa)
            print "gtk.keysyms." + bb[0], "\t (" + bb[2] + ")"


