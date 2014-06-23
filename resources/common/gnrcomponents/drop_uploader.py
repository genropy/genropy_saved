# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebstruct import struct_method
import os

class DropUploaderBase(BaseComponent):
    @struct_method
    def du_slotbar_doupload(self,pane,**kwargs):
        return pane.slotButton(label='!!Upload',publish='doupload',iconClass='iconbox inbox')
    
    @extract_kwargs(uploader=None,external=None)
    @struct_method
    def du_dropUploader(self, pane,uploaderId=None, ext='', uploader_kwargs=None, external_kwargs=None, **kwargs):
        uploaderId = uploaderId or 'stdupload'
        uploadPath = uploader_kwargs.pop('path', 'site:uploaded_files')
        pane.div(dropTypes='Files', drop_ext=ext, dropTarget=True, nodeId=uploaderId,
                 #onDrop="""console.log(files);drop_uploader.send_files(files)""",
                 onDrop="FIRE .prepare_files=files;",
                 width='100px', height='100px', _class="document_empty_64",
                 style="""border: 2px dashed #989898;border-radius: 3px;""")
        pane.data('.uploading_data', Bag())
        pane.dataController("""
                dojo.forEach(files,
                            function(f){
                                var row = objectUpdate({_name:f.name,_size:f.size,_type:f.type,_file:f,_uploaderId:uploaderId},external_params);
                                var label = (f.name+'_'+f.size+'_'+f.type).replace(/\W/g,'_');
                                if(filebag.index(label)<0){
                                    var r = new gnr.GnrBag(row);
                                    filebag.setItem(label,r);
                                }
                            });
                FIRE .doupload;
                """, filebag="=.uploading_data", files='^.prepare_files',
                          external_params=external_kwargs, uploaderId=uploaderId)
        pane.dataController("""
                            genro.rpc.uploadMultipartFiles(filebag,{onResult:funcCreate(onResult,'result',this),
                                                                    onFileUploaded:funcCreate(onFileUploaded,'node',this),
                                                                    uploadPath:uploadPath,uploaderId:uploaderId});
                            """, filebag='=.uploading_data', 
                          uploaderId=uploaderId, onResult=uploader_kwargs.get('onResult',''), 
                          onFileUploaded=uploader_kwargs.get('onUploaded',''),
                          uploadPath=uploadPath,_fired='^.doupload')

    @extract_kwargs(uploader=None,metacol=None,external=None,process=dict(slice_prefix=False))
    @struct_method
    def du_dropFileFrame(self,pane,uploaderId=None,label=None,datapath=None,preview=None,
                        uploader_kwargs=None,metacol_kwargs=None,process_kwargs=None,
                        external_kwargs=None,**kwargs):
        uploaderId = uploaderId or 'stdupload'
        datapath=datapath or 'gnr.%s' %uploaderId
        frame = pane.framePane(frameCode=uploaderId,datapath=datapath,**kwargs)
        self.__uploader_grid(frame,uploaderId=uploaderId,preview=preview,uploader_kwargs=uploader_kwargs,
                            metacol_kwargs=metacol_kwargs,process_kwargs=process_kwargs,
                            external_kwargs=external_kwargs,label=label)
        return frame
        
    def __uploader_grid(self,frame,uploaderId=None,preview=None,label=None,
                        uploader_kwargs=None,metacol_kwargs=None,process_kwargs=None,
                        external_kwargs=None):
        uploadPath = uploader_kwargs.pop('path', 'site:uploaded_files')
        external_kwargs.update(process_kwargs)
        bar = frame.top.slotToolbar(slots='3,framelabel,*,delrow,doupload,3',delrow_disabled=False)
        bar.framelabel.div(label or '!!Uploader')
        def _struct(struct):
            r = struct.view().rows()
            r.cell('_name', name='!!File name', width='10em')
            r.cell('_size', name='!!Size', width='5em')
            r.cell('_type', name='!!Type', width='5em')
            for k, v in metacol_kwargs.items():
                r.cell(k, **v)
            r.cell('_status', name='Status', width='6em')

        if preview:
            footer = frame.bottom.slotBar('preview',closable='close',closable_tip='!!Preview',splitter=True)
            footer.preview.contentPane(height='200px',width='100%',_lazyBuild=True).previewPane(uploaderId=uploaderId)

        grid = frame.includedview(storepath='.uploading_data',struct=_struct,datamode='bag',datapath='.uploader',
                                 onDrop="FIRE .prepare_files=files;FIRE .on_drop = 1000;",
                                 selfsubscribe_delrow="this.widget.delBagRow('*', true);",
                                 selfsubscribe_doupload='FIRE .doupload;',selectedLabel='.selectedLabel',
                                 dropTarget_grid='Files',dropTarget=True,dropTypes='Files')
        gridEditor = grid.gridEditor()
        for k, v in metacol_kwargs.items():
            _tag = 'textbox'
            dtype = v.get('dtype')
            widget = v.get('widget')
            if widget:
                _tag = widget
            elif dtype:
                if(dtype == 'I' or dtype == 'R' or dtype == 'N'):
                    _tag = 'numberTextBox'
                elif(dtype == 'D'):
                    _tag = 'dateTextBox'
                elif(dtype == 'B'):
                    _tag = 'checkbox'
            gridEditor.child(_tag, gridcell=k)
        grid.dataController("""grid.editBagRow(null,fired);""", fired='^.on_drop',
                          grid=grid.js_widget)
        grid.dataController("""
                dojo.forEach(files,
                            function(f){
                                var row = objectUpdate({_name:f.name,_size:f.size,_type:f.type,_file:f,_uploaderId:uploaderId},external_params);
                                var label = (f.name+'_'+f.size+'_'+f.type).replace(/\W/g,'_');
                                if(filebag.index(label)<0){
                                    var r = new gnr.GnrBag(row);
                                    filebag.setItem(label,r);
                                }
                            });
                """, filebag="=.uploading_data", files='^.prepare_files',
                          external_params=external_kwargs, uploaderId=uploaderId)
        grid.dataController("""
                            genro.rpc.uploadMultipartFiles(filebag,{onResult:funcCreate(onResult,'result',this),
                                                                    onFileUploaded:funcCreate(onFileUploaded,'node',this),
                                                                    uploadPath:uploadPath,uploaderId:uploaderId});
                            """, filebag='=.uploading_data', 
                          uploaderId=uploaderId, onResult=uploader_kwargs.get('onResult',''), 
                          onFileUploaded=uploader_kwargs.get('onUploaded',''),
                          uploadPath=uploadPath,_fired='^.doupload')
        return grid
    
    @struct_method
    def du_previewPane(self, pane,uploaderId=None):
        sc = pane.stackContainer(selectedPage='^.selpreview',
                                datapath='#%s_grid' %uploaderId,margin='2px',_class='pbl_roundedGroup')
        sc.dataController("""
                           //if(dojo.isSafari){
                           //    console.log("no filereader, use Firefox")
                           //    return;
                           //}
                            var selectedType = filebag.getItem(selectedLabel+'._type');
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
                             fileReader.onloadend = function(evt) {
                                that.fireEvent('.reader_result',evt.target.result);
                             };
                             fileReader[readFunc](selectedFile);

                        """, selectedLabel="^.selectedLabel", filebag='=.uploading_data',
                          _if='selectedLabel', _else='SET .selpreview  = "no_prev";',_delay=1)
        sc.dataController("""if(selpreview=='image'){
                                SET .preview_img = reader_result;
                                SET .preview_txt=null;
                            }else{
                                SET .preview_txt = reader_result;
                                SET .preview_img = null;
                            }
                           """, reader_result='^.reader_result', selpreview='=.selpreview')
        sc.contentPane(pageName='no_prev').div('!!No preview available',font_size='15pt',height='50px',width='100%',text_align='center',position='absolute',
                                                top='50%',margin_top='-25px',color='#555')
        sc.contentPane(pageName='image', overflow='hidden').img(height='100%', src='^.preview_img')
        sc.contentPane(pageName='text').div(innerHTML='^.preview_txt')
        
    def fileaction_resize(self, file_path=None, file_url=None, file_ext=None, height=None, width=None, filetype=None,
                          action_name=None, dest_dir=None, **kwargs):
        from PIL import Image

        with open(file_path, 'rb') as image_file:
            try:
                original = Image.open(image_file)
            except:
                return dict()
            if original.mode != "RGB":
                original = original.convert("RGB")
            dir_path, filename = os.path.split(file_path)
            imagename, ext = os.path.splitext(filename)
            if dest_dir:
                dir_path = self.site.getStaticPath(dest_dir)
                dest_url = self.site.getStaticUrl(dest_dir)
            else:
                dir_path = os.path.join(dir_path, action_name)
                dest_url = "%s/%s" % (file_url.rpartition('/')[0], action_name)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                #landscape=original.size[0]>original.size[1]
            if height and width:
                imagename = '%s_h%i_w%i' % (imagename, height, width)
                original.resize(height, width)
            elif height or width:
                if height:
                    width = int(height * original.size[0] * 1.0 / original.size[1])
                    imagename = '%s_h%i' % (imagename, height)
                elif width:
                    height = int(width * original.size[1] * 1.0 / original.size[0])
                    imagename = '%s_w%i' % (imagename, width)
                dest_size = width, height
                print 'dest_size ', dest_size
                original.thumbnail(dest_size)
            filetype = filetype or ext[1:]
            image_filename = '%s.%s' % (imagename, filetype.lower())
            image_path = os.path.join(dir_path, image_filename)
            original.save(image_path)
            image_url = '%s/%s' % (dest_url, image_filename)
        return dict(file_url=image_url, file_path=image_path)
        
class DropUploader(DropUploaderBase):
    py_requires = 'foundation/includedview'
    def dropUploader(self, pane, ext='', **kwargs):
        pane.div(dropTypes='Files', drop_ext=ext,
                 onDrop="""console.log(files);drop_uploader.send_files(files)""",
                 width='100px', height='50px', background_color='#c7ff9a')
        
    def dropFileGrid(self, pane, uploaderId=None, datapath=None,
                     label=None, footer=None, enabled=True, onResult=None,
                     onFileUploaded=None, uploadPath=None,
                     preview=False, savedFilesGrid=None, **kwargs):
        bc = pane.borderContainer(height='100%', design='sidebar', datapath=datapath, nodeId=uploaderId)

        if savedFilesGrid:
            self.dropFileGrid_saved_files_grid(bc.borderContainer(region='right', width='50%', splitter=True),
                                               uploaderId=uploaderId, savedFilesGrid=savedFilesGrid)

        self.dropFileGrid_uploader_grid(bc.borderContainer(region='center'),
                                        uploaderId=uploaderId, label=label, footer=footer, preview=preview,
                                        enabled=enabled, onResult=onResult, onFileUploaded=onFileUploaded,
                                        uploadPath=uploadPath, **kwargs)

    def dropFileGrid_uploader_grid(self, bc, uploaderId=None,
                                   label=None, footer=None, enabled=True, onResult=None,
                                   onFileUploaded=None, uploadPath=None,
                                   preview=False, **kwargs):
        uploadPath = uploadPath or 'site:uploaded_files'
        metacol_dict = dictExtract(kwargs, 'metacol_')
        external_dict = dictExtract(kwargs, 'external_') or {}
        process_dict = dictExtract(kwargs, 'process_', slice_prefix=False) or {}
        external_dict.update(process_dict)
        datapath = '.uploader'
        gridId = '%s_uploader' % uploaderId

        def _struct(struct):
            r = struct.view().rows()
            r.cell('_name', name='!!File name', width='10em')
            r.cell('_size', name='!!Size', width='5em')
            r.cell('_type', name='!!Type', width='5em')
            for k, v in metacol_dict.items():
                r.cell(k, **v)
            r.cell('_status', name='Status', width='6em')

        if preview:
            self._dropFileGrid_preview(bc, datapath=datapath)

        iv = self.includedViewBox(bc.borderContainer(region='center'), label=label,
                                  storepath='.uploading_data', nodeId=gridId,
                                  struct=_struct, datamode='bag', datapath=datapath,
                                  footer=footer, del_action=True, del_enabled=enabled,
                                  editorEnabled=enabled, autoWidth=True,
                                  onDrop="FIRE .prepare_files=files;FIRE .on_drop = 1000;",
                                  dropTarget_grid='Files',
                                  dropTarget=True,
                                  dropTypes='Files')
        gridEditor = iv.gridEditor()
        for k, v in metacol_dict.items():
            _tag = 'textbox'
            dtype = v.get('dtype')
            widget = v.get('widget')
            if widget:
                _tag = widget
            elif dtype:
                if(dtype == 'I' or dtype == 'R' or dtype == 'N'):
                    _tag = 'numberTextBox'
                elif(dtype == 'D'):
                    _tag = 'dateTextBox'
                elif(dtype == 'B'):
                    _tag = 'checkbox'
            gridEditor.child(_tag, gridcell=k)
        bc.dataController("""genro.wdgById(gridId).editBagRow(null,fired);""", fired='^.on_drop',
                          gridId=gridId, datapath=datapath)
        bc.dataController("""
                dojo.forEach(files,
                            function(f){
                                var row = objectUpdate({_name:f.name,_size:f.size,_type:f.type,_file:f,_uploaderId:uploaderId},external_params);
                                var label = (f.name+'_'+f.size+'_'+f.type).replace(/\W/g,'_');
                                if(filebag.index(label)<0){
                                    var r = new gnr.GnrBag(row);
                                    filebag.setItem(label,r);
                                }
                            });
                """, filebag="=.uploading_data", files='^.prepare_files', datapath=datapath,
                          external_params=external_dict, uploaderId=uploaderId)
        bc.dataController("""
                            genro.rpc.uploadMultipartFiles(filebag,{onResult:funcCreate(onResult,'result',this),
                                                                    onFileUploaded:funcCreate(onFileUploaded,'node',this),
                                                                    uploadPath:uploadPath,uploaderId:uploaderId});
                            """, filebag='=.uploading_data', datapath=datapath,
                          uploaderId=uploaderId, onResult=onResult or '', onFileUploaded=onFileUploaded or '',
                          uploadPath=uploadPath,
                          **{'subscribe_%s_upload' % uploaderId: True})
                          
    def _dropFileGrid_preview(self, bc, datapath=None):
        sc = bc.stackContainer(region='bottom', height='50%', splitter=True, selectedPage='^.selpreview',
                               datapath=datapath)
        sc.dataController("""
                            if(dojo.isSafari){
                                console.log("no filereader, use Firefox")
                                return;
                            }
                            var selectedType = filebag.getItem(selectedLabel+'._type');
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
                        """, selectedLabel="^.selectedLabel", filebag='=.uploading_data',
                          _if='selectedLabel', _else='SET .selpreview  = "no_prev";')
        sc.dataController("""if(selpreview=='image'){
                                SET .preview_img = reader_result;
                                SET .preview_txt=null;
                            }else{
                                SET .preview_txt = reader_result;
                                SET .preview_img = null;
                            }
                           """, reader_result='^.reader_result', selpreview='=.selpreview')
        sc.contentPane(pageName='no_prev').div('no-preview')
        sc.contentPane(pageName='image', overflow='hidden').img(height='100%', src='^.preview_img')
        sc.contentPane(pageName='text').div(innerHTML='^.preview_txt')

    def dropFileGrid_saved_files_grid(self, bc, uploaderId, metacol_dict=None, savedFilesGrid=None):
        def _struct(struct):
            r = struct.view().rows()
            r.cell('_name', name='!!File name', width='10em')
            r.cell('_size', name='!!Size', width='5em')
            r.cell('_type', name='!!Type', width='5em')
            for k, v in metacol_dict.items():
                r.cell(k, **v)
            r.cell('_thumb', name='!!Thumb', width='5em')

        savedFilesGrid['struct'] = savedFilesGrid['struct']
        self.includedViewBox(bc.borderContainer(region='top', height='50%', splitter=True),
                             reloader=savedFilesGrid.pop('reloader', None),
                             label='!!Uploaded elements', datapath='.files_grid', nodeId='%s_uploaded_grid' % uploaderId
                             ,
                             struct=savedFilesGrid['struct'],
                             autoWidth=True, selectionPars=dict(**savedFilesGrid))
    