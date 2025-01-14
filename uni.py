#!/usr/bin/env python

import sys, os, re

if __name__ == "__main__":
    #print "Hello"

    cnt = 1024; lim = 2048

    while True:
        if cnt > lim:
            break
        print " '" + unichr(cnt) + "' ", cnt, "    ",
        if cnt % 8 == 0 and cnt:
            print
        cnt = cnt+1

    print

