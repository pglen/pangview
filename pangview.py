#!/usr/bin/env python3

#from __future__ import absolute_import
#from __future__ import print_function

import sys, os, re, time
import signal, pickle

VERSION = "1.3.0"

# Our modules

import  panglib.parser as parser
import  panglib.stack as stack
import  panglib.textstate as textstate
import  panglib.lexer as lexer
import  panglib.pangdisp as pangdisp
import  panglib.pangfunc as pangfunc
import  panglib.utils as utils
import  panglib.pangparse as pangparse

pvg = utils.pvg
myname = os.path.basename(sys.argv[0])

# Our display object
mainview = pangdisp.PangoView(pvg)

import inspect
if inspect.isbuiltin(time.process_time):
    time.clock = time.process_time

# ------------------------------------------------------------------------

def bslink():

    if pvg.lstack.stacklen() == 1:
        return
    pvg.lstack.pop()
    strx = pvg.lstack.last()
    #print ("backspace linking to:", strx)
    if strx == None or strx == "":
        return
    mainview.showcur(True)
    mainview.showfile(strx)

def link(strx):

    if strx == None or strx == "":
        return

    if not isfile(strx):
        mainview.showcur(False)
        message_dialog("Missing or broken link",
            "Cannot find file '%s'" % strx );
        return
    #print ("linking to:", strx)
    mainview.showfile(strx)

# ------------------------------------------------------------------------

def     message_dialog(title, strx):

    dialog = Gtk.MessageDialog(mainview,
            Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
            Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK, strx)
    dialog.set_title(title);
    dialog.run()
    dialog.destroy()

# ------------------------------------------------------------------------

def help():
    print()
    print (myname + ":", "Version %s - Utility for displaying a pango file." % VERSION)
    print ()
    print ("Usage: " + myname + " [options] filename")
    print ()
    print ("Options are:")
    print ("            -d level  - Debug level (1-10)")
    print ("            -c file   - Contents file for left pane")
    print ("            -a pos    - Set pane position (pixels)")
    print ("            -w        - Display syntax warnings")
    print ("            -v        - Verbose. (repeat -v for more)")
    print ("            -f        - Full screen")
    print ("            -o        - Cover all windows (Full screen)")
    print ("            -t        - Show timing")
    print ("            -x        - Show lexer output")
    print ("            -g        - Show parser state changes")
    print ("            -s        - Show parser states")
    print ("            -p        - Show parser messages")
    print ("            -e        - Emit parse string")
    print ("            -l        - Show all parser messages")
    print ("            -h        - Help")
    print ()

# ------------------------------------------------------------------------

def mainfunc():

    import getopt

    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:c:a:hvxftopeswlg")
    except getopt.GetoptError as err:
        print ("Invalid option(s) on command line:", err)
        sys.exit(1)

    #print ("opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pvg.pgdebug = int(aa[1])
            except:
                pvg.pgdebug = 0

        if aa[0] == "-c":
            pvg.second = aa[1]
            #print (pvg.second)

        if aa[0] == "-a":
            try:
                pvg.pane_pos = int(aa[1])
            except:
                print ("Pane position must be a number")

            print (pvg.pane_pos)

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": pvg.verbose += 1
        if aa[0] == "-x": pvg.show_lexer = True
        if aa[0] == "-f": pvg.full_screen = True
        if aa[0] == "-o": pvg.xfull_screen = True
        if aa[0] == "-t": pvg.show_timing = True
        if aa[0] == "-e": pvg.emit = True
        if aa[0] == "-p": pvg.show_parse  = True
        if aa[0] == "-s": pvg.show_state  = True
        if aa[0] == "-c": pvg.show_state_change  = True
        if aa[0] == "-w": pvg.warnings = True
        if aa[0] == "-l": pvg.all = True
        if aa[0] == "-g": pvg.show_state_change = True

    try:
        strx = args[0]
    except:
        print ("Use: " + myname + " -h  for usage info.")
        exit(1)

    global lstack
    lstack = stack.Stack()

    fullpath = os.path.abspath(strx);
    pvg.docroot = os.path.dirname(fullpath)

    if pvg.xfull_screen:
        mainview.fullscreen()
    elif pvg.full_screen:
        mainview.set_fullscreen()

    mainview.callback = link
    mainview.bscallback = bslink

    if pvg.second != "":
        if pvg.pane_pos >= 0:
            mainview.set_pane_position(pvg.pane_pos)
        else:
            mainview.set_pane_position(250)
        pvg.flag = True
        mainview.showfile(pvg.second)

    pvg.flag = False
    mainview.showfile(strx)
    mainview.main()

if __name__ == "__main__":
    mainfunc()

# EOF
