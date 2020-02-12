# -*- coding: utf-8 -*-

# serverpath.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Serverpath"""
from gnr.core.gnrbag import DirectoryResolver
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    auto_polling = 10
    user_polling = 3

    def test_0_tree(self, pane):
        pane.dataRemote('.store',self.relationExplorer,table='glbl.provincia',currRecordPath='record')
        pane.tree('.store',hideValues=True)
    
    
    def test_1_checkboxtree(self,pane,**kwargs):
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
                      #checked_abs_path='.checked_abspath:\n',
                      labelAttribute='nodecaption')

    def test_2_treegrid(self,pane):
        resolver= DirectoryResolver('/users')
        pane.data('.root.genropy',resolver())
        box=pane.div(height='400px',margin='60px',border='1px solid silver',position='relative')
        tg = box.treeGrid(storepath='.root.genropy',headers=True)
        tg.column('nodecaption',header='Name')
       #tg.column('rel_path',dtype='T',header='Rel Path',size=150)
       #tg.column('mtime',dtype='DH',header='mtime',size=100,format='short')
       #tg.column('atime',dtype='DH',header='atime',size=100,format='short')
       #tg.column('ctime',dtype='DH',header='ctime',size=100,format='short')
       #tg.column('size',dtype='L',header='size',size=100,format='bytes')

    def test_29_treegrid(self,pane):
        resolver= DirectoryResolver('/users')
        pane.data('.root.genropy',resolver())
        box=pane.div(height='400px',margin='60px',border='1px solid silver',position='relative')
        box.tree(storepath='.root.genropy',_class='branchtree noIcon')
        #tg.column('nodecaption',header='Name')
  

    def test_3_tree_searchOn(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
    
        pane.div(height='400px').tree(storepath='.tree',_class="branchtree noIcon",hideValues=True,autoCollapse=True,
                    height='200px',
                    width='300px',
                    border='1px solid #efefef',
                    searchOn=True
                    )
        
    def test_4_tree_popup(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
    
        pane.div(height='20px',width='20px',
                    background='green',margin='20px'
                    ).tree(storepath='.tree',popup=dict(closeEvent='onClick'))

    def test_5_tree_searchOn(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
        pane.div(height='20px',width='20px',
                    background='green',margin='20px'
                    ).tree(storepath='.tree',popup=True,searchOn=True)

