#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip, countOf

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.fileInputBlind(label='Sfoglia...',cancel='Annulla',
                            remote_username='pippo',
                            method='uploadImage')
    def main_(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.data('record.name','John')
        root.data('record.age',23)
        root.data('record.email','pironi.matteo@roppodoppo.com')
        root.data('record.prov','TK')
        
        #root.dbField(field='utils.anagrafiche.an_provincia')
        fb=root.formbuilder(cols="2",cellspacing='10')
        fb.textbox(lbl='Name',value='^record.name',lbl_color='red',validate_case='c',required=True,width='auto')
        fb.NumberTextBox(lbl='Age',value='^record.age')
        fb.textbox(lbl='Email', value='^record.email', width='30em',lbl_color='green',validate_email=True)
        fb.dbCombobox(lbl='Province', value = '^record.prov',ignoreCase=True,
                           dbtable='utils.province',columns='descrizione')
    
        fb.dbCombobox(lbl='Localita', value='^record.localita', dbtable='utils.localita', columns='localita')
        fb.button('message',action="genro.dlg.message('Test message....','message',10000, this.getDomNode());")
        fb.button('warning',action="genro.dlg.message('Test warning....','warning',10000, this.getDomNode());")
        fb.button('error',action="genro.dlg.message('Test error....','error',10000, this.getDomNode());")
        fb.button('fatal',action="genro.dlg.message('Test fatal....','fatal',10000, this.getDomNode());")
