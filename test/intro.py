#!/usr/bin/env python

# Save an object state, compare for change

import sys, os, re, string

class Hello():
    zzz = "1"

# Remember object state
def dupstate(fromx):
    class Blank():
        def __setitem__(self, aaa, bbb):
            self.__dict__[aaa] = bbb
            
    ccc = Blank()
    for aa in fromx.__dict__:
        ccc[aa] =  fromx.__dict__[aa]
    return ccc           

# Check for new state
def chkstate(obj_1, obj_2):
    
    if not obj_1: return True 
    if not obj_2: return True 
    
    # See if dictionaries match
    if len(obj_1.__dict__) != len(obj_2.__dict__):
        return True   
   
    ret = False
    # See if variables match  
    for aa in obj_1.__dict__:
        if obj_1.__dict__[aa] !=  obj_2.__dict__[aa]:
            ret = True 
            break
    return ret

if __name__ == '__main__':

    Hellx =  dupstate(Hello)
    print chkstate(Hello, Hellx)
    
    Hellx.zzz = "2"
    print chkstate(Hello, Hellx)
    
    print "Hello ->", Hello.__dict__
    print "Hellx ->", Hellx.__dict__
    
