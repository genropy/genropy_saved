# -*- coding: utf-8 -*-

# autocast.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

import datetime
from gnr.core.gnrdecorator import public_method,autocast
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """autocast test"""
        fb = pane.formbuilder(datapath='test1')

        fb.textbox('^.a', lbl='Type an integer')
        fb.textbox('^.b', lbl='Type a date YYYY-MM-DD')
        fb.textbox('^.c', lbl='Type a decimal')
        pane.button('Cast types', action='FIRE casting')
        fb.dataRpc('.result', self.getCastedTypes , a='=.a',b='=.b', c='=.c', _fired='^casting')
        pane.tree(storepath='test1.result')

    
    @public_method
    @autocast(a='L',b='D',c='N')
    def getCastedTypes(self, a=None, b=None,c=None):
        return Bag(dict(integer_p=a,date_p=b, decimal_p=c))
        
