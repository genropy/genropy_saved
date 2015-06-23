#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:XmlRpc'

    @public_method
    def fillString(self,s='',nchar=20,filler='.'):
        "fill a string"
        return s.ljust(nchar,filler)
    
    @public_method
    def sum(self,a=0,b=0):
        "sum of numbers"
        return a+b
        
    @public_method
    def days(self,daylist):
        "days from numbers"
        result=[]
        days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for d in daylist:
            result.append(days[d-1])
        return result
        
    
