#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from past.builtins import basestring
from gnr.lib.services import GnrBaseService
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import splitAndStrip
from datetime import datetime
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
            d['create_time']=datetime.fromtimestamp(d['create_time'])
            d['cpu_percent']=d['cpu_percent'] or 0
            d['memory_percent']=d['memory_percent'] or 0
            
            if items:
                d = [(k,d[k]) for k in items if k in d]
            return Bag(d)
            
        return Bag([('p_%s'%p.pid,bagFromProcess(p)) for p in ps.process_iter() if filteredProcess(p)])