# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-10-12.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class PrinterOption(BaseComponent):
    py_requires='foundation/dialogs'
    def onMain_prepare_printer_option_dialog(self):
        dlgBc = self.simpleDialog(self.pageSource(),dlgId='printer_option_dialog',title='!!Server Printer options',
                                datapath='gnr.server_print',height='140px',width='345px')
        dlgBc.dataController("""
                             var currPrinterOpt = this.getRelativeData('_clientCtx.printerSetup.'+resource) || this.getRelativeData('_clientCtx.printerSetup.default');
                             SET .printer.params = currPrinterOpt? currPrinterOpt.deepCopy():new gnr.GnrBag();
                            """,resource_name='^.open')
        dlgBc.dataController("""var currPrinterOpt = GET .printer.params;
                                var defaultParams = this.getRelativeData('_clientCtx.printerSetup.default');
                                var optbag = currPrinterOpt.deepCopy(); 
                                if(!defaultParams){
                                    this.setRelativeData('_clientCtx.printerSetup.default',optbag)
                                }
                                this.setRelativeData('_clientCtx.printerSetup.'+resource_name,optbag); 
                                    """,_fired="^.save",resource_name='=.opener')
        pane = dlgBc.contentPane(region='center',datapath='.options')
        pane.data('.serverPrinters', self.rpc_getPrinters())
        pane.dataRpc('.printer_attributes','getPrinterAttributes',
                    printer_name='^.params.printer_name',_if='printer_name!="PDF"')
        pane.data('.selected_printer','-')
        fb= pane.formbuilder(cols=3,margin='5px')
        ddb = fb.dropDownButton(label='!!Select printer',lbl='!!Printer')
        ddb.menu(storepath='.serverPrinters',action="""SET .selected_printer = $1.fullpath; 
                                                       SET .params.printer_name=$1.name;""")
        fb.div(value='^.params.printer_name',font_size='.9em',font_style='italic',width='15em',colspan=2)
        fb.filteringselect(value='^.params.printer_option.paper',lbl='!!Paper:',width='20em', 
                            colspan=3,storepath='.printer_attributes.paper_supported')
        fb.filteringselect(value='^.params.printer_option.tray',lbl='!!Tray:',width='20em', colspan=3,
                            storepath='.printer_attributes.tray_supported')