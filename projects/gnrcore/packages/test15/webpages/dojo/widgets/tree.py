# -*- coding: UTF-8 -*-

# serverpath.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Serverpath"""
from gnr.core.gnrbag import Bag,DirectoryResolver
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    auto_polling = 10
    user_polling = 3

    def test_0_tree(self, pane):
        pane.dataRemote('.store',self.relationExplorer,table='glbl.provincia',currRecordPath='record')
        pane.tree('.store',hideValues=True)
    
    
    def test_6_checkboxtree(self,pane,**kwargs):
        bc=pane.borderContainer(height='500px')
        self.treePane(bc.contentPane(region='left',splitter=True,
                                     width='250px',padding='4px'))    
        center=bc.contentPane(region='center')
        right=bc.contentPane(region='right',width='300px',splitter=True)
        center.simpleTextArea(value='^.checked',font_size='.9em',height='100%')
        right.pre(value='^.checked_abspath',font_size='.9em',height='100%')
        
    def treePane(self,pane):
        resolver= DirectoryResolver('/')
        pane.data('.root.genropy',resolver())
        pane.tree(storepath='.root',hideValues=True,autoCollapse=True,
                      checkChildren=True,checkedPaths='.checked',checkedPaths_joiner='\n',
                      checked_abs_path='.checked_abspath:\n',
                      labelAttribute='nodecaption')

    
