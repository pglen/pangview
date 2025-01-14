#!/usr/bin/env python

import sys, os, re
import pygtk, gobject, gtk, pango


if __name__ == "__main__":

    try:
        arg = ord(sys.argv[1])
    except:
        print "usage:", sys.argv[0]
        sys.exit(0)

    print "Number: ", str.format("{0:b} \\x{0:x} \\{0:o}", arg, arg, arg)
                   
