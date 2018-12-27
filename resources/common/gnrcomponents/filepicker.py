# -*- coding: utf-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
import os


class FilePicker(BaseComponent):
    py_requires = "gnrcomponents/framegrid:FrameGrid"
    @struct_method
    def fp_imgPickerPalette(self,parent,folders=None,drop_folder=None,code=None,title=None,include=None,width=None,externalSnapshot=False,**kwargs):
        code = code or self.getUuid()
        drop_folder = drop_folder or folders
        pane = parent.palettePane(paletteCode='imgPalette_%s' %code,title=title or 'Images',
                                width= width or '500px',**kwargs)

        bc = pane.borderContainer()
        view = bc.contentPane(region='center').frameGrid(frameCode='mgGrid_%s' %code,struct=self._fp_img_grid_struct,
                                    gridEditorPars=False,
                                    autoToolbar=False,
                                    grid_selected_fileurl='.selected_url',
                                    datapath='.view')
        parent.dataController("""
            var folder_list = folders.split(',');
            if(folder_list.length>1){

                var r = folder_list[0].split(':');
                r.pop();
                view.setRelativeData('.currentFolder',r.join(':'));
                view.setRelativeData('.folderValues',folders);
            }else{
                view.setRelativeData('.currentFolder',folder_list[0]);
                view.setRelativeData('.folderValues',null);
            }

            """,folders=folders,view=view,_onStart=True,_if='folders')
        view.grid.attributes.update(dropTarget_grid='Files' ,
                                        onDrop="""
                                        var drop_folder = this.getAttributeFromDatasource('_uploader_drop_folder');
                                        if(drop_folder=='*ask*'){
                                            genro.dlg.alert('Warning','Not implemented')
                                            return
                                        }
                                        var sourceNode = this;
                                        var params = {onUploadingMethod:this.getAttributeFromDatasource('_uploader_onUploadingMethod'),
                                                     drop_folder:drop_folder}
                                        var kw = {uploaderId:'pmg_uploader',
                                            onProgress:function(e){console.log('onProgress',e)},
                                            onResult:function(e){
                                                sourceNode.publish('importstatus',{importing:false});
                                            }
                                        }
                                        var sendKw,sendParams;
                                        dojo.forEach(files,function(file){
                                            sendKw = objectUpdate({filename:file.name},kw);
                                            sendParams = objectUpdate({mimetype:file.type},params);

                                            sourceNode.publish('importstatus',{importing:true});
                                            sendParams.importerGrid = sourceNode.attr.nodeId;
                                            genro.rpc.uploadMultipart_oneFile(file, sendParams, sendKw);
                                        });
                                        """,
                                        selfsubscribe_importstatus="""
                                            var importing = $1.importing;
                                            var store = this.widget.collectionStore();
                                            store.freezed = importing;
                                            genro.lockScreen(importing,this);
                                            if(!importing){
                                                store.loadData();
                                            }
                                        """,
                                        _uploader_drop_folder='=.#parent.currentFolder',
                                        dropTypes='Files',_uploader_onUploadingMethod=self._fp_pimg_uploadImage)

        bar = view.top.slotToolbar('5,multiFolder,*,snapShot,5,delrow,5,searchOn,5')
        bar.snapShot.slotButton('"Snapshot',iconClass='iconbox photo',
                                action="""FIRE .takeSnapshot;""",uploadPath='=.currentFolder')
        view.dataController("""
                        var that = this;
                        this.getParentWidget('floatingPane').hide();
                        if(externalSnapshot){
                            var fm = genro.getParentGenro().framedIndexManager;
                            fm.callOnCurrentIframe('dev','takePicture',[uploadPath,function(){
                                    that.getParentWidget('floatingPane').show()
                                    that.fireEvent('.reloadStore',true);
                            }]);
                        }else{
                            genro.dev.takePicture(uploadPath,function(){
                                    that.getParentWidget('floatingPane').show()
                                    that.fireEvent('.reloadStore',true);
                            });
                        }
            """,uploadPath='=.currentFolder',_fired='^.takeSnapshot',externalSnapshot=externalSnapshot)
        bar.multiFolder.multiButton(value='^.currentFolder',values='^.folderValues')
        view.data('.grid.sorted','created_ts:d')

        view.grid.tooltip(callback="""
                    var r = n;
                    while(!r || r.gridRowIndex==null){
                        r = r.parentElement;
                    }
                    var grid = dijit.getEnclosingWidget(n).grid;
                    var row = grid.rowByIndex(r.gridRowIndex);
                    var tpl = "<img src='$fileurl' style='max-height:300px'></img>";
                    var result = dataTemplate(tpl,row);
                    return result;
                """,modifiers='Ctrl',validclass='dojoxGrid-cell,cellContent')

        view.grid.fsStore(childname='store',
                                    folders='^.currentFolder',
                                    _fired='^.reloadStore',
                                    include= include or '*.jpg,*.png,*.gif',
                                    _if='folders',_else='this.store.clear();',
                                    applymethod=self._fp_checkFileImg,
                                    apply_currentFolder='=.currentFolder',
                                    sortedBy='^.grid.sorted')
        bc.contentPane(region='bottom',height='50%',closable='close',overflow='hidden',
                        border_top='1px solid silver',splitter=True).iframe(src='^.view.grid.selected_url',height='100%',width='100%',border=0)
        return pane

    def _fp_img_grid_struct(self,struct=None):
        r = struct.view().rows()
        r.cell('img_element',width='20em',name='!!Image')
        r.cell('file_name',width='15em',name='!!Title')
        r.cell('created_ts',width='7em',name='!!Created')
        r.cell('size',width='6em',name='!!Size')

    @public_method
    def _fp_pimg_uploadImage(self,kwargs):
        kwargs['uploadPath'] = self.site.getStaticPath(kwargs['drop_folder'],kwargs['filename'],autocreate=-1)

        

    @public_method
    def _fp_checkFileImg(self,filesbag,currentFolder=None,**kwargs):
        urlprefix = self.site.getStaticUrl(currentFolder)
        for n in filesbag:
            n.attr['fileurl'] = '/'.join([urlprefix,n.attr['rel_path']])
            n.attr['img_element'] = '<img src="%s" style="height:40px;"></img>' %n.attr['fileurl']

       