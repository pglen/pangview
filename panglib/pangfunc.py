#!/usr/bin/env python

#import pygtk, gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango
from gi.repository import GdkPixbuf

import copy
import panglib.stack as stack
import panglib.parser as parser
import panglib.utils as utils
import panglib.pangparse as parsedata

old_stresc = ""
accum = ""
old_xtag = None
fontstack = stack.Stack()

#MainView = None

# ------------------------------------------------------------------------
# Hack for caching interaction with the pango subsystem.
# If the text formatting parameters have not changed, we accumulate the strings
# and dump it out when needed

# Check for state change by comparing object vars

def chkstate(obj_1, obj_2):

    ret = True
    if not obj_1: return ret
    if not obj_2: return ret

    # See if dictionaries match
    if len(obj_1.__dict__) != len(obj_2.__dict__):
        return ret
    ret = False
    # See if variables match
    for aa in obj_1.__dict__:
        if obj_1.__dict__[aa] !=  obj_2.__dict__[aa]:
            ret = True
            break
    return ret

class xTextTag(Gtk.TextTag):

    def __init__(self):
        Gtk.TextTag.__init__(self)
        self.link = ""
        #self.set_sensitive(True)
        #self.connect("event", self.clicked)

    def clicked(self, arg1, arg2, arg3, arg4):
        #print("Event", arg1, arg2,)
        pass

    def do_event(self, arg1, arg2, arg3):
        if arg2.type == Gdk.EventType.MOTION_NOTIFY:
            return
        #if not self.link:
        #    return
        #if arg2.type == Gdk.EventType.BUTTON_RELEASE:
        #    print("Link event", self.link)

# Callback class, extraction of callback functions from the pangview parser.
# The class TextState is the format controlling class, Mainview is the target
# window, and the Emit() function is to aid debug. These funtions may also
# manipulate the parser stack. Note the naming convention like Bold() for
# bold start, eBold() for bold end.

class CallBack():

    def __init__(self, TextState, mainadd, mainimg, mainemit):
        self.TextState = TextState
        self.TextStateOrg = copy.copy(self.TextState)
        self.gl_mainadd = mainadd
        self.gl_mainimg = mainimg
        self.gl_emit = mainemit
        self.pvg =  utils.pvg
        self.oldstate = None

    def emit(self, strx):
        self.flush()
        self.gl_emit(strx)

    def Comm(self, vparser, token, tentry):
        #print ("textstate comm", vparser.strx)
        self.TextState.skip = 1
        self.emit( "<comm>")

    def Comm2(self, vparser, token, tentry):
        self.TextState.comm2 = vparser.strx
        self.emit( "<comm2>")

    def Tab(self, vparser, token, tentry):
        #print ("textstate tab", vparser.strx)
        self.TextState.tab += 1
        self.emit( "<tab>")

    def Strike(self, vparser, token, tentry):
        self.TextState.strike = True
        self.emit( "<strike>")

    def eStrike(self, vparser, token, tentry):
        self.TextState.strike = False
        vparser.popstate()
        self.emit( "<estrike>")

    def Bold(self, vparser, token, tentry):
        #print ("got bold")
        self.TextState.bold = True
        self.emit( "<bold>")

    def eBold(self, vparser, token, tentry):
        #print ("got ebold")
        self.TextState.bold = False
        vparser.popstate()
        #vparser.popstate()
        self.emit( "<ebold>")

    def Italic(self, vparser, token, tentry):
        #print ("Got Italic")
        self.TextState.italic = True
        self.emit("<italic>")

    def eItalic(self, vparser, token, tentry):
        self.TextState.italic = False
        vparser.popstate()
        self.emit ("<eitalic>")

    def flush(self):
        #return
        global oldstate, accum

        if self.pvg.verbose > 3:
            print("flush:", accum)

        if accum != "":
            if self.oldstate:
                TextState2 = self.oldstate
            else:
                TextState2 =  self.TextState

            accum, xtag2 =  self.parseTextState(accum, TextState2)
            self.gl_mainadd(accum, xtag2)
            accum = ""

    # --------------------------------------------------------------------
    def Text(self, vparser, token, tentry):

        global oldstate, accum, old_stresc

        self.emit(vparser.strx)
        stresc = utils.unescape(vparser.strx)
        # If wrapping, output one space only
        if self.TextState.wrap:
            if stresc == " ":
                if old_stresc == " ":
                    return
                old_stresc = " "
            else:
                old_stresc = ""

        # Enable / Disable caching
        enable_cache = False #True
        #if enable_cache:
        #    if not chkstate(self.oldstate, self.TextState) and len(accum) < 1000:
        #        #print ("caching: '" + accum + "'")
        #        accum += stresc
        #        pass
        #    else:
        #        #print ("printing: '" +  accum + "'")
        #        pass
        #else:
        #    accum += stresc

        # Materialize text
        if self.TextState.hidden:
            if self.pvg.verbose:
                print ("Hidden text:", accum)
        else:
            #print   ("func", self.pvg.flag)
            #self.gl_mainadd(stresc, xtag, self.pvg.flag)
            textstate2 = self.TextState

            #if enable_cache:
            #    if self.oldstate:
            #        textstate2 = self.oldstate

            accum, xtag2 = self.parseTextState(accum, textstate2, vparser)
            self.gl_mainadd(accum, xtag2)
            accum = ""

        # Save tag state
        #self.oldstate = dupstate(self.TextState)
        accum += stresc
        self.oldstate = copy.deepcopy(self.TextState)

    def show_textstate_diff(self, TextState, strx):
        print(strx, "textstate:", end = " ")
        for aa in dir(TextState):
            if aa[:2] != "__":
                val = getattr(TextState, aa)
                if getattr(self.TextStateOrg, aa) != val:
                    print("diff =", aa, val, end = " ")
        print()

    # --------------------------------------------------------------------
    def parseTextState(self, text2, TextState, vparser = None):

        xtag = xTextTag()

        #print("textstate on ", "'" + text2 + "'")
        #self.show_textstate_diff(TextState)

        if self.TextState.comm2 != "":
            # Split
            pos = self.TextState.comm2.find("##")
            #print(self.TextState.comm2[:pos], " comm2", "\'" + text2 + "\'")
            text2 = "\n" + self.TextState.comm2[:pos]
            self.TextState.comm2 = ""

        if self.TextState.skip:
            #print(self.TextState.skip, "skip at", "\'" + text2 + "\'")
            if text2 == "\n":
                self.TextState.skip = 0
            return "", xtag

        # This is one shot per count, reset tab
        while  self.TextState.tab:
            self.TextState.tab -= 1
            #print(self.TextState.tab, "tab at", "\'" + text2 + "\'")
            text2 += "\t"

        if TextState.font != "":
            xtag.set_property("font", TextState.font)

        SCALE_LARGE = 1.2
        SCALE_X_LARGE = 1.4
        SCALE_XX_LARGE = 1.8
        SCALE_SMALL = 0.8
        SCALE_X_SMALL = 0.6

        # Decorate textag according to machine state
        if TextState.fixed:    xtag.set_property("family", "Monospace")
        if TextState.bold:     xtag.set_property("weight", Pango.Weight.BOLD)
        if TextState.italic:   xtag.set_property("style", Pango.Style.ITALIC)
        #if TextState.itbold:   xtag.set_property("foreground", "red")
        if TextState.large:    xtag.set_property("scale", SCALE_LARGE)
        if TextState.xlarge:   xtag.set_property("scale", SCALE_X_LARGE)
        if TextState.xxlarge:  xtag.set_property("scale", SCALE_XX_LARGE)
        if TextState.small:    xtag.set_property("scale", SCALE_SMALL)
        if TextState.xsmall:    xtag.set_property("scale", SCALE_X_SMALL)
        if TextState.ul:       xtag.set_property("underline", Pango.Underline.SINGLE)
        if TextState.dul:      xtag.set_property("underline", Pango.Underline.DOUBLE)

        if TextState.red:      xtag.set_property("foreground", "red")
        if TextState.green:    xtag.set_property("foreground", "green")
        if TextState.blue:     xtag.set_property("foreground", "blue")

        if TextState.bgred:    xtag.set_property("background", "red")
        if TextState.bggreen:  xtag.set_property("background", "green")
        if TextState.bgblue:   xtag.set_property("background", "blue")

        if TextState.strike:   xtag.set_property("strikethrough", True)
        if TextState.wrap:     xtag.set_property("wrap_mode", Gtk.WrapMode.WORD)

        if TextState.center:   xtag.set_property("justification", Gtk.Justification.CENTER)
        if TextState.right:    xtag.set_property("justification", Gtk.Justification.RIGHT)
        if TextState.fill:     xtag.set_property("justification", Gtk.Justification.FILL)

        #print ("bgcolor:",  TextState.bgcolor )
        if TextState.bgcolor != "":
            xtag.set_property("background", TextState.bgcolor)

        #print ("color:",  TextState.color )
        if TextState.color != "":
            xtag.set_property("foreground", TextState.color)

        if TextState.size != 0:
            xtag.set_property("size", TextState.size * Pango.SCALE)

        if TextState.link != "":
            xtag.link = TextState.link
            #xtag.set_property("link", TextState.link)
            #print("Link", TextState.link)
            if TextState.color == "":
                xtag.set_property("foreground", "blue")

        # Sub / Super sets the size again ...
        if TextState.sub:
            rr = -4; ss = 8
            if TextState.size != 0:
                rr = - TextState.size / 6
                ss  = TextState.size / 2
            xtag.set_property("rise", rr * Pango.SCALE)
            xtag.set_property("size", ss * Pango.SCALE)

        if TextState.sup:
            rr = 6; ss = 8
            if TextState.size != 0:
                rr =  TextState.size / 2
                ss  = TextState.size /2
            xtag.set_property("rise", rr * Pango.SCALE)
            xtag.set_property("size", ss * Pango.SCALE)

        # Calculate current indent
        ind = TextState.indent * 32;
        #if TextState.indent > 0:
        xtag.set_property("indent", ind)

        # Calculate current margin
        ind = TextState.margin * 32;
        if TextState.margin > 0:
            xtag.set_property("left_margin", ind)
            xtag.set_property("right_margin", ind)

        # Calculate current Left margin
        ind = TextState.lmargin * 32;
        if TextState.lmargin > 0:
            xtag.set_property("left_margin", ind)

        return text2, xtag


    def Bgred(self, vparser, token, tentry):
        self.TextState.bgred = True
        self.emit( "<bgred>")

    def eBgred(self, vparser, token, tentry):
        self.TextState.bgred = False
        vparser.popstate()
        self.emit( "<ebgred>")

    def Bggreen(self, vparser, token, tentry):
        self.TextState.bggreen = True
        self.emit( "<bggreen>")

    def eBggreen(self, vparser, token, tentry):
        self.TextState.bggreen = False
        vparser.popstate()
        self.emit( "<ebggreen>")

    def Bgblue(self, vparser, token, tentry):
        self.TextState.bgblue = True
        self.emit( "<bgblue>")

    def eBgblue(self, vparser, token, tentry):
        self.TextState.bgblue = False
        vparser.popstate()
        self.emit( "<ebgblue>")

    def Xlarge(self, vparser, token, tentry):
        self.TextState.xlarge = True
        self.emit( "<xlarge>")

    def eXlarge(self, vparser, token, tentry):
        self.TextState.xlarge = False
        vparser.popstate()
        self.emit( "<exlarge>")

    def Large(self, vparser, token, tentry):
        self.TextState.large = True
        self.emit( "<large>")

    def eLarge(self, vparser, token, tentry):
        self.TextState.large = False
        vparser.popstate()
        self.emit( "<elarge>")

    def Dunderline(self, vparser, token, tentry):
        self.TextState.dul = True
        self.emit( "<dunderline>")

    def eDunderline(self, vparser, token, tentry):
        self.TextState.dul = False
        vparser.popstate()
        self.emit( "<edunderline>")

    def Underline(self, vparser, token, tentry):
        self.TextState.ul = True
        self.emit( "<underline>")

    def eUnderline(self, vparser, token, tentry):
        self.TextState.ul = False
        vparser.popstate()
        self.emit( "<eunderline>")

    def ItBold(self, vparser, token, tentry):
        self.TextState.itbold = True
        self.emit( "<itbold>")

    def eItBold(self, vparser, token, tentry):
        self.TextState.itbold = False
        vparser.popstate()
        self.emit( "<eitbold>")

    def Green(self, vparser, token, tentry):
        self.TextState.green = True
        self.emit( "<green>")

    def eGreen(self, vparser, token, tentry):
        self.TextState.green = False
        vparser.popstate()
        self.emit( "<egreen>")

    def Blue(self, vparser, token, tentry):
        self.TextState.blue = True
        self.emit( "<blue>")

    def eBlue(self, vparser, token, tentry):
        self.TextState.blue = False
        vparser.popstate()
        self.emit( "<eblue>")

    def Red(self, vparser, token, tentry):
        self.TextState.red = True
        self.emit( "<red>")

    def eRed(self, vparser, token, tentry):
        self.TextState.red = False
        vparser.popstate()
        self.emit( "<ered>")

    def Center(self, vparser, token, tentry):
        self.TextState.center = True
        self.emit( "<center>")

    def eCenter(self, vparser, token, tentry):
        self.TextState.center = False
        vparser.popstate()
        self.emit( "<ecenter>")

    def Right(self, vparser, token, tentry):
        self.TextState.right = True
        self.emit( "<right>")

    def eRight(self, vparser, token, tentry):
        self.TextState.right = False
        vparser.popstate()
        self.emit( "<eright>")

    def Xsmall(self, vparser, token, tentry):
        self.TextState.xsmall = True
        self.emit( "<xsmall>")

    def eXsmall(self, vparser, token, tentry):
        self.TextState.xsmall = False
        vparser.popstate()
        self.emit( "<exsmall>")

    def Small(self, vparser, token, tentry):
        self.TextState.small = True
        self.emit( "<small>")

    def eSmall(self, vparser, token, tentry):
        self.TextState.small = False
        vparser.popstate()
        self.emit( "<esmall>")

    def Xxlarge(self, vparser, token, tentry):
        self.TextState.xxlarge = True
        self.emit( "<xxlarge>")

    def eXxlarge(self, vparser, token, tentry):
        self.TextState.xxlarge = False
        vparser.popstate()
        self.emit( "<exxlarge>")

    def Margin(self, vparser, token, tentry):
        self.TextState.margin += 1
        self.emit( "<margin>")

    def eMargin(self, vparser, token, tentry):
        if self.TextState.margin > 0:
            self.TextState.margin -= 1
        vparser.popstate()
        self.emit( "<emargin>")

    def Lmargin(self, vparser, token, tentry):
        self.TextState.lmargin += 1
        self.emit( "<margin>")

    def eLmargin(self, vparser, token, tentry):
        if self.TextState.lmargin > 0:
            self.TextState.lmargin -= 1
        vparser.popstate()
        self.emit( "<emargin>")

    def Fixed(self, vparser, token, tentry):
        self.TextState.fixed = True
        self.emit( "<fixed>")

    def eFixed(self, vparser, token, tentry):
        self.TextState.fixed = False
        vparser.popstate()
        self.emit( "<efixed>")

    def Sup(self, vparser, token, tentry):
        self.TextState.sup = True
        self.emit( "<sup>")

    def eSup(self, vparser, token, tentry):
        self.TextState.sup = False
        vparser.popstate()
        self.emit( "<esup>")

    def Sub(self, vparser, token, tentry):
        self.TextState.sub = True
        self.emit( "<sub>")

    def eSub(self, vparser, token, tentry):
        self.TextState.sub = False
        vparser.popstate()
        self.emit( "<esub>")

    def Hid(self, vparser, token, tentry):
        self.TextState.hidden = True
        self.emit( "<hid>")

    def eHid(self, vparser, token, tentry):
        self.TextState.hidden = False
        vparser.popstate()
        self.emit( "<ehid>")

    def Indent(self, vparser, token, tentry):
        self.TextState.indent += 1
        self.emit( "<indent>")

    def eIndent(self, vparser, token, tentry):
        if self.TextState.indent > 0:
            self.TextState.indent -= 1
        vparser.popstate()
        self.emit( "<eindent>")

    def Wrap(self, vparser, token, tentry):
        self.TextState.wrap = True
        self.emit( "<wrap>")

    def eWrap(self, vparser, token, tentry):
        self.TextState.wrap = False
        vparser.popstate()
        self.emit( "<ewrap>")

    def Fill(self, vparser, token, tentry):
        self.TextState.fill = True
        self.emit( "<fill>")

    def eFill(self, vparser, token, tentry):
        self.TextState.fill = False
        vparser.popstate()
        self.emit( "<efill>")

    def Nbgcol(self, vparser, token, tentry):
        self.emit( "<nbgcol> " + vparser.strx[3:len(vparser.strx)-1])
        self.TextState.bgcolor = vparser.strx[3:len(vparser.strx)-1]

    def eNbgcol(self, vparser, token, tentry):
        vparser.popstate()
        self.TextState.bgcolor = ""
        self.emit( "<enbgcol> ")

    def Ncol(self, vparser, token, tentry):
        self.emit( "<ncol> " + vparser.strx)
        self.TextState.color = vparser.strx[1:len(vparser.strx)-1]

    def Ncol2(self, vparser, token, tentry):
        self.emit( "<ncol2> " + vparser.strx)
        self.TextState.color = vparser.strx[3:len(vparser.strx)-1]

    def eNcol(self, vparser, token, tentry):
        vparser.popstate()
        self.TextState.color = ""
        self.emit( "<encol> ")

    def Link(self, vparser, token, tentry):
        self.emit( "<link>")

    def Link2(self, vparser, token, tentry):
        xstack = stack.Stack()
        # Walk link optionals:
        while True:
            fsm, contflag, ttt, stry = vparser.fstack.peek()
            if fsm == parsedata.st.KEYVAL:
                fsm, contflag, ttt, stry = vparser.fstack.pop()
                #print (" Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            )
                xstack.push([ttt, "=", stry])
            else:
                break
            if vparser.contflag == 0:
                break
        while True:
            xkey = xstack.pop()
            if not xkey:
                break
            kk, ee, vv = xkey;
            vv = vv.replace("\"",""); vv = vv.replace("\'","")
            #print ("link key: '" + kk + "' val: '" + vv + "'")
            if kk == "file" or kk == "name":
                # Try docroot - current dir - home dir
                fname = self.pvg.docroot + "/" + vv
                if not utils.isfile(fname):
                    fname = vv
                    if not utils.isfile(fname):
                        fname = "~/" + vv
                        if not utils.isfile(fname):
                            fname = vv

                self.TextState.link = fname
            if kk == "color" or kk == "fg":
                #print ("setting color in link")
                self.TextState.color = vv

        self.emit( "<link2>")

    def eLink(self, vparser, token, tentry):
        self.TextState.link = ""
        self.TextState.color = ""
        vparser.popstate()
        self.emit( "<elink>")

    def Image(self, vparser, token, tentry):
        self.emit( "<image>")
        #print("Image")

    def Image2(self, vparser, token, tentry):
        self.flush()
        xstack = stack.Stack()
        # Walk optionals:
        while True:
            fsm, contflag, ttt, stry = vparser.fstack.peek()
            if fsm == parsedata.st.KEYVAL:
                fsm, contflag, ttt, stry = vparser.fstack.pop()
                xstack.push([ttt, "=", stry])
            else:
                break
            if vparser.contflag == 0:
                break
        xtag = xTextTag();  fname = ""; www = 0; hhh = 0
        while True:
            xkey = xstack.pop()
            if not xkey:
                break
            kk, ee, vv = xkey;
            vv = vv.replace("\"",""); vv = vv.replace("\'","")

            #print ("key: '" + kk + "' val: '" + vv + "'")

            if kk == "align":
                if vv == "left":
                    xtag.set_property("justification", Gtk.Justification.LEFT)
                elif vv == "center":
                    xtag.set_property("justification", Gtk.Justification.CENTER)
                elif vv == "right":
                    xtag.set_property("justification", Gtk.Justification.RIGHT)

            if kk == "width":
                www = int(vv)

            if kk == "height":
                hhh = int(vv)

            if kk == "name" or kk == "file":
                # Try docroot - curr dir - home/Pictures - home
                fname = self.pvg.docroot + "/" + vv
                if not utils.isfile(fname):
                    fname = vv
                    if not utils.isfile(fname):
                        fname = "~/Pictures" + vv
                        if not utils.isfile(fname):
                            fname = "~/" + vv

        # Exec collected stuff
        self.gl_mainadd(" ", xtag)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(fname)
            if www and hhh:
                #print ("scaling to", www, hhh)
                pixbuf2 = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, www, hhh)
                pixbuf.scale(pixbuf2, 0, 0, www, hhh,
                    0, 0, float(www)/pixbuf.get_width(), float(hhh)/pixbuf.get_height(),
                        GdkPixbuf.InterpType.BILINEAR)
                pixbuf = pixbuf2
            self.gl_mainimg(pixbuf)

        except GObject.GError as error:
            #print ("Failed to load image file '" + vv + "'")
            self.gl_mainimg(None)
            pass

        vparser.popstate()
        self.emit( "<image2>")

    def eImage(self, vparser, token, tentry):
        print("eimage")
        vparser.popstate()
        self.emit( "<eimage>")

    def Span(self, vparser, token, tentry):
        fontstack.push(copy.copy(self.TextState))
        self.emit("<span >")

    def Span2(self, vparser, token, tentry):

        #vparser.pushstate(token)

        xstack2 = stack.Stack()
        # Walk keyvals and optionals:
        while True:
            fsm, contflag, ttt, stry = vparser.fstack.peek()
            if fsm == parsedata.st.KEYVAL:
                fsm, contflag, ttt, stry = vparser.fstack.pop()
                #print (" pop      ", fsm, contflag, ttt, stry)
                xstack2.push([ttt, "=", stry])
            else:
                break
            if contflag == 0:
                break

        # Set font parameters:
        while True:
            xkey = xstack2.pop()
            if not xkey:
                break
            kk, ee, vv = xkey;
            vv = vv.replace("\"",""); vv = vv.replace("\'","")
            #print ("key: ",kk, vv)
            if kk == "background" or kk == "bg" or kk == "bgcolor":
                self.TextState.bgcolor = vv
            if kk == "foreground" or kk == "fg" or kk == "color":
                self.TextState.color = vv
            elif kk == "size":
                self.TextState.size = int(vv)
            elif kk == "font":
                self.TextState.font = vv
            elif kk == "bold":
                if utils.isTrue(vv):
                    self.TextState.bold = True
                else:
                    self.TextState.bold = False

            elif kk == "italic":
                if utils.isTrue(vv):
                    self.TextState.italic = True
                else:
                    self.TextState.italic = False

            elif kk == "under" or kk == "underline":
                if utils.isTrue(vv):
                    self.TextState.ul = True
                else:
                    self.TextState.ul = False

            elif kk == "align" or kk == "alignment":
                vvv = vv.lower()
                if vvv == "left":
                    self.TextState.left = True
                elif vvv == "right":
                    self.TextState.right = True
                elif vvv == "center":
                    #print (" centering")
                    self.TextState.center = True
                elif vvv == "middle":
                    #print (" centering")
                    self.TextState.center = True
            else:
                if self.pvg.warnings:
                   print("span - invalid argument:", "'" + kk + "'")

        vparser.popstate()
        self.emit("<spantxt >");

    def eSpan(self, vparser, token, tentry):
        #self.show_textstate_diff(self.TextState, "Org")
        old_state = fontstack.pop()
        if old_state:
            self.TextState = copy.copy(old_state)
            #self.show_textstate_diff(old_state, "Rest")

        #self.TextState.color    = old_state.color
        #self.TextState.bgcolor  = old_state.bgcolor
        #self.TextState.size     = old_state.size
        #self.TextState.font     = old_state.font
        #self.TextState.left     = old_state.left
        #self.TextState.center   = old_state.center
        #self.TextState.right    = old_state.right
        #self.TextState.ul       = old_state.ul
        #self.TextState.bold     = old_state.bold
        #self.show_textstate_diff(self.TextState)

        vparser.popstate()
        self.emit ("<espan>" )

    def Keyval(self, vparser, token, tentry):

        #print ("called keyval", vparser.fsm, "strx =", vparser.strx)

        # Pop two items, create keyval
        fsm, contflag, ttt, stry = vparser.fstack.pop()      # EQ
        #print("pop:", stry, "fsm:", fsm)
        fsm2, contflag2, ttt2, stry2 = vparser.fstack.pop()  # Key
        #print("pop2:", stry2, "fsm:", fsm2)

        # Push back summed item (reduce)
        #print("push key:", parsedata.st.KEYVAL, contflag, "name:", stry2, "val:", vparser.strx)
        vparser.fstack.push([parsedata.st.KEYVAL, contflag, stry2, vparser.strx])
        vparser.fsm = fsm2

# EOF
