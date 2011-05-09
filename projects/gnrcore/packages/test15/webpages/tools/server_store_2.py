# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-03-02.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return 'Test'
         
    def test_0_firsttest(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top').slotToolbar('*,dropbox,*,confirm')
        top.dropbox.div(height='30px',width='100px',border='1px solid green',
                                        rounded=10,onDrop_webpage='SET .remote_page_id=data; FIRE .getRemotePageData;',dropTarget=True)
        top.confirm.button('Apply Changes',fire='.applyOnRemote')
        bc.dataRpc('.remote_page.data','getRemotePageData',p_id='=.remote_page_id',
                    onResult='FIRE .rebuild_tree',_fired='^.getRemotePageData')
       #bc.dataController('console.log("edititedData",edititedData)',edititedData='=.bagNodeEditor.data',_fired='^.applyOnRemote',
       #           currpath='=.currpath',p_id='=.remote_page_id',_onResult='FIRE .getRemotePageData;')
       #
        bc.dataRpc('.dummy','applyOnRemote',_fired='^.applyOnRemote',_editedData='=.bagNodeEditor.data',
                    editedData='==_editedData.deepCopy();',
                    currpath='=.currpath',p_id='=.remote_page_id',_onResult='FIRE .getRemotePageData;')
        
        left = bc.contentPane(region='left',width='200px').tree(storepath='.remote_page',selectedPath='.currpath',_fired='^.rebuild_tree',nodeId='remote_page_tree')
        center = bc.contentPane(region='center').BagNodeEditor(nodeId='remote_page_tree_editbagbox',
                                                                datapath='.bagNodeEditor',bagpath='.remote_page')
    def rpc_getRemotePageData(self,p_id=None,**kwargs):
        store = self.pageStore(p_id)
        return store.getItem(None)
        
    def rpc_applyOnRemote(self,p_id=None,editedData=None,currpath=None,**kwargs):
        currpath = currpath.replace('data.','')
        with self.pageStore(p_id) as store:
            for row in editedData.values():
                if row['attr_name'] == '*value':
                    store.setItem(currpath,row['attr_value'])
