#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    
    def main(self, root, **kwargs):        
        root.data('values.sport',self.sports(),id='.pkey', caption='.Description')

        tbl=root.table()
        r=tbl.tr()
        r.td('Sport')
        r.td().checkbox(value='^choose')
        r.dataController("SET dynamic = 'values.sport'",chooser="^choose",
                        _if='chooser',_else="SET dynamic = 'values.other'", _onstart='^gnr.onStart')
        
        r.td(datapath='values').combobox(lbl='Sport', value = '^record.sport',
                        storepath='.sport',ignoreCase=True)
        r.td('dynamic')
        r.td().combobox(lbl='Sport', value = '^aaaa',
                        storepath='dynamic',ignoreCase=True)
                        
        r.td().div('loaded from values')
        r.td().combobox(lbl='Sport', values='Soccer,Baseball,Hockey')
    
    def sports(self,**kwargs):
        mytable=Bag()
        mytable.setItem('r1.pkey','SC')
        mytable.setItem('r1.Description','Soccer')
        mytable.setItem('r2.pkey','BK')
        mytable.setItem('r2.Description','Basket')
        mytable.setItem('r3.pkey','TE')
        mytable.setItem('r3.Description','Tennis')
        mytable.setItem('r4.pkey','HK')
        mytable.setItem('r4.Description','Hockey')
        mytable.setItem('r5.pkey','BB')
        mytable.setItem('r5.Description','Baseball')
        mytable.setItem('r6.pkey','SB')
        mytable.setItem('r6.Description','Snowboard')
        return mytable
        
    

 
        
