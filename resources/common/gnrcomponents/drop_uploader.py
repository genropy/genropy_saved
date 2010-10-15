# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdict import dictExtract

class DropUploader(BaseComponent):  
    py_requires='foundation/includedview'  
    def dropUploader(self,pane,ext='',**kwargs):
        pane.div(drop_types='Files',drop_ext=ext,
                 drop_action="""console.log(files);drop_uploader.send_files(files)""",
                 width='100px',height='50px',background_color='#c7ff9a')

    def dropFileGrid(self,pane,uploaderId=None,datapath=None,
                      label=None,footer=None,enabled=True,onResult=None,
                      onFileUploaded=None,uploadPath=None,
                      preview=False,uploadedFilesGrid=False,**kwargs):
        uploadPath = uploadPath or 'site:uploaded_files'
        metacol_dict = dictExtract(kwargs,'metacol_')
        external_dict = dictExtract(kwargs,'external_')
        def _struct(struct):
            r = struct.view().rows()
            r.cell('_name', name='!!File name', width='10em')
            r.cell('_size', name='!!Size', width='5em')
            r.cell('_type', name='!!Type', width='5em')
            for k,v in metacol_dict.items():
                r.cell(k,**v)
            r.cell('_status', name='Status', width='6em')
        bc = pane.borderContainer(height='100%')
        if preview:
            self._dropFileGrid_preview(bc,datapath=datapath)
        if uploadedFilesGrid and False:
            onFileUploaded = """
                               var uploaded_data = GET .uploaded_data;
                               uploaded_data = uploaded_data || new gnr.GnrBag();
                               console.log(node);
                               console.log(result);
                               uploaded_data.setItem(node.label,node.getValue());
                               """ 
            self._dropFileGrid_uploadedFilesGrid(bc,datapath,uploaderId,uploadPath=uploadPath,metacol_dict=metacol_dict)
        iv = self.includedViewBox(bc.borderContainer(region='center'),label=label,datapath=datapath,
                            storepath='.uploading_data',nodeId=uploaderId,
                            struct=_struct,datamode='bag',
                            footer=footer,del_action=True,del_enabled=enabled,
                            editorEnabled=enabled,autoWidth=True,
                            box_drop_action="FIRE .prepare_files=files;FIRE .on_drop = 1000;",
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
        bc.dataController("""genro.wdgById(gridId).editBagRow(null,fired);""",fired='^.on_drop',
                            gridId=uploaderId,datapath=datapath)
        bc.dataController("""
                dojo.forEach(files,
                            function(f){
                                var row = objectUpdate({_name:f.name,_size:f.size,_type:f.type,_file:f,_uploaderId:uploaderId},external_params);
                                var label = (f.name+'_'+f.size+'_'+f.type).replace(/\W/g,'_');
                                if(filebag.index(label)<0){
                                    filebag.setItem(label,new gnr.GnrBag(row));
                                }
                            });
                """,filebag="=.uploading_data",files='^.prepare_files',datapath=datapath,
                    external_params=external_dict,uploaderId=uploaderId)
        bc.dataController("""
                            genro.rpc.uploadMultipartFiles(filebag,{onResult:funcCreate(onResult,'result',this),
                                                                    onFileUploaded:funcCreate(onFileUploaded,'node',this),
                                                                    uploadPath:uploadPath,uploaderId:uploaderId});
                            """,filebag='=.uploading_data',datapath=datapath,
                            uploaderId=uploaderId,onResult=onResult or '',onFileUploaded=onFileUploaded or '',uploadPath=uploadPath,
                            **{'subscribe_%s_upload' %uploaderId:True})
    
    def _dropFileGrid_preview(self,bc,datapath):
        sc = bc.stackContainer(region='bottom',height='50%',splitter=True,selectedPage='^.selpreview',datapath=datapath)
        sc.dataController("""var selectedType = filebag.getItem(selectedLabel+'._type');
                             var selectedFile = filebag.getItem(selectedLabel+'._file');
                             console.log(selectedFile);
                             var readFunc;
                             if (selectedType.indexOf('image')>=0){
                                 SET .selpreview='image'
                                 readFunc = 'readAsDataURL';
                             }else if(selectedType.indexOf('text')>=0){
                                 SET .selpreview  = 'text';
                                 readFunc = 'readAsText';
                             }else{
                                  SET .selpreview  = 'no_prev';
                                  return;
                             }
                             var fileReader = new FileReader();
                             var that = this;
                             fileReader.addEventListener("loadend", function(){
                                 that.fireEvent('.reader_result',fileReader.result);
                             }, false);
                             fileReader[readFunc](selectedFile);
                        """,selectedLabel="^.selectedLabel",filebag='=.uploading_data',
                        _if='selectedLabel',_else='SET .selpreview  = "no_prev";')
        sc.dataController("""if(selpreview=='image'){
                                SET .preview_img = reader_result;
                                SET .preview_txt=null;
                            }else{
                                SET .preview_txt = reader_result;
                                SET .preview_img = null;
                            }
                           """,reader_result='^.reader_result',selpreview='=.selpreview')
        sc.contentPane(pageName='no_prev').div('no-preview')
        sc.contentPane(pageName='image',overflow='hidden').img(height='100%',src='^.preview_img')
        sc.contentPane(pageName='text').div(innerHTML='^.preview_txt')       
    
    def _dropFileGrid_uploadedFilesGrid(self,bc,datapath,uploaderId,uploadPath=None,metacol_dict=None):
        def _struct(struct):
            r = struct.view().rows()
            r.cell('_name', name='!!File name', width='10em')
            r.cell('_size', name='!!Size', width='5em')
            r.cell('_type', name='!!Type', width='5em')
            for k,v in metacol_dict.items():
                r.cell(k,**v)
        self.includedViewBox(bc.borderContainer(region='right',width='50%',splitter=True),
                            label='!!Uploaded elements',
                            datapath=datapath,storepath='.uploaded_data',
                            nodeId='%s_uploaded_grid' %uploaderId,
                            struct=_struct,datamode='bag',autoWidth=True)
        
