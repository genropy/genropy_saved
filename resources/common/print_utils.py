#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
import cups
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class PrintUtils(BaseComponent):
    
    def paper_size(self):
        paper_size = {
            'A4': '!!A4',
            'Legal':'!!Legal',
            'A4Small': '!!A4 with margins',
            'COM10': '!!COM10',
            'DL':'!!DL',
            'Letter':'!!Letter',
            'ISOB5':'ISOB5',
            'JISB5':'JISB5',
            'LetterSmall':'LetterSmall',
            'LegalSmall':'LegalSmall'
            }
        return paper_size
    
    def paper_tray(self):
        paper_tray = {
            'MultiPurpose':'!!MultiPurpose',
            'Transparency':'!!Transparency',
            'Upper':'!!Upper',
            'Lower':'!!Lower',
            'LargeCapacity':'!!LargeCapacity'
            }
        return paper_tray
    
    def printDialog(self,data, title=None, _fired=None, parentDialog=None):
        page = self.pageSource()
        dlgId = data.replace('.','_')
        dlg = page.dialog(nodeId=dlgId, title=title,
                          parentDialog=parentDialog,
                          datapath=data)
        dlg.data('.printers', self.rpc_getPrinters())
        dlg.data('.selected_printer','-')
        page.dataController("genro.wdgById('%s').show()"%dlgId, _fired=_fired)
        dlgStackContainer = dlg.stackContainer(datapath='.params',
                                               height='300px', 
                                               width='420px', nodeId='printDlgStack',
                                               selectedPage='^%s.selPage'%data)
        generalPage = dlgStackContainer.borderContainer(pageName='general')
        pdfPage = dlgStackContainer.borderContainer(pageName='pdf')
        pdfPage.button('!!General', float='right', action='SET .selPage="general";')
        bottomBar = generalPage.contentPane(region='bottom', height='25px',datapath=data)
        centerForm = generalPage.contentPane(region='center')
        cfb= centerForm.formbuilder(cols=1)
        cfb.textbox(value='^.selected_printer',
                   lbl='Printer:',readOnly=True).menu(storepath='%s.printers' % data,
                                          modifiers='*',
                                          action='SET .selected_printer = $1.fullpath; SET .printer_name=$1.name;')
        cfb.filteringselect(value='^.printer_options.paper',lbl='!!Paper:', storepath='.printer_attributes.paper_supported')
        cfb.filteringselect(value='^.printer_options.tray',lbl='!!Tray:', storepath='.printer_attributes.tray_supported')
        cfb.dataRpc('.printer_attributes','getPrinterAttributes', printer_name='^.printer_name')
        bottomBar.button('!!PDF', float='right', action='SET .selPage="pdf";')
        
        bottomBar.button('!!Print', float='right', action="FIRE .run; genro.wdgById('%s').hide();"%dlgId)
        bottomBar.button('!!Cancel', float='right', action="genro.wdgById('%s').hide()"%dlgId)
        
    def rpc_getPrinters(self):
        printersBag=Bag()
        cups_connection = cups.Connection()
        for printer_name, printer in cups_connection.getPrinters().items():
            printer.update(dict(name=printer_name))
            printersBag.setItem('%s.%s'%(printer['printer-location'],printer_name),None,printer)
        return printersBag
        
    def rpc_getPrinterAttributes(self,printer_name):
        cups_connection = cups.Connection()
        printer_attributes = cups_connection.getPrinterAttributes(printer_name)
        attributesBag = Bag()
        for i,(media,description) in enumerate(self.paper_size().items()):
            if media in printer_attributes['media-supported']:
                attributesBag.setItem('paper_supported.%i'%i,None,id=media,caption=description)
        for i,(tray,description) in enumerate(self.paper_tray().items()):
            if tray in printer_attributes['media-supported']:
                attributesBag.setItem('tray_supported.%i'%i,None,id=tray,caption=description)
        return attributesBag
        