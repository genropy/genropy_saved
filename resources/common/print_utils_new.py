#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent


class PrintUtils(BaseComponent):
    py_requires = 'batch_runner_new:BatchRunner'

    def serverPrint(self, pane, name, table=None, table_resource=None,
                    selectionName='=list.selectionName',
                    selectionFilterCb=None,
                    recordId=None,
                    datapath=None, parameters_cb=None,
                    resultpath='.print_result',
                    docName=None, rebuild=True,
                    gridId='maingrid', batch_class=None,
                    commitAfterPrint=None,
                    selectedRowidx=None, pdfOnly=False,
                    _onResult='', data_method=None,
                    waitingDlg=None, **kwargs):
        table = table or self.maintable
        if not batch_class:
            if recordId:
                batch_class = 'PrintRecord'
                if recordId == '*':
                    recordId = None
            else:
                batch_class = 'PrintSelection'
        if not recordId and not selectedRowidx and not selectionFilterCb:
            selectedRowidx = "==genro.wdgById('%s').getSelectedRowidx();" % gridId
        datapath = datapath or 'serverprint.%s' % name
        dlgPars = {}
        for k, v in kwargs.items():
            if k.startswith('dlg_'):
                dlgPars[k[4:]] = v
                kwargs.pop(k)
        self.printOptDialog(pane, name, datapath, dlgPars=dlgPars, parameters_cb=parameters_cb, pdfOnly=pdfOnly)
        pane.dataController("FIRE .run = 'print';", _if='cachedPrinterParams.getItem("printer_name")',
                            cachedPrinterParams="=_clientCtx.printerSetup.%s" % name,
                            _fired='^.print', _else='genro.dlg.alert(msg,title)',
                            msg='!!No printer selected', title='!!Warning', datapath=datapath)
        batchPars = dict(datapath=datapath,
                         table=table, batch_class=batch_class,
                         table_resource=table_resource,
                         rebuild=rebuild, recordId=recordId,
                         resultpath=resultpath,
                         selectionName=selectionName,
                         selectionFilterCb=selectionFilterCb,
                         commitAfterPrint=commitAfterPrint,
                         docName=docName, selectedRowidx=selectedRowidx,
                         runKwargs='=.parameters.data', batch_note='=.batch.note',
                         batch_forked='=.batch_forked',
                         data_method=data_method, waitingDlg=waitingDlg,
                         **kwargs)
        self.buildBatchRunner(pane, _onResult='if($1){genro.download($1)};%s' % _onResult,
                              pdfParams='=.pdf', fired='^.dlpdf', **batchPars)
        if not pdfOnly:
            self.buildBatchRunner(pane, printParams='=_clientCtx.printerSetup.%s' % name,
                                  _onResult=_onResult, fired='^.run', **batchPars)


    def printOptDialog(self, pane, name, datapath=None, dlgPars=None, parameters_cb=None, pdfOnly=False):
        title = dlgPars.get('title', "!!Print options")
        height = dlgPars.get('height', "200px")
        width = dlgPars.get('width', "500px")
        dialog = pane.dialog(title="!!Print options", nodeId=name, datapath=datapath)
        bc = dialog.borderContainer(height=height, width=width, _class='pbl_roundedGroup')
        bc.dataController('genro.wdgById("%s").hide();' % name, _fired="^.close")
        bc.dataController("""var currPrinterOpt = GET _clientCtx.printerSetup.%s;
                             SET .printer.params = currPrinterOpt? currPrinterOpt.deepCopy():new gnr.GnrBag();
                             genro.wdgById("%s").show();""" % (name, name), _fired='^.open')
        bottom = bc.contentPane(region='bottom', _class='dialog_bottom')

        bottom.button('!!Close', baseClass='bottom_btn', float='left', margin='1px', fire='.close')
        bottom.button('!!Pdf', baseClass='bottom_btn', float='right', margin='1px',
                      action='FIRE .close; FIRE .dlpdf;')
        if not pdfOnly:
            bottom.button('!!Print', baseClass='bottom_btn', float='right', margin='1px',
                          action="""  FIRE .close;
                                    var currPrinterOpt = GET .printer.params;
                                    SET _clientCtx.printerSetup.%s = currPrinterOpt.deepCopy(); 
                                    FIRE .print; 
                                    """ % name)
        bottom.div(float='right').checkbox(value='^.batch.forked', label='!!Forked process',
                                           margin='3px', font_weight='normal')
        center = bc.borderContainer(region='center')
        self._utl_batch_opt(center.contentPane(region='top', datapath='.batch'))
        tc_opt = center.tabContainer(region='center')

        if parameters_cb:
            parameters_cb(tc_opt, datapath='.parameters')
        if not pdfOnly:
            self._utl_print_opt(tc_opt)
        self._utl_pdf_opt(tc_opt)

    def _utl_batch_opt(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px', width='100%')
        fb.textbox(value='^.note', lbl='!!Note', width='100%')

    def _utl_print_opt(self, tc):
        pane = tc.contentPane(title='Printer', datapath='.printer')
        pane.data('.serverPrinters', self.rpc_getPrinters())
        pane.dataRpc('.printer_attributes', 'getPrinterAttributes',
                     printer_name='^.params.printer_name', _if='printer_name!="PDF"')
        pane.data('.selected_printer', '-')
        fb = pane.formbuilder(cols=3, margin='5px')
        ddb = fb.dropDownButton(label='!!Select printer', lbl='!!Printer')
        ddb.menu(storepath='.serverPrinters', action="""SET .selected_printer = $1.fullpath;
                                                       SET .params.printer_name=$1.name;""")
        fb.div(value='^.params.printer_name', font_size='.9em', font_style='italic', width='15em', colspan=2)
        fb.filteringselect(value='^.params.printer_option.paper', lbl='!!Paper:', width='20em',
                           colspan=3, storepath='.printer_attributes.paper_supported')
        fb.filteringselect(value='^.params.printer_option.tray', lbl='!!Tray:', width='20em', colspan=3,
                           storepath='.printer_attributes.tray_supported')

    def rpc_getPrinters(self):
        print_handler = self.getService('print')
        if print_handler:
            return print_handler.getPrinters()

    def rpc_getPrinterAttributes(self, printer_name,**kwargs):
        if printer_name and printer_name != 'PDF':
            attributes = self.getService('print').getPrinterAttributes(printer_name)
            return attributes

    def _utl_pdf_opt(self, tc):
        pane = tc.contentPane(title='!!Pdf', datapath='.pdf')
        fb = pane.formbuilder(cols=1)
        fb.dataFormula('.zipped', 'false', _onStart=True)
        fb.checkbox(value='^.zipped', label='!!Zip folder')

