# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-10-12.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class PrinterOption(BaseComponent):
    py_requires='foundation/dialogs'
    def onMain_printer_option_controllers(self):
        pane = self.pageSource()
        pane.dataController("""
                             var currPrinterOpt = currPrinterOpt? currPrinterOpt.deepCopy():new gnr.GnrBag();
                             SET gnr.server_print.printer = currPrinterOpt;
                            """,subscribe_onCookieLoaded=True,currPrinterOpt='=_clientCtx.printerSetup',_if='currPrinterOpt')
                            
        pane.dataController("""var optbag = currPrinterOpt.deepCopy(); 
                               SET _clientCtx.printerSetup  =optbag; 
                                    """,subscribe_onCookieSaving=True,
                                    currPrinterOpt='=gnr.server_print.printers',_if='currPrinterOpt')


    def server_print_option_pane(self,pane,resource=None):
        box = pane.div(datapath='gnr.server_print.printers.%s' %resource)
        box.data('gnr.server_print.serverPrinters', self.rpc_getPrinters())
        box.dataRpc('gnr.server_print.printer_attributes','getPrinterAttributes',
                    printer_name='^.printer_name',_if='printer_name!="PDF"')
        box.data('gnr.server_print.selected_printer','-')
        fb= box.formbuilder(cols=3,margin='5px')
        ddb = fb.dropDownButton(label='!!Select printer',lbl='!!Printer')
        ddb.menu(storepath='gnr.server_print.serverPrinters',
                        action="""SET gnr.server_print.selected_printer = $1.fullpath; 
                                SET .printer_name=$1.name;""")
        fb.div(value='^.printer_name',font_size='.9em',font_style='italic',width='15em',colspan=2)
        fb.filteringselect(value='^.printer_option.paper',lbl='!!Paper:',width='20em', 
                            colspan=3,
                            storepath='gnr.server_print.printer_attributes.paper_supported')
        fb.filteringselect(value='^.printer_option.tray',lbl='!!Tray:',width='20em', colspan=3,
                            storepath='gnr.server_print.printer_attributes.tray_supported')
                            
class PrinterOptionDialog(PrinterOption):
    def onMain_prepare_printer_option_dialog(self):
        dlgBc = self.simpleDialog(self.pageSource(),dlgId='printer_option_dialog',title='!!Server Printer options',
                                datapath='gnr.server_print',height='140px',width='345px')
        pane = dlgBc.contentPane(region='center',datapath='.print_options')
    
        
    
    