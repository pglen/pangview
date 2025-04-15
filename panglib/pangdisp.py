#!/usr/bin/env python

import sys, os, re, time, copy

import  panglib.parser as parser
import  panglib.stack as stack
import  panglib.lexer as lexer
import  panglib.utils as utils
import  panglib.pangedit as pangedit
import  panglib.pangdisp as pangdisp
import  panglib.pangfunc as pangfunc
import  panglib.textstate as textstate
import  panglib.pangparse as pangparse

ts = textstate.TextState()

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GdkPixbuf

# XPM data for missing image

#xstack = stack.Stack()

rcnt = 1
# ------------------------------------------------------------------------
# Accumulate output: (mostly for testing)
_cummulate = ""

def emit_one(strx):
    #return
    global _cummulate;
    _cummulate += " '" + strx + "' "

def show_emit():
    global _cummulate;
    print (_cummulate)

def reset_state():
    if mw:
        mw.reset()

xpm_data = [
"16 16 3 1",
"       c None",
".      c #000000000000",
"X      c #FFFFFFFFFFFF",
"                ",
"   ......       ",
"   .XXX.X.      ",
"   .XXX.XX.     ",
"   .XXX.XXX.    ",
"   .XXX.....    ",
"   ..XXXXX..    ",
"   .X.XXX.X.    ",
"   .XX.X.XX.    ",
"   .XXX.XXX.    ",
"   .XX.X.XX.    ",
"   .X.XXX.X.    ",
"   ..XXXXX..    ",
"   .........    ",
"                ",
"                "
]

mv = None

# This was necessary to separate presentation

def add_text(accum, xtag2):
    if mw:
        mw.add_text_xtag(accum, xtag2)

def add_image(pixbuf):
    if mw:
        if pixbuf:
            mw.add_pixbuf(pixbuf)
        else:
            mw.add_broken()

def add_sub(txt, flag = False):
    if mw:
        mw.add_text_sub(txt, flag)

class PangoView(Gtk.Window):

    # Create the toplevel window
    def __init__(self, pvg, pglink, bslink, parent=None):

        global mw
        mw = self
        self.pvg = pvg
        self.lastfile = ""
        Gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: Gtk.main_quit())

        self.set_title(self.__class__.__name__)
        #self.set_border_width(0)
        img_dir = os.path.dirname(os.path.abspath(__file__))
        #img_path = os.path.join(img_dir, "pangview.png")
        img_path = os.path.join(img_dir, "pang.png")
        self.broken_img_path = os.path.join(img_dir, "broken.png")
        try:
            self.set_icon_from_file(img_path)
        except:
            #print ("Cannot load app icon.")
            pass
        #rect = self.get_allocation()

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print (disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        #www = rect.width;
        #hhh = rect.height;

        #self.set_default_size(7*www/8, 7*hhh/8)
        if self.pvg.full_screen:
            self.set_default_size(www, hhh)
        else:
            #self.set_default_size(3*www/4, 3*hhh/4)
            self.set_default_size(hhh, 3*hhh/4)

        self.set_position(Gtk.WindowPosition.CENTER)
        #self.set_title("Pango test display");

        hpaned = Gtk.HPaned()
        hpaned.set_border_width(5)

        self.add(hpaned)

        self.view1 = pangedit.PangEdit(self.pvg);
        self.view1.link_callback = pglink
        self.view1.bs_callback = bslink
        self.buffer_1 = self.view1.get_buffer()
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.view1)

        self.view2 = pangedit.PangEdit(self.pvg);
        self.buffer_2 = self.view2.get_buffer()
        sw2 = Gtk.ScrolledWindow()
        sw2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw2.add(self.view2)

        hpaned.add1(sw2)
        hpaned.add2(sw)

        self.hpaned = hpaned
        self.set_pane_position(1)

        self.set_focus(self.view1)

        self.show_all()

    def set_pane_position(self, pos):
        self.hpaned.set_position(pos);

    def set_fullscreen(self):
        www = Gdk.screen_width();
        hhh = Gdk.screen_height();
        self.resize(www, hhh)

    # We clear the buffers through these functions:

    def clear(self, flag=False):
        if flag:
            self.buffer_2.set_text("", 0)
        else:
            self.buffer_1.set_text("", 0)

    def showfile(self, strx, reload = 1):
        #self.loadname = strx
        GLib.timeout_add(10, self._showfile, strx)

    def _showfile(self, strx, reload = 1):

        #global buf, xstack, self.pvg, ts
        self.view1.showcursor(True)

        if self.pvg.verbose:
            print ("Showing file:", strx)
        try:
            fh = open(strx)
        except:
            strerr = "File:  '" + strx + "'  must be an existing and readble file. "
            print (strerr)
            self.add_text(strerr)
            return
        try:
            buf = fh.read();
        except:
            strerr2 =  "Cannot read file '" + strx + "'"
            print (strerr2)
            self.add_text(strerr2)
            fh.close()
            return
        fh.close()
        if self.pvg.pgdebug > 5:
            print (buf)
        if self.lastfile != strx:
            self.pvg.lstack.push(strx)
            self.lastfile = strx
        self.showbuffer(buf, strx, reload)

        self.view1.showcursor(False)

    def reset(self):
        ''' Reset parser '''
        global ts
        ts.reset()

    def showbuffer(self, buf, strx = "", reload = ""):

        self.clear()
        self.reset()

        self.view1.showbuff(buf)

        #parser.Parser(self.pvg).process(buf)
        #self.view1.showcursor(False)

        # Output results
        if self.pvg.emit:
            show_emit()

        if strx:
            self.set_title("%s -- %d" % (strx, reload))

        self.buffer_1.place_cursor(self.buffer_1.get_start_iter())
        self.buffer_2.place_cursor(self.buffer_2.get_start_iter())

# ------------------------------------------------------------------------

    def message_dialog(self, title, strx):

        dialog = Gtk.MessageDialog()
        #mw,
        #        Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
        #        Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK, strx)

        dialog.set_title(title);
        dialog.set_markup(strx);
        dialog.add_button("OK", 0)
        dialog.run()
        dialog.destroy()

    def main(self):
        Gtk.main()

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep(msec):

    got_clock = time.clock() + float(msec) / 1000
    #print(got_clock)
    while True:
        if time.clock() > got_clock:
            break
        Gtk.main_iteration_do(False)

# EOF
