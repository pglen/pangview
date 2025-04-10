#!/usr/bin/env python

import  panglib.pangfunc as pangfunc
import  panglib.pangdisp as pangdisp

# This parser digests formatted text similar to pango in Gtk.
# Was created to quickly display formatted messages.
# See SYNTAX for details on text formats

cb = pangfunc.CallBack(pangdisp.ts, pangdisp.add_one, pangdisp.emit_one)
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
        #print ("Token '" + strx + "' not found, please correct it.")
        #sys.exit(1)
        tokdef.append((unique(), strx))

    for aa in tokdef:
        if strx == aa[1]:
            #print "found", aa
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

tokens =  [
    [lookup("comm"),      "##.*"          , None, ],
    [lookup("comm2"),     ".*##.*"        , None, ],
    [lookup("span"),      "<span "        , None  ],
    [lookup("espan"),     "</span>"       , None, ],
    [lookup("it"),        "<i>"           , None, ],
    [lookup("eit"),       "</i>"          , None, ],
    [lookup("hid"),       "<hid>"         , None, ],
    [lookup("ehid"),      "</hid>"        , None, ],
    [lookup("bold"),      "<b>"           , None, ],
    [lookup("tab"),       "<tab>"         , None, ],
    [lookup("ebold"),     "</b>"          , None, ],
    [lookup("itbold"),    "<ib>"          , None, ],
    [lookup("eitbold"),   "</ib>"         , None, ],
    [lookup("red"),       "<r>"           , None, ],
    [lookup("ered"),      "</r>"          , None, ],
    [lookup("bgred"),     "<rb>"           , None, ],
    [lookup("ebgred"),    "</rb>"          , None, ],
    [lookup("indent"),    "<in>"          , None, ],
    [lookup("eindent"),   "</in>"         , None, ],
    [lookup("margin"),    "<m>"          , None, ],
    [lookup("emargin"),   "</m>"         , None, ],
    [lookup("lmargin"),    "<lm>"          , None, ],
    [lookup("elmargin"),   "</lm>"         , None, ],
    [lookup("blue"),      "<e>"           , None, ],
    [lookup("eblue"),     "</e>"          , None, ],
    [lookup("bgblue"),    "<eb>"           , None, ],
    [lookup("ebgblue"),   "</eb>"          , None, ],
    [lookup("green"),     "<g>"           , None, ],
    [lookup("egreen"),    "</g>"          , None, ],
    [lookup("bggreen"),   "<gb>"           , None, ],
    [lookup("ebggreen"),  "</gb>"          , None, ],
    [lookup("large"),     "<l>"           , None, ],
    [lookup("elarge"),    "</l>"          , None, ],
    [lookup("xlarge"),    "<xl>"          , None, ],
    [lookup("exlarge"),   "</xl>"         , None, ],
    [lookup("xxlarge"),   "<xxl>"         , None, ],
    [lookup("exxlarge"),  "</xxl>"        , None, ],
    [lookup("small"),     "<sm>"          , None, ],
    [lookup("esmall"),    "</sm>"         , None, ],
    [lookup("xsmall"),    "<xs>"          , None, ],
    [lookup("exsmall"),   "</xs>"          , None, ],
    [lookup("cent"),      "<c>"           , None, ],
    [lookup("ecent"),     "</c>"          , None, ],
    [lookup("right"),     "<t>"           , None, ],
    [lookup("eright"),    "</t>"          , None, ],
    [lookup("strike"),    "<s>"           , None, ],
    [lookup("estrike"),   "</s>"          , None, ],
    [lookup("ul"),        "<u>"           , None, ],
    [lookup("eul"),       "</u>"          , None, ],
    [lookup("dul"),       "<uu>"          , None, ],
    [lookup("edul"),      "</uu>"         , None, ],
    [lookup("wrap"),      "<w>"           , None, ],
    [lookup("ewrap"),     "</w>"          , None, ],
    [lookup("link"),      "<link "        , None, ],
    [lookup("elink"),     "</link>"       , None, ],
    [lookup("image"),      "<image "      , None, ],
    [lookup("eimage"),     "</image>"     , None, ],
    [lookup("sub"),       "<sub>"         , None, ],
    [lookup("esub"),      "</sub>"        , None, ],
    [lookup("sup"),       "<sup>"         , None, ],
    [lookup("esup"),      "</sup>"        , None, ],
    [lookup("fill"),      "<j>"           , None, ],
    [lookup("efill"),      "</j>"         , None, ],
    [lookup("fixed"),      "<f>"          , None, ],
    [lookup("efixed"),     "</f>"         , None, ],
    [lookup("nbgcol"),    "<bg#[0-9a-fA-F]+ *>"  , None, ],
    [lookup("enbgcol"),   "</bg#>"          , None, ],
    [lookup("ncol2"),      "<fg#[0-9a-fA-F]+ *>"  , None, ],
    [lookup("ncol"),      "<#[0-9a-fA-F]+ *>"  , None, ],
    [lookup("encol"),     "</#>"          , None, ],
    [lookup("escquo"),    r"\\\""         , None, ],
    [lookup("dblbs"),     r"\\\\"         , None, ],
    [lookup("ident"),     "[A-Za-z0-9_\-\./]+" , None, ],
    [lookup("str4"),      "\#[0-9a-zA-Z]+", None, ],
    [lookup("str3"),      "(\\\\[0-7]+)+"    , None, ],
    [lookup("str"),       "\".*?\""       , None, ],
    [lookup("str2"),      "\'.*?\'"       , None, ],
    [lookup("eq"),        "="             , None, ],
    [lookup("lt"),        "<"             , None, ],
    [lookup("gt"),        ">"             , None, ],
    [lookup("sp"),        " "             , None, ],
    [lookup("colu"),      "<colu>"        , None, ],
    [lookup("bsnl"),      "\\\\\n"        , None, ],
    [lookup("nl"),        r"\n"            , None, ],
    [lookup("any"),       "."             , None, ],
    ]

token_alias =  [
    [lookup("fixed"),      "<fixed>"      , None, ],
    [lookup("efixed"),     "</fixed>"     , None, ],
]

# Just to make sure no one is left out: (for debug only)

if len(tokens) != len(tokdef):
    print ("Number of token definitions and tokens do not match.")
    print("tok:", len(tokens), "def:", len(tokdef))

tokens +=  token_alias

def dumptokens():
    cnt = 0
    for aa in tokens:
        strx = str(aa[0]) + " = " + aa[1]
        xlen = 40 - len(strx)
        print(strx, end = " " * xlen)
        cnt += 1
        if cnt % 2 == 0:
            print()
    print()

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

def dumpstates():
    pass

# Color instructions: (not used)

STATECOL = [RED, GREEN, BLUE]

# ------------------------------------------------------------------------
# State groups for recursion:

# These are states that have recursive actions:
# (like bold in italic or size in color etc ...) Note specifically, that
# the SPAN state is not in this list, as inside span definitions formatting
# does not make sence. This parser ignores such occurances.

STATEFMT = [INIT,  BOLD, ITALIC, RED,
            GREEN, BLUE, BGRED, BGGREEN,
            BGBLUE, UL, DUL, STRIKE,
            SMALL, NCOL, NBGCOL, XSMALL,
            LARGE, XLARGE, XXLARGE,
            SUB, SUP, LINK, CENT,
            RIGHT, WRAP, FILL, INDENT,
            SPANTXT, FIXED, MARGIN, LMARGIN ]

# ------------------------------------------------------------------------
# Parser functions that are called on parser events. Note the 'e' prefix
# for the 'end' function -> bold() -> ebold()  (end bold)
# The trivial functions are extracted to pungfunc.py

# May be redefined, included here for required initial states:

IGNORE      = [unique(), "ignore"]
INIT        = [unique(), "init"]
ANYSTATE    = [-2, "anystate"]
REDUCE      = [-1, "reduce"]

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
# Parser starts in INIT. Parser skips IGNORE. (in those cases, usually
# the function sets the new state)
#
# Use textual context for development, numeric for production
#
# This table specifies a grammar for text processing, similar to Pango
#
# -State -StateClass -Token -TokenClass -Function -newState -contFlag

parsetable = [
    [ None,    STATEFMT,  pl("span"),     None,   cb.Span,      SPAN, 0 ],
    [ None,    STATEFMT,  pl("bold"),     None,   cb.Bold,      BOLD, 0 ],
    [ None,    STATEFMT,  pl("it"),       None,   cb.Italic,    ITALIC, 0 ],
    [ None,    STATEFMT,  pl("itbold"),   None,   cb.ItBold,    ITBOLD, 0 ],
    [ None,    STATEFMT,  pl("ul"),       None,   cb.Underline, UL, 0 ],
    [ None,    STATEFMT,  pl("dul"),      None,   cb.Dunderline,DUL, 0 ],
    [ None,    STATEFMT,  pl("red"),      None,   cb.Red,       RED, 0 ],
    [ None,    STATEFMT,  pl("bgred"),    None,   cb.Bgred,     BGRED, 0 ],
    [ None,    STATEFMT,  pl("blue"),     None,   cb.Blue,      BLUE, 0 ],
    [ None,    STATEFMT,  pl("bgblue"),   None,   cb.Bgblue,    BGBLUE, 0 ],
    [ None,    STATEFMT,  pl("green"),    None,   cb.Green,     GREEN, 0 ],
    [ None,    STATEFMT,  pl("bggreen"),  None,   cb.Bggreen,   BGGREEN, 0 ],
    [ None,    STATEFMT,  pl("strike"),   None,   cb.Strike,    STRIKE, 0 ],
    [ None,    STATEFMT,  pl("large"),    None,   cb.Large,     LARGE, 0 ],
    [ None,    STATEFMT,  pl("xlarge"),   None,   cb.Xlarge,    XLARGE, 0 ],
    [ None,    STATEFMT,  pl("xxlarge"),  None,   cb.Xxlarge,   XXLARGE, 0 ],
    [ None,    STATEFMT,  pl("small"),    None,   cb.Small,     SMALL, 0 ],
    [ None,    STATEFMT,  pl("xsmall"),   None,   cb.Xsmall,    XSMALL, 0 ],
    [ None,    STATEFMT,  pl("cent"),     None,   cb.Center,    CENT, 0 ],
    [ None,    STATEFMT,  pl("right"),    None,   cb.Right,     RIGHT, 0 ],
    [ None,    STATEFMT,  pl("wrap"),     None,   cb.Wrap,      WRAP, 0 ],
    [ None,    STATEFMT,  pl("link"),     None,   cb.Link,      LINK, 0 ],
    [ None,    STATEFMT,  pl("image"),    None,   cb.Image,     IMAGE, 0 ],
    [ None,    STATEFMT,  pl("sub"),      None,   cb.Sub,       SUB, 0 ],
    [ None,    STATEFMT,  pl("sup"),      None,   cb.Sup,       SUP, 0 ],
    [ None,    STATEFMT,  pl("fill"),     None,   cb.Fill,      FILL, 0 ],
    [ None,    STATEFMT,  pl("fixed"),    None,   cb.Fixed,     FIXED, 0 ],
    [ None,    STATEFMT,  pl("indent"),   None,   cb.Indent,    INDENT, 0 ],
    [ None,    STATEFMT,  pl("margin"),   None,   cb.Margin,    MARGIN, 0 ],
    [ None,    STATEFMT,  pl("lmargin"),  None,   cb.Lmargin,   LMARGIN, 0 ],
    [ None,    STATEFMT,  pl("hid"),      None,   cb.Hid,       HID, 0 ],
    [ None,    STATEFMT,  pl("ncol"),     None,   cb.Ncol,      NCOL, 0 ],
    [ None,    STATEFMT,  pl("ncol2"),    None,   cb.Ncol2,     NCOL, 0 ],
    [ None,    STATEFMT,  pl("nbgcol"),   None,   cb.Nbgcol,    NBGCOL, 0 ],

    [ INIT,     None,    None,       TXTCLASS,    cb.Text,   IGNORE, 0 ],

    [ None,   STATEFMT,   pl("tab"),      None,   cb.Tab,       IGNORE, 0 ],
    [ None,   STATEFMT,   pl("comm"),     None,   cb.Comm,      IGNORE, 0 ],
    [ None,   STATEFMT,   pl("comm2"),     None,  cb.Comm2,     IGNORE, 0 ],
    [ None,   STATEFMT,   pl("bsnl"),     None,   None,         IGNORE, 0 ],

    [ SPAN,   None,     pl("ident"),    None,     None,     KEY, 1 ],
    [ KEYVAL, None,     pl("ident"),    None,     cb.Keyval,   KEY, 1 ],
    [ KEY,    None,     pl("eq"),       None,     None,     VAL, 1 ],
    [ VAL,    None,     pl("ident"),    None,     cb.Keyval,   IGNORE, 0 ],
    [ VAL,    None,     pl("str"),      None,     cb.Keyval,   IGNORE, 0 ],
    [ VAL,    None,     pl("str2"),     None,     cb.Keyval,   IGNORE, 0 ],
    [ VAL,    None,     pl("str4"),     None,     cb.Keyval,   IGNORE, 0 ],
    [ SPAN,   None,     pl("gt"),       None,     cb.Span2,    SPANTXT, 0 ],
    [ SPAN,   None,     pl("sp"),       None,     None,     IGNORE, 0 ],

    [ IMAGE,   None,    pl("ident"),    None,     None,     KEY, 1 ],
    [ IMAGE,   None,    pl("gt"),       None,     cb.Image2,   IGNORE, 0 ],
    [ IMAGE,   None,    pl("sp"),       None,     None,     IGNORE, 0 ],

    [ LINK,   None,     pl("ident"),    None,     None,     KEY, 1 ],
    [ LINK,   None,     pl("gt"),       None,     cb.Link2,    SPANTXT, 0 ],
    [ LINK,   None,     pl("sp"),       None,     None,     IGNORE, 0 ],

    [ SPANTXT, None,    pl("espan"),    None,     cb.eSpan,      INIT, 0 ],
    [ SPANTXT, None,    pl("elink"),    None,     cb.eLink,      IGNORE, 0 ],

    [ SPANTXT, None,    pl("bold"),     None,     cb.Bold,   BOLD, 0 ],
    [ SPANTXT, None,    pl("it"),       None,     cb.Italic, ITALIC, 0 ],
    [ SPANTXT, None,    None,       TXTCLASS,     cb.Text,   IGNORE, 0 ],

    [ ITALIC,   None, None,       TXTCLASS,       cb.Text,       IGNORE, 0 ],
    [ ITALIC,   None,  pl("eit"),      None,      cb.eItalic,    IGNORE, 0 ],

    [ BOLD,     None, None,       TXTCLASS,       cb.Text,   IGNORE, 0 ],
    [ BOLD,     None,  pl("ebold"),    None,      cb.eBold,  IGNORE, 0 ],

    [ ITBOLD,   None,   None,       TXTCLASS,     cb.Text,       IGNORE, 0 ],
    [ ITBOLD,   None,   pl("eitbold"), None,      cb.eItBold,    IGNORE, 0 ],

    [ UL,       None,   None,       TXTCLASS,     cb.Text,         IGNORE, 0 ],
    [ UL,       None,  pl("eul"),       None,     cb.eUnderline,   IGNORE, 0 ],

    [ DUL,       None,   None,       TXTCLASS,    cb.Text,   IGNORE, 0 ],
    [ DUL,       None,  pl("edul"),       None,   cb.eDunderline,   IGNORE, 0 ],

    [ RED,      None,   None,       TXTCLASS,     cb.Text,        IGNORE, 0 ],
    [ RED,      None,   pl("ered"),     None,     cb.eRed,        IGNORE, 0 ],

    [ BGRED,    None,   None,       TXTCLASS,     cb.Text,        IGNORE, 0 ],
    [ BGRED,    None,   pl("ebgred"),     None,   cb.eBgred,      IGNORE, 0 ],

    [ BLUE,     None,    None,       TXTCLASS,    cb.Text,       IGNORE, 0 ],
    [ BLUE,     None,   pl("eblue"),     None,    cb.eBlue,       IGNORE, 0 ],

    [ BGBLUE,     None,    None,       TXTCLASS,  cb.Text,       IGNORE, 0 ],
    [ BGBLUE,     None,  pl("ebgblue"),    None,  cb.eBgblue,       IGNORE, 0 ],

    [ GREEN,    None,    None,       TXTCLASS,    cb.Text,      IGNORE, 0 ],
    [ GREEN,    None,   pl("egreen"),     None,   cb.eGreen,    IGNORE, 0 ],

    [ BGGREEN,    None,    None,       TXTCLASS,  cb.Text,      IGNORE, 0 ],
    [ BGGREEN,    None,   pl("ebggreen"),     None,    cb.eBggreen,    IGNORE, 0 ],

    [ STRIKE,   None,   None,       TXTCLASS,     cb.Text,      IGNORE, 0 ],
    [ STRIKE,   None,   pl("estrike"), None,      cb.eStrike,   IGNORE, 0 ],

    [ LARGE,    None,   None,       TXTCLASS,     cb.Text,      IGNORE, 0 ],
    [ LARGE,    None,   pl("elarge"),    None,    cb.eLarge,    IGNORE, 0 ],

    [ XLARGE,    None,   None,       TXTCLASS,    cb.Text,      IGNORE, 0 ],
    [ XLARGE,    None,   pl("exlarge"),    None,  cb.eXlarge,    IGNORE, 0 ],

    [ XXLARGE,    None,   None,       TXTCLASS,   cb.Text,      IGNORE, 0 ],
    [ XXLARGE,    None,   pl("exxlarge"),    None,  cb.eXxlarge,    IGNORE, 0 ],

    [ SMALL,     None,   None,       TXTCLASS,    cb.Text,      IGNORE, 0 ],
    [ SMALL,     None,  pl("esmall"),    None,    cb.eSmall,    IGNORE, 0 ],

    [ XSMALL,     None,   None,       TXTCLASS,   cb.Text,      IGNORE, 0 ],
    [ XSMALL,     None,  pl("exsmall"),    None,  cb.eXsmall,    IGNORE, 0 ],

    [ CENT,     None,   None,       TXTCLASS,     cb.Text,       IGNORE, 0 ],
    [ CENT,     None,  pl("ecent"),    None,      cb.eCenter,     IGNORE, 0 ],

    [ RIGHT,     None,   None,      TXTCLASS,     cb.Text,       IGNORE, 0 ],
    [ RIGHT,     None,  pl("eright"),    None,    cb.eRight,     IGNORE, 0 ],

    [ WRAP,     None,   None,       TXTCLASS,     cb.Text,       IGNORE, 0 ],
    [ WRAP,     None,  pl("ewrap"),    None,      cb.eWrap,      IGNORE, 0 ],

    [ SUB,     None,   None,       TXTCLASS,      cb.Text,       IGNORE, 0 ],
    [ SUB,     None,  pl("esub"),      None,      cb.eSub,      IGNORE, 0 ],

    [ SUP,     None,   None,       TXTCLASS,      cb.Text,       IGNORE, 0 ],
    [ SUP,     None,  pl("esup"),      None,      cb.eSup,      IGNORE, 0 ],

    [ FILL,     None,   None,       TXTCLASS,     cb.Text,       IGNORE, 0 ],
    [ FILL,     None,  pl("efill"),    None,      cb.eFill,      IGNORE, 0 ],

    [ FIXED,     None,   None,       TXTCLASS,    cb.Text,       IGNORE, 0 ],
    [ FIXED,     None,  pl("efixed"),    None,    cb.eFixed,      IGNORE, 0 ],

    [ INDENT,     None,   None,       TXTCLASS,   cb.Text,       IGNORE, 0 ],
    [ INDENT,     None,  pl("eindent"),    None,  cb.eIndent,  IGNORE, 0 ],

    [ MARGIN,     None,   None,       TXTCLASS,   cb.Text,       IGNORE, 0 ],
    [ MARGIN,     None,  pl("emargin"),    None,  cb.eMargin,  IGNORE, 0 ],

    [ LMARGIN,     None,   None,       TXTCLASS,  cb.Text,       IGNORE, 0 ],
    [ LMARGIN,     None,  pl("elmargin"),  None,  cb.eLmargin,  IGNORE, 0 ],

    [ HID,     None,   None,       TXTCLASS,      None,     IGNORE, 0 ],
    [ HID,     None,  pl("ehid"),    None,        cb.eHid,     IGNORE, 0 ],

    [ NCOL,     None,   None,     TXTCLASS,       cb.Text,      IGNORE, 0 ],
    [ NCOL,     None,  pl("encol"),    None,      cb.eNcol,    IGNORE, 0 ],

    [ NBGCOL,     None,   None,     TXTCLASS,     cb.Text,      IGNORE, 0 ],
    [ NBGCOL,     None,  pl("enbgcol"),    None,  cb.eNbgcol,    IGNORE, 0 ],
    ]

    #    [ None,   STATEFMT,   pl("tab2"),  None, cb.Tab,      IGNORE, 0 ],

def _printrow(row):
    for aa in row:
        if type(aa) == type(cb.Text):
            print("Func:", str(aa)[13:30], end = " ")
        else:
            print(aa, end = " ")
    print()

def dumpptable():
    cnt = 0
    for aa in parsetable:
        print("Row", cnt, ":", _printrow(aa))
        cnt += 1
    print()

# EOF
