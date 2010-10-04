# -*- coding: UTF-8 -*-

# dbCombobox.py
# Created by Giovanni Porcari on 2007-03-24.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Tooltip"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        pane.fileInputBlind(label='Sfoglia...',cancel='Annulla',
                            remote_username='pippo',
                            method='uploadImage')
                            
    def test_2_try(self,pane):
        #pane = self.rootLayoutContainer(pane)
        pane.data('record.age',23)
        pane.data('record.email','pironi.matteo@roppodoppo.com')
        pane.data('record.prov','TK')
        
        #pane.dbField(field='utils.anagrafiche.an_provincia')
        fb=pane.formbuilder(cols="2",cellspacing='10')
        fb.textbox(lbl='Name',value='^record.name',lbl_color='red',validate_case='c',required=True,width='auto')
        fb.NumberTextBox(lbl='Age',value='^record.age')
        fb.textbox(lbl='Email', value='^record.email',width='30em',lbl_color='green',validate_email=True)
        fb.dbCombobox(lbl='Province',value='^record.prov',ignoreCase=True,
                      dbtable='utils.province',columns='descrizione')
        fb.dbCombobox(lbl='Localita',value='^record.localita', dbtable='utils.localita', columns='localita')
        fb.button('message',action="genro.dlg.message('Test message....','message',10000, this.getDomNode());")
        fb.button('warning',action="genro.dlg.message('Test warning....','warning',10000, this.getDomNode());")
        fb.button('error',action="genro.dlg.message('Test error....','error',10000, this.getDomNode());")
        fb.button('fatal',action="genro.dlg.message('Test fatal....','fatal',10000, this.getDomNode());")
