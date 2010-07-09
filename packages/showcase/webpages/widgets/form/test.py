#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" Buttons """
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):   
    def main(self, root, **kwargs):
        box = root.div(datapath='pluto')
        box.textbox(value='^.pippo')
        self.debugger('py',ggg='uiuiuiui')
        box.data('.pippo','antonio')
        box.textbox(value='^.pippo?color')
        box.button('sss',fire='xx')
        self.debugger('py',yyyyy='weerftghjgfds')
        box.dataRpc('dummy','test',_fired='^xx')
        
    def rpc_test(self,**kwargs):
        self.debugger('py')  