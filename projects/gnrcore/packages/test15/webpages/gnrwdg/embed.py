# -*- coding: UTF-8 -*-

# drop_uploader.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test drop uploader"""

from gnr.core.gnrlist import XlsReader
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                   gnrcomponents/drop_uploader:DropUploader"""
    css_requires='public'
    def test_0_noCrop(self, pane):
        fb=pane.formbuilder(cols=1)
        pane.data('.pdfurl',"/_site/test/testimages/test.pdf")
        fb.textbox(lbl='Url',value='^.pdfurl',width='50em')
        
        fb.div(height='200px',width='300px',border='1px solid silver').embed(lbl='Pdf',src="^.pdfurl",
                    height='100%',width='100%',zoom='.2')



    def test__embed(self, pane):
        fb=pane.formbuilder(cols=1)
        pane.data('.pdfurl',"/_site/test/testimages/test.pdf")
        fb.textbox(lbl='Url',value='^.pdfurl',width='50em')
        fb.embed(lbl='Pdf',src="^.pdfurl",margin='10px',
                    border='1px solid red',crop_height='400px',crop_width='600px',crop_border='1px solid gray',height='800px',width='1000px',edit=True)

    def test_2_img_uploader_edit(self, pane):
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
          
    def test_3_img_uploader_edit(self, pane):
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
                        
                        
                        

        
        
