#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('values.sport',self.sports(),id='.pkey',caption='.Description')
        
        fb = root.formbuilder(cols=2)
        fb.combobox(lbl='loaded from Bag',value='^record.sport',storepath='values.sport',
                    hasDownArrow=True,ignoreCase=True)
        # default parameter of combobox:
                    # hasDownArrow=True --> create the selection arrow
                    # ignoreCase=True   --> user can write ignoring the case
                    
        fb.combobox(lbl='loaded from values', values='Football, Golf, Karate')
        
    def sports(self,**kwargs):
        mytable=Bag()
        mytable['r1.pkey'] = 'SC'
        mytable['r1.Description'] = 'Soccer'
        mytable['r2.pkey'] = 'BK'
        mytable['r2.Description'] = 'Basket'
        mytable['r3.pkey'] = 'TE'
        mytable['r3.Description'] = 'Tennis'
        mytable['r4.pkey'] = 'HK'
        mytable['r4.Description'] = 'Hockey'
        mytable['r5.pkey'] = 'BB'
        mytable['r5.Description'] = 'Baseball'
        mytable['r6.pkey'] = 'SB'
        mytable['r6.Description'] = 'Snowboard'
        return mytable