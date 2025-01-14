#!/usr/bin/env python

import sys, os, re, copy


class TextState():
    
    def __init__(self):
        bold = False;  itbold = False;  italic = False
    
    def dump(self):
    
        for aa in TextState.__dict__:
            print "dic", aa

        for aa in self.__dict__:
            print "ee", aa

if __name__ == '__main__':

    ts =  TextState()
    ts2 = TextState()
    ts3 = copy.copy(ts2)
    
    print "  TextState"
    ts.dump()
    print "  TextState2"
    ts2.dump()
    
    print "  TextState3"
    ts3.dump()

