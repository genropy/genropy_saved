# -*- coding: UTF-8 -*-

# drop_uploader.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test drop uploader"""

from gnr.core.gnrlist import XlsReader
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                   gnrcomponents/drop_uploader"""
    css_requires='public'

    def test_0_img_uploader(self, pane):
        #pane.img(src='^.avatar_url')
        fb=pane.formbuilder(cols=2)
        # fb.textbox(value='^.id',lbl='Image identifier')
        # fb.textbox(value='^.avatar_url',lbl='Image url',width='30em')
        # pane.imgUploader(value='^.avatar_url',height='100px',width='100px',folder='site:test/testimages',filename='=.id',
        #                 placeholder='http://images.apple.com/euro/home/images/icloud_hero.png')
      
    def test_5_img_uploader_edit(self, pane):
        bc=pane.borderContainer(height='500px')
        top=bc.contentPane(region='top')
        fb=top.formbuilder(cols=1)
     
        fb.textbox(value='^.id',lbl='Image identifier')
        fb.textbox(value='^.avatar_url',lbl='Image url',width='50em')
        center=bc.contentPane(region='center')             
        center.img(src='^.avatar_url',crop_height='200px',crop_width='250px',upload_folder='site:test/testimages',upload_filename='=.id',
                           border='1px solid silver',rounded=8,margin='10px',
                           placeholder='http://images.apple.com/euro/home/images/icloud_hero.png',
                           shadow='2px 2px 5px silver',edit=True,zoomWindow='ImageDeatail' )
          
    def test_9_img_uploader_edit(self, pane):
        bc=pane.borderContainer(height='500px')
        top=bc.contentPane(region='top')
        fb=top.formbuilder(cols=1)
     
        fb.textbox(value='^.id',lbl='Image identifier')
        fb.textbox(value='^.avatar_url',lbl='Image url',width='50em')
        center=bc.contentPane(region='center')             
        center.embed(src='^.avatar_url',height='100%',width='100%',upload_folder='site:test/testimages',upload_filename='=.id',
                           border='1px solid silver',rounded=8,margin='10px',
                           #placeholder='http://images.apple.com/euro/home/images/icloud_hero.png',
                           shadow='2px 2px 5px pink',edit=False,zoomWindow='ImageDeatail' )
                        
                        
                        
    def test_1_uploader(self, pane):
        """File Uploader"""
        pane.data('.pippo','42')
        pane.dropUploader(uploaderId="test_uploader", external_pippo='^.pippo')

    def onUploading_test_uploader(self, file_url=None, file_path=None, file_ext=None, pippo=None,
                                  action_results=None, **kwargs):
        print pippo
        print file_path
        #def test_2_dropFileGrid(self,pane):
        #    """dropFileGrid"""
        #    def footer(footer,**kwargs):
        #        footer.button('Upload',action='PUBLISH foo_uploader_upload',float='right')
        #    self.dropFileGrid(pane.contentPane(height='400px'),uploaderId='foo_uploader',datapath='.uploader',
        #                  label='Upload here',enabled=True,onResult='alert("Done")',
        #                  metacol_description=dict(name='!!Description',width='10em'),footer=footer,
        #                  uploadPath='site:testuploader/foo_up',
        #                  preview=True,uploadedFilesGrid=True)
        #

    def test_3_dropFileGridXLS(self, pane):
        """dropFileGrid xls"""
        bc = pane.borderContainer(height='400px')
        left = bc.borderContainer(region='left', width='40%', margin='5px')
        right = bc.borderContainer(region='right', width='40%', margin='5px')

        center = bc.borderContainer(region='center', margin='5px')

        def footer(footer, **kwargs):
            footer.button('Upload', action='PUBLISH foo_uploader_upload', float='right')

        self.dropFileGrid(left, uploaderId='foo_uploader', datapath='.uploader',
                          label='Upload here', enabled=True,
                          onResult='alert("Done"); FIRE test.test_3_dropFileGridXLS.update_loaded;',
                          metacol_description=dict(name='!!Description', width='10em'), footer=footer,
                          uploadPath='site:testuploader/foo_up',
                          preview=True, uploadedFilesGrid=True)

        pane.dataRpc('.loaded_content', 'getLoadedFiles', _fired='^.update_loaded',
                     uploadPath='site:testuploader/foo_up', _onStart=True)

        def struct(struct):
            r = struct.view().rows()
            r.cell('filename', name='Filename', width='10em')

        iv = self.includedViewBox(center, label='!!loaded content',
                                  datapath='test.test_3_dropFileGridXLS',
                                  storepath='.loaded_content',
                                  selected_filepath='.uploaded_filepath',
                                  hiddencolumns='filepath',
                                  struct=struct)
        pane.dataRpc('#xlsgrid.data', 'xlsRows', docname='^.uploaded_filepath', _onResult='FIRE #xlsgrid.reload;')

        iv = self.includedViewBox(right, label='!!Xls Rows',
                                  nodeId='xlsgrid',
                                  datapath='test.test_3_dropFileGridXLS.xlsgrid',
                                  storepath='.data.store', structpath='.data.struct',
                                  autoWidth=True)
        gridEditor = iv.gridEditor()

    def rpc_xlsRows(self, docname=None):
        result = Bag()
        reader = XlsReader(docname)
        headers = reader.headers
        result['struct'] = self.newGridStruct()
        r = result['struct'].view().rows()
        for colname in headers:
            r.cell(colname, name=colname, width='5em')
        for i, row in enumerate(reader()):
            result.setItem('store.r_%i' % i, None, dict(row))
        return result


    def rpc_getLoadedFiles(self, uploadPath=None, **kwargs):
        path = self.site.getStaticPath(uploadPath)
        result = Bag()
        b = DirectoryResolver(path)
        for i, n in enumerate(
                [(t[1], t[2]) for t in b.digest('#a.file_ext,#a.file_name,#a.abs_path') if t[0] == 'xls']):
            result.setItem('r_%i' % i, None, filename=n[0], filepath=n[1])
        return result


    def onUploading_foo_uploader(self, file_url=None, file_path=None,
                                 description=None, titolo=None, **kwargs):
        result = dict(file_url=file_url, file_path=file_path)
        #reader = XlsReader(file_path)
        #headers = reader.headers()
        #content = list(reader())
        print result
        return result
        

    def test_4_newUploader(self,pane):
        pane.dropFileFrame(height='300px',rounded=6,border='1px solid gray',preview=True,
                            metacol_description=dict(name='!!Description', width='10em'))
    def test_8_movable(self,pane):
        
        pane.div(height='100px',width='150px',overflow='hidden').img(src='http://images.apple.com/euro/home/images/icloud_hero.png',
               margin_top='^.margin_top',margin_left='^.margin_left',
               onCreated="""
                  var that=this;
                  this._onDragImage=function(e){
                     var dx=this.s_x-e.clientX;
                 	 var dy=this.s_y-e.clientY;
                 	 that.s_x=e.clientX;
                      that.s_y=e.clientY;
                 	  var mt=GET .margin_top || '0px';
                      var ml=GET .margin_left || '0px';
                      SET .margin_top=(parseFloat(mt)-dy)+'px';
                      SET .margin_left=(parseFloat(ml)-dx)+'px';
                  };
                  dojo.connect(this.domNode,'ondragstart',function(e){
                        e.stopPropagation();
                        e.preventDefault();
                        that.s_x=e.clientX;
                        that.s_y=e.clientY;
                        var d=dojo.body();
                        d.style.cursor='move'
                        var c1= dojo.connect(d, "onmousemove",that,'_onDragImage');
			            var c2=dojo.connect(d, "onmouseup",  function(e){
			                d.style.cursor='auto'
                 	        dojo.disconnect(c1);
                 	        dojo.disconnect(c2);
                 	        });
                  });
               """)
        
                            
                            
        #var move = new dojo.dnd.Moveable(this.domNode,{ handle: this.focusNode });
    
        
        
