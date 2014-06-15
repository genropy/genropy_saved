#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import splitAndStrip
import re

try:
    import psutil as ps
except ImportError:
    pass

class Main(GnrBaseService):
    def __init__(self, parent=None,**kwargs):
        self.parent = parent

    def getCpuTimes(self):
        result=Bag()
        columns='user,nice,system,idle'.split(',')
        for k, core in enumerate(ps.cpu_times(True)):
            row = Bag()
            row['core']=k+1
            for c in columns:
                row.setItem(c,getattr(core,c))
            result.setItem('r_%i'%k,row)
        return result
        
    def getProcessesBag(self,items=None,name=None,user=None):
        
        if isinstance(items,basestring):
            items=splitAndStrip(items)
    
        def filteredProcess(p):
            if user and user != p.username:
                return False
            return (not name) or re.match(name,p.name)

        def bagFromProcess(p):
            d=p.as_dict()
            if items:
                d = [(k,v) for k,v in d.items() if k in items]
            return Bag(d)
            
        return Bag([('p_%s'%p.pid,bagFromProcess(p)) for p in ps.process_iter() if filteredProcess(p)])