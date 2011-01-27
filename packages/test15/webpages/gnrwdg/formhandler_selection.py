# -*- coding: UTF-8 -*-

# formhandler_selection.py
# Created by Francesco Porcari on 2011-01-18.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method

"Test formhandler selection store"
class GnrCustomWebPage(object):
    user_polling=0
    auto_polling=0
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler,
                  gnrcomponents/palette_manager:PaletteManager"""
    
    @struct_method
    def formTester(self,pane,formId=None,**kwargs):
        form = pane.frameForm(formId=formId,datapath='.provincia',store='provinceRegione',**kwargs)
        form.loader('recordCluster')
        form.saver('recordCluster')
        form.deleter('recordCluster')
        
        form.top.slotBar('prova','navigation,*,|,semaphore,|,formcommands,|,locker')
        fb = form.content.formbuilder(cols=1, border_spacing='4px', width="300px", fld_width="100%")
        fb.field('sigla')
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        return form

         
    def test_0_base(self,pane):
        bc = pane.borderContainer(height='250px')
        bc.selectionStore('provinceRegione',table='glbl.provincia',where='$regione=:r',
                          r='^#selector.regione',_fired='^#selector.reload')
    
        frameGrid = bc.frameGrid('province',region='left',struct='regione',width='300px',
                                store='provinceRegione',
                                autoSelect=True,selectedId='.selectedPkey',
                                selfsubscribe_onSelectedRow='genro.formById("provincia").publish("load",{destPkey:$1.selectedId});',
                                subscribe_form_provincia_onLoaded="this.widget.selectByRowAttr('_pkey',$1.pkey)")
                                
        frameGrid.slotBar('gridtoolbar','*,selector',side='top')
        
        center = bc.contentPane(region='center',border='1px solid blue').formTester(formId='provincia')

         
    def _test_0_includedview_store(self,pane):
        pane = pane.framePane(height='200px')
        pane.slotBar('gridtoolbar','selector,*,searchOn',searchOn=True,wdgNodeId='test_0',side='top')
        pane.includedView(nodeId='test_0',struct='regione',
                        relativeWorkspace=True,datapath='.tblprovince'
                          ).selectionStore(table='glbl.provincia',where='$regione=:r',r='^#selector.regione',_fired='^#selector.reload')
        
        
        
        
    def _test_1_includedview_store(self,pane):
        bc = pane.borderContainer(height='200px')
        bc.selectionStore(storeCode='provinceRegione',table='glbl.provincia',where='$regione=:r',
                          r='^#selector.regione',_fired='^#selector.reload')
        
        pane = bc.framePane(region='left',width='70%',datapath='.A')
        pane.slotBar('gridtoolbar','selector,*,searchOn',searchOn=True,wdgNodeId='test_1_a',side='top')
        pane.includedView(nodeId='test_1_a',struct='full',relativeWorkspace=True,datapath='.tblprovince',
                         storepath='gnr.stores.provinceRegione.data',store='provinceRegione')
                         
                         
        pane = bc.framePane(region='center',datapath='.B')
        pane.slotBar('gridtoolbar_b','*,searchOn',searchOn=True,searchOn_width='8em',wdgNodeId='test_1_b',side='top')
        pane.includedView(nodeId='test_1_b',struct='regione',relativeWorkspace=True,datapath='.tblprovince',
                         storepath='gnr.stores.provinceRegione.data',store='provinceRegione')

        
    @struct_method('gridtoolbar_selector')
    def gridtoolbar_selector(self,pane,wdgNodeId=None,**kwargs):
        fb = pane.formbuilder(cols=2, border_spacing='2px',nodeId='selector')
        fb.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        fb.button('reload',fire='.reload')

    
        