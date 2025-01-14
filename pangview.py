#!/usr/bin/env python
 
import sys, os, re, time
import pygtk, gobject, gtk, pango

# Our modules

import panglib.parser as parser
import panglib.stack as stack
import panglib.lexer as lexer
import panglib.pangodisp as pangodisp
from   panglib.utils import *

# This parser digests formatted text similar to pango in GTK.
# Was created to quickly display formatted messages.
# See SYNTAX for details on text formats

'''
# We initialize parser variables in the context of the parser module.
#
# a.) Token definitions, b.) Lexer tokens, 
# c.) Parser functions,  d.) Parser state, e.) Parse table
#
# To create a custom parser, just add new tokens / states
#

# Quick into: The lexer creates a stack of tokens. The parser scans
# the tokens, and walks the state machine for matches. If match 
# is encountered, the parser calls the function in the state table, 
# and / or changes state. Reduce is called after the state has been 
# successfully digested. For more info see lex / yacc literature.
'''

# Connect parser token to lexer item. This way the definitions
# are synced without the need for double definition

def parse_lookup(strx):
    ret = None
    for aa in parser.tokdef:
        if strx == aa[1]:
            #print "found", aa
            ret = aa
            break
    if ret == None: 
        print "Token '" + strx + "' not found, please correct."
        sys.exit(1)
    return aa

# ------------------------------------------------------------------------
# Token definitions:
# Use textual context [x][1] for development, numeric [x][0] for production  
# The order of the definitions do not matter.
#
# To add a new syntactic element, search for an existing feature (like 'wrap')
# Add the new element into the a.) definition, b.) regex defintion, 
# c.) state definition, d.) state table, e.) action function.
#
# The script is self checking, will report on missing defintions. However,
# it can not (will not) report on syntactic anomalies.
#

parser.tokdef = \
         [parser.unique(), "span"   ],  \
         [parser.unique(), "espan"],    \
         [parser.unique(), "it"     ],  \
         [parser.unique(), "eit"    ],  \
         [parser.unique(), "bold"   ],  \
         [parser.unique(), "ebold"  ],  \
         [parser.unique(), "itbold" ],  \
         [parser.unique(), "eitbold"],  \
         [parser.unique(), "ul"   ],    \
         [parser.unique(), "eul"  ],    \
         [parser.unique(), "dul"   ],    \
         [parser.unique(), "edul"  ],    \
         [parser.unique(), "ncol"   ],   \
         [parser.unique(), "ncol2"   ],   \
         [parser.unique(), "encol"  ],   \
         [parser.unique(), "nbgcol"   ],  \
         [parser.unique(), "enbgcol"  ],  \
         [parser.unique(), "hid"   ],    \
         [parser.unique(), "ehid"  ],    \
         [parser.unique(), "indent"   ], \
         [parser.unique(), "eindent"  ],  \
         [parser.unique(), "margin"   ], \
         [parser.unique(), "emargin"  ],  \
         [parser.unique(), "lmargin"   ], \
         [parser.unique(), "elmargin"  ],  \
         [parser.unique(), "wrap"   ],    \
         [parser.unique(), "ewrap"  ],    \
         [parser.unique(), "link"   ],    \
         [parser.unique(), "elink"  ],    \
         [parser.unique(), "image"   ],    \
         [parser.unique(), "eimage"  ],    \
         [parser.unique(), "sub"   ],    \
         [parser.unique(), "esub"  ],    \
         [parser.unique(), "sup"   ],    \
         [parser.unique(), "esup"  ],    \
         [parser.unique(), "fill"   ],    \
         [parser.unique(), "efill"  ],    \
         [parser.unique(), "fixed"   ],    \
         [parser.unique(), "efixed"  ],    \
         [parser.unique(), "cent"   ],    \
         [parser.unique(), "ecent"  ],    \
         [parser.unique(), "right"   ],   \
         [parser.unique(), "eright"  ],   \
         [parser.unique(), "red"   ],     \
         [parser.unique(), "ered"  ],     \
         [parser.unique(), "bgred"   ],   \
         [parser.unique(), "ebgred"  ],   \
         [parser.unique(), "green"   ], \
         [parser.unique(), "egreen"  ], \
         [parser.unique(), "bggreen"   ], \
         [parser.unique(), "ebggreen"  ], \
         [parser.unique(), "blue"   ],  \
         [parser.unique(), "eblue"  ],  \
         [parser.unique(), "bgblue"   ],  \
         [parser.unique(), "ebgblue"  ],  \
         [parser.unique(), "large"   ],  \
         [parser.unique(), "elarge"  ],  \
         [parser.unique(), "xlarge"   ],  \
         [parser.unique(), "exlarge"  ],  \
         [parser.unique(), "xxlarge"   ],  \
         [parser.unique(), "exxlarge"  ],  \
         [parser.unique(), "small"   ],  \
         [parser.unique(), "esmall"  ],  \
         [parser.unique(), "xsmall"   ],  \
         [parser.unique(), "exsmall"  ],  \
         [parser.unique(), "strike"   ],\
         [parser.unique(), "estrike"  ],\
         [parser.unique(), "escquo" ],  \
         [parser.unique(), "dblbs"  ],  \
         [parser.unique(), "ident"  ],  \
         [parser.unique(), "str"    ],  \
         [parser.unique(), "str2"   ],  \
         [parser.unique(), "str3"   ],  \
         [parser.unique(), "str4"   ],  \
         [parser.unique(), "eq"     ],  \
         [parser.unique(), "comm"   ],  \
         [parser.unique(), "bsnl"   ],  \
         [parser.unique(), "lt"     ],  \
         [parser.unique(), "gt"     ],  \
         [parser.unique(), "sp"     ],  \
         [parser.unique(), "tab"    ],  \
         [parser.unique(), "nl"     ],  \
         [parser.unique(), "any"    ],  \
         
# ------------------------------------------------------------------------
# Lexer tokens. The lexer will search for the next token. 
# When editing, update tokdef and tokens together. 
#
# The order of the definitions matter. First token match is returned.
#
# Please note for simplicity we defined a stateless lexer. For example,
# the str is delimited by "" and str2 is delimited by '' to allow
# quotes in the str. For more complex string with quotes in it, escape 
# the quotes. (\48)
# 
# Elements:
#      --- enum tokdef -- token regex -- placeholder (compiled regex) --

parser.tokens =    \
            [parse_lookup("span"),      "<span "        ,  None  ],  \
            [parse_lookup("espan"),     "</span>"       ,  None, ],  \
            [parse_lookup("it"),        "<i>"           ,  None, ],  \
            [parse_lookup("eit"),       "</i>"          ,  None, ],  \
            [parse_lookup("hid"),       "<hid>"         ,  None, ],  \
            [parse_lookup("ehid"),      "</hid>"        ,  None, ],  \
            [parse_lookup("bold"),      "<b>"           ,  None, ],  \
            [parse_lookup("ebold"),     "</b>"          ,  None, ],  \
            [parse_lookup("itbold"),    "<ib>"          ,  None, ],  \
            [parse_lookup("eitbold"),   "</ib>"         ,  None, ],  \
            [parse_lookup("red"),       "<r>"           ,  None, ],  \
            [parse_lookup("ered"),      "</r>"          ,  None, ],  \
            [parse_lookup("bgred"),      "<rb>"           ,  None, ],  \
            [parse_lookup("ebgred"),      "</rb>"          ,  None, ],  \
            [parse_lookup("indent"),    "<in>"          ,  None, ],  \
            [parse_lookup("eindent"),   "</in>"         ,  None, ],  \
            [parse_lookup("margin"),    "<m>"          ,  None, ],  \
            [parse_lookup("emargin"),   "</m>"         ,  None, ],  \
            [parse_lookup("lmargin"),    "<lm>"          ,  None, ],  \
            [parse_lookup("elmargin"),   "</lm>"         ,  None, ],  \
            [parse_lookup("blue"),      "<e>"           ,  None, ],  \
            [parse_lookup("eblue"),     "</e>"          ,  None, ],  \
            [parse_lookup("bgblue"),    "<eb>"           ,  None, ],  \
            [parse_lookup("ebgblue"),   "</eb>"          ,  None, ],  \
            [parse_lookup("green"),     "<g>"           ,  None, ],  \
            [parse_lookup("egreen"),    "</g>"          ,  None, ],  \
            [parse_lookup("bggreen"),   "<gb>"           ,  None, ],  \
            [parse_lookup("ebggreen"),  "</gb>"          ,  None, ],  \
            [parse_lookup("large"),     "<l>"           ,  None, ],  \
            [parse_lookup("elarge"),    "</l>"          ,  None, ],  \
            [parse_lookup("xlarge"),    "<xl>"          ,  None, ],  \
            [parse_lookup("exlarge"),   "</xl>"         ,  None, ],  \
            [parse_lookup("xxlarge"),   "<xxl>"         ,  None, ],  \
            [parse_lookup("exxlarge"),  "</xxl>"        ,  None, ],  \
            [parse_lookup("small"),     "<sm>"          ,  None, ],  \
            [parse_lookup("esmall"),    "</sm>"         ,  None, ],  \
            [parse_lookup("xsmall"),    "<xs>"          ,  None, ],  \
            [parse_lookup("exsmall"),   "</xs>"          ,  None, ],  \
            [parse_lookup("cent"),      "<c>"           ,  None, ],  \
            [parse_lookup("ecent"),     "</c>"          ,  None, ],  \
            [parse_lookup("right"),     "<t>"           ,  None, ],  \
            [parse_lookup("eright"),    "</t>"          ,  None, ],  \
            [parse_lookup("strike"),    "<s>"           ,  None, ],  \
            [parse_lookup("estrike"),   "</s>"          ,  None, ],  \
            [parse_lookup("ul"),        "<u>"           ,  None, ],  \
            [parse_lookup("eul"),       "</u>"          ,  None, ],  \
            [parse_lookup("dul"),       "<uu>"          ,  None, ],  \
            [parse_lookup("edul"),      "</uu>"         ,  None, ],  \
            [parse_lookup("wrap"),      "<w>"           ,  None, ],  \
            [parse_lookup("ewrap"),     "</w>"          ,  None, ],  \
            [parse_lookup("link"),      "<link "           ,  None, ],  \
            [parse_lookup("elink"),     "</link>"          ,  None, ],  \
            [parse_lookup("image"),      "<image "           ,  None, ],  \
            [parse_lookup("eimage"),     "</image>"          ,  None, ],  \
            [parse_lookup("sub"),       "<sub>"          ,  None, ],  \
            [parse_lookup("esub"),      "</sub>"         ,  None, ],  \
            [parse_lookup("sup"),       "<sup>"          ,  None, ],  \
            [parse_lookup("esup"),      "</sup>"         ,  None, ],  \
            [parse_lookup("fill"),      "<j>"           ,  None, ],  \
            [parse_lookup("efill"),      "</j>"          ,  None, ],  \
            [parse_lookup("fixed"),      "<f>"          ,  None, ],  \
            [parse_lookup("efixed"),     "</f>"         ,  None, ],  \
            [parse_lookup("nbgcol"),    "<bg#[0-9a-fA-F]+ *>"  ,  None, ],  \
            [parse_lookup("enbgcol"),   "</bg#>"          ,  None, ],  \
            [parse_lookup("ncol2"),      "<fg#[0-9a-fA-F]+ *>"  ,  None, ],  \
            [parse_lookup("ncol"),      "<#[0-9a-fA-F]+ *>"  ,  None, ],  \
            [parse_lookup("encol"),     "</#>"          ,  None, ],  \
            [parse_lookup("escquo"),    r"\\\""         ,  None, ],  \
            [parse_lookup("dblbs"),     r"\\\\"         ,  None, ],  \
            [parse_lookup("ident"),     "[A-Za-z0-9_\-\./]+" ,  None, ],  \
            [parse_lookup("str4"),      "\#[0-9a-zA-Z]+",  None, ],  \
            [parse_lookup("str3"),      "(\\\\[0-7]+)+"    ,  None, ],  \
            [parse_lookup("str"),       "\".*?\""       ,  None, ],  \
            [parse_lookup("str2"),      "\'.*?\'"       ,  None, ],  \
            [parse_lookup("bsnl"),      "\\\\\n"        ,  None, ],  \
            [parse_lookup("comm"),     "\n##.*"          ,  None, ],  \
            [parse_lookup("eq"),        "="             ,  None, ],  \
            [parse_lookup("lt"),        "<"             ,  None, ],  \
            [parse_lookup("gt"),        ">"             ,  None, ],  \
            [parse_lookup("sp"),        " "             ,  None, ],  \
            [parse_lookup("tab"),       "\t"            ,  None, ],  \
            [parse_lookup("nl"),        "\n"            ,  None, ],  \
            [parse_lookup("any"),       "."             ,  None, ],  \

# Just to make sure no one is left out:

#if len(parser.tokens) != len(parser.tokdef):
#    print "Number of token definitions and tokens do not match."
#    sys.exit(1)    

# ------------------------------------------------------------------------
# Parser state machine states. The state machine runs through the whole 
# file stepping the rules. The functions may do anything, including reduce.
# Blank reduce may be executed with the state transition set to 'REDUCE'
#
# The number is the state, the string is for debugging / analyzing
# Once ready, operate on the numbers for speed.
# The E-states are not used, kept it for extensibility.

parser.IGNORE  = [parser.unique(),  "ignore"]
parser.INIT    = [parser.unique(),  "init"]
parser.SPAN    = [parser.unique(),  "span"]
parser.SPANTXT = [parser.unique(),  "spantxt"]
parser.IDENT   = [parser.unique(),  "ident"]
parser.KEY     = [parser.unique(),  "key"]
parser.VAL     = [parser.unique(),  "val"]
parser.EQ      = [parser.unique(),  "eq"]
parser.KEYVAL  = [parser.unique(),  "keyval"]
parser.ITALIC  = [parser.unique(),  "italic"]
parser.EITALIC = [parser.unique(),  "eitalic"]
parser.BOLD    = [parser.unique(),  "bold"]
parser.EBOLD   = [parser.unique(),  "ebold"]
parser.ITBOLD  = [parser.unique(),  "itbold"]
parser.EITBOLD = [parser.unique(),  "eitbold"]
parser.UL      = [parser.unique(),  "ul"]
parser.EUL     = [parser.unique(),  "eul"]
parser.DUL     = [parser.unique(),  "dul"]
parser.EDUL    = [parser.unique(),  "edul"]
parser.RED     = [parser.unique(),  "red"]
parser.ERED    = [parser.unique(),  "ered"]
parser.BGRED     = [parser.unique(), "bgred"]
parser.EBGRED    = [parser.unique(),  "ebgred"]
parser.GREEN   = [parser.unique(),  "green"]
parser.EGREEN  = [parser.unique(),  "egreen"]
parser.BGGREEN   = [parser.unique(),  "bggreen"]
parser.EBGGREEN  = [parser.unique(),  "ebggreen"]
parser.BLUE    = [parser.unique(),  "blue"]
parser.EBLUE   = [parser.unique(),  "eblue"]
parser.BGBLUE    = [parser.unique(),  "bgblue"]
parser.EBGBLUE   = [parser.unique(),  "ebgblue"]
parser.STRIKE  = [parser.unique(),  "strike"]
parser.ESTRIKE = [parser.unique(),  "estrike"]
parser.LARGE  = [parser.unique(),   "large"]
parser.ELARGE = [parser.unique(),   "elarge"]
parser.XLARGE  = [parser.unique(),  "xlarge"]
parser.EXLARGE = [parser.unique(),  "exlarge"]
parser.XXLARGE  = [parser.unique(), "xlarge"]
parser.EXXLARGE = [parser.unique(), "exlarge"]
parser.SMALL  = [parser.unique(),   "small"]
parser.ESMALL = [parser.unique(),   "esmall"]
parser.XSMALL  = [parser.unique(),   "xsmall"]
parser.EXSMALL = [parser.unique(),   "exsmall"]
parser.CENT  = [parser.unique(),    "cent"]
parser.ECENT = [parser.unique(),    "ecent"]
parser.RIGHT  = [parser.unique(),   "right"]
parser.ERIGHT = [parser.unique(),   "eright"]
parser.WRAP  = [parser.unique(),    "wrap"]
parser.EWRAP = [parser.unique(),    "ewrap"]
parser.LINK  = [parser.unique(),    "link"]
parser.ELINK = [parser.unique(),    "elink"]
parser.IMAGE  = [parser.unique(),    "image"]
parser.EIMAGE = [parser.unique(),    "eimage"]
parser.SUB  = [parser.unique(),     "sup"]
parser.ESUB = [parser.unique(),     "esup"]
parser.SUP  = [parser.unique(),     "sub"]
parser.ESUP = [parser.unique(),     "esub"]
parser.FILL  = [parser.unique(),    "fill"]
parser.EFILL = [parser.unique(),    "efill"]
parser.FIXED  = [parser.unique(),    "fixed"]
parser.EFIXED = [parser.unique(),    "efixed"]
parser.INDENT  = [parser.unique(),  "indent"]
parser.EINDENT = [parser.unique(),  "eindent"]
parser.MARGIN  = [parser.unique(),  "margin"]
parser.EMARGIN = [parser.unique(),  "emargin"]
parser.LMARGIN  = [parser.unique(),  "lmargin"]
parser.ELMARGIN = [parser.unique(),  "elmargin"]
parser.HID  = [parser.unique(),     "hid"]
parser.EIHID = [parser.unique(),    "ehid"]
parser.NCOL  = [parser.unique(),    "ncol"]
parser.ENCOL = [parser.unique(),    "encol"]
parser.NBGCOL  = [parser.unique(),  "nbgcol"]
parser.ENBNCOL = [parser.unique(),  "enbgcol"]

# ------------------------------------------------------------------------
# State groups for recursion:

# Color instructions: (not used)

STATECOL = [parser.RED, parser.GREEN, parser.BLUE]

# These are states that have recursive actions: 
# (like bold in italic or size in color etc ...) Note specifically, that
# the SPAN state is not in this list, as inside span definitions formatting
# does not make sence. This parser ignores such occurances.

STATEFMT = [parser.INIT,  parser.BOLD, parser.ITALIC, \
            parser.RED, parser.GREEN, parser.BLUE, \
            parser.BGRED, parser.BGGREEN, parser.BGBLUE, \
            parser.UL, parser.DUL, parser.STRIKE, parser.SMALL, \
            parser.NCOL, parser.NBGCOL, \
            parser.XSMALL, parser.LARGE, parser.XLARGE, parser.XXLARGE,\
            parser.SUB, parser.SUP, parser.LINK, \
            parser.CENT, parser.RIGHT, parser.WRAP, parser.FILL, parser.INDENT, \
            parser.SPANTXT, parser.FIXED, parser.MARGIN, parser.LMARGIN ]

# Some globals:

buf = None; xstack = None; verbose = False
pgdebug = False; show_lexer = False; full_screen = False
lstack = None;  fullpath = None; docroot = None
got_clock = 0; show_timing = False; 

# Accumulate output: (mostly for testing)
_cummulate = ""
def emit(strx):
    global _cummulate;
    _cummulate += " '" + strx + "' "

# Our display object
mainview = None

# ------------------------------------------------------------------------
# Parser functions that are called on parser events. Note the 'e' prefix
# for the 'end' function -> bold() -> ebold()  (end bold)

def Nbgcol(vparser, token, tentry):
    emit( "<nbgcol> " + vparser.strx[3:len(vparser.strx)-1])
    TextState.bgcolor = vparser.strx[3:len(vparser.strx)-1]
    
def eNbgcol(vparser, token, tentry):
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    TextState.bgcolor = ""
    emit( "<enbgcol> ")
    
def Ncol(vparser, token, tentry):
    emit( "<ncol> " + vparser.strx)
    TextState.color = vparser.strx[1:len(vparser.strx)-1]
    
def Ncol2(vparser, token, tentry):
    emit( "<ncol2> " + vparser.strx)
    TextState.color = vparser.strx[3:len(vparser.strx)-1]
    
def eNcol(vparser, token, tentry):
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    TextState.color = ""
    emit( "<encol> ")
    
def Hid(vparser, token, tentry):
    TextState.hidden = True
    emit( "<hid>")
    
def eHid(vparser, token, tentry):
    TextState.hidden = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<ehid>")

def Indent(vparser, token, tentry):
    TextState.indent += 1
    emit( "<indent>")
    
def eIndent(vparser, token, tentry):
    if TextState.indent > 0:
        TextState.indent -= 1
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<eindent>")

def Margin(vparser, token, tentry):
    TextState.margin += 1
    emit( "<margin>")
    
def eMargin(vparser, token, tentry):
    if TextState.margin > 0:
        TextState.margin -= 1
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<emargin>")
    
def Lmargin(vparser, token, tentry):
    TextState.lmargin += 1
    emit( "<margin>")
    
def eLmargin(vparser, token, tentry):
    if TextState.lmargin > 0:
        TextState.lmargin -= 1
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<emargin>")
    
def Fixed(vparser, token, tentry):
    TextState.fixed = True
    emit( "<fixed>")
    
def eFixed(vparser, token, tentry):
    TextState.fixed = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<efixed>")

def Fill(vparser, token, tentry):
    TextState.fill = True
    emit( "<fill>")
    
def eFill(vparser, token, tentry):
    TextState.fill = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<efill>")

def Sup(vparser, token, tentry):
    TextState.sup = True
    emit( "<sup>")
    
def eSup(vparser, token, tentry):
    TextState.sup = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<esup>")

def Sub(vparser, token, tentry):
    TextState.sub = True
    emit( "<sub>")
    
def eSub(vparser, token, tentry):
    TextState.sub = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<esub>")

def Wrap(vparser, token, tentry):
    TextState.wrap = True
    emit( "<wrap>")
    
def eWrap(vparser, token, tentry):
    TextState.wrap = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<ewrap>")

def Link(vparser, token, tentry):
    emit( "<link>")
    
def Link2(vparser, token, tentry):
    xstack = stack.Stack()
    # Walk optionals:
    while True:             
        vparser.popstate()
        if vparser.fsm == parser.KEYVAL:          
            #print " Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            
            xstack.push([vparser.ttt, "=", vparser.stry])
        if vparser.contflag == 0:            
            break

    while True:
        xkey = xstack.pop()     
        if not xkey:
            break
        kk, ee, vv = xkey;
        vv = vv.replace("\"",""); vv = vv.replace("\'","")

        #print "link key: '" + kk + "' val: '" + vv + "'"
        if kk == "file" or kk == "name":
            # Try docroot - current dir - home dir
            fname = docroot + "/" + vv
            if not isfile(fname):
                fname = vv
                if not isfile(fname):
                    fname = "~/" + vv                                                        
                    if not isfile(fname):
                        fname = vv                                                        
                    
            TextState.link = fname                        
        if kk == "color" or kk == "fg":
            #print "setting color in link"
            TextState.color = vv
        
    emit( "<link2>")
    
def eLink(vparser, token, tentry):
    TextState.link = ""
    TextState.color = ""
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<elink>")

def Image(vparser, token, tentry):
    emit( "<image>")

def Image2(vparser, token, tentry):
    xstack = stack.Stack()
    # Walk optionals:
    while True:             
        vparser.popstate()
        if vparser.fsm == parser.KEYVAL:          
            #print " Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            
            xstack.push([vparser.ttt, "=", vparser.stry])
        if vparser.contflag == 0:            
            break

    xtag = gtk.TextTag();  fname = ""; www = 0; hhh = 0

    while True:
        xkey = xstack.pop()     
        if not xkey:
            break
        kk, ee, vv = xkey;
        vv = vv.replace("\"",""); vv = vv.replace("\'","")

        #print "key: '" + kk + "' val: '" + vv + "'"

        if kk == "align":
            if vv == "left":
                xtag.set_property("justification", gtk.JUSTIFY_LEFT)
            elif vv == "center":
                xtag.set_property("justification", gtk.JUSTIFY_CENTER)
            elif vv == "right":
                xtag.set_property("justification", gtk.JUSTIFY_RIGHT)

        if kk == "width":
            www = int(vv)
            
        if kk == "height":
            hhh = int(vv)
            
        if kk == "name" or kk == "file":
            # Try docroot - curr dir - home/Pictures - home
            fname = docroot + "/" + vv
            if not isfile(fname):
                fname = vv
                if not isfile(fname):
                    fname = "~/Pictures" + vv
                    if not isfile(fname):
                        fname = "~/" + vv
        
    # Exec collected stuff
    mainview.add_text_xtag(" ", xtag)
    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file(fname)
        if www and hhh:
            #print "scaling to", www, hhh
            pixbuf2 = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, www, hhh)
            pixbuf.scale(pixbuf2, 0, 0, www, hhh, 
                0, 0, float(www)/pixbuf.get_width(), float(hhh)/pixbuf.get_height(), 
            gtk.gdk.INTERP_BILINEAR)
            mainview.add_pixbuf(pixbuf2)
        else:
            mainview.add_pixbuf(pixbuf)
        
    except gobject.GError, error:
        #print "Failed to load image file '" + vv + "'"
        mainview.add_broken()

    #vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<image2>")
    
def eImage(vparser, token, tentry):
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<eimage>")

def Center(vparser, token, tentry):
    TextState.center = True
    emit( "<center>")
    
def eCenter(vparser, token, tentry):
    TextState.center = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<ecenter>")

def Right(vparser, token, tentry):
    TextState.right = True
    emit( "<right>")
    
def eRight(vparser, token, tentry):
    TextState.right = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<eright>")

def Xsmall(vparser, token, tentry):
    TextState.xsmall = True
    emit( "<xsmall>")
    
def eXsmall(vparser, token, tentry):
    TextState.xsmall = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<exsmall>")

def Small(vparser, token, tentry):
    TextState.small = True
    emit( "<small>")
    
def eSmall(vparser, token, tentry):
    TextState.small = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<esmall>")

def Xxlarge(vparser, token, tentry):
    TextState.xxlarge = True
    emit( "<xxlarge>")
    
def eXxlarge(vparser, token, tentry):
    TextState.xxlarge = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<exxlarge>")

def Xlarge(vparser, token, tentry):
    TextState.xlarge = True
    emit( "<xlarge>")
    
def eXlarge(vparser, token, tentry):
    TextState.xlarge = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<exlarge>")

def Large(vparser, token, tentry):
    TextState.large = True
    emit( "<large>")
    
def eLarge(vparser, token, tentry):
    TextState.large = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<elarge>")

def Dunderline(vparser, token, tentry):
    TextState.dul = True
    emit( "<dunderline>")
    
def eDunderline(vparser, token, tentry):
    TextState.dul = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<edunderline>")
   
def Underline(vparser, token, tentry):
    TextState.ul = True
    emit( "<underline>")
    
def eUnderline(vparser, token, tentry):
    TextState.ul = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<eunderline>")
   
def ItBold(vparser, token, tentry):
    TextState.itbold = True
    emit( "<itbold>")
    
def eItBold(vparser, token, tentry):
    TextState.itbold = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<eitbold>")

def Green(vparser, token, tentry):
    TextState.green = True
    emit( "<green>")
    
def eGreen(vparser, token, tentry):
    TextState.green = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<egreen>")
    
def Blue(vparser, token, tentry):
    TextState.blue = True
    emit( "<blue>")
    
def eBlue(vparser, token, tentry):
    TextState.blue = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<eblue>")
    
def Strike(vparser, token, tentry):
    TextState.strike = True
    emit( "<strike>")
    
def eStrike(vparser, token, tentry):
    TextState.strike = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<estrike>")    
    
def Bgred(vparser, token, tentry):
    TextState.bgred = True
    emit( "<bgred>")
    
def eBgred(vparser, token, tentry):
    TextState.bgred = False
    #    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    vparser.popstate()
    emit( "<ebgred>")
    
def Bggreen(vparser, token, tentry):
    TextState.bggreen = True
    emit( "<bggreen>")
    
def eBggreen(vparser, token, tentry):
    TextState.bggreen = False
    #    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    vparser.popstate()
    emit( "<ebggreen>")

def Bgblue(vparser, token, tentry):
    TextState.bgblue = True
    emit( "<bgblue>")
    
def eBgblue(vparser, token, tentry):
    TextState.bgblue = False
    #    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    vparser.popstate()
    emit( "<ebgblue>")
    
def Red(vparser, token, tentry):
    TextState.red = True
    emit( "<red>")
    
def eRed(vparser, token, tentry):
    TextState.red = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<ered>")
    
def Bold(vparser, token, tentry):
    TextState.bold = True
    emit( "<bold>")
    
def eBold(vparser, token, tentry):
    TextState.bold = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit( "<ebold>")
    
def Italic(vparser, token, tentry):
    TextState.italic = True
    emit("<italic>")
    
def eItalic(vparser, token, tentry):
    TextState.italic = False
    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit ( "<eitalic>")
    
def Ident(vparser, token, tentry):
    #print "called ident"
    pass

def Span(vparser, token, tentry):
    emit("<span ");
    pass

def Span2(vparser, token, tentry):
    xstack = stack.Stack()
    # Walk optionals:
    while True:             
        fsm, contflag, ttt, stry = vparser.fstack.pop()
        if fsm == parser.KEYVAL:          
            #print " Reducing keyval", fsm, "'"+ttt+"'", "\"" + stry + "\""            
            xstack.push([ttt, "=", stry])
        if contflag == 0:
            break
    
    # Set font parameters:
    while True:
        xkey = xstack.pop()     
        if not xkey:
            break
        kk, ee, vv = xkey;
        vv = vv.replace("\"",""); vv = vv.replace("\'","")

        #print "key ",kk, vv
        if kk == "background" or kk == "bg" or kk == "bgcolor":
            TextState.bgcolor = vv
        if kk == "foreground" or kk == "fg" or kk == "color":
            TextState.color = vv
        elif kk == "size":
            TextState.size = int(vv)
        elif kk == "font":
            TextState.font = vv
        elif kk == "bold":
            if isTrue(vv):
                TextState.bold = True
            else:
                TextState.bold = False
            
        elif kk == "italic":
            if isTrue(vv):
                TextState.italic = True
            else:
                TextState.italic = False

        elif kk == "under" or kk == "underline":
            if isTrue(vv):
                TextState.ul = True
            else:
                TextState.ul = False

        elif kk == "align" or kk == "alignment":
            vvv = vv.lower()
            if vvv == "left":
                TextState.left = True
            elif vvv == "right":
                TextState.right = True
            elif vvv == "center":
                #print " centering"
                TextState.center = True

    emit(" spantxt >");


def eSpan(vparser, token, tentry):
    #print "called span", parser.strx
    TextState.color = ""
    TextState.bgcolor = ""
    TextState.size = 0
    TextState.font = ""
    TextState.left = False
    TextState.center = False
    TextState.right = False
    TextState.ul = False

    vparser.fsm, vparser.contflag, ttt, vparser.stry = vparser.fstack.pop()
    emit ("<espan>" )
        
def Keyval(vparser, token, tentry):

    #print "called keyval", vparser.fsm, token, vparser.strx
    
    # Pop two items, create keyval
    fsm, contflag, ttt, stry = vparser.fstack.pop()      # EQ
    fsm2, contflag2, ttt2, stry2 = vparser.fstack.pop()  # Key

    # Push back summed item (reduce)
    vparser.fstack.push([parser.KEYVAL, 1, stry2, vparser.strx])
    vparser.fsm = fsm2

# ------------------------------------------------------------------------
# Text display state:
   
class TextState():

    bold = False;  itbold = False;  italic = False
    ul = False; dul = False
    red = False;  blue = False; green = False
    bgred = False;  bgblue = False; bggreen = False
    strike = False; large = False; small = False; xsmall = False
    xlarge = False; xxlarge = False; center = False
    wrap = False; hidden = False; color =  ""; right = False
    indent = 0; margin = 0; size = 0; font = ""; fixed = False; bgcolor = ""
    sub = False; sup = False; image = ""; link = ""; lmargin = 0
    fill = False
    
def clearTextState():
    TextState.bold = False;  TextState.itbold = False;  TextState.italic = False
    TextState.ul = False; TextState.dul = False
    TextState.red = False;  TextState.blue = False; TextState.green = False
    TextState.bgred = False;  TextState.bgblue = False; TextState.bggreen = False
    TextState.strike = False; TextState.large = False; TextState.small = False; 
    TextState.xsmall = False
    TextState.xlarge = False; TextState.xxlarge = False; TextState.center = False
    TextState.wrap = False; TextState.hidden = False; TextState.color =  ""; 
    TextState.right = False
    TextState.indent = 0; TextState.margin = 0; TextState.size = 0; 
    TextState.font = ""; TextState.fixed = False; TextState.bgcolor = ""
    TextState.sub = False; TextState.sup = False; TextState.image = ""; 
    TextState.link = ""; TextState.lmargin = 0;
    TextState.fill = False
        
old_stresc = ""

def Text(vparser, token, tentry):
    global mainview
    emit(vparser.strx)        

    xtag = gtk.TextTag()
    xtag2 = gtk.TextTag()

    if TextState.font != "":
        xtag.set_property("font", TextState.font)

    # Decorate textag according to machine state
    if TextState.fixed:    xtag.set_property("family", "Monospace")
    if TextState.bold:     xtag.set_property("weight", pango.WEIGHT_BOLD)
    if TextState.italic:   xtag.set_property("style", pango.STYLE_ITALIC)
    #if TextState.itbold:   xtag.set_property("foreground", "red")
    if TextState.large:    xtag.set_property("scale", pango.SCALE_LARGE) 
    if TextState.xlarge:   xtag.set_property("scale", pango.SCALE_X_LARGE) 
    if TextState.xxlarge:  xtag.set_property("scale", pango.SCALE_XX_LARGE) 
    if TextState.small:    xtag.set_property("scale", pango.SCALE_SMALL) 
    if TextState.xsmall:    xtag.set_property("scale", pango.SCALE_X_SMALL) 
    if TextState.ul:       xtag.set_property("underline", pango.UNDERLINE_SINGLE)
    if TextState.dul:      xtag.set_property("underline", pango.UNDERLINE_DOUBLE)

    if TextState.red:      xtag.set_property("foreground", "red")
    if TextState.green:    xtag.set_property("foreground", "green")
    if TextState.blue:     xtag.set_property("foreground", "blue")
    
    if TextState.bgred:    xtag.set_property("background", "red")
    if TextState.bggreen:  xtag.set_property("background", "green")
    if TextState.bgblue:   xtag.set_property("background", "blue")
    
    if TextState.strike:   xtag.set_property("strikethrough", True)
    if TextState.wrap:     xtag.set_property("wrap_mode", gtk.WRAP_WORD)

    if TextState.center:   xtag.set_property("justification", gtk.JUSTIFY_CENTER)
    if TextState.right:    xtag.set_property("justification", gtk.JUSTIFY_RIGHT)
    if TextState.fill:     xtag.set_property("justification", gtk.JUSTIFY_FILL)
        
    #print "bgcolor:",  TextState.bgcolor 
    if TextState.bgcolor != "":
        xtag.set_property("background", TextState.bgcolor)

    #print "color:",  TextState.color 
    if TextState.color != "":
        xtag.set_property("foreground", TextState.color)

    if TextState.size != 0:
        xtag.set_property("size", TextState.size * pango.SCALE)

    if TextState.link != "":        
        xtag.set_data("link", TextState.link)
        if TextState.color == "":
            xtag.set_property("foreground", "blue")

    # Sub / Super sets the size again ...
    if TextState.sub:       
        rr = -4; ss = 8
        if TextState.size != 0:
            rr = - TextState.size / 6
            ss  = TextState.size / 2
        xtag.set_property("rise", rr * pango.SCALE)        
        xtag.set_property("size", ss * pango.SCALE)

    if TextState.sup:       
        rr = 6; ss = 8
        if TextState.size != 0:
            rr =  TextState.size / 2
            ss  = TextState.size /2
        xtag.set_property("rise", rr * pango.SCALE)        
        xtag.set_property("size", ss * pango.SCALE)

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

    stresc = unescape(vparser.strx)    

    # if wrapping, output one space only
    global old_stresc
    if TextState.wrap:
        if stresc == " ": 
            if old_stresc == " ":                        
                return
            old_stresc = " "
        else:
            old_stresc = ""


    if not TextState.hidden:
        mainview.add_text_xtag(stresc, xtag)
        pass
    else:
        print stresc

def pl(strx):
    ret = None
    for aa in parser.tokdef:
        if strx == aa[1]:
            ret = aa
            break
    if ret == None: 
        print "Token '" + strx + "' not found, please correct."
        sys.exit(1)
    return aa[0]

# ------------------------------------------------------------------------
# Class of tokens for simple alternates:

# This token class is for generic text.
TXTCLASS = pl("ident"), pl("eq"), pl("lt"), pl("str"), pl("str2"), \
             pl("str3"), pl("gt"), pl("nl"), pl("sp"), \
                pl("tab"), pl("any"),
    
# ------------------------------------------------------------------------
# Parse table.
#
# Specify state machine state, token to see for action or class to see for
# action, function to execute when match encountered, the new parser 
# state when match encountered, continuation flag for reduce. (will 
# reduce until cont flag == 0) See reduce example for key->val.
#
# Alternatives can be specified with multiple lines for the same state.
# New parser state field overrides state set by function. (set to IGNORE)
#
# Parser ignores unmatched entries. 
#    (Bad for languages, good for error free parsing like text parsing)
#
# Parser starts in INIT. Parser skips IGNORE. (in those cases, usually 
# the function sets the new state)
#
# Use textual context for development, numeric for production
#
# This table specifies a grammar for text processing, similar to Pango
#
#     -- State -- StateClass -- Token -- TokenClass -- Function -- newState -- cont. flag
 
parser.parsetable = \
         [ None,    STATEFMT,     pl("span"),     None,   Span,       parser.SPAN, 0 ],       \
         [ None,    STATEFMT,     pl("bold"),     None,   Bold,       parser.BOLD, 0 ],       \
         [ None,    STATEFMT,     pl("it"),       None,   Italic,     parser.ITALIC, 0 ],     \
         [ None,    STATEFMT,     pl("itbold"),   None,   ItBold,     parser.ITBOLD, 0 ],     \
         [ None,    STATEFMT,     pl("ul"),       None,   Underline,  parser.UL, 0 ],         \
         [ None,    STATEFMT,     pl("dul"),      None,   Dunderline, parser.DUL, 0 ],        \
         [ None,    STATEFMT,     pl("red"),      None,   Red,        parser.RED, 0 ],        \
         [ None,    STATEFMT,     pl("bgred"),    None,   Bgred,      parser.BGRED, 0 ],      \
         [ None,    STATEFMT,     pl("blue"),     None,   Blue,       parser.BLUE, 0 ],       \
         [ None,    STATEFMT,     pl("bgblue"),   None,   Bgblue,     parser.BGBLUE, 0 ],     \
         [ None,    STATEFMT,     pl("green"),    None,   Green,      parser.GREEN, 0 ],      \
         [ None,    STATEFMT,     pl("bggreen"),  None,   Bggreen,    parser.BGGREEN, 0 ],      \
         [ None,    STATEFMT,     pl("strike"),   None,   Strike,     parser.STRIKE, 0 ],     \
         [ None,    STATEFMT,     pl("large"),    None,   Large,      parser.LARGE, 0 ],      \
         [ None,    STATEFMT,     pl("xlarge"),   None,   Xlarge,     parser.XLARGE, 0 ],     \
         [ None,    STATEFMT,     pl("xxlarge"),  None,   Xxlarge,    parser.XXLARGE, 0 ],    \
         [ None,    STATEFMT,     pl("small"),    None,   Small,      parser.SMALL, 0 ],      \
         [ None,    STATEFMT,     pl("xsmall"),    None,  Xsmall,     parser.XSMALL, 0 ],     \
         [ None,    STATEFMT,     pl("cent"),     None,   Center,     parser.CENT, 0 ],       \
         [ None,    STATEFMT,     pl("right"),    None,   Right,      parser.RIGHT, 0 ],      \
         [ None,    STATEFMT,     pl("wrap"),     None,   Wrap,       parser.WRAP, 0 ],       \
         [ None,    STATEFMT,     pl("link"),     None,   Link,       parser.LINK, 0 ],       \
         [ None,    STATEFMT,     pl("image"),     None,  Image,      parser.IMAGE, 0 ],       \
         [ None,    STATEFMT,     pl("sub"),     None,    Sub,        parser.SUB, 0 ],        \
         [ None,    STATEFMT,     pl("sup"),     None,    Sup,        parser.SUP, 0 ],        \
         [ None,    STATEFMT,     pl("fill"),     None,   Fill,       parser.FILL, 0 ],       \
         [ None,    STATEFMT,     pl("fixed"),    None,   Fixed,      parser.FIXED, 0 ],       \
         [ None,    STATEFMT,     pl("indent"),   None,   Indent,     parser.INDENT, 0 ],     \
         [ None,    STATEFMT,     pl("margin"),   None,   Margin,     parser.MARGIN, 0 ],     \
         [ None,    STATEFMT,     pl("lmargin"),   None,  Lmargin,    parser.LMARGIN, 0 ],     \
         [ None,    STATEFMT,     pl("hid"),      None,   Hid,        parser.HID, 0 ],        \
         [ None,    STATEFMT,     pl("ncol"),     None,   Ncol,       parser.NCOL, 0 ],       \
         [ None,    STATEFMT,     pl("ncol2"),     None,  Ncol2,       parser.NCOL, 0 ],       \
         [ None,    STATEFMT,     pl("nbgcol"),   None,   Nbgcol,     parser.NBGCOL, 0 ],       \
                                                                                          \
         [ parser.INIT,   None,   None,       TXTCLASS, Text,     parser.IGNORE, 0 ],     \
                                                                                          \
         [ parser.SPAN,   None,   pl("ident"),    None,     None,     parser.KEY, 1 ],        \
         [ parser.KEYVAL, None,   pl("ident"),    None,     Keyval,   parser.KEY, 1 ],        \
         [ parser.KEY,    None,   pl("eq"),       None,     None,     parser.VAL, 1 ],        \
         [ parser.VAL,    None,   pl("ident"),    None,     Keyval,   parser.IGNORE, 0 ],     \
         [ parser.VAL,    None,   pl("str"),      None,     Keyval,   parser.IGNORE, 0 ],     \
         [ parser.VAL,    None,   pl("str2"),     None,     Keyval,   parser.IGNORE, 0 ],     \
         [ parser.VAL,    None,   pl("str4"),     None,     Keyval,   parser.IGNORE, 0 ],     \
         [ parser.SPAN,   None,   pl("gt"),       None,     Span2,    parser.SPANTXT, 0 ],    \
         [ parser.SPAN,   None,   pl("sp"),       None,     None,     parser.IGNORE, 0 ],     \
                                                                                          \
         [ parser.IMAGE,   None,   pl("ident"),    None,     None,     parser.KEY, 1 ],       \
         [ parser.IMAGE,   None,   pl("gt"),       None,     Image2,   parser.IGNORE, 0 ],    \
         [ parser.IMAGE,   None,   pl("sp"),       None,     None,     parser.IGNORE, 0 ],    \
                                                                                          \
         [ parser.LINK,   None,   pl("ident"),    None,     None,     parser.KEY, 1 ],        \
         [ parser.LINK,   None,   pl("gt"),       None,     Link2,    parser.SPANTXT, 0 ],    \
         [ parser.LINK,   None,   pl("sp"),       None,     None,     parser.IGNORE, 0 ],     \
                                                                                          \
         [ parser.SPANTXT, None,  pl("espan"),    None,     eSpan,      parser.INIT, 0 ],     \
         [ parser.SPANTXT, None,  pl("elink"),    None,     eLink,      parser.IGNORE, 0 ],            \
                                                                                          \
         [ parser.SPANTXT,  None,  pl("bold"),     None,        Bold,   parser.BOLD, 0 ],     \
         [ parser.SPANTXT,  None,  pl("it"),       None,        Italic, parser.ITALIC, 0 ],         \
         [ parser.SPANTXT,  None,  None,       TXTCLASS,    Text,   parser.IGNORE, 0 ],         \
                                                                                                \
         [ parser.ITALIC,   None,  None,       TXTCLASS,    Text,       parser.IGNORE, 0 ],     \
         [ parser.ITALIC,   None,  pl("eit"),      None,        eItalic,    parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.BOLD,     None,  None,       TXTCLASS,    Text,       parser.IGNORE, 0 ],     \
         [ parser.BOLD,     None,  pl("ebold"),    None,        eBold,      parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.ITBOLD,   None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.ITBOLD,   None,   pl("eitbold"),  None,       eItBold,    parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.UL,       None,   None,       TXTCLASS,   Text,         parser.IGNORE, 0 ],   \
         [ parser.UL,       None,  pl("eul"),       None,       eUnderline,   parser.IGNORE, 0 ],   \
                                                                                                \
         [ parser.DUL,       None,   None,       TXTCLASS,   Text,         parser.IGNORE, 0 ],   \
         [ parser.DUL,       None,  pl("edul"),       None,       eDunderline,   parser.IGNORE, 0 ],   \
                                                                                                \
         [ parser.RED,      None,   None,       TXTCLASS,   Text,        parser.IGNORE, 0 ],    \
         [ parser.RED,      None,   pl("ered"),     None,       eRed,        parser.IGNORE, 0 ],    \
                                                                                                \
         [ parser.BGRED,    None,   None,       TXTCLASS,   Text,        parser.IGNORE, 0 ],    \
         [ parser.BGRED,    None,   pl("ebgred"),     None,     eBgred,      parser.IGNORE, 0 ],    \
                                                                                                \
         [ parser.BLUE,     None,    None,       TXTCLASS,  Text,       parser.IGNORE, 0 ],     \
         [ parser.BLUE,     None,   pl("eblue"),     None,      eBlue,       parser.IGNORE, 0 ],    \
                                                                                                \
         [ parser.BGBLUE,     None,    None,       TXTCLASS,  Text,       parser.IGNORE, 0 ],     \
         [ parser.BGBLUE,     None,  pl("ebgblue"),     None,      eBgblue,       parser.IGNORE, 0 ],  \
                                                                                                \
         [ parser.GREEN,    None,    None,       TXTCLASS,  Text,      parser.IGNORE, 0 ],      \
         [ parser.GREEN,    None,   pl("egreen"),     None,     eGreen,    parser.IGNORE, 0 ],      \
                                                                                                \
         [ parser.BGGREEN,    None,    None,       TXTCLASS,  Text,      parser.IGNORE, 0 ],      \
         [ parser.BGGREEN,    None,   pl("ebggreen"),     None,    eBggreen,    parser.IGNORE, 0 ],  \
                                                                                                \
         [ parser.STRIKE,   None,   None,       TXTCLASS,   Text,      parser.IGNORE, 0 ],      \
         [ parser.STRIKE,   None,   pl("estrike"),  None,       eStrike,   parser.IGNORE, 0 ],      \
                                                                                                \
         [ parser.LARGE,    None,   None,       TXTCLASS,   Text,      parser.IGNORE, 0 ],      \
         [ parser.LARGE,    None,   pl("elarge"),    None,      eLarge,    parser.IGNORE, 0 ],      \
                                                                                                \
         [ parser.XLARGE,    None,   None,       TXTCLASS,  Text,      parser.IGNORE, 0 ],      \
         [ parser.XLARGE,    None,   pl("exlarge"),    None,    eXlarge,    parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.XXLARGE,    None,   None,       TXTCLASS, Text,      parser.IGNORE, 0 ],      \
         [ parser.XXLARGE,    None,   pl("exxlarge"),    None,  eXxlarge,    parser.IGNORE, 0 ],    \
                                                                                                \
         [ parser.SMALL,     None,   None,       TXTCLASS,  Text,      parser.IGNORE, 0 ],      \
         [ parser.SMALL,     None,  pl("esmall"),    None,      eSmall,    parser.IGNORE, 0 ],      \
                                                                                                \
         [ parser.XSMALL,     None,   None,       TXTCLASS,  Text,      parser.IGNORE, 0 ],      \
         [ parser.XSMALL,     None,  pl("exsmall"),    None,     eXsmall,    parser.IGNORE, 0 ],      \
                                                                                                \
         [ parser.CENT,     None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.CENT,     None,  pl("ecent"),    None,        eCenter,     parser.IGNORE, 0 ],    \
                                                                                                \
         [ parser.RIGHT,     None,   None,      TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.RIGHT,     None,  pl("eright"),    None,      eRight,     parser.IGNORE, 0 ],    \
                                                                                                \
         [ parser.WRAP,     None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.WRAP,     None,  pl("ewrap"),    None,        eWrap,      parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.SUB,     None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.SUB,     None,  pl("esub"),      None,        eSub,      parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.SUP,     None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.SUP,     None,  pl("esup"),      None,        eSup,      parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.FILL,     None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.FILL,     None,  pl("efill"),    None,        eFill,      parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.FIXED,     None,   None,       TXTCLASS,   Text,       parser.IGNORE, 0 ],     \
         [ parser.FIXED,     None,  pl("efixed"),    None,      eFixed,      parser.IGNORE, 0 ],     \
                                                                                                \
         [ parser.INDENT,     None,   None,       TXTCLASS, Text,       parser.IGNORE, 0 ],     \
         [ parser.INDENT,     None,  pl("eindent"),    None,    eIndent,  parser.IGNORE, 0 ],       \
                                                                                                \
         [ parser.MARGIN,     None,   None,       TXTCLASS, Text,       parser.IGNORE, 0 ],     \
         [ parser.MARGIN,     None,  pl("emargin"),    None,    eMargin,  parser.IGNORE, 0 ],       \
                                                                                                \
         [ parser.LMARGIN,     None,   None,       TXTCLASS, Text,       parser.IGNORE, 0 ],     \
         [ parser.LMARGIN,     None,  pl("elmargin"),    None,   eLmargin,  parser.IGNORE, 0 ],       \
                                                                                                \
         [ parser.HID,     None,   None,       TXTCLASS,    None,     parser.IGNORE, 0 ],       \
         [ parser.HID,     None,  pl("ehid"),    None,          eHid,     parser.IGNORE, 0 ],       \
                                                                                                \
         [ parser.NCOL,     None,   None,     TXTCLASS,     Text,      parser.IGNORE, 0 ],      \
         [ parser.NCOL,     None,  pl("encol"),    None,        eNcol,    parser.IGNORE, 0 ],       \
                                                                                                \
         [ parser.NBGCOL,     None,   None,     TXTCLASS,     Text,      parser.IGNORE, 0 ],    \
         [ parser.NBGCOL,     None,  pl("enbgcol"),    None,      eNbgcol,    parser.IGNORE, 0 ],   \

'''         
# Check parse table: (obsolete: now it is self checking)
for aa in parser.parsetable:
    if aa[2]:
        found = 0
        for bb in parser.tokdef:
            if aa[2] == bb[1]:
                found = True
        if not found :
            print "Parse table contains unkown definition '" + aa[2] + "'"
            sys.exit(1)
'''

def main():  
    gtk.main()
    return 0

# ------------------------------------------------------------------------

def bslink():

    if lstack.stacklen() == 1:
        return
    
    lstack.pop()
    strx = lstack.last()
    
    #print "backspace linking to:", strx
    
    if strx == None or strx == "":
        return

    mainview.showcur(True)
    showfile(strx)

def link(strx):

    if strx == None or strx == "":
        return

    if not isfile(strx):
        mainview.showcur(False)
        message_dialog("Missing or broken link",
            "Cannot find file '%s'" % strx );        
        return
    #print "linking to:", strx
    showfile(strx)

# ------------------------------------------------------------------------

def     message_dialog(title, strx):

    dialog = gtk.MessageDialog(mainview,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO, gtk.BUTTONS_OK, strx)
    dialog.set_title(title);
    dialog.run()
    dialog.destroy()

# ------------------------------------------------------------------------
  
def showfile(strx):

    global buf, xstack, mainview

    got_clock =  time.clock()
  
    if verbose:
        print "Showing file:", strx

    try:
        f = open(strx)
    except:
        strerr = "File:  '" + strx + "'  must be an existing and readble file. "
        print strerr
        mainview.add_text(strerr)
        return
    
    try:
        buf = f.read();
    except:
        strerr2 =  "Cannot read file '" + strx + "'"
        print strerr2
        mainview.add_text(strerr2)        
        return

    f.close()
    if show_timing:
        print  "loader:", time.clock() - got_clock
  
    if pgdebug > 5: print buf
    
    lstack.push(strx)

    mainview.clear()
    clearTextState()

    xstack = stack.Stack()       
    lexer.Lexer(buf, xstack, parser.tokens)
    
    if show_timing:
        print  "lexer:", time.clock() - got_clock
    
    if show_lexer: xstack.dump() # To show what the lexer did
  
    parser.Parse(buf, xstack)
    mainview.showcur(False)
        

    if show_timing:
        print  "parser:", time.clock() - got_clock
  
    # Output results 
    if pgdebug > 6: print _cummulate
    

def help():
    print "Usage: " + sys.argv[0] + " [options] filename"
    print "Options are:"
    print "            -d level  - Debug level (1-10)"
    print "            -v        - Verbose"
    print "            -f        - Full screen"
    print "            -x        - show lexer output"
    print "            -h        - Help"
    print
  
# ------------------------------------------------------------------------

if __name__ == "__main__":

    import getopt
   
    
    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:vhxft")
    except getopt.GetoptError, err:
        print "Invalid option(s) on command line:", err
        sys.exit(1)

    #print "opts", opts, "args", args
    
    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
            except:
                pgdebug = 0

        if aa[0] == "-v": verbose = True            
        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-x": show_lexer = True
        if aa[0] == "-f": full_screen = True
        if aa[0] == "-t": show_timing = True

    try:
        strx = args[0]
    except:
        help(); exit(1)

    #strx = "pango/formats.pango"

    lstack = stack.Stack()
    fullpath = os.path.abspath(strx);
    docroot = os.path.dirname(fullpath)    
  
    mainview = pangodisp.PangoView(full=full_screen)
    mainview.callback = link
    mainview.bscallback = bslink   
    
    #import pstats, profile
    #profile.run("showfile(strx)", "aa")

    #import pstats, cProfile
    #cProfile.run("showfile(strx)", "aa")
    #ss = pstats.Stats("aa"); ss.strip_dirs()
    #ss.sort_stats('cumulative'); ss.print_stats()'''

    showfile(strx)

    main()
 
#EOF
