#!/usr/bin/env python

#print "pangview installation script"

import time, sys, os, re, stat
import string, pickle
import commands
import site
import distutils.sysconfig

installerdir = sys.argv[0][:sys.argv[0].rfind("/")] + "/"

depfailed = False

# ------------------------------------------------------------------------
# Return True if exists

def isdir(fname):

    try:    
        ss = os.stat(fname)
    except:
        return False
    if stat.S_ISDIR(ss[stat.ST_MODE]):
        return True
    return False

# Make dir if it does not exist
def softmkdir(dirx):
    if not isdir(dirx):
        #print "Creating directory '" + dirx + "'"
        os.mkdir(dirx, 0755)
        if not isdir(dirx):
            return False
    return True

if commands.getoutput("whoami").strip() != "root":
    print "FAILED: You must be root to install pangview."
    sys.exit()
   
#print "Verifying dependencies:"
 
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gobject
except ImportError:
    print "  >>>  Missing Dependencies: Python GTK+ bindings (python-gtk2)."
    depfailed = True

try:
    import gnome.ui
except ImportError:
    print "  >>>  Missing Dependencies: Python GNOME bindings (python-gnome2)."
    depfailed = True

# not stricly needed, just a validity check

prefix = sys.prefix
if not isdir(prefix):
    print "  >>>  Missing Dependencies: sys prefix dir does not exist."
    depfailed = True

libdir = distutils.sysconfig.get_python_lib()
if not isdir(libdir):
    print "  >>>  Missing Dependencies: Python Library dir does not exist."
    depfailed = True

libdir2 = libdir + "/panglib"
if not softmkdir(libdir2):
    print "  >>>  Missing Dependencies: Cannot create panglib  dir."
    depfailed = True

shared  = "/usr/share/pangview/"
if not softmkdir(shared):
    print "  >>>  Missing Dependencies: Cannot create data dir."
    depfailed = True

# ------------------------------------------------------------------------
if depfailed:
    print "FAILED: Dependencies not met. Exiting."
    sys.exit()

#print
print "All dependencies are met."

#print "prefix:", prefix
#print "libdir:", libdir

    # --- file  ---  target dir ---- exec flag ----
filelist = \
    ['pangview.py',   '/usr/bin',     True ],     \
    ['pang.png',       shared,  False ],     \
    ['README',         shared,       False ],     \

    # --- dir  ---  target dir ---- root owner flag ----
dirlist = \
    ['pango',       shared,     True ], \
    ['panglib',     libdir,     True ], \

# Copy all to target:

print "Copying files:"

for source, dest, exe in filelist:
    targ =  dest +  "/"+ source 
    print "   '" + source + "' -> '" + targ + "'"
    commands.getoutput("cp " + source + " " + targ)

    if exe:
        os.chmod(targ, 0755) # Root can rwx; can rx 
    else:
        os.chmod(targ, 0644) # Root can rw; others r

print "Copying directories:"

for source, dest, exe in dirlist:
    print "   '" + source + "' -> '" + dest + "'"
    commands.getoutput ("cp -a " + source + " " + dest)
    if exe:
        commands.getoutput(" chown root.root " + dest + "/" + source + "/*")

print 
print "You may now use the 'pangview.py' utility on your system."
print
