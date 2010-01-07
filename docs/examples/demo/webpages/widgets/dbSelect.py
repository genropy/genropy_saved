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
        root = self.rootLayoutContainer(root)
        root.data('record.name','John')
        root.data('record.age',23)
        root.data('record.prov','TO')
        #root.dbField(field='utils.anagrafiche.an_provincia')
        fb=root.formbuilder(cols="2", cellspacing='10')
        fb.textbox(lbl='Name', value='^record.name', lbl_color='red')
        fb.NumberTextBox(lbl='Age',value='^record.age')
        fb.dbSelect(lbl='Province', value = '^record.prov',ignoreCase=True,
                           dbtable='utils.province',columns='descrizione')
        fb.textarea(lbl='Notes')
        
        


