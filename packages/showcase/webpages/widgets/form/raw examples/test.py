#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    
    
    
################### ??? Non va il debugger!! Cos'è?
    
    
    
    def main(self, root, **kwargs):
        box = root.div(datapath='myform')
        box.textbox(value='^.data')
        self.debugger('py',ggg='uiuiuiui')
        box.data('.data','antonio')
        box.textbox(value='^.data?color')
        box.button('click me!',_fired='^bah')
        self.debugger('py',yyyyy='weerftghjgfds')
        box.dataRpc('dummy','test',_fired='^bah')
        
    def rpc_test(self,**kwargs):
        self.debugger('py')  