# -*- coding: utf-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

import os

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.lib.services.storage import StorageResolver

from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method


class StorageTree(BaseComponent):
    @extract_kwargs(tree=True,preview=True,store=True)
    @struct_method
    def st_storageTreeFrame(self,pane,frameCode=None,datapath=None,storagepath=None,title=None,tree_kwargs=None,
                            preview_kwargs=None,store_kwargs=None,**kwargs):
        frame = pane.framePane(frameCode=frameCode,datapath=datapath,_workspace=True,**kwargs)
        bar = frame.top.slotToolbar('2,vtitle,*,mkdir,downloadSelected,2')
        bar.vtitle.div(title or  'Storage',font_weight='bold',color='#666')
        tree_kw = dict(selectedLabelClass='selectedTreeNode',hideValues=True,
                        storepath='#WORKSPACE.store',nodeId='%s_tree' %frameCode,
                        selected_internal_url='#WORKSPACE.selected_url',
                        selected_abs_path='#WORKSPACE.selected_abs_path',
                        selected_file_ext='#WORKSPACE.selected_file_ext',
                        onDrag_storageNode=self.st_storageNode_onDrag(),
                      headers=True,draggable=True,
                      dragClass='draggedItem',
                      _moveMethod=self.st_moveStorageNode,

                      dropTypes='storageNode,Files',
                      onDrop="""
                      if(_kwargs.files){
                            var that = this;
                            var kw = {uploadPath:dropInfo.treeItem.attr.abs_path,
                                    onProgress:function(e){console.log('onProgress',e)},
                                    onResult:function(e){that.fireEvent('#WORKSPACE.reload_store',true);}
                                    }
                            var sendKw,sendParams;
                            dojo.forEach(files,function(file){
                                sendKw = objectUpdate({filename:file.name},kw);
                                sendParams = {mimetype:file.type};
                                genro.rpc.uploadMultipart_oneFile(file, sendParams, sendKw);
                            });
                      }
                      """,
                      onDrop_storageNode="""
                            if(dropInfo.treeItem.attr.file_ext!='directory'){
                                return false;
                            }else{
                                var that = this;
                                genro.serverCall(this.attr._moveMethod,{targetpath:data,
                                                                        destpath:dropInfo.treeItem.attr.abs_path},
                                                 function(){
                                                     that.fireEvent('#WORKSPACE.reload_store',true);
                                                 });
                            }
                     """,dropTargetCb="""
                     if(dropInfo.treeItem.attr.file_ext!='directory'){
                         return false;
                     }
                     return true;
                     """)
        tree_kw.update(tree_kwargs)
        bar.mkdir.slotButton('Make dir',disabled='^#WORKSPACE.selected_file_ext?=#v!="directory"',
                            action='FIRE #WORKSPACE.make_dir = dirname',
                            ask=dict(title='New directory',fields=[dict(name='dirname',lbl='Dirname')]))
        bar.downloadSelected.slotButton('Download selected file',disabled='^#WORKSPACE.selected_file_ext?=!#v || #v=="directory"',
                            action='genro.download(sel_url)',
                            sel_url='=%(selected_internal_url)s' %tree_kw)
        bc = frame.center.borderContainer()
        
        treebox = bc.contentPane(region='center').div(position='absolute',top='2px',left='2px',right='2px',bottom='2px',overflow='auto')

        treebox.tree(**tree_kw)
        bar = frame.bottom.slotBar('5,urlbox,*',_class='slotbar_dialog_footer',height='23px')
        bar.urlbox.div(_class='selectable').div('^%(selected_internal_url)s' %tree_kw)
        if preview_kwargs:
            preview_kwargs.setdefault('closable','close')
            preview_pane = bc.contentPane(overflow='hidden',**preview_kwargs)
            preview_pane.htmliframe(src='^%(selected_internal_url)s' %tree_kw,height='100%',width='100%',border=0)

        store_kwargs['_reloader'] = '^#WORKSPACE.reload_store'
        bc.dataRpc('%(storepath)s' %tree_kw,self.st_getStorageRes,
                    storagepath=storagepath,_if='storagepath',
                    _else='return new gnr.GnrBag();',**store_kwargs)
        bc.dataRpc(None,self.st_newStorageDir,
                    storage_node='=#WORKSPACE.selected_abs_path',
                    dirname='^#WORKSPACE.make_dir',_onResult="FIRE #WORKSPACE.reload_store;")
        return frame
    
    @public_method
    def st_newStorageDir(self,dirname=None,storage_node=None,**kwargs):
        self.site.storageNode(storage_node).mkdir(dirname)
     
    @public_method
    def st_moveStorageNode(self,targetpath=None,destpath=None,**kwargs):
        filename = os.path.basename(targetpath)
        self.site.storageNode(targetpath).move(self.site.storageNode(destpath,filename))


    @public_method
    def st_getStorageRes(self,storagepath=None):
        result = Bag()
        result.setItem('root',StorageResolver(storagepath,cacheTime=2,
                                                dropext=True,readOnly=False, _page=self)())
        return result


    def st_storageNode_onDrag(self):
        return """var children=treeItem.getValue('static');
                  if(children){
                      return
                  }
                  dragValues['storageNode'] = treeItem.attr.abs_path;
                  console.log('dragValues',dragValues)

               """