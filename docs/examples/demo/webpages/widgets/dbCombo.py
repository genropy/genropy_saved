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

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.data('record.name','John')
        root.data('record.age',23)
        root.data('record.prov','TO')
        #root.dbField(field='utils.anagrafiche.an_provincia')
        fb=root.formbuilder(cols="2", cellspacing='10')
        fb.textbox(lbl='Name', value='^record.name', lbl_color='red')
        fb.NumberTextBox(lbl='Age',value='^record.age')
        fb.dbCombobox(lbl='Province', value = '^record.prov',ignoreCase=True,
                           dbtable='utils.province',columns='descrizione')
        fb.dbCombobox(lbl='Client', value='^record.ragsoc', dbtable='utils.anagrafiche', columns='an_ragione_sociale',
                                   auxColumns='$an_localita,$an_provincia,@an_provincia.@regione.descrizione as regione')
    
        fb.dbCombobox(lbl='Localita', value='^record.localita', dbtable='utils.localita', columns='localita')
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()