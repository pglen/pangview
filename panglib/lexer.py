#!/usr/bin/env python

import re, sys

# ------------------------------------------------------------------------
#

class _LexIter():

    def __init__(self, tokens, tokenregex):
        cnt = 0;
        self.tokens = tokens
        self.tokenregex = tokenregex;

    def lexiter(self, pos, strx):
        for posx in range(len(self.tokenregex)):
            mmm = self.tokenregex[posx].match(strx, pos)
            if mmm:
                bb, cc = self.tokens[posx];
                #print (bb, cc, mmm.end() - mmm.start(), strx[mmm.start():mmm.end()])
                tt = bb, mmm, strx[mmm.start():mmm.end()], mmm.start(), mmm.end()
                return tt
        #print("not")
        return None;

class Lexer():

    def __init__(self, data, stack, tokens):

        # Pre-compile tokens
        self.tokenregex = []
        for aa in tokens:
            try:
                rr = re.compile(aa[1])
            except:
                print("Cannot compile: ", aa, sys.exc_info())
                rr = re.compile("error")
                raise
            self.tokenregex.append(rr)

        #for cnt, xx in enumerate(tokens):
        #    print ("token:", xx, self.tokenregex[cnt])
        #sys.exit()

        lexiter = _LexIter(tokens, self.tokenregex)
        lastpos = 0; pos = 0; lenx = len(data)
        while True:
            if pos >= lenx:
                break;
            tt = lexiter.lexiter(pos, data)
            if tt == None:
                break
            mmm = tt[1]
            if mmm:
                # skip token
                pos = mmm.end()
                #print  (tt[1], "'" + data[mmm.start():mmm.end()] + "' - ",)
                #print   ("'" + data[mmm.start():mmm.end()] + "' - ",)
                stack.push(tt)
            else:
                pos += 1  # step to next

if __name__ == "__main__":
    print ("This module was not meant to operate as main.")

# EOF
