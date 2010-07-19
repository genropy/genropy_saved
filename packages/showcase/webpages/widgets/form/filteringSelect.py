#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('bag',self.sports(),id='.pkey',caption='.Description')
        bc = root.borderContainer(datapath='record.sport',padding='1em')
        fb = bc.formbuilder(cols=6)
        fb.div('------ Sport ------',colspan=6)
        fb.div('loaded from bag')
        fb.filteringSelect(value='^.bag_values',storepath='bag',ignoreCase=True,colspan=2)
        fb.div('loaded from values')
        fb.filteringSelect(value='^.loaded_values',colspan=2,
                           values='SC:Soccer,BK:Basket,HK:Hockey,TE:Tennis,BB:Baseball,SB:Snowboard')
        
    def sports(self,**kwargs):
        mytable=Bag()
        mytable['r1.pkey']='SC'
        mytable['r1.Description']='Soccer'
        mytable['r2.pkey']='BK'
        mytable['r2.Description']='Basket'
        mytable['r3.pkey']='TE'
        mytable['r3.Description']='Tennis'
        mytable['r4.pkey']='HK'
        mytable['r4.Description']='Hockey'
        mytable['r5.pkey']='BB'
        mytable['r5.Description']='Baseball'
        mytable['r6.pkey']='SB'
        mytable['r6.Description']='Snowboard'
        return mytable