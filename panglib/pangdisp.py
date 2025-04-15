#!/usr/bin/env python

import sys, os, re, time, copy

import  panglib.parser as parser
import  panglib.stack as stack
import  panglib.lexer as lexer
import  panglib.utils as utils
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

    hovering_over_link = False
    waiting = False

    hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
    regular_cursor = Gdk.Cursor(Gdk.CursorType.XTERM)
    wait_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)

    # Create the toplevel window
    def __init__(self, pvg, parent=None):

        global mw
        mw = self
        self.old_time = time.time()
        self.pvg = pvg
        self.lastfile = ""
        Gtk.Window.__init__(self)
        self.cb = pangfunc.CallBack(ts, add_text, add_image, add_sub, emit_one)
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

        self.floatlist = []
        self.currfloat = 0
        self.wait = False

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

        view1 = Gtk.TextView();
        view1.set_border_width(8)

        view1.connect("key-press-event", self.key_press_event)
        view1.connect("event-after", self.event_after)
        view1.connect("motion-notify-event", self.motion_notify_event)
        view1.connect("visibility-notify-event", self.visibility_notify_event)
        #view1.connect("realize", self.realized)

        view1.set_editable(False)
        view1.set_cursor_visible(False)
        self.view1 = view1

        self.buffer_1 = view1.get_buffer()
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(view1)

        view2 = Gtk.TextView();
        view2.set_border_width(8)
        view2.set_editable(False)
        self.buffer_2 = view2.get_buffer()
        sw2 = Gtk.ScrolledWindow()
        sw2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw2.add(view2)

        view2.connect("key-press-event", self.key_press_event2)
        view2.connect("event-after", self.event_after2)
        view2.connect("motion-notify-event", self.motion_notify_event2)
        view2.connect("visibility-notify-event", self.visibility_notify_event2)

        hpaned.add1(sw2)
        hpaned.add2(sw)

        self.hpaned = hpaned
        self.set_pane_position(1)

        self.set_focus(view1)

        self.show_all()

    def set_pane_position(self, pos):
        self.hpaned.set_position(pos);

    def set_fullscreen(self):
        www = Gdk.screen_width();
        hhh = Gdk.screen_height();
        self.resize(www, hhh)

    def showcursor(self, flag):

        self.waiting = flag
        if self.waiting:
            #print("Wait cursor on")
            cur = self.wait_cursor
        else:
            cur = self.regular_cursor

        self.view1.get_window(Gtk.TextWindowType.TEXT).set_cursor(cur)

        wx, wy = self.view1.get_pointer()
        bx, by = self.view1.window_to_buffer_coords(Gtk.TextWindowType.TEXT, wx, wy)
        self.set_cursor_if_appropriate (self.view1, bx, by)

    # We manipulate the buffers through these functions:

    def clear(self, flag=False):
        if flag:
            self.buffer_2.set_text("", 0)
        else:
            self.buffer_1.set_text("", 0)

    def add_pixbuf(self, pixbuf, flag=False):
        #print("pix beg", self.curriter().get_offset())
        if flag:
            self.buffer_2.insert_pixbuf(curriter(), pixbuf)
        else:
            self.buffer_1.insert_pixbuf(self.curriter(), pixbuf)
        self.waiting = False
        #print("pix end", self.curriter().get_offset())

    def add_broken(self, flag=False):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.broken_img_path)
        except:
            #print("insert broken", sys.exc_info())
            self.waiting = False
            return
        self.add_pixbuf(pixbuf, flag)

    def add_text(self, text, flag=False):
        #print("txt beg", self.curriter().get_offset())
        if flag:
            self.buffer_2.insert(self.curriter2(), text)
        else:
            self.buffer_1.insert(self.curriter(), text)
        self.waiting = False

    def curriter(self):
        pos = self.buffer_1.get_property("cursor-position")
        iterx = self.buffer_1.get_iter_at_offset(pos)
        return iterx

    def curriter2(self):
        pos = self.buffer_2.get_property("cursor-position")
        iterx = self.buffer_2.get_iter_at_offset(pos)
        return iterx

    def add_text_xtag(self, text, tags, flag=False):

        #print("add_text_xtag", self.curriter().get_offset(), "text:", "'" + utils.esc(text) + "'")
        if flag:
            try: self.buffer_2.get_tag_table().add(tags)
            except: pass
            self.buffer_2.insert_with_tags(curriter2(), text, tags)
        else:
            try: self.buffer_1.get_tag_table().add(tags)
            except: print("get_tag", sys.exc_info())
            self.buffer_1.insert_with_tags(self.curriter(), text, tags)

        #self.curriter().forward_char()
        #print("xtxt end", self.curriter().get_offset())
        self.waiting = False

    def add_text_sub(self, txt, create = False, flag=False):

        print("add_text_sub", self.curriter().get_offset(), "text:", "'" + utils.esc(txt) + "'")
        if flag:
            pass
        else:
            mark = None
            if create:
                while True:
                    if not self.wait:
                        break
                    usleep(10)
                vvv = self.view1.get_buffer()
                pos = vvv.get_property("cursor-position")
                #print("cursor:", pos)
                iterx = vvv.get_iter_at_offset(pos-1)
                mark = vvv.create_mark(None, iterx, False)
            self.wait = True
            GLib.timeout_add(10, self.add_subx, txt, mark, create)

            #self.add_subx(txt, mark, create)
        self.waiting = False
        # Wait

    def add_subx(self, txt, mark, create):
        #print("add_subx(", txt, ")", mark, create)
        vvv = self.view1.get_buffer()
        if create:
            iterx = vvv.get_iter_at_mark(mark)
            #print(iterx", iterx)
            anc = vvv.create_child_anchor(iterx)
            floater = self.new_sub_text(txt)
            self.view1.add_child_at_anchor(floater, anc)
        else:
            #iterx = vvv.get_iter_at_mark(self.mark)
            floater = self.floatlist[self.currfloat - 1]
            #fff = floater.get_buffer()
            #end   = fff.get_end_iter()
            #old = self.floater.get_buffer().get_text(start, end, False)
            #print("old", old)
            floater.get_buffer().set_text(txt)
            #self.floater.queue_draw()

        #floater2 = self.new_sub_text("hello\nWorkld2")
        #self.view1.add_child_at_anchor(floater2, anc)

        #self.view1.add_child_in_window(self.lab,
        #    self.view1, 100, 100)
        self.wait = False

    def new_sub_text(self, txt):
        #floater = PangoView(self.pvg)
        floater = Gtk.TextView()
        #floater = Gtk.PangoView()
        floater.get_buffer().set_text(txt)
        floater.override_background_color(Gtk.StateFlags.NORMAL,
                                                    Gdk.RGBA(.9, .9, .9))
        floater.show()
        self.floatlist.append(floater)
        self.currfloat += 1
        return floater

    # --------------------------------------------------------------------
    # Links can be activated by pressing Enter.

    def key_press_event(self, text_view, event):

        if self.pvg.verbose > 1:
            print("Key", event.keyval)

        if (event.keyval == Gdk.KEY_Return or
            event.keyval == Gdk.KEY_KP_Enter):
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.follow_if_link(text_view, iter)
        elif event.keyval == Gdk.KEY_Tab:
            if self.pvg.verbose > 0:
                print ("Tab")
            return True
            pass
        elif event.keyval == Gdk.KEY_space:
            if self.pvg.verbose > 0:
                print ("Space")
                # Imitate page down

        elif event.keyval == Gdk.KEY_BackSpace:
            if self.bs_callback:
                self.bs_callback()

        elif event.keyval == Gdk.KEY_Left:
            if self.bs_callback:
                self.bs_callback()

        elif event.keyval == Gdk.KEY_b:
            if self.bs_callback:
                self.bs_callback()

        elif event.keyval == Gdk.KEY_r:
            if self.pvg.verbose:
                print("reload")
            global rcnt
            rcnt += 1

            self.showfile(self.lastfile, rcnt)

        elif event.keyval == Gdk.KEY_Escape or event.keyval == Gdk.KEY_q:
            sys.exit(0)

        elif event.state & Gdk.ModifierType.MOD1_MASK:
            if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
                sys.exit(0)
        else:
            if self.pvg.verbose > 1:
                print("Dead key")

        return False

    def key_press_event2(self, text_view, event):

        if (event.keyval == Gdk.KEY_Return or
            event.keyval == Gdk.KEY_KP_Enter):
            buffer = text_view.get_buffer()
            iter = buffer.get_iter_at_mark(buffer.get_insert())
            self.follow_if_link(text_view, iter)
        elif event.keyval == Gdk.KEY_Tab:
            if self.pvg.verbose > 1:
                print ("Tab2")
            pass
        elif event.keyval == Gdk.KEY_space:
            if self.pvg.verbose > 1:
                print ("Space2")
            pass
        elif event.keyval == Gdk.KEY_BackSpace:
            if self.bs_callback:
                self.bs_callback()

        elif event.keyval == Gdk.KEY_Escape or event.keyval == Gdk.KEY_q:
            sys.exit(0)

        elif event.keyval == Gdk.KEY_r:
            if self.pvg.verbose:
                print("reload2")
            self.showfile(self.lastfile)

        elif event.state & Gdk.ModifierType.MOD1_MASK:
            if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
                sys.exit(0)
        else:
            pass

        return False

    # Links can also be activated by clicking.
    def event_after(self, text_view, event):
        if event.type != Gdk.EventType.BUTTON_RELEASE:
            return False
        #print("event", event)
        #if event.button != 1:
        #    return False
        buffer = text_view.get_buffer()
        # We should not follow a link if the user has selected something
        try:
            start, end = buffer.get_selection_bounds()
        except ValueError:
            # If there is nothing selected ..
            pass
        else:
            if start.get_offset() != end.get_offset():
                return False
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        #print("got", x, y)
        iter = text_view.get_iter_at_location(x, y)[1]
        #print("iter", iter)
        self.follow_if_link(text_view, iter)
        return False

    def follow_if_link(self, text_view, iter):

        ''' Looks at all tags covering the position of iter in the text view,
            and if one of them is a link, follow it by showing the page identified
            by the data attached to it.
        '''

        tags = iter.get_tags()
        for tag in tags:
            page = tag.link
            #prinpage", page)
            if page != "":
                #print ("Calling link ", page)
                # Paint a new cursor
                self.waiting = True
                wx, wy = text_view.get_pointer()
                bx, by = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, wx, wy)
                self.set_cursor_if_appropriate (text_view, bx, by)
                if self.link_callback:
                    self.link_callback(page)
                break

    # Looks at all tags covering the position (x, y) in the text view,
    # and if one of them is a link, change the cursor to the "hands" cursor
    # typically used by web browsers.

    def set_cursor_if_appropriate(self, text_view, x, y):

        buffer = text_view.get_buffer()
        iterx = text_view.get_iter_at_position(x, y)
        tags = iterx[1].get_tags()
        hovering = False
        for tag in tags:
            page = tag.link
            #if page != 0:
            if page != "":
                #print("tag link:", page)
                hovering = True
                break

        if self.waiting:
            #print("Wait cursor on")
            cur = self.wait_cursor
        elif hovering:
            cur = self.hand_cursor
        else:
            cur = self.regular_cursor
        try:
            text_view.get_window(Gtk.TextWindowType.TEXT).set_cursor(cur)
        except:
            print (sys.exc_info())

    # Update the cursor image if the pointer moved.

    def motion_notify_event(self, text_view, event):

        # Throttle it
        now = time.time()
        if  now - self.old_time < .1:
            return
        self.old_time = now
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
                int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)

    def realized(self, win):
        # Load file
        #print("realized")
        pass

    # Also update the cursor image if the window becomes visible
    # (e.g. when a window covering it got iconified).

    def visibility_notify_event(self, text_view, event):

        wx, wy = text_view.get_pointer()
        bx, by = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def event_after2(self, text_view, event):
        if event.type != Gdk.EventType.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False
        buffer = text_view.get_buffer()

        # we should not follow a link if the user has selected something
        try:
            start, end = buffer.get_selection_bounds()
        except ValueError:
            # If there is nothing selected, None is return
            pass
        else:
            if start.get_offset() != end.get_offset():
                return False

        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        iter = text_view.get_iter_at_location(x, y)

        self.follow_if_link(text_view, iter)
        return False

    def visibility_notify_event2(self, text_view, event):
        wx, wy = text_view.get_pointer()
        bx, by = text_view.window_to_buffer_coords\
            (Gtk.TextWindowType.WIDGET, wx, wy)

        self.set_cursor_if_appropriate (text_view, bx, by)
        return False

    def motion_notify_event2(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        #text_view.window.get_pointer()
        return False

    def reset(self):
        ''' Reset parser '''
        global ts
        ts.reset()

    def showfile(self, strx, reload = 1):
        #self.loadname = strx
        GLib.timeout_add(10, self._showfile, strx)

    def _showfile(self, strx, reload = 1):

        #global buf, xstack, self.pvg, ts
        self.showcursor(True)

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

        self.clear()
        self.reset()
        parser.Parser(self.pvg).process(buf)
        self.showcursor(False)

        # Output results
        if self.pvg.emit:
            show_emit()

        self.set_title("%s -- %d" % (strx, reload))

        self.buffer_1.place_cursor(self.buffer_1.get_start_iter())
        self.buffer_2.place_cursor(self.buffer_2.get_start_iter())

    def main(self):
        Gtk.main()

# ------------------------------------------------------------------------

def     message_dialog(title, strx):

    dialog = Gtk.MessageDialog()
    #mw,
    #        Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
    #        Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK, strx)

    dialog.set_title(title);
    dialog.set_markup(strx);
    dialog.add_button("OK", 0)
    dialog.run()
    dialog.destroy()

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
