#!/usr/bin/env python

import  panglib.pangfunc as pangfunc
import  panglib.pangdisp as pangdisp

# This parser digests formatted text similar to pango in Gtk.
# Was created to quickly display formatted messages.
# See SYNTAX for details on text formats

cb = pangfunc.CallBack(pangdisp.ts, pangdisp.add_text,
                    pangdisp.add_image, pangdisp.emit_one)
tokdef = []

_gl_cnt = 0
def unique():             # create a unique temporary number
    global _gl_cnt; _gl_cnt += 1
    return _gl_cnt

# Connect parser token to lexer item. This way the definitions are synced
# without the need for double definition
# Look up, create if not found

def lookup(strx):
    ret = None
    for aa in tokdef:
        if strx == aa[1]:
            #print "found", aa
            ret = aa
            break
    if ret == None:
        #print ("Token '" + strx + "' not found, adding ... ", end = " " )
        tokdef.append((unique(), strx))
        for aa in tokdef:
            if strx == aa[1]:
                #print(aa)
                ret = aa
                break
        if ret == None:
            print ("Token '" + strx + "' not found, please correct it.")
    return aa

def rlookup(idn):
    ret =  "none"
    for aa in tokdef:
        #print("idx =", idn, "aa =", aa)
        if idn == aa[0]:
            ret = aa[1]
            break
    return ret

def dumpids():
    cnt = 0
    for aa in tokdef:
        strx = str(aa[0]) + " = " + aa[1]
        xlen = 18 - len(strx)
        print(strx, end = " " * xlen)
        cnt += 1
        if cnt % 4 == 0:
            print()
    print()

# The short verion, returning the num only
def pl(strx):
    aa = lookup(strx)
    return aa[0]

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

tokens =  (
    (lookup("comm"),      "##.*"                ),
    (lookup("comm2"),     ".*##.*"              ),
    (lookup("espan"),     "</span>"             ),
    (lookup("span"),      "<span "              ),
    (lookup("fixed"),     "<fixed>"             ),
    (lookup("efixed"),    "</fixed>"            ),
    (lookup("xsp"),       "<sp>"                ),
    (lookup("inc"),       "<inc "               ),
    (lookup("einc"),      "</inc>"              ),
    (lookup("it"),        "<i>"                 ),
    (lookup("eit"),       "</i>"                ),
    (lookup("hid"),       "<hid>"               ),
    (lookup("ehid"),      "</hid>"              ),
    (lookup("bold"),      "<b>"                 ),
    (lookup("tab"),       "<tab>"               ),
    (lookup("ebold"),     "</b>"                ),
    (lookup("itbold"),    "<ib>"                ),
    (lookup("eitbold"),   "</ib>"               ),
    (lookup("red"),       "<r>"                 ),
    (lookup("ered"),      "</r>"                ),
    (lookup("bgred"),     "<rb>"                ),
    (lookup("ebgred"),    "</rb>"               ),
    (lookup("indent"),    "<in>"                ),
    (lookup("eindent"),   "</in>"               ),
    (lookup("margin"),    "<m>"                 ),
    (lookup("emargin"),   "</m>"                ),
    (lookup("lmargin"),    "<lm>"               ),
    (lookup("elmargin"),   "</lm>"              ),
    (lookup("blue"),      "<e>"                 ),
    (lookup("eblue"),     "</e>"                ),
    (lookup("bgblue"),    "<eb>"                ),
    (lookup("ebgblue"),   "</eb>"               ),
    (lookup("green"),     "<g>"                 ),
    (lookup("egreen"),    "</g>"                ),
    (lookup("bggreen"),   "<gb>"                ),
    (lookup("ebggreen"),  "</gb>"               ),
    (lookup("large"),     "<l>"                 ),
    (lookup("elarge"),    "</l>"                ),
    (lookup("xlarge"),    "<xl>"                ),
    (lookup("exlarge"),   "</xl>"               ),
    (lookup("xxlarge"),   "<xxl>"               ),
    (lookup("exxlarge"),  "</xxl>"              ),
    (lookup("small"),     "<sm>"                ),
    (lookup("esmall"),    "</sm>"               ),
    (lookup("xsmall"),    "<xs>"                ),
    (lookup("exsmall"),   "</xs>"               ),
    (lookup("cent"),      "<c>"                 ),
    (lookup("ecent"),     "</c>"                ),
    (lookup("right"),     "<t>"                 ),
    (lookup("eright"),    "</t>"                ),
    (lookup("strike"),    "<s>"                 ),
    (lookup("estrike"),   "</s>"                ),
    (lookup("ul"),        "<u>"                 ),
    (lookup("eul"),       "</u>"                ),
    (lookup("dul"),       "<uu>"                ),
    (lookup("edul"),      "</uu>"               ),
    (lookup("wrap"),      "<w>"                 ),
    (lookup("ewrap"),     "</w>"                ),
    (lookup("link"),      "<link "              ),
    (lookup("elink"),     "</link>"             ),
    (lookup("image"),      "<image "            ),
    (lookup("eimage"),     "</image>"           ),
    (lookup("sub"),       "<sub>"               ),
    (lookup("esub"),      "</sub>"              ),
    (lookup("sup"),       "<sup>"               ),
    (lookup("esup"),      "</sup>"              ),
    (lookup("fill"),      "<j>"                 ),
    (lookup("efill"),      "</j>"               ),
    (lookup("fixed"),      "<f>"                ),
    (lookup("efixed"),     "</f>"               ),
    (lookup("nbgcol"),    "<bg#[0-9a-fA-F]+ *>" ),
    (lookup("enbgcol"),   "</bg#>"              ),
    (lookup("ncol2"),     "<fg#[0-9a-fA-F]+ *>" ),
    (lookup("ncol"),      "<#[0-9a-fA-F]+ *>"   ),
    (lookup("encol"),     "</#>"                ),
    (lookup("escquo"),    r"\\\""               ),
    (lookup("dblbs"),     r"\\\\"               ),
    (lookup("ident"),     "[A-Za-z0-9_\-\./]+"  ),
    (lookup("str4"),      "\#[0-9a-zA-Z]+"      ),
    (lookup("str3"),      "(\\\\[0-7]+)+"       ),
    (lookup("str"),       "\".*?\""             ),
    (lookup("str2"),      "\'.*?\'"             ),
    (lookup("eq"),        "="                   ),
    (lookup("lt"),        "<"                   ),
    (lookup("gt"),        ">"                   ),
    (lookup("sp"),        " "                   ),
    (lookup("colu"),      "<colu>"              ),
    (lookup("bsnl"),      "\\\\\n"              ),
    (lookup("nl"),        r"\n"                 ),
    (lookup("any"),       "."                   ),
    )

def dumptokens():
    cnt = 0
    for cnt, aa in enumerate(tokens):
        strx = str(aa[0]) + " = " + aa[1]
        xlen = 40 - len(strx)
        print(strx, end = " " * xlen)
        cnt += 1
        if cnt % 2 == 0:
            print()
    print()

#dumptokens()

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

# ------------------------------------------------------------------------
# Token definitions:
# Use textual context nn[idx][1] for development, numeric nn[idx][0]
# for production use.
#
# The order of the definitions do not matter.
#
# To add a new syntactic element, search for an existing feature (like 'wrap')
# Add the new element into the a.) definition, b.) regex defintion,
# c.) state definition, d.) state table, e.) action function.
#
# The script is self checking, will report on missing defintions. However,
# it can not (will not) report on syntactic anomalies.
#

#[unique(), "tab2"   ],      \

#    sys.exit(1)

# ------------------------------------------------------------------------
# Parser state machine states. The state machine runs through the whole
# file stepping the rules. The functions may do anything, including reduce.
# Blank reduce may be executed with the state transition set to 'REDUCE'
#
# The number is the state, the string is for debugging / analyzing
# Once ready, operate on the numbers for speed.
# The E-states are not used, kept it for extensibility.

# ------------------------------------------------------------------------
# Parser functions that are called on parser events. Note the 'e' prefix
# for the 'end' function -> bold() -> ebold()  (end bold)
# The trivial functions are extracted to pungfunc.py

# May be redefined, included here for required initial states:

class st():

    ANYSTATE    = [-2, "anystate"]
    REDUCE      = [-1, "reduce"]
    IGNORE  = [unique(),      "ignore"]
    INIT    = [unique(),      "init"]
    SPAN    = [unique(),      "span"]
    SPANTXT = [unique(),      "spantxt"]
    IDENT   = [unique(),      "ident"]
    KEY     = [unique(),      "key"]
    VAL     = [unique(),      "val"]
    EQ      = [unique(),      "eq"]
    KEYVAL  = [unique(),      "keyval"]
    ITALIC  = [unique(),      "italic"]
    EITALIC = [unique(),      "eitalic"]
    BOLD    = [unique(),      "bold"]
    EBOLD   = [unique(),      "ebold"]
    ITBOLD  = [unique(),      "itbold"]
    EITBOLD = [unique(),      "eitbold"]
    UL      = [unique(),      "ul"]
    EUL     = [unique(),      "eul"]
    DUL     = [unique(),      "dul"]
    EDUL    = [unique(),      "edul"]
    RED     = [unique(),      "red"]
    ERED    = [unique(),      "ered"]
    BGRED     = [unique(),     "bgred"]
    EBGRED    = [unique(),    "ebgred"]
    GREEN   = [unique(),      "green"]
    EGREEN  = [unique(),      "egreen"]
    BGGREEN   = [unique(),    "bggreen"]
    EBGGREEN  = [unique(),    "ebggreen"]
    BLUE    = [unique(),      "blue"]
    EBLUE   = [unique(),      "eblue"]
    BGBLUE    = [unique(),    "bgblue"]
    EBGBLUE   = [unique(),    "ebgblue"]
    STRIKE  = [unique(),      "strike"]
    ESTRIKE = [unique(),      "estrike"]
    LARGE  = [unique(),       "large"]
    ELARGE = [unique(),       "elarge"]
    XLARGE  = [unique(),      "xlarge"]
    EXLARGE = [unique(),      "exlarge"]
    XXLARGE  = [unique(),     "xlarge"]
    EXXLARGE = [unique(),     "exlarge"]
    SMALL  = [unique(),       "small"]
    ESMALL = [unique(),       "esmall"]
    XSMALL  = [unique(),      "xsmall"]
    EXSMALL = [unique(),      "exsmall"]
    CENT  = [unique(),        "cent"]
    ECENT = [unique(),        "ecent"]
    RIGHT  = [unique(),       "right"]
    ERIGHT = [unique(),       "eright"]
    WRAP  = [unique(),        "wrap"]
    EWRAP = [unique(),        "ewrap"]
    LINK  = [unique(),        "link"]
    ELINK = [unique(),        "elink"]
    INC   = [unique(),        "inc"]
    EINC  = [unique(),        "einc"]
    IMAGE  = [unique(),       "image"]
    EIMAGE = [unique(),       "eimage"]
    SUB  = [unique(),         "sup"]
    ESUB = [unique(),         "esup"]
    SUP  = [unique(),         "sub"]
    ESUP = [unique(),         "esub"]
    FILL  = [unique(),        "fill"]
    EFILL = [unique(),        "efill"]
    FIXED  = [unique(),       "fixed"]
    EFIXED = [unique(),       "efixed"]
    INDENT  = [unique(),      "indent"]
    EINDENT = [unique(),      "eindent"]
    MARGIN  = [unique(),      "margin"]
    EMARGIN = [unique(),      "emargin"]
    LMARGIN  = [unique(),     "lmargin"]
    ELMARGIN = [unique(),     "elmargin"]
    HID  = [unique(),         "hid"]
    EIHID = [unique(),        "ehid"]
    NCOL  = [unique(),        "ncol"]
    ENCOL = [unique(),        "encol"]
    NBGCOL  = [unique(),      "nbgcol"]
    ENBNCOL = [unique(),      "enbgcol"]
    XSP = [unique(),          "xsp"]

def dumpstates():
    pass

# Color instructions: (not used)

#STATECOL = [RED, GREEN, BLUE]

# ------------------------------------------------------------------------
# State groups for recursion:

# These are states that have recursive actions:
# (like bold in italic or size in color etc ...) Note specifically, that
# the SPAN state is not in this list, as inside span definitions formatting
# does not make sence. This parser ignores such occurances.

STATEFMT = [st.INIT,  st.BOLD, st.ITALIC, st.RED,
            st.GREEN, st.BLUE, st.BGRED, st.BGGREEN,
            st.BGBLUE, st.UL, st.DUL, st.STRIKE,
            st.SMALL, st.NCOL, st.NBGCOL, st.XSMALL,
            st.LARGE, st.XLARGE, st.XXLARGE,
            st.SUB, st.SUP, st.LINK, st.CENT,
            st.RIGHT, st.WRAP, st.FILL, st.INDENT,
            st.SPAN, st.SPANTXT, st.FIXED, st.MARGIN, st.LMARGIN ]

#STATEFMT = None

# ------------------------------------------------------------------------
# Class of tokens for simple alternates:

# This token class is for generic text.
TXTCLASS = pl("ident"), pl("eq"), pl("lt"), pl("str"), pl("str2"), \
             pl("str3"), pl("gt"), pl("nl"), pl("sp"), pl("any"),

#cb.Text("d", "dd", "ddd")

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
#   Fri 11.Apr.2025 turned it read only  [] => ()
#
# Parser starts in INIT. Parser skips IGNORE. (in those cases, usually
# the function sets the new state)
#
# Use textual context for development, numeric for production
#
# This table specifies a grammar for text processing, similar to Pango
#
# -State -StateClass -Token -TokenClass -Function -newState -contFlag

parsetable = (
    ( None,    STATEFMT,  pl("span"),     None,   cb.Span,      st.SPAN, 0 ),
    ( None,    STATEFMT,  pl("bold"),     None,   cb.Bold,      st.BOLD, 0 ),
    ( None,    STATEFMT,  pl("it"),       None,   cb.Italic,    st.ITALIC, 0 ),
    ( None,    STATEFMT,  pl("itbold"),   None,   cb.ItBold,    st.ITBOLD, 0 ),
    ( None,    STATEFMT,  pl("ul"),       None,   cb.Underline, st.UL, 0 ),
    ( None,    STATEFMT,  pl("dul"),      None,   cb.Dunderline,st.DUL, 0 ),
    ( None,    STATEFMT,  pl("red"),      None,   cb.Red,       st.RED, 0 ),
    ( None,    STATEFMT,  pl("bgred"),    None,   cb.Bgred,     st.BGRED, 0 ),
    ( None,    STATEFMT,  pl("blue"),     None,   cb.Blue,      st.BLUE, 0 ),
    ( None,    STATEFMT,  pl("bgblue"),   None,   cb.Bgblue,    st.BGBLUE, 0 ),
    ( None,    STATEFMT,  pl("green"),    None,   cb.Green,     st.GREEN, 0 ),
    ( None,    STATEFMT,  pl("bggreen"),  None,   cb.Bggreen,   st.BGGREEN, 0 ),
    ( None,    STATEFMT,  pl("strike"),   None,   cb.Strike,    st.STRIKE, 0 ),
    ( None,    STATEFMT,  pl("large"),    None,   cb.Large,     st.LARGE, 0 ),
    ( None,    STATEFMT,  pl("xlarge"),   None,   cb.Xlarge,    st.XLARGE, 0 ),
    ( None,    STATEFMT,  pl("xxlarge"),  None,   cb.Xxlarge,   st.XXLARGE, 0 ),
    ( None,    STATEFMT,  pl("small"),    None,   cb.Small,     st.SMALL, 0 ),
    ( None,    STATEFMT,  pl("xsmall"),   None,   cb.Xsmall,    st.XSMALL, 0 ),
    ( None,    STATEFMT,  pl("cent"),     None,   cb.Center,    st.CENT, 0 ),
    ( None,    STATEFMT,  pl("right"),    None,   cb.Right,     st.RIGHT, 0 ),
    ( None,    STATEFMT,  pl("wrap"),     None,   cb.Wrap,      st.WRAP, 0 ),
    ( None,    STATEFMT,  pl("link"),     None,   cb.Link,      st.LINK, 0 ),
    ( None,    STATEFMT,  pl("image"),    None,   cb.Image,     st.IMAGE, 0 ),
    ( None,    STATEFMT,  pl("inc"),      None,   cb.Inc,       st.INC, 0 ),
    ( None,    STATEFMT,  pl("sub"),      None,   cb.Sub,       st.SUB, 0 ),
    ( None,    STATEFMT,  pl("sup"),      None,   cb.Sup,       st.SUP, 0 ),
    ( None,    STATEFMT,  pl("fill"),     None,   cb.Fill,      st.FILL, 0 ),
    ( None,    STATEFMT,  pl("fixed"),    None,   cb.Fixed,     st.FIXED, 0 ),
    ( None,    STATEFMT,  pl("indent"),   None,   cb.Indent,    st.INDENT, 0 ),
    ( None,    STATEFMT,  pl("margin"),   None,   cb.Margin,    st.MARGIN, 0 ),
    ( None,    STATEFMT,  pl("lmargin"),  None,   cb.Lmargin,   st.LMARGIN, 0 ),
    ( None,    STATEFMT,  pl("hid"),      None,   cb.Hid,       st.HID, 0 ),
    ( None,    STATEFMT,  pl("ncol"),     None,   cb.Ncol,      st.NCOL, 0 ),
    ( None,    STATEFMT,  pl("ncol2"),    None,   cb.Ncol2,     st.NCOL, 0 ),
    ( None,    STATEFMT,  pl("nbgcol"),   None,   cb.Nbgcol,    st.NBGCOL, 0 ),

    ( st.INIT,     None,    None,       TXTCLASS,    cb.Text,      st.IGNORE, 0 ),

    ( None,   STATEFMT,   pl("xsp"),      None,   cb.Sp,       st.IGNORE, 0 ),
    ( None,   STATEFMT,   pl("tab"),      None,   cb.Tab,      st.IGNORE, 0 ),
    ( None,   STATEFMT,   pl("comm"),     None,   cb.Comm,     st.IGNORE, 0 ),
    ( None,   STATEFMT,   pl("comm2"),     None,  cb.Comm2,    st.IGNORE, 0 ),
    ( None,   STATEFMT,   pl("bsnl"),     None,   None,        st.IGNORE, 0 ),

    ( st.SPAN,   None,     pl("ident"),    None,     None,        st.KEY, 1 ),
    #( KEYVAL, None,     pl("ident"),    None,     cb.Keyval,   st.KEY, 1 ),
    ( st.KEY,    None,     pl("eq"),       None,     None,        st.VAL, 1 ),
    ( st.VAL,    None,     pl("ident"),    None,     cb.Keyval,   st.IGNORE, 0 ),
    ( st.VAL,    None,     pl("str"),      None,     cb.Keyval,   st.IGNORE, 0 ),
    ( st.VAL,    None,     pl("str2"),     None,     cb.Keyval,   st.IGNORE, 0 ),
    ( st.VAL,    None,     pl("str4"),     None,     cb.Keyval,   st.IGNORE, 0 ),
    ( st.SPAN,   None,     pl("gt"),       None,     cb.Span2,    st.SPANTXT, 0 ),
    ( st.SPAN,   None,     pl("sp"),       None,     None,        st.IGNORE, 0 ),

    ( st.IMAGE,   None,    pl("ident"),    None,     None,         st.KEY, 1 ),
    ( st.IMAGE,   None,    pl("gt"),       None,     cb.Image2,    st.IGNORE, 0 ),
    ( st.IMAGE,   None,    pl("sp"),       None,     None,         st.IGNORE, 0 ),

    ( st.INC,   None,     pl("ident"),    None,     None,         st.KEY, 1 ),
    ( st.INC,   None,     pl("gt"),       None,     cb.Inc2,      st.IGNORE, 0 ),
    ( st.INC,   None,     pl("sp"),       None,     None,         st.IGNORE, 0 ),

    ( st.LINK,   None,     pl("ident"),    None,     None,          st.KEY, 1 ),
    ( st.LINK,   None,     pl("gt"),       None,     cb.Link2,      st.SPANTXT, 0 ),
    ( st.LINK,   None,     pl("sp"),       None,     None,          st.IGNORE, 0 ),

    ( st.SPANTXT, None,    pl("espan"),    None,     cb.eSpan,      st.IGNORE, 0 ),
    ( st.SPANTXT, None,    pl("elink"),    None,     cb.eLink,      st.IGNORE, 0 ),

    ( st.SPANTXT, None,    pl("bold"),     None,     cb.Bold,       st.BOLD, 0 ),
    ( st.SPANTXT, None,    pl("it"),       None,     cb.Italic,     st.ITALIC, 0 ),
    ( st.SPANTXT, None,    None,       TXTCLASS,     cb.Text,       st.IGNORE, 0 ),

    ( st.ITALIC,   None, None,       TXTCLASS,       cb.Text,       st.IGNORE, 0 ),
    ( st.ITALIC,   None,  pl("eit"),      None,      cb.eItalic,    st.IGNORE, 0 ),

    ( st.BOLD,     None, None,       TXTCLASS,       cb.Text,   st.IGNORE, 0 ),
    ( st.BOLD,     None,  pl("ebold"),    None,      cb.eBold,  st.IGNORE, 0 ),

    ( st.ITBOLD,   None,   None,       TXTCLASS,     cb.Text,       st.IGNORE, 0 ),
    ( st.ITBOLD,   None,   pl("eitbold"), None,      cb.eItBold,    st.IGNORE, 0 ),

    ( st.UL,       None,   None,       TXTCLASS,     cb.Text,         st.IGNORE, 0 ),
    ( st.UL,       None,  pl("eul"),       None,     cb.eUnderline,   st.IGNORE, 0 ),

    ( st.DUL,       None,   None,       TXTCLASS,    cb.Text,         st.IGNORE, 0 ),
    ( st.DUL,       None,  pl("edul"),       None,   cb.eDunderline,  st.IGNORE, 0 ),

    ( st.RED,      None,   None,       TXTCLASS,     cb.Text,         st.IGNORE, 0 ),
    ( st.RED,      None,   pl("ered"),     None,     cb.eRed,         st.IGNORE, 0 ),

    ( st.BGRED,    None,   None,       TXTCLASS,     cb.Text,         st.IGNORE, 0 ),
    ( st.BGRED,    None,   pl("ebgred"),     None,   cb.eBgred,       st.IGNORE, 0 ),

    ( st.BLUE,     None,    None,       TXTCLASS,    cb.Text,         st.IGNORE, 0 ),
    ( st.BLUE,     None,   pl("eblue"),     None,    cb.eBlue,        st.IGNORE, 0 ),

    ( st.BGBLUE,     None,    None,       TXTCLASS,  cb.Text,         st.IGNORE, 0 ),
    ( st.BGBLUE,     None,  pl("ebgblue"),    None,  cb.eBgblue,      st.IGNORE, 0 ),

    ( st.GREEN,    None,    None,       TXTCLASS,    cb.Text,         st.IGNORE, 0 ),
    ( st.GREEN,    None,   pl("egreen"),     None,   cb.eGreen,       st.IGNORE, 0 ),

    ( st.BGGREEN,    None,    None,       TXTCLASS,  cb.Text,         st.IGNORE, 0 ),
    ( st.BGGREEN,    None,   pl("ebggreen"),     None,    cb.eBggreen, st.IGNORE, 0 ),

    ( st.STRIKE,   None,   None,       TXTCLASS,     cb.Text,         st.IGNORE, 0 ),
    ( st.STRIKE,   None,   pl("estrike"), None,      cb.eStrike,      st.IGNORE, 0 ),

    ( st.LARGE,    None,   None,       TXTCLASS,     cb.Text,         st.IGNORE, 0 ),
    ( st.LARGE,    None,   pl("elarge"),    None,    cb.eLarge,       st.IGNORE, 0 ),

    ( st.XLARGE,    None,   None,       TXTCLASS,    cb.Text,         st.IGNORE, 0 ),
    ( st.XLARGE,    None,   pl("exlarge"),    None,  cb.eXlarge,      st.IGNORE, 0 ),

    ( st.XXLARGE,    None,   None,       TXTCLASS,   cb.Text,         st.IGNORE, 0 ),
    ( st.XXLARGE,    None,   pl("exxlarge"),    None,  cb.eXxlarge,   st.IGNORE, 0 ),

    ( st.SMALL,     None,   None,       TXTCLASS,    cb.Text,         st.IGNORE, 0 ),
    ( st.SMALL,     None,  pl("esmall"),    None,    cb.eSmall,       st.IGNORE, 0 ),

    ( st.XSMALL,     None,   None,       TXTCLASS,   cb.Text,         st.IGNORE, 0 ),
    ( st.XSMALL,     None,  pl("exsmall"),    None,  cb.eXsmall,      st.IGNORE, 0 ),

    ( st.CENT,     None,   None,       TXTCLASS,     cb.Text,         st.IGNORE, 0 ),
    ( st.CENT,     None,  pl("ecent"),    None,      cb.eCenter,      st.IGNORE, 0 ),

    ( st.RIGHT,     None,   None,      TXTCLASS,     cb.Text,       st.IGNORE, 0 ),
    ( st.RIGHT,     None,  pl("eright"),    None,    cb.eRight,     st.IGNORE, 0 ),

    ( st.WRAP,     None,   None,       TXTCLASS,     cb.Text,       st.IGNORE, 0 ),
    ( st.WRAP,     None,  pl("ewrap"),    None,      cb.eWrap,      st.IGNORE, 0 ),

    ( st.SUB,     None,   None,       TXTCLASS,      cb.Text,       st.IGNORE, 0 ),
    ( st.SUB,     None,  pl("esub"),      None,      cb.eSub,      st.IGNORE, 0 ),

    ( st.SUP,     None,   None,       TXTCLASS,      cb.Text,       st.IGNORE, 0 ),
    ( st.SUP,     None,  pl("esup"),      None,      cb.eSup,      st.IGNORE, 0 ),

    ( st.FILL,     None,   None,       TXTCLASS,     cb.Text,       st.IGNORE, 0 ),
    ( st.FILL,     None,  pl("efill"),    None,      cb.eFill,      st.IGNORE, 0 ),

    ( st.FIXED,     None,   None,       TXTCLASS,    cb.Text,       st.IGNORE, 0 ),
    ( st.FIXED,     None,  pl("efixed"),    None,    cb.eFixed,      st.IGNORE, 0 ),

    ( st.INDENT,     None,   None,       TXTCLASS,   cb.Text,       st.IGNORE, 0 ),
    ( st.INDENT,     None,  pl("eindent"),    None,  cb.eIndent,  st.IGNORE, 0 ),

    ( st.MARGIN,     None,   None,       TXTCLASS,   cb.Text,       st.IGNORE, 0 ),
    ( st.MARGIN,     None,  pl("emargin"),    None,  cb.eMargin,  st.IGNORE, 0 ),

    ( st.LMARGIN,     None,   None,       TXTCLASS,  cb.Text,       st.IGNORE, 0 ),
    ( st.LMARGIN,     None,  pl("elmargin"),  None,  cb.eLmargin,  st.IGNORE, 0 ),

    ( st.HID,     None,   None,       TXTCLASS,      None,     st.IGNORE, 0 ),
    ( st.HID,     None,  pl("ehid"),    None,        cb.eHid,     st.IGNORE, 0 ),

    ( st.NCOL,     None,   None,     TXTCLASS,       cb.Text,      st.IGNORE, 0 ),
    ( st.NCOL,     None,  pl("encol"),    None,      cb.eNcol,    st.IGNORE, 0 ),

    ( st.NBGCOL,     None,   None,     TXTCLASS,     cb.Text,      st.IGNORE, 0 ),
    ( st.NBGCOL,     None,  pl("enbgcol"),    None,  cb.eNbgcol,    st.IGNORE, 0 ),
    )

    #    [ None,   STATEFMT,   pl("tab2"),  None, cb.Tab,      st.IGNORE, 0 ],

def _printrow(row):

    cnt = 0
    for aa in row:
        cnt += 1
        if cnt == 4:
            #print("cnt", cnt, aa, end = " ")
            if aa:
                for aaa in aa:
                    print(rlookup(aaa), end = " ")
            else:
                print("Nonz", end = "")
        elif cnt == 5:
            #if type(aa) == type(cb.Text):
            print(str(aa)[13:30], end = " ")
        else:
            print(aa, end = " ")
    print()

def dumpPtable():
    cnt = 0
    for aa in parsetable:
        print("Row", cnt, ":") ; _printrow(aa)
        cnt += 1
    print()

#dumpPtable()

# EOF
