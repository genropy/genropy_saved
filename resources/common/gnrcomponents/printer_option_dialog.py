# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-10-12.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class PrinterOption(BaseComponent):
    py_requires = 'foundation/dialogs'

    def onMain_printer_option_controllers(self):
        pane = self.pageSource()
        pane.dataController("""var currPrinterOpt = currPrinterOpt? currPrinterOpt.deepCopy():new gnr.GnrBag();
                                SET gnr.server_print.printer = currPrinterOpt;
                            """, subscribe_onCookieLoaded=True, currPrinterOpt='=_clientCtx.printerSetup',
                            _if='currPrinterOpt')
        pane.dataController("""var optbag = currPrinterOpt.deepCopy(); 
                               SET _clientCtx.printerSetup  =optbag; 
                                    """, subscribe_onCookieSaving=True,
                            currPrinterOpt='=gnr.server_print.printers', _if='currPrinterOpt')


    def server_print_option_fb(self, fb, resource=None):
        datapath='gnr.server_print.printers.%s' % resource
        fb.data('gnr.server_print.serverPrinters', self.rpc_getPrinters())
        fb.dataRpc('gnr.server_print.printer_attributes', 'getPrinterAttributes',
                    printer_name='^.printer_name', _if='printer_name!="PDF"',datapath=datapath)
        fb.data('gnr.server_print.selected_printer', '-')
        ddb = fb.div(innerHTML='==_printer_name?_printer_name:_no_printer',
                    _printer_name='^.printer_name',lbl='!!Printer', _class='fakeTextBox',cursor='pointer',
                    _no_printer='!!No printer',datapath=datapath)
        ddb.menu(storepath='gnr.server_print.serverPrinters',
                 action="""SET gnr.server_print.selected_printer = $1.fullpath;
                                SET .printer_name=$1.name;""",datapath=datapath,modifiers='*')
        fb.filteringselect(value='^.printer_option.paper', lbl='!!Paper',
                           storepath='gnr.server_print.printer_attributes.paper_supported',datapath=datapath)
        fb.filteringselect(value='^.printer_option.tray', lbl='!!Tray',
                           storepath='gnr.server_print.printer_attributes.tray_supported',datapath=datapath)
        return fb

class PrinterOptionDialog(PrinterOption):
    def onMain_prepare_printer_option_dialog(self):
        dlgBc = self.simpleDialog(self.pageSource(), dlgId='printer_option_dialog', title='!!Server Printer options',
                                  datapath='gnr.server_print', height='140px', width='345px')
        dlgBc.contentPane(region='center', datapath='.print_options')
    
        
    
    