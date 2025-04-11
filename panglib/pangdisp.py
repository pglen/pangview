#!/usr/bin/env python

import sys, os, re, time

import  panglib.parser as parser
import  panglib.stack as stack
import  panglib.lexer as lexer
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

class PangoView(Gtk.Window):

    hovering_over_link = False
    waiting = False

    hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
    regular_cursor = Gdk.Cursor(Gdk.CursorType.XTERM)
    wait_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
    callback = None
    bscallback = None

    # Create the toplevel window
    def __init__(self, pvg, parent=None):

        global mw
        mw = self
        self.pvg = pvg
        self.lastfile = ""
        Gtk.Window.__init__(self)
        self.cb = pangfunc.CallBack(ts, add_text, add_image, emit_one)
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

        view1 = Gtk.TextView();
        view1.set_border_width(8)

        view1.connect("key-press-event", self.key_press_event)
        view1.connect("event-after", self.event_after)
        view1.connect("motion-notify-event", self.motion_notify_event)
        view1.connect("visibility-notify-event", self.visibility_notify_event)

        view1.set_editable(False)
        view1.set_cursor_visible(False)
        self.view = view1

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

        self.iter = self.buffer_1.get_iter_at_offset(0)
        self.iter2 = self.buffer_1.get_iter_at_offset(0)

        self.set_focus(view1)

        self.show_all()

    def set_pane_position(self, pos):
        self.hpaned.set_position(pos);

    def set_fullscreen(self):
        www = Gdk.screen_width();
        hhh = Gdk.screen_height();
        self.resize(www, hhh)

    def showcur(self, flag):
        #return
        self.waiting = flag
        #wx, wy, modx = self.view.window.get_pointer()
        wx, wy = self.view.get_pointer()

        bx, by = self.view.window_to_buffer_coords(Gtk.TextWindowType.TEXT, wx, wy)
        self.set_cursor_if_appropriate (self.view, bx, by)
        #self.view.window.get_pointer()

    # We manipulate the buffers through these functions:

    def clear(self, flag=False):
        if flag:
            self.buffer_2.set_text("", 0)
            self.iter2 = self.buffer_2.get_iter_at_offset(0)
        else:
            self.buffer_1.set_text("", 0)
            self.iter = self.buffer_1.get_iter_at_offset(0)

    def add_pixbuf(self, pixbuf, flag=False):
        #print("pix beg", self.iter.get_offset())
        if flag:
            self.buffer_2.insert_pixbuf(self.iter2, pixbuf)
        else:
            self.buffer_1.insert_pixbuf(self.iter, pixbuf)
        self.waiting = False
        #print("pix end", self.iter.get_offset())

    def add_broken(self, flag=False):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.broken_img_path)
        except:
            #print("insert broken", sys.exc_info())
            self.waiting = False
            return
        self.add_pixbuf(pixbuf, flag)

    def add_text(self, text, flag=False):
        #print("txt beg", self.iter.get_offset())
        if flag:
            self.buffer_2.insert(self.iter2, text)
        else:
            self.buffer_1.insert(self.iter, text)
        self.waiting = False

    def add_text_tag(self, text, tags, flag=False):
        #print("txt tag beg", self.iter.get_offset())
        if flag:
            self.buffer_2.insert_with_tags_by_name(self.iter2, text, tags)
        else:
            self.buffer_1.insert_with_tags_by_name(self.iter, text, tags)
        #print("txtt end", self.iter.get_offset())
        self.waiting = False

    def add_text_xtag(self, text, tags, flag=False):
        #print("xtxt beg", self.iter.get_offset(), "text:", "'" + text + "'")
        if flag:
            try: self.buffer_2.get_tag_table().add(tags)
            except: pass
            self.buffer_2.insert_with_tags(self.iter2, text, tags)
        else:
            try: self.buffer_1.get_tag_table().add(tags)
            except: print("get_tag", sys.exc_info())

            self.buffer_1.insert_with_tags(self.iter, text, tags)
        #self.iter.forward_char()
        #print("xtxt end", self.iter.get_offset())
        self.waiting = False

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

            pass
        elif event.keyval == Gdk.KEY_BackSpace:
            if self.bscallback:
                self.bscallback()

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
            #print ("Tab2")
            pass
        elif event.keyval == Gdk.KEY_space:
            #print ("Space2")
            pass
        elif event.keyval == Gdk.KEY_BackSpace:
            if self.bscallback:
                self.bscallback()

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
            #print("page", page)
            if page != None:
                #print ("Calling link ", page)
                # Paint a new cursor
                self.waiting = True
                wx, wy = text_view.get_pointer()
                bx, by = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, wx, wy)
                self.set_cursor_if_appropriate (text_view, bx, by)
                #text_view.window.get_pointer()

                if self.callback:
                    self.callback(page)
                break

    # Looks at all tags covering the position (x, y) in the text view,
    # and if one of them is a link, change the cursor to the "hands" cursor
    # typically used by web browsers.

    def set_cursor_if_appropriate(self, text_view, x, y):

        '''hovering = False
        buffer = text_view.get_buffer()
        #iter = text_view.get_iter_at_location(x, y)
        iter = text_view.get_iter_at_position(x, y)
        tags = iter.get_tags()
        for tag in tags:
            page = tag.get_data("link")
            #if page != 0:
            if page != None:
                hovering = True
                break

        if hovering != self.hovering_over_link:
            self.hovering_over_link = hovering
        '''

        if self.waiting:
            cur = self.wait_cursor
        elif self.hovering_over_link:
            cur = self.hand_cursor
        else:
            cur = self.regular_cursor

        try:
            text_view.get_window(Gtk.TextWindowType.TEXT).set_cursor()
        except:
            print (sys.exc_info())

    # Update the cursor image if the pointer moved.

    def motion_notify_event(self, text_view, event):
        x, y = text_view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
            int(event.x), int(event.y))
        self.set_cursor_if_appropriate(text_view, x, y)
        #text_view.window.get_pointer()
        return False

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

    def set_cursor_if_appropriate2(self, text_view, x, y):

        hovering = False
        buffer = text_view.get_buffer()
        iter = text_view.get_iter_at_location(x, y)
        tags = iter.get_tags()
        for tag in tags:
            page = tag.get_data("link")
            #if page != 0:
            if page != None:
                hovering = True
                break

        if hovering != self.hovering_over_link:
            self.hovering_over_link = hovering

        if self.waiting:
            text_view.get_window(Gtk.TEXT_WINDOW_TEXT).set_cursor(self.wait_cursor)
        elif self.hovering_over_link:
            text_view.get_window(Gtk.TEXT_WINDOW_TEXT).set_cursor(self.hand_cursor)
        else:
            text_view.get_window(Gtk.TEXT_WINDOW_TEXT).set_cursor(self.regular_cursor)

    def reset(self):
        ''' Reset parser '''
        self.clear(self.pvg.flag)
        #ts.clear()
        global ts
        ts = textstate.TextState()

    def showfile(self, strx, reload = 1):

        #global buf, xstack, self.pvg, ts

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

        self.reset()
        got_clock =  time.clock()
        parser.Parser(self.pvg).process(buf)
        self.showcur(False)

        if self.pvg.show_timing:
            print  ("parser:", time.clock() - got_clock)

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

# EOF
