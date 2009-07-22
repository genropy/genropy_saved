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
        return self.site.print_handler.getPrinters()
        
    def rpc_getPrinterAttributes(self,printer_name):
        return self.site.print_handler.getPrinterAttributes(printer_name)
        