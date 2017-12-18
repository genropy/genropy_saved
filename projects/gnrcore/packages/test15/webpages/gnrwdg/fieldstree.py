# -*- coding: UTF-8 -*-

# gnrlayout.py
# Created by Francesco Porcari on 2011-01-27.
# Copyright (c) 2011 Softwell. All rights reserved.


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def windowTitle(self):
        return 'fieldstree'
         
    def test_0_base(self,pane):
        bc = pane.borderContainer(height='400px',width='800px')
        top = bc.contentPane(region='top',height='50px')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.filteringSelect(value='^.table',values='adm.user,adm.htag')
        fb.data('.table','adm.user')
        center = bc.contentPane(region='center')
        center.dataRpc('.tree.currentData', self.relationExplorer, 
                            table='^.table', dosort=False)
        tree = center.treeGrid(storepath='.tree.currentData', 
                    #onDrag=self.onDrag(),
                    draggable=True,
                    checked_fieldpath='.zzz',
                    dragClass='draggedItem',headers=True)
        tree.column('fieldpath',header='Field',size=400) 
        tree.column('dtype',size=60,header='Dtype')
        tree.column('caption',header='Caption',size=200)
