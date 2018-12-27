# -*- coding: utf-8 -*-

# formclientstore.py
# Created by Francesco Porcari on 2012-05-12.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.web.gnrwebstruct import struct_method
import os

"Store memory"
class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,
                   gnrcomponents/formhandler:FormHandler,
                   gnrcomponents/framegrid:FrameGrid"""

  # def windowTitle(self):
  #     return ''
  # 
  # 
  # def folderPath(self):
  #     return self.site.getStaticPath('pkg:%s' %self.package.name,'testdata','docstore')


  # def documentStoreData(self):
  #     result = Bag()
  #     folder = self.folderPath()
  #     if not os.path.exists(folder):
  #         os.mkdir(folder)
  #     for fname in os.listdir(folder):
  #         fpath = os.path.join(folder,fname)
  #         b = Bag(fpath)
  #         name = os.path.splitext(fname)[1]
  #         result.setItem(name,Bag(path=fpath,name=name,
  #                        description=b['description'],date=b['date']))

  # def test_01_document_item(self,pane):
  #     pass



    def test_4_document_folder(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox('^.folders',lbl='Folders')
        fb.dataRpc('.store','app.getFileSystemSelection',folders='^.folders',columns='name,description,date',include='*.xml')

    def struct_doc(self,struct):
        r = struct.view().rows()
        r.cell('name',width='10em',name='!!Name')
        r.cell('description',width='20em',name='!!Description')
        r.cell('date',dtype='D',width='5em',name='!!Date')

    def test_2_document_view(self,pane):
        frame = pane.borderContainer(height='400px').frameGrid(frameCode='test2',struct=self.struct_doc,
                                    autoToolbar=False,
                                    region='center',
                                    datapath='.view')
        frame.grid.fsStore(childname='store',folders='pkg:test15/testdata/docstore',_onStart=True,_fired='^.reload')

    def test_3_document_collection_form(self,pane):
        view = pane.borderContainer(height='400px').frameGrid(frameCode='test3',struct=self.struct_doc,
                                    autoToolbar=False,
                                    region='center',
                                    datapath='.view')
        view.grid.fsStore(childname='store',folders='pkg:test15/testdata/docstore',_onStart=True,_fired='^.reload')
        form = view.grid.linkedForm(frameCode='F_documents' ,
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='450px',dialog_width='620px',
                                 dialog_title='Ticket',
                                 handlerType='dialog',
                                 childname='form',attachTo=pane,
                                 store='document')
        self.doc_form(form)

    def doc_form(self,form):
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,locker,2')
        fb = form.record.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='Code')
        fb.textbox(value='^.description',lbl='Description')
        fb.dateTextBox(value='^.date',lbl='Date')



        
        