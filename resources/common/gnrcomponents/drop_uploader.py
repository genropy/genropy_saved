# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
import os

class DropUploader(BaseComponent):  
    py_requires='foundation/includedview'  
    def dropUploader(self,pane,ext='',**kwargs):
        pane.div(drop_types='Files',drop_ext=ext,
                 drop_action="""console.log(files);drop_uploader.send_files(files)""",
                 width='100px',height='50px',background_color='#c7ff9a')


    


    def dropFileGrid(self,pane,uploaderId=None,datapath=None,
                      label=None,footer=None,enabled=True,onResult=None,uploadPath=None,
                      preview=False,**kwargs):
        uploadPath = uploadPath or 'site:uploaded_files'
        metacol_dict = dictExtract(kwargs,'metacol_')
        external_dict = dictExtract(kwargs,'external_')
        def _struct(struct):
            r = struct.view().rows()
            r.cell('_name', name='File name', width='10em')
            r.cell('_size', name='Size', width='5em')
            r.cell('_type', name='Type', width='5em')
            for k,v in metacol_dict.items():
                r.cell(k,**v)
            r.cell('_status', name='Status', width='6em')
        bc = pane.borderContainer()
        if preview:
            previewpane = bc.contentPane(region='bottom',height='50%',splitter=True)
            previewpane.img(height='100%',width='100%',src='^.preview_img',datapath=datapath)
            previewpane.dataController("""
                                        var selectedFile = filebag.getItem(selectedLabel+'._file');
                                        console.log(selectedFile);
                                        var fileReader = new FileReader();
                                        var that = this;
                                        fileReader.addEventListener("loadend", function(){
                                            that.setRelativeData('.preview_img',fileReader.result);
                                        }, false);
                                        fileReader.readAsDataURL(selectedFile);
                                    """,selectedLabel="^.selectedLabel",filebag='=.uploaded_files',
                                        datapath=datapath)
        iv = self.includedViewBox(bc.borderContainer(region='center'),label=label,datapath=datapath,
                            storepath='.uploaded_files',nodeId=uploaderId,
                            struct=_struct,datamode='bag',
                            footer=footer,del_action=True,del_enabled=enabled,
                            editorEnabled=enabled,autoWidth=True,
                            box_drop_action="FIRE .prepare_files=files;",
                            box_drop_types='Files')
        gridEditor = iv.gridEditor()
        for k,v in metacol_dict.items():
            _tag='textbox'
            dtype = v.get('dtype')
            widget = v.get('widget')
            if widget:
                _tag=widget
            elif dtype:
                if(dtype=='I' or dtype=='R' or dtype=='N'):
                    _tag='numberTextBox'
                elif(dtype=='D'):
                    _tag='dateTextBox'
                elif(dtype=='B'):
                    _tag='checkbox'            
            gridEditor.child(_tag,gridcell=k)
        bc.dataController("""
                dojo.forEach(files,
                            function(f){
                                var row = objectUpdate({_name:f.name,_size:f.size,_type:f.type,_file:f,_uploaderId:uploaderId},external_params);
                                var label = (f.name+'_'+f.size+'_'+f.type).replace(/\W/g,'_');
                                if(filebag.index(label)<0){
                                    filebag.setItem(label,new gnr.GnrBag(row));
                                }
                            });
                """,filebag="=.uploaded_files",files='^.prepare_files',datapath=datapath,
                    external_params=external_dict,uploaderId=uploaderId)
        bc.dataController("""
                            genro.rpc.uploadMultipartFiles(filebag,{onResult:onResult,uploadPath:uploadPath,uploaderId:uploaderId});
                            """,filebag='=.uploaded_files',datapath=datapath,
                            uploaderId=uploaderId,onResult=onResult or '',uploadPath=uploadPath,
                            **{'subscribe_%s_upload' %uploaderId:True})
                                
