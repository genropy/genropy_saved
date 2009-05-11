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
from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.script("var ccc=0")
        split=root.splitContainer(height='100%')
        tree=split.contentPane(sizeShare='30',background_color='smoke').tree(storepath='*D',gnrId='mydataTree',
                                             inspect='shift',label="data")
        fb=split.contentPane(sizeShare='70').formbuilder(cols=2,lblpos='T')
        fb.button('Prepara',action="genro.setData('test',new genro.rpc.RemoteResolver({method:'test',name:'piero'}))")
        fb.button('test sync',action="""function(){var dn=genro.getDataNode('test');
                                                   console.log(dn.getValue_new())}""")
        
        fb.button('test async',action="""function(){ccc=ccc+1;var dn=genro.getDataNode('test');
                                                       dn.doWithValue(function(r){
                                                       console.log('callback:'+r[0]+' - '+r[1]+'    ('+r[2]+')')
                                                       },
                                                       {name:'pierino_'+ccc})
                                                       }""")
def rpc_test(req, name='',**kwargs):     
    b=Bag()
    b['name']=name
    b['test']='test'+name
    return b       
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
