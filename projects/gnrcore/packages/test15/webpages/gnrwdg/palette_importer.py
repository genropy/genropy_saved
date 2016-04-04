# -*- coding: UTF-8 -*-

# paletteImporter.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""paletteImporter"""

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """paletteImporter basic example"""
        bc = pane.borderContainer(height='800px')
        fb = bc.contentPane(region='top').formbuilder()
        fb.paletteImporter(paletteCode='testimporter',
                            dockButton_iconClass='iconbox inbox',
                            title='!!Table from csv/xls',
                            importButton_label='Import test',
                            previewLimit=50,
                            dropMessage='Please drop here your file',
                            importButton_action="""
                                    genro.publish('importa_file',{filepath:imported_file_path,name:name})
                                """,
                            importButton_ask=dict(title='Parametrone',fields=[dict(name='name',lbl='Name')]),
                            matchColumns='*')

        fb.dataRpc('dummy',self.importFileTest,subscribe_importa_file=True,
            _onResult="""
                genro.publish('testimporter_onResult',result);
            """,_onError="""
                genro.publish('testimporter_onResult',{error:error});
            """)
        
    def test_2_dropUploader(self,pane):
        fb = pane.formbuilder()

        fb.dropUploader(label='Drop the file to import here',width='300px',onUploadedMethod=self.testUpl,
                        onResult="console.log('finito',evt)",progressBar=True)

        #fb.fileInputBlind(value='^.fileInputBlind',lbl='Import file')

    @public_method
    def testUpl(*args,**kwargs):
        print 'pippo'

    @public_method
    def importFileTest(self,filepath=None,name=None):
        if not name:
            return dict(error='Name required')
        else:
            return dict(message='Import ok',closeImporter=True)

