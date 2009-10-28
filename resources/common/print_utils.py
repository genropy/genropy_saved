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
                    thermoParams=None,**kwargs):
        datapath = datapath or 'gnr.print.%s' %name
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
                              thermoParams=dict(field='*'),
                              selectionName=selectionName,
                              printParams='=.printer',fired='^.run',
                              runKwargs='=.parameters.data',**kwargs)    
                              
                                
        pane.dataRpc("dummy","runBatch" ,_onCalling="""SET .printer.printer_name = PDF;""",
                      _onResult='console.log("devo fare il dl")'
                             table=self.maintable,
                             batch_class='SelectedRecordsToPrint', 
                             table_resource=table_resource,
                             resultpath=resultpath, 
                             thermoParams=dict(field='*'),
                             selectionName=selectionName,
                             printParams='=.printer',_fired='^.dlpdf',
                             docName='testxx',
                             runKwargs='=.parameters.data',datapath=datapath)
                             
      
    def _printOptDialog(self,pane,name,datapath,dlgPars=None,parameters_cb=None):
        title = dlgPars.get('title',"!!Print options")
        height = dlgPars.get('height',"200px")
        width = dlgPars.get('width',"450px")
        dialog = pane.dialog(title="!!Print options",nodeId=name,datapath=datapath)
        bc=dialog.borderContainer(height=height,width=width,_class='pbl_roundedGroup')
        bc.dataController('genro.wdgById("%s").hide();' %name,_fired="^.hide" )
        bc.dataController('genro.wdgById("%s").show();' %name ,_fired='^.open')
        bottom = bc.contentPane(region='bottom',_class='dialog_bottom')
        bottom.button('!!Close',baseClass='bottom_btn',float='left',margin='1px',fire='.hide')
        bottom.button('!!Pdf',baseClass='bottom_btn',float='right',margin='1px',
                        action='FIRE .dlpdf;')
        bottom.button('!!Print',baseClass='bottom_btn',float='right',margin='1px',
                        action='FIRE .run;')
        tc_opt = bc.tabContainer(region='center',margin='5px')
        if parameters_cb:
            parameters_cb(tc_opt,datapath='.parameters')
        self._utl_print_opt(tc_opt)
        #self._utl_pdf_opt(tc_opt)
        
    def _utl_print_opt(self,tc):
        pane = tc.contentPane(title='Printer',datapath='.printer')
        pane.data('.printers', self.rpc_getPrinters())
        pane.data('.selected_printer','-')
        fb= pane.formbuilder(cols=3,margin='5px')
        fb.dropDownButton(label='!!Select printer',lbl='!!Printer').menu(storepath='.printers',
                         modifiers='*',action='SET .selected_printer = $1.fullpath; SET .printer_name=$1.name;')
        fb.div(value='^.selected_printer',font_size='.9em',font_style='italic',width='15em',colspan=2)
        fb.filteringselect(value='^.printer_options.paper',lbl='!!Paper:',width='20em', colspan=3,storepath='.printer_attributes.paper_supported')
        fb.filteringselect(value='^.printer_options.tray',lbl='!!Tray:',width='20em', colspan=3,storepath='.printer_attributes.tray_supported')
        fb.dataRpc('.printer_attributes','getPrinterAttributes', printer_name='^.printer_name',_if='printer_name=!"PDF"')
        
    def _utl_pdf_opt(self,tc):
        pane = tc.contentPane(title='!!Pdf',datapath='pdf')
        fb= pane.formbuilder(cols=1) 
        fb.textbox(value='^.folder_location',lbl='!!Location')
        fb.checkbox(label='!!Zip folder')
        
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
        
    def rpc_getPrinters(self):
        if self.site.print_handler:
            return self.site.print_handler.getPrinters()
        
    def rpc_getPrinterAttributes(self,printer_name):
        if printer_name!='PDF':
            return self.site.print_handler.getPrinterAttributes(printer_name)
        