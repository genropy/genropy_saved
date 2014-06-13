#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrbag import Bag

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
            for c in columns:
                row.setItem(c,getattr(core,c))
            row['core']=k+1
            result.setItem('r_%i'%k,row)
        return result