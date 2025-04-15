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

class PangEdit(Gtk.TextView):

    hovering_over_link = False
    waiting = False

    hand_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
    regular_cursor = Gdk.Cursor(Gdk.CursorType.XTERM)
    wait_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)

    def __init__(self, pvg):

        Gtk.TextView.__init__(self)

        self.rcnt = 0
        self.floatlist = []
        self.currfloat = 0
        self.old_time = time.time()
        self.pvg = pvg
        self.set_border_width(8)

        self.connect("key-press-event", self.key_press_event)
        self.connect("event-after", self.event_after)
        self.connect("motion-notify-event", self.motion_notify_event)
        self.connect("visibility-notify-event", self.visibility_notify_event)

        self.set_editable(False)
        self.set_cursor_visible(False)

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
            pass
            #if self.pvg.verbose:
            #    print("reload")
            #self.rcnt += 1
            #self.showfile(self.lastfile, self.rcnt)

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

        #self.view1.get_window(Gtk.TextWindowType.TEXT).set_cursor(cur)
        #wx, wy = self.view1.get_pointer()
        #bx, by = self.view1.window_to_buffer_coords(Gtk.TextWindowType.TEXT, wx, wy)
        #self.set_cursor_if_appropriate (self.view1, bx, by)

    def showcursor(self, flag):
        self.waiting = flag
        if self.waiting:
            #print("Wait cursor on")
            cur = self.wait_cursor
        else:
            cur = self.regular_cursor

        #self.get_window(Gtk.TextWindowType.TEXT).set_cursor(cur)
        wx, wy = self.get_pointer()
        bx, by = self.window_to_buffer_coords(Gtk.TextWindowType.TEXT, wx, wy)
        self.set_cursor_if_appropriate (self, bx, by)

    def curriter(self):
        pos = self.get_buffer().get_property("cursor-position")
        iterx = self.get_buffer().get_iter_at_offset(pos)
        return iterx

    def add_image(self, pixbuf):
        self.get_buffer().insert_pixbuf(self.curriter(), pixbuf)

    def insert(self, txt):
        self.get_buffer().insert(self.curriter(), txt)

    def add_text_xtag(self, txt, tags):
        vvv = self.get_buffer()
        try:
            vvv.get_tag_table().add(tags)
        except: pass
        vvv.insert_with_tags(self.curriter(), txt, tags)

    def add_text_sub(self, txt, create, background):

        #print("add_text_sub", self.curriter().get_offset(),
        #            txt, create, background)

        if create:
            vvv = self.get_buffer()
            pos = vvv.get_property("cursor-position")
            iterx = vvv.get_iter_at_offset(pos-1)
            #mark = vvv.create_mark(None, iterx)
            #iterx2 = vvv.get_iter_at_mark(mark)
            anc = vvv.create_child_anchor(iterx)
            floater = self._new_sub_text(txt)
            self.add_child_at_anchor(floater, anc)
        else:
            #GLib.timeout_add(300, self.execsub, txt)
            floater = self.floatlist[self.currfloat - 1]
            if background:
                #print("bg", "'" + background + "'")
                col = Gdk.RGBA(.97,.97,.97)
                ret = Gdk.RGBA.parse(col, background)
                #print("colparse", ret)
                floater.override_background_color(
                        Gtk.StateFlags.NORMAL, col)

            floater.showbuff(txt)
            self.usleep(10)      # Must bread for showing sub
        self.waiting = False

    def _new_sub_text(self, txt):
        floater = PangEdit(self.pvg)
        self.floatlist.append(floater)
        self.currfloat += 1
        floater.show()
        return floater

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

        self.waiting = False

    def showbuff(self, buf):

        action = parser.Action()
        action.mainadd = self.add_text_xtag
        action.mainimg = self.add_image
        action.mainsub = self.add_text_sub
        ppp = parser.Parser(self.pvg)
        ppp.action = action
        ppp.process(buf)
        #self.showcursor(False)

    def  usleep(self, msec):
        got_clock = time.clock() + float(msec) / 1000
        #print(got_clock)
        while True:
            if time.clock() > got_clock:
                break
            Gtk.main_iteration_do(False)

# EOF
