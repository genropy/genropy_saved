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
    def serverPrint(self,pane,name,table_resource=None,datapath=None,parameters_cb=None,
                    selectionName='=list.selectionName',resultpath='.print_result',
                    thermoParams=None,docName=None,rebuild=True,**kwargs):
        datapath = datapath or 'serverprint.%s' %name
        dlgPars = {}
        for k,v in kwargs.items():
            if k.startswith('dlg_'):
                dlgPars[k[4:]] = v
                kwargs.pop(k)        
                    
        self._printOptDialog(pane,name,datapath,dlgPars=dlgPars,parameters_cb=parameters_cb)
        self.buildBatchRunner(pane.div(datapath=datapath), 
                              batch_class='SelectedRecordsToPrint', 
                              table_resource=table_resource,
                              resultpath=resultpath, 
                              rebuild=rebuild,
                              thermoParams=dict(field='*'),
                              selectionName=selectionName,
                              printParams='=.printer.params',fired='^.run',
                              runKwargs='=.parameters.data',**kwargs)    
                                
        pane.dataRpc("dummy","runBatch" ,
                      _onResult='genro.download($1)',
                      table=self.maintable,
                      batch_class='SelectedRecordsToPrint', 
                      table_resource=table_resource,
                      rebuild=rebuild,
                      resultpath=resultpath,thermoParams=dict(field='*'),
                      selectionName=selectionName,pdfParams='=.pdf',
                      docName=docName,selectedRowidx="==genro.wdgById('maingrid').getSelectedRowidx();",
                      _fired='^.dlpdf',runKwargs='=.parameters.data',datapath=datapath)
                             
      
    def _printOptDialog(self,pane,name,datapath,dlgPars=None,parameters_cb=None):
        title = dlgPars.get('title',"!!Print options")
        height = dlgPars.get('height',"200px")
        width = dlgPars.get('width',"450px")
        dialog = pane.dialog(title="!!Print options",nodeId=name,datapath=datapath)
        bc=dialog.borderContainer(height=height,width=width,_class='pbl_roundedGroup')
        bc.dataController('genro.wdgById("%s").hide();' %name,_fired="^.hide" )
        bc.dataController("""var currPrinterOpt = GET _clientCtx.printerSetup.%s;
                             SET .printer.params = currPrinterOpt?currPrinterOpt.deepCopy():new gnr.GnrBag();
                             genro.wdgById("%s").show();""" %(name,name) ,_fired='^.open')
        bottom = bc.contentPane(region='bottom',_class='dialog_bottom')
        bottom.button('!!Close',baseClass='bottom_btn',float='left',margin='1px',fire='.hide')
        bottom.button('!!Pdf',baseClass='bottom_btn',float='right',margin='1px',
                        action='FIRE .dlpdf; FIRE .hide;')
                        
        bottom.button('!!Print',baseClass='bottom_btn',float='right',margin='1px',
                        action="""  FIRE .hide;
                                    var currPrinterOpt = GET .printer.params;
                                    SET _clientCtx.printerSetup.%s = currPrinterOpt.deepCopy(); 
                                    FIRE .run; 
                                    """ %name)
        tc_opt = bc.tabContainer(region='center',margin='5px')
        if parameters_cb:
            parameters_cb(tc_opt,datapath='.parameters')
        self._utl_print_opt(tc_opt)
        self._utl_pdf_opt(tc_opt)
        
    def _utl_print_opt(self,tc):
        pane = tc.contentPane(title='Printer',datapath='.printer')
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
    def rpc_getPrinters(self):
        if self.site.print_handler:
            return self.site.print_handler.getPrinters()
        
    def rpc_getPrinterAttributes(self,printer_name):
        if printer_name!='PDF':
            attributes = self.site.print_handler.getPrinterAttributes(printer_name)
            print attributes
            return attributes

    def _utl_pdf_opt(self,tc):
        pane = tc.contentPane(title='!!Pdf',datapath='.pdf')
        fb= pane.formbuilder(cols=1)
        fb.dataFormula('.zipped','false',_onStart=True)
        fb.checkbox(value='^.zipped',label='!!Zip folder')
        
####################DEPRECATED STUFF###################
    def printDialog(self,data, title=None, _fired=None):
        page = self.pageSource()
        dlgId = data.replace('.','_')
        dlg = page.dialog(nodeId=dlgId, title=title,datapath=data)
        dlg.data('.printers', self.rpc_getPrinters())
        dlg.data('.selected_printer','-')
        page.dataController("genro.wdgById('%s').show()"%dlgId, _fired=_fired)
        tc = dlg.tabContainer(datapath='.params',
                                               height='300px', 
                                               width='420px', nodeId='printDlgStack',
                                               selectedPage='^%s.selPage'%data)
        generalPage = tc.borderContainer(title='!!Print options')
        pdfPage = tc.borderContainer(pageName='pdf')
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
        