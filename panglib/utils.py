#!/usr/bin/env python

import sys, os, re, time, stat, traceback

import  panglib.stack as stack


# Some globals read: (Pang View Globals):

class pvg():

    lstack = stack.Stack();

    buf = None; xstack = None; pgdebug = 0;
    fullpath = None; docroot = None
    verbose = False; show_lexer = False; full_screen = False
    got_clock = False; show_timing = False; second = ""
    xfull_screen = False; flag = False; show_parse = False
    emit = False; show_state = False;  show_state_change = False;
    pane_pos = -1;  warnings = False; show_all = False

# ------------------------------------------------------------------------
# Convert octal string to integer

def oct2int(strx):
    retx = 0
    for aa in strx:
        num = ord(aa) - ord("0")
        if num > 7 or num < 0:
            break
        retx <<= 3; retx += num
    #print ("oct:", strx, "int:", retx)
    return retx

# ------------------------------------------------------------------------
# Convert unicode sequence to unicode char

def uni(xtab):

    #print (str.format("{0:b}",  xtab[0]))

    cc = 0
    try:
        if xtab[0] & 0xe0 == 0xc0:  # two numbers
            cc = (xtab[0] & 0x1f) << 6
            cc += (xtab[1] & 0x3f)
        elif xtab[0] & 0xf0 == 0xe0: # three numbers
            cc = (xtab[0] & 0x0f) << 12
            cc += (xtab[1] & 0x3f) << 6
            cc += (xtab[2] & 0x3f)
        elif xtab[0] & 0xf8 == 0xf0: # four numbers
            cc = (xtab[0] & 0x0e)  << 18
            cc += (xtab[1] & 0x3f) << 12
            cc += (xtab[2] & 0x3f) << 6
            cc += (xtab[3] & 0x3f)
        elif xtab[0] & 0xfc == 0xf8: # five numbers
            cc = (xtab[0] & 0x03)  << 24
            cc += (xtab[1] & 0x3f) << 18
            cc += (xtab[2] & 0x3f) << 12
            cc += (xtab[3] & 0x3f) << 6
            cc += (xtab[4] & 0x3f)
        elif xtab[0] & 0xfe == 0xf8: # six numbers
            cc = (xtab[0] & 0x01)  << 30
            cc += (xtab[1] & 0x3f) << 24
            cc += (xtab[2] & 0x3f) << 18
            cc += (xtab[3] & 0x3f) << 12
            cc += (xtab[4] & 0x3f) << 6
            cc += (xtab[5] & 0x3f)

        #ccc = unichr(cc)
        ccc = chr(cc)
    except:
        pass

    return ccc

def revesc(strx):

    ''' reverse 'C' escape sequences \\n '''

    retx = ""; pos = 0; lenx = len(strx)
    while True:
        if pos >= lenx:
            break
        chh = strx[pos]
        if(chh == '\\'):
            if pos >= lenx:
                retx += chh
                break
            chh2 = strx[pos+1]
            if chh2 == "n":
                retx += '\n'
                pos += 1
            elif chh2 == "r":
                retx += '\r'
                pos += 1
            elif chh2 == "a":
                retx += '\a'
                pos += 1
            elif chh2 == "t":
                retx += '\t'
                pos += 1
            else:
                retx += chh + chh2;
        else:
            retx += chh
        pos += 1

    #print("revesc", strx)
    #for aa in retx:
    #    print(ord(retx))

    return retx


def esc(strx):

    ''' erase new line as \\n '''

    #print (" x[" + strx + "]x ")

    retx = u""; pos = 0; lenx = len(strx)

    while True:
        if pos >= lenx:
            break
        chh = strx[pos]
        if(chh == '\n'):
            retx += '\\n'
        elif(chh == '\r'):
            retx += '\\r'
        elif(chh == '\a'):
            retx += '\\a'
        elif(chh == '\\'):
            retx += '\\\\'
        else:
            retx += chh
        pos += 1
    return retx

# ------------------------------------------------------------------------
# Print( an exception as the system would print it)

def put_exc(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print("Could not print trace stack. ", sys.exc_info())
    print(cumm, end = "")

# ------------------------------------------------------------------------
# Unescape unicode into displayable sequence

xtab = []; xtablen = 0

def unescape(strx):

    #print (" x[" + strx + "]x ")

    global xtab, xtablen
    retx = u""; pos = 0; lenx = len(strx)

    while True:
        if pos >= lenx:
            break

        chh = strx[pos]

        if(chh == '\\'):
            #print ("backslash", strx[pos:])
            pos2 = pos + 1; strx2 = ""
            while True:
                if pos2 >= lenx:
                    # See if we accumulated anything
                    if strx2 != "":
                        xtab.append(oct2int(strx2))
                    if len(xtab) > 0:
                        #print ("final:", xtab)
                        if xtablen == len(xtab):
                            retx += uni(xtab)
                            xtab = []; xtablen = 0
                    pos = pos2 - 1
                    break
                chh2 = strx[pos2]
                if chh2  >= "0" and chh2 <= "7":
                    strx2 += chh2
                else:
                    #print ("strx2: '"  + strx2 + "'")
                    if strx2 != "":
                        octx = oct2int(strx2)
                        if xtablen == 0:
                            if octx & 0xe0 == 0xc0:
                                #print ("two ",str.format("{0:b}", octx))
                                xtablen = 2
                                xtab.append(octx)
                            elif octx & 0xf0 == 0xe0: # three numbers
                                #print ("three ",str.format("{0:b}", octx))
                                xtablen = 3
                                xtab.append(octx)
                            elif octx & 0xf8 == 0xf0: # four numbers
                                print ("four ",str.format("{0:b}", octx))
                                xtablen = 4
                                xtab.append(octx)
                            elif octx & 0xfc == 0xf8: # five numbers
                                print ("five ",str.format("{0:b}", octx))
                                xtablen = 5
                                xtab.append(octx)
                            elif octx & 0xfe == 0xfc: # six numbers
                                print ("six ",str.format("{0:b}", octx))
                                xtablen = 6
                                xtab.append(octx)
                            else:
                                #print ("other ",str.format("{0:b}", octx))
                                retx += chr(octx)
                                #retx += unichr(octx)
                        else:
                            xtab.append(octx)
                            #print ("data ",str.format("{0:b}", octx))
                            if xtablen == len(xtab):
                                retx += uni(xtab)
                                xtab = []; xtablen = 0

                    pos = pos2 - 1
                    break
                pos2 += 1
        else:

            if xtablen == len(xtab) and xtablen != 0:
                retx += uni(xtab)
            xtab=[]; xtablen = 0

            try:
                retx += chh
            except:
                pass
        pos += 1

    #print ("y[" + retx + "]y")
    return retx

# ------------------------------------------------------------------------
# Give the user the usual options for true / false - 1 / 0 - y / n

def isTrue(strx):
    if strx == "1": return True
    if strx == "0": return False
    uuu = strx.upper()
    if uuu == "TRUE": return True
    if uuu == "FALSE": return False
    if uuu == "Y": return True
    if uuu == "N": return False
    if uuu == "YES": return True
    if uuu == "NO": return False
    return False

# ------------------------------------------------------------------------
# Return True if file exists

def isfile(fname):

    try:
        ss = os.stat(fname)
    except:
        return False

    if stat.S_ISREG(ss[stat.ST_MODE]):
        return True
    return False

# EOF
