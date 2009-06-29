#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrwebpage import BaseComponent

# --------------------------- GnrWebPage subclass ---------------------------
class PrintUtils(BaseComponent):
    def buildPrintDlg(self,path, title=None,
                      onAccept='', printerNamePath='',
                      printerOptionsPath='', _fired=None, parentDialog=None):
        page = self.pageSource()
        dlg = page.dialog(nodeId='printer_dlg_%s'%name, title=title,
                          parentDialog=parentDialog)
        dlgStackContainer = dlg.stackContainer(datapath=path,
                                               height='300px', 
                                               width='420px')
        
        pageBase = dlgStackContainer.borderContainer()
        bottomBar = pageBase.contentPane(region='bottom', height='25px')
        centerForm = pageBase.contentPane(region='center')
        cfb= centerForm.formbuilder(cols=1)
        cfb.
        
    def getPrintersBag(self, user = None):
        connection = cups.Connection()
        printersBag=Bag(connection.getPrinters())
        printersMenuValues=Bag(printersBag.digest('#k,#v.printer-info'))